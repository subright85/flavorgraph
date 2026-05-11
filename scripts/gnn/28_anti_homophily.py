"""
28_anti_homophily.py — Anti-Homophily HGN
TC idea: compound sharing is anti-correlated with PMI (r=-0.054).
Standard GNN has homophily bias: similar compounds → similar embeddings.
Fix: explicitly subtract the compound-averaged signal from ingredient embeddings.

z_final = z_ing - lambda * z_comp_avg
z_comp_avg[i] = mean(z_compound[c] for c in compounds(i))

This removes compound-similarity from embeddings, leaving complementarity signal.

Proper eval: dedup + 80/20 split. Target: test Spearman > 1L-HGN baseline (0.7174).
"""

import sqlite3, json, time, numpy as np
import torch, torch.nn as nn, torch.nn.functional as F
from scipy.stats import spearmanr

DB_PATH = "flavorgraph_v2.db"
TIME_BUDGET = 180
SEEDS = [42, 123, 2024]
TEST_RATIO = 0.2
HGN_BASELINE = 0.7174

# ============================================================
# Data loading
# ============================================================

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
    pair_rows = cur.execute(
        "SELECT ing_a, ing_b, pmi_score FROM pair_score WHERE ing_a < ing_b"
    ).fetchall()
    pairs = [(name2id[a]-1, name2id[b]-1, float(p))
             for a, b, p in pair_rows if a in name2id and b in name2id]
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
    return hdata, ing_t, com_t


def train_test_split(pairs, seed, test_ratio):
    rng = np.random.RandomState(seed)
    idx = np.arange(len(pairs))
    rng.shuffle(idx)
    n_test = int(len(pairs) * test_ratio)
    return [pairs[i] for i in idx[n_test:]], [pairs[i] for i in idx[:n_test]]


# ============================================================
# Models
# ============================================================

class HGTLayer(nn.Module):
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
            "compound":   self.comp_proj(hdata["compound"].x),
        }
        x_dict = self.conv(x_dict, {k: hdata[k].edge_index for k in hdata.edge_types})
        return x_dict["ingredient"], x_dict["compound"]


class AntiHomophilyHGN(nn.Module):
    """z_final = z_ing - lambda * z_comp_avg (remove compound-similarity signal)"""
    def __init__(self, n_ing, n_comp, hidden, lam=0.5):
        super().__init__()
        self.layer = HGTLayer(n_ing, n_comp, hidden)
        self.lam = nn.Parameter(torch.tensor(float(lam)))

    def get_embeddings(self, hdata, ing_t, com_t):
        z_ing, z_comp = self.layer(hdata)
        n_ing = z_ing.shape[0]
        hidden = z_ing.shape[1]
        # Compute per-ingredient mean of compound embeddings
        z_comp_sum = torch.zeros(n_ing, hidden, device=z_ing.device)
        count = torch.zeros(n_ing, 1, device=z_ing.device)
        z_comp_sum.scatter_add_(0, ing_t.unsqueeze(1).expand(-1, hidden), z_comp[com_t])
        count.scatter_add_(0, ing_t.unsqueeze(1), torch.ones(ing_t.shape[0], 1, device=z_ing.device))
        z_comp_avg = z_comp_sum / (count + 1e-8)
        # Anti-homophily: subtract compound-averaged signal
        lam = torch.sigmoid(self.lam)
        return z_ing - lam * z_comp_avg

    def forward_score(self, hdata, ing_t, com_t, i_idx, j_idx):
        z = self.get_embeddings(hdata, ing_t, com_t)
        return (z[i_idx] * z[j_idx]).sum(-1)


class BaselineHGN(nn.Module):
    def __init__(self, n_ing, n_comp, hidden):
        super().__init__()
        self.layer = HGTLayer(n_ing, n_comp, hidden)

    def forward_score(self, hdata, i_idx, j_idx):
        z_ing, _ = self.layer(hdata)
        return (z_ing[i_idx] * z_ing[j_idx]).sum(-1)


# ============================================================
# Training
# ============================================================

def bpr_loss(pos_s, neg_s):
    return -F.logsigmoid(pos_s - neg_s).mean()


def run_model(model, hdata, ing_t, com_t, train_pairs, test_pairs, seed, time_budget, device, use_anti):
    torch.manual_seed(seed)
    pmi_tr = torch.tensor([p[2] for p in train_pairs], dtype=torch.float, device=device)
    i_tr = torch.tensor([p[0] for p in train_pairs], dtype=torch.long, device=device)
    j_tr = torch.tensor([p[1] for p in train_pairs], dtype=torch.long, device=device)
    pmi_te = torch.tensor([p[2] for p in test_pairs], dtype=torch.float, device=device)
    i_te = torch.tensor([p[0] for p in test_pairs], dtype=torch.long, device=device)
    j_te = torch.tensor([p[1] for p in test_pairs], dtype=torch.long, device=device)
    med = pmi_tr.median()
    hi = (pmi_tr >= med).nonzero(as_tuple=True)[0]
    lo = (pmi_tr < med).nonzero(as_tuple=True)[0]
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    BATCH = 512
    model.train()
    t0 = time.time()
    while time.time() - t0 < time_budget:
        pp = hi[torch.randint(len(hi), (BATCH,))]
        np_ = lo[torch.randint(len(lo), (BATCH,))]
        if use_anti:
            ps = model.forward_score(hdata, ing_t, com_t, i_tr[pp], j_tr[pp])
            ns = model.forward_score(hdata, ing_t, com_t, i_tr[np_], j_tr[np_])
        else:
            ps = model.forward_score(hdata, i_tr[pp], j_tr[pp])
            ns = model.forward_score(hdata, i_tr[np_], j_tr[np_])
        loss = bpr_loss(ps, ns)
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
    model.train(False)
    with torch.no_grad():
        if use_anti:
            tr_sc = model.forward_score(hdata, ing_t, com_t, i_tr, j_tr).cpu().numpy()
            te_sc = model.forward_score(hdata, ing_t, com_t, i_te, j_te).cpu().numpy()
        else:
            tr_sc = model.forward_score(hdata, i_tr, j_tr).cpu().numpy()
            te_sc = model.forward_score(hdata, i_te, j_te).cpu().numpy()
    tr_sp = float(spearmanr(tr_sc, pmi_tr.cpu().numpy()).statistic)
    te_sp = float(spearmanr(te_sc, pmi_te.cpu().numpy()).statistic)
    return tr_sp, te_sp


# ============================================================
# Main
# ============================================================

LAMBDAS = [0.3, 0.5, 0.7]


def fmt(vals):
    return f"{np.mean(vals):.4f}+/-{np.std(vals):.4f}"


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    print("Loading data...")
    data = load_data()
    pairs = data["pairs"]
    print(f"  {data['n_ing']} ingredients, {len(pairs)} unique pairs")
    print(f"  Target: 1L-HGN test baseline={HGN_BASELINE}")

    hdata, ing_t, com_t = build_pyg_data(data, device)

    results = {}

    # Baseline
    tag = "1L-HGN"
    print(f"\n--- {tag} ---")
    tr_list, te_list = [], []
    for seed in SEEDS:
        train_p, test_p = train_test_split(pairs, seed, TEST_RATIO)
        torch.manual_seed(seed)
        model = BaselineHGN(data["n_ing"], data["n_comp"], 64).to(device)
        tr_sp, te_sp = run_model(model, hdata, ing_t, com_t, train_p, test_p, seed, TIME_BUDGET, device, False)
        tr_list.append(tr_sp); te_list.append(te_sp)
        print(f"  seed={seed}  train={tr_sp:.4f}  test={te_sp:.4f}")
    results[tag] = {"train": tr_list, "test": te_list}
    print(f"  -> {fmt(tr_list)}  {fmt(te_list)}")

    # Anti-homophily with different lambda values
    for lam in LAMBDAS:
        tag = f"AntiHomo-lam{lam}"
        print(f"\n--- {tag} ---")
        tr_list, te_list = [], []
        for seed in SEEDS:
            train_p, test_p = train_test_split(pairs, seed, TEST_RATIO)
            torch.manual_seed(seed)
            model = AntiHomophilyHGN(data["n_ing"], data["n_comp"], 64, lam=lam).to(device)
            tr_sp, te_sp = run_model(model, hdata, ing_t, com_t, train_p, test_p, seed, TIME_BUDGET, device, True)
            tr_list.append(tr_sp); te_list.append(te_sp)
            beat = "BEAT" if te_sp > HGN_BASELINE else "x"
            print(f"  seed={seed}  train={tr_sp:.4f}  test={te_sp:.4f}  {beat}")
        results[tag] = {"train": tr_list, "test": te_list}
        te_mean = np.mean(te_list)
        status = "BEAT HGN *" if te_mean > HGN_BASELINE else "below"
        print(f"  -> {fmt(tr_list)}  {fmt(te_list)}  [{status}]")

    print("\n" + "="*70)
    print("=== 28: Anti-Homophily HGN (Proper Eval) ===")
    print("="*70)
    print(f"  Baseline: 1L-HGN test={HGN_BASELINE}")
    print(f"{'Model':<22} {'Train':>18}  {'Test':>16}  delta_test")
    print("-"*72)
    for tag, r in results.items():
        tr = fmt(r["train"]); te = fmt(r["test"])
        delta = np.mean(r["test"]) - HGN_BASELINE
        print(f"{tag:<22} {tr:>18}  {te:>16}  {delta:>+.4f}")

    with open("scripts/gnn/28_results.json", "w") as f:
        json.dump({k: {kk: list(v) for kk, v in vs.items()}
                   for k, vs in results.items()}, f, indent=2)
    print("\nSaved -> scripts/gnn/28_results.json")


if __name__ == "__main__":
    main()
