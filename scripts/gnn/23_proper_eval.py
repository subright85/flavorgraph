"""
23_proper_eval.py — Proper train/test split evaluation
Fixes: (1) pair deduplication (WHERE ing_a < ing_b), (2) 80/20 split, (3) held-out test evaluation

Compares: BPR-MF vs 1L-HGN vs Dual Encoder on held-out test pairs.
"""

import sqlite3, json, time, numpy as np
import torch, torch.nn as nn, torch.nn.functional as F
from scipy.stats import spearmanr

DB_PATH = "flavorgraph_v2.db"
TIME_BUDGET = 180
SEEDS = [42, 123, 2024]
TEST_RATIO = 0.2

def load_data():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    rows = cur.execute("SELECT id, name FROM ingredient ORDER BY id").fetchall()
    id2name = {r[0]: r[1] for r in rows}
    name2id = {r[1]: r[0] for r in rows}
    n_ing = len(id2name)

    comp_rows = cur.execute("SELECT id FROM compound ORDER BY id").fetchall()
    n_comp = len(comp_rows)
    comp_ids = [r[0] for r in comp_rows]
    comp2idx = {cid: i for i, cid in enumerate(comp_ids)}

    ic_rows = cur.execute("SELECT ingredient_id, compound_id FROM ingredient_compound").fetchall()
    ing_edge, comp_edge = [], []
    for ing_id, comp_id in ic_rows:
        if ing_id in id2name and comp_id in comp2idx:
            ing_edge.append(ing_id - 1)
            comp_edge.append(comp2idx[comp_id])

    # DEDUPLICATION: only ing_a < ing_b
    pair_rows = cur.execute(
        "SELECT ing_a, ing_b, pmi_score FROM pair_score WHERE ing_a < ing_b"
    ).fetchall()
    pairs = []
    for a, b, pmi in pair_rows:
        if a in name2id and b in name2id:
            pairs.append((name2id[a]-1, name2id[b]-1, float(pmi)))

    con.close()
    return {"n_ing": n_ing, "n_comp": n_comp,
            "ing_edge": ing_edge, "comp_edge": comp_edge, "pairs": pairs}

def build_pyg_data(data, device):
    from torch_geometric.data import HeteroData
    hdata = HeteroData()
    n_ing, n_comp = data["n_ing"], data["n_comp"]
    hdata["ingredient"].x = torch.eye(n_ing, device=device)
    hdata["compound"].x = torch.eye(n_comp, device=device)
    ing_t = torch.tensor(data["ing_edge"], dtype=torch.long, device=device)
    com_t = torch.tensor(data["comp_edge"], dtype=torch.long, device=device)
    hdata["ingredient", "has", "compound"].edge_index = torch.stack([ing_t, com_t])
    hdata["compound", "rev_has", "ingredient"].edge_index = torch.stack([com_t, ing_t])
    return hdata

def train_test_split(pairs, seed, test_ratio):
    rng = np.random.RandomState(seed)
    idx = np.arange(len(pairs))
    rng.shuffle(idx)
    n_test = int(len(pairs) * test_ratio)
    test_idx = idx[:n_test]
    train_idx = idx[n_test:]
    train = [pairs[i] for i in train_idx]
    test  = [pairs[i] for i in test_idx]
    return train, test

class BPRMF(nn.Module):
    def __init__(self, n_ing, dim=64):
        super().__init__()
        self.emb = nn.Embedding(n_ing, dim)
        nn.init.normal_(self.emb.weight, std=0.01)
    def score(self, i, j):
        return (self.emb(i) * self.emb(j)).sum(-1)

class HGTEncoder(nn.Module):
    def __init__(self, n_ing, n_comp, hidden):
        super().__init__()
        from torch_geometric.nn import HGTConv
        self.ing_proj = nn.Linear(n_ing, hidden, bias=False)
        self.comp_proj = nn.Linear(n_comp, hidden, bias=False)
        metadata = (
            ["ingredient", "compound"],
            [("ingredient", "has", "compound"), ("compound", "rev_has", "ingredient")]
        )
        self.conv = HGTConv(hidden, hidden, metadata, heads=2)
    def forward(self, hdata):
        x_dict = {
            "ingredient": self.ing_proj(hdata["ingredient"].x),
            "compound": self.comp_proj(hdata["compound"].x),
        }
        x_dict = self.conv(x_dict, {k: hdata[k].edge_index for k in hdata.edge_types})
        return x_dict["ingredient"]


class DualEncoder(nn.Module):
    """z = sigmoid(α)·z_graph + (1-sigmoid(α))·z_free"""
    def __init__(self, n_ing, n_comp, hidden):
        super().__init__()
        self.graph_enc = HGTEncoder(n_ing, n_comp, hidden)
        self.free_emb = nn.Embedding(n_ing, hidden)
        nn.init.normal_(self.free_emb.weight, std=0.01)
        self.alpha = nn.Parameter(torch.tensor(0.5))
    def forward(self, hdata):
        z_graph = self.graph_enc(hdata)
        z_free = self.free_emb.weight
        a = torch.sigmoid(self.alpha)
        return a * z_graph + (1 - a) * z_free

def make_bpr_tensors(pairs, device):
    pmi_t = torch.tensor([p[2] for p in pairs], dtype=torch.float, device=device)
    i_t = torch.tensor([p[0] for p in pairs], dtype=torch.long, device=device)
    j_t = torch.tensor([p[1] for p in pairs], dtype=torch.long, device=device)
    med = pmi_t.median()
    hi = (pmi_t >= med).nonzero(as_tuple=True)[0]
    lo = (pmi_t < med).nonzero(as_tuple=True)[0]
    return pmi_t, i_t, j_t, hi, lo

def bpr_loss(pos_s, neg_s):
    return -F.logsigmoid(pos_s - neg_s).mean()

def run_model(model_fn, data, train_pairs, test_pairs, seed, time_budget, device):
    torch.manual_seed(seed)
    pmi_tr, i_tr, j_tr, hi_tr, lo_tr = make_bpr_tensors(train_pairs, device)
    pmi_te = torch.tensor([p[2] for p in test_pairs], dtype=torch.float, device=device)
    i_te = torch.tensor([p[0] for p in test_pairs], dtype=torch.long, device=device)
    j_te = torch.tensor([p[1] for p in test_pairs], dtype=torch.long, device=device)

    model, hdata = model_fn(data, device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    BATCH = 512

    t0 = time.time()
    while time.time() - t0 < time_budget:
        pp = hi_tr[torch.randint(len(hi_tr), (BATCH,))]
        np_ = lo_tr[torch.randint(len(lo_tr), (BATCH,))]
        if hdata is not None:
            z = model(hdata)
            ps = (z[i_tr[pp]] * z[j_tr[pp]]).sum(-1)
            ns = (z[i_tr[np_]] * z[j_tr[np_]]).sum(-1)
        else:
            ps = model.score(i_tr[pp], j_tr[pp])
            ns = model.score(i_tr[np_], j_tr[np_])
        loss = bpr_loss(ps, ns)
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()

    model.eval()
    with torch.no_grad():
        if hdata is not None:
            z = model(hdata)
            train_scores = (z[i_tr] * z[j_tr]).sum(-1).cpu().numpy()
            test_scores  = (z[i_te] * z[j_te]).sum(-1).cpu().numpy()
        else:
            train_scores = model.score(i_tr, j_tr).cpu().numpy()
            test_scores  = model.score(i_te, j_te).cpu().numpy()

    train_sp = float(spearmanr(train_scores, pmi_tr.cpu().numpy()).statistic)
    test_sp  = float(spearmanr(test_scores,  pmi_te.cpu().numpy()).statistic)
    return train_sp, test_sp

def mf_factory(data, device):
    return BPRMF(data["n_ing"], dim=64).to(device), None

def hgn_factory(data, device):
    hdata = build_pyg_data(data, device)
    model = HGTEncoder(data["n_ing"], data["n_comp"], hidden=64).to(device)
    return model, hdata

def dual_factory(data, device):
    hdata = build_pyg_data(data, device)
    model = DualEncoder(data["n_ing"], data["n_comp"], hidden=64).to(device)
    return model, hdata

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    print("Loading data (deduplicated pairs)...")
    data = load_data()
    pairs = data["pairs"]
    print(f"  {data['n_ing']} ingredients, {len(pairs)} unique pairs (deduped)")

    results = {}
    for model_name, factory in [("BPR-MF", mf_factory), ("1L-HGN", hgn_factory), ("DualEncoder", dual_factory)]:
        print(f"\n--- {model_name} ---")
        tr_scores, te_scores = [], []
        for seed in SEEDS:
            train_p, test_p = train_test_split(pairs, seed, TEST_RATIO)
            tr_sp, te_sp = run_model(factory, data, train_p, test_p, seed, TIME_BUDGET, device)
            tr_scores.append(tr_sp)
            te_scores.append(te_sp)
            print(f"  seed={seed}  train_Spearman={tr_sp:.4f}  test_Spearman={te_sp:.4f}")
        results[model_name] = {"train": tr_scores, "test": te_scores}
        print(f"  → train={np.mean(tr_scores):.4f}±{np.std(tr_scores):.4f}  test={np.mean(te_scores):.4f}±{np.std(te_scores):.4f}")

    print("\n" + "="*60)
    print("=== 23: Proper Eval (Train/Test Split, Deduped Pairs) ===")
    print("="*60)
    print(f"{'Model':<12} {'Train Spearman':>18}  {'Test Spearman':>16}")
    print("-"*50)
    for name, r in results.items():
        tr = f"{np.mean(r['train']):.4f}±{np.std(r['train']):.4f}"
        te = f"{np.mean(r['test']):.4f}±{np.std(r['test']):.4f}"
        print(f"{name:<12} {tr:>18}  {te:>16}")

    with open("scripts/gnn/23_results.json", "w") as f:
        json.dump({k: {kk: list(v) for kk, v in vs.items()} for k, vs in results.items()}, f, indent=2)
    print("\nSaved → scripts/gnn/23_results.json")

if __name__ == "__main__":
    main()
