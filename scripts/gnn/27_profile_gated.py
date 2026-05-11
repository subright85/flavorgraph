"""
27_profile_gated.py — Profile-Gated HGN
TC idea: s(i,j) = (z_i * gate_i) . (z_j * gate_j)
gate_i = sigmoid(W @ flavor_profile_i)  [10 -> hidden]

Motivation: flavor profile acts as dimension-wise attention over the graph embedding.
Ingredients with different profiles activate different embedding dimensions,
encoding complementarity rather than similarity.

Proper eval: dedup + 80/20 split. Target: beat 1L-HGN test=0.7174.
"""

import sqlite3, json, time, numpy as np
import torch, torch.nn as nn, torch.nn.functional as F
from scipy.stats import spearmanr

DB_PATH = "flavorgraph_v2.db"
TIME_BUDGET = 180
SEEDS = [42, 123, 2024]
TEST_RATIO = 0.2
HGN_BASELINE = 0.7174

CLASS_KEYS = ["alcohol","ester","sulfur","aldehyde","nitrogen","acid","terpene","aromatic","phenol","other"]
N_PROFILE = len(CLASS_KEYS)

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
    pairs = []
    for a, b, pmi in pair_rows:
        if a in name2id and b in name2id:
            pairs.append((name2id[a]-1, name2id[b]-1, float(pmi)))

    with open("data/ingredient_flavor_profile.json") as f:
        raw_profiles = json.load(f)
    profile_mat = np.zeros((n_ing, N_PROFILE), dtype=np.float32)
    for name, vec in raw_profiles.items():
        if name in name2id:
            idx = name2id[name] - 1
            total = max(float(vec.get("total", 1)), 1.0)
            for k, key in enumerate(CLASS_KEYS):
                profile_mat[idx, k] = float(vec.get(key, 0.0)) / total

    con.close()
    return {
        "n_ing": n_ing, "n_comp": n_comp,
        "ing_edge": ing_edge, "comp_edge": comp_edge,
        "pairs": pairs,
        "profile_mat": profile_mat,
    }


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
    return [pairs[i] for i in idx[n_test:]], [pairs[i] for i in idx[:n_test]]


# ============================================================
# Models
# ============================================================

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


class ProfileGatedHGN(nn.Module):
    """s(i,j) = (z_i * g_i) . (z_j * g_j)  where g = sigmoid(W @ profile)"""
    def __init__(self, n_ing, n_comp, hidden, n_profile):
        super().__init__()
        self.encoder = HGTEncoder(n_ing, n_comp, hidden)
        self.gate_proj = nn.Linear(n_profile, hidden)

    def get_gated_emb(self, hdata, profile_t):
        z = self.encoder(hdata)
        gate = torch.sigmoid(self.gate_proj(profile_t))
        return z * gate

    def forward_score(self, hdata, profile_t, i_idx, j_idx):
        z_gated = self.get_gated_emb(hdata, profile_t)
        return (z_gated[i_idx] * z_gated[j_idx]).sum(-1)


class BaselineHGN(nn.Module):
    def __init__(self, n_ing, n_comp, hidden):
        super().__init__()
        self.encoder = HGTEncoder(n_ing, n_comp, hidden)

    def forward_score(self, hdata, i_idx, j_idx):
        z = self.encoder(hdata)
        return (z[i_idx] * z[j_idx]).sum(-1)


# ============================================================
# Training + eval
# ============================================================

def bpr_loss(pos_s, neg_s):
    return -F.logsigmoid(pos_s - neg_s).mean()


def run_model(model, hdata, profile_t, train_pairs, test_pairs, seed, time_budget, device):
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
        if profile_t is not None:
            ps = model.forward_score(hdata, profile_t, i_tr[pp], j_tr[pp])
            ns = model.forward_score(hdata, profile_t, i_tr[np_], j_tr[np_])
        else:
            ps = model.forward_score(hdata, i_tr[pp], j_tr[pp])
            ns = model.forward_score(hdata, i_tr[np_], j_tr[np_])
        loss = bpr_loss(ps, ns)
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()

    model.train(False)
    with torch.no_grad():
        if profile_t is not None:
            tr_sc = model.forward_score(hdata, profile_t, i_tr, j_tr).cpu().numpy()
            te_sc = model.forward_score(hdata, profile_t, i_te, j_te).cpu().numpy()
        else:
            tr_sc = model.forward_score(hdata, i_tr, j_tr).cpu().numpy()
            te_sc = model.forward_score(hdata, i_te, j_te).cpu().numpy()

    tr_sp = float(spearmanr(tr_sc, pmi_tr.cpu().numpy()).statistic)
    te_sp = float(spearmanr(te_sc, pmi_te.cpu().numpy()).statistic)
    return tr_sp, te_sp


# ============================================================
# Main
# ============================================================

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

    hdata = build_pyg_data(data, device)
    profile_t = torch.tensor(data["profile_mat"], dtype=torch.float, device=device)

    MODELS = [
        ("1L-HGN",         False),
        ("ProfileGated",   True),
    ]

    results = {}
    for tag, use_profile in MODELS:
        print(f"\n--- {tag} ---")
        tr_list, te_list = [], []
        for seed in SEEDS:
            train_p, test_p = train_test_split(pairs, seed, TEST_RATIO)
            torch.manual_seed(seed)
            if use_profile:
                model = ProfileGatedHGN(data["n_ing"], data["n_comp"], 64, N_PROFILE).to(device)
                pt = profile_t
            else:
                model = BaselineHGN(data["n_ing"], data["n_comp"], 64).to(device)
                pt = None

            tr_sp, te_sp = run_model(model, hdata, pt, train_p, test_p, seed, TIME_BUDGET, device)
            tr_list.append(tr_sp)
            te_list.append(te_sp)
            beat = "BEAT HGN" if te_sp > HGN_BASELINE else "x"
            print(f"  seed={seed}  train={tr_sp:.4f}  test={te_sp:.4f}  {beat}")

        results[tag] = {"train": tr_list, "test": te_list}
        te_mean = np.mean(te_list)
        status = "BEAT HGN *" if te_mean > HGN_BASELINE else "below HGN"
        print(f"  -> train={fmt(tr_list)}  test={fmt(te_list)}  [{status}]")

    print("\n" + "="*65)
    print("=== 27: Profile-Gated HGN (Proper Eval) ===")
    print("="*65)
    print(f"  1L-HGN baseline: {HGN_BASELINE}")
    print(f"{'Model':<18} {'Train':>18}  {'Test':>16}  delta_test")
    print("-"*65)
    for tag, r in results.items():
        tr = fmt(r["train"])
        te = fmt(r["test"])
        delta = np.mean(r["test"]) - HGN_BASELINE
        print(f"{tag:<18} {tr:>18}  {te:>16}  {delta:>+.4f}")

    with open("scripts/gnn/27_results.json", "w") as f:
        json.dump({k: {kk: list(v) for kk, v in vs.items()}
                   for k, vs in results.items()}, f, indent=2)
    print("\nSaved -> scripts/gnn/27_results.json")


if __name__ == "__main__":
    main()
