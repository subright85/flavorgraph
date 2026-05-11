"""
22_beat_mf.py — Strategies to beat BPR-MF (Spearman=0.8361)
Target: Spearman(model_score, pmi_score) > 0.8361

Strategies:
  A: Dual Encoder — 1L-HGN graph embedding + free MF embedding, α-weighted sum
  B: Flavor Profile Input — 10-dim flavor profile as GNN node features (not one-hot)
  C: Hard Negative Mining — Jaccard-high pairs sampled as hard BPR negatives
  D: Dual + Hard Neg — combine A and C
"""

import sqlite3, json, time, os, numpy as np
import torch, torch.nn as nn, torch.nn.functional as F
from scipy.stats import spearmanr

DB_PATH = "flavorgraph_v2.db"
TIME_BUDGET = 180
SEEDS = [42, 123, 2024]
MF_BASELINE = 0.8361

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
    ing_compounds = {i: set() for i in range(n_ing)}
    for ing_id, comp_id in ic_rows:
        if ing_id in id2name and comp_id in comp2idx:
            ii = ing_id - 1
            ci = comp2idx[comp_id]
            ing_edge.append(ii)
            comp_edge.append(ci)
            ing_compounds[ii].add(ci)

    pair_rows = cur.execute(
        "SELECT ing_a, ing_b, pmi_score, shared_count FROM pair_score"
    ).fetchall()
    pairs, jaccards = [], []
    for a, b, pmi, sc in pair_rows:
        if a in name2id and b in name2id:
            ii, jj = name2id[a]-1, name2id[b]-1
            u = len(ing_compounds[ii] | ing_compounds[jj])
            jac = sc / u if u > 0 else 0.0
            pairs.append((ii, jj, float(pmi), jac))

    # Flavor profiles (10-dim, normalized by total)
    CLASS_KEYS = ["alcohol","ester","sulfur","aldehyde","nitrogen","acid","terpene","aromatic","phenol","other"]
    with open("data/ingredient_flavor_profile.json") as f:
        raw_profiles = json.load(f)
    profile_mat = np.zeros((n_ing, len(CLASS_KEYS)), dtype=np.float32)
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
        "ing_compounds": ing_compounds,
        "pairs": pairs, "name2id": name2id,
        "profile_mat": profile_mat,
        "n_profile": len(CLASS_KEYS),
    }


def build_pyg_data(data, device, use_profile=False):
    from torch_geometric.data import HeteroData
    hdata = HeteroData()
    n_ing, n_comp = data["n_ing"], data["n_comp"]
    if use_profile:
        hdata["ingredient"].x = torch.tensor(data["profile_mat"], device=device)
    else:
        hdata["ingredient"].x = torch.eye(n_ing, device=device)
    hdata["compound"].x = torch.eye(n_comp, device=device)
    ing_t = torch.tensor(data["ing_edge"], dtype=torch.long, device=device)
    com_t = torch.tensor(data["comp_edge"], dtype=torch.long, device=device)
    hdata["ingredient", "has", "compound"].edge_index = torch.stack([ing_t, com_t])
    hdata["compound", "rev_has", "ingredient"].edge_index = torch.stack([com_t, ing_t])
    return hdata


# ============================================================
# Models
# ============================================================

class HGTEncoder(nn.Module):
    def __init__(self, in_ing, n_comp, hidden):
        super().__init__()
        from torch_geometric.nn import HGTConv
        self.ing_proj = nn.Linear(in_ing, hidden, bias=False)
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
        edge_index_dict = {k: hdata[k].edge_index for k in hdata.edge_types}
        x_dict = self.conv(x_dict, edge_index_dict)
        return x_dict["ingredient"]


class DualEncoder(nn.Module):
    """Strategy A: z = α·z_graph + (1-α)·z_free"""
    def __init__(self, n_ing, n_comp, hidden):
        super().__init__()
        self.graph_enc = HGTEncoder(n_ing, n_comp, hidden)
        self.free_emb = nn.Embedding(n_ing, hidden)
        nn.init.normal_(self.free_emb.weight, std=0.01)
        self.alpha = nn.Parameter(torch.tensor(0.5))

    def embed(self, hdata, idx):
        z_graph = self.graph_enc(hdata)
        z_free = self.free_emb(idx)
        a = torch.sigmoid(self.alpha)
        return a * z_graph[idx] + (1 - a) * z_free

    def score_all(self, hdata, i_idx, j_idx):
        z_graph = self.graph_enc(hdata)
        z_free = self.free_emb.weight
        a = torch.sigmoid(self.alpha)
        z = a * z_graph + (1 - a) * z_free
        return (z[i_idx] * z[j_idx]).sum(-1)


class ProfileHGN(nn.Module):
    """Strategy B: 10-dim flavor profile as node features"""
    def __init__(self, n_profile, n_comp, hidden):
        super().__init__()
        self.enc = HGTEncoder(n_profile, n_comp, hidden)

    def forward(self, hdata):
        return self.enc(hdata)


# ============================================================
# BPR helpers
# ============================================================

def bpr_loss(pos_s, neg_s):
    return -F.logsigmoid(pos_s - neg_s).mean()


def make_pair_tensors(pairs, device):
    pmi_t = torch.tensor([p[2] for p in pairs], dtype=torch.float, device=device)
    jac_t = torch.tensor([p[3] for p in pairs], dtype=torch.float, device=device)
    pos_i = torch.tensor([p[0] for p in pairs], dtype=torch.long, device=device)
    pos_j = torch.tensor([p[1] for p in pairs], dtype=torch.long, device=device)
    med = pmi_t.median()
    high_idx = (pmi_t >= med).nonzero(as_tuple=True)[0]
    low_idx  = (pmi_t < med).nonzero(as_tuple=True)[0]
    return pmi_t, jac_t, pos_i, pos_j, high_idx, low_idx


def sample_hard_neg(low_idx, jac_t, batch_size):
    """Sample hard negatives weighted by Jaccard similarity."""
    jac_neg = jac_t[low_idx].clamp(min=1e-6)
    probs = jac_neg / jac_neg.sum()
    chosen = torch.multinomial(probs, batch_size, replacement=True)
    return low_idx[chosen]


def spearman(scores, pmi_np):
    r, _ = spearmanr(scores, pmi_np)
    return float(r)


# ============================================================
# Experiment runners
# ============================================================

BATCH = 512
HIDDEN = 64


def run_A_dual(data, seed, time_budget, device):
    """Dual Encoder: HGN + free embedding."""
    torch.manual_seed(seed)
    hdata = build_pyg_data(data, device, use_profile=False)
    pmi_t, jac_t, pos_i, pos_j, high_idx, low_idx = make_pair_tensors(data["pairs"], device)

    model = DualEncoder(data["n_ing"], data["n_comp"], HIDDEN).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)

    t0 = time.time()
    while time.time() - t0 < time_budget:
        pp = high_idx[torch.randint(len(high_idx), (BATCH,))]
        np_ = low_idx[torch.randint(len(low_idx), (BATCH,))]
        ps = model.score_all(hdata, pos_i[pp], pos_j[pp])
        ns = model.score_all(hdata, pos_i[np_], pos_j[np_])
        loss = bpr_loss(ps, ns)
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()

    model.eval()
    with torch.no_grad():
        scores = model.score_all(hdata, pos_i, pos_j).cpu().numpy()
    return spearman(scores, pmi_t.cpu().numpy())


def run_B_profile(data, seed, time_budget, device):
    """Flavor Profile Input: 10-dim features as GNN input."""
    torch.manual_seed(seed)
    hdata = build_pyg_data(data, device, use_profile=True)
    pmi_t, jac_t, pos_i, pos_j, high_idx, low_idx = make_pair_tensors(data["pairs"], device)

    model = ProfileHGN(data["n_profile"], data["n_comp"], HIDDEN).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)

    t0 = time.time()
    while time.time() - t0 < time_budget:
        pp = high_idx[torch.randint(len(high_idx), (BATCH,))]
        np_ = low_idx[torch.randint(len(low_idx), (BATCH,))]
        z = model(hdata)
        ps = (z[pos_i[pp]] * z[pos_j[pp]]).sum(-1)
        ns = (z[pos_i[np_]] * z[pos_j[np_]]).sum(-1)
        loss = bpr_loss(ps, ns)
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()

    model.eval()
    with torch.no_grad():
        z = model(hdata)
        scores = (z[pos_i] * z[pos_j]).sum(-1).cpu().numpy()
    return spearman(scores, pmi_t.cpu().numpy())


def run_C_hardneg(data, seed, time_budget, device):
    """Hard Negative Mining: Jaccard-weighted negative sampling."""
    torch.manual_seed(seed)
    hdata = build_pyg_data(data, device, use_profile=False)
    pmi_t, jac_t, pos_i, pos_j, high_idx, low_idx = make_pair_tensors(data["pairs"], device)

    model = HGTEncoder(data["n_ing"], data["n_comp"], HIDDEN).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)

    t0 = time.time()
    while time.time() - t0 < time_budget:
        pp = high_idx[torch.randint(len(high_idx), (BATCH,))]
        np_ = sample_hard_neg(low_idx, jac_t, BATCH)  # hard negatives!
        z = model(hdata)
        ps = (z[pos_i[pp]] * z[pos_j[pp]]).sum(-1)
        ns = (z[pos_i[np_]] * z[pos_j[np_]]).sum(-1)
        loss = bpr_loss(ps, ns)
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()

    model.eval()
    with torch.no_grad():
        z = model(hdata)
        scores = (z[pos_i] * z[pos_j]).sum(-1).cpu().numpy()
    return spearman(scores, pmi_t.cpu().numpy())


def run_D_dual_hardneg(data, seed, time_budget, device):
    """A + C: Dual Encoder + Hard Negative Mining."""
    torch.manual_seed(seed)
    hdata = build_pyg_data(data, device, use_profile=False)
    pmi_t, jac_t, pos_i, pos_j, high_idx, low_idx = make_pair_tensors(data["pairs"], device)

    model = DualEncoder(data["n_ing"], data["n_comp"], HIDDEN).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)

    t0 = time.time()
    while time.time() - t0 < time_budget:
        pp = high_idx[torch.randint(len(high_idx), (BATCH,))]
        np_ = sample_hard_neg(low_idx, jac_t, BATCH)
        ps = model.score_all(hdata, pos_i[pp], pos_j[pp])
        ns = model.score_all(hdata, pos_i[np_], pos_j[np_])
        loss = bpr_loss(ps, ns)
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()

    model.eval()
    with torch.no_grad():
        scores = model.score_all(hdata, pos_i, pos_j).cpu().numpy()
    return spearman(scores, pmi_t.cpu().numpy())


# ============================================================
# Main
# ============================================================

RUNNERS = [
    ("A_dual_encoder",   run_A_dual),
    ("B_profile_input",  run_B_profile),
    ("C_hard_neg",       run_C_hardneg),
    ("D_dual_hardneg",   run_D_dual_hardneg),
]


def fmt(vals):
    return f"{np.mean(vals):.4f}±{np.std(vals):.4f}"


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    print("Loading data...")
    data = load_data()
    print(f"  {data['n_ing']} ingredients, {len(data['pairs'])} pairs")
    print(f"  Target: BPR-MF baseline = {MF_BASELINE}")

    results = {}
    for tag, runner in RUNNERS:
        print(f"\n--- {tag} ---")
        scores = []
        for seed in SEEDS:
            r = runner(data, seed, TIME_BUDGET, device)
            scores.append(r)
            beat = "✓ BEAT MF" if r > MF_BASELINE else "✗"
            print(f"  seed={seed}  Spearman={r:.4f}  {beat}")
        mean_s = float(np.mean(scores))
        results[tag] = scores
        status = "BEAT MF ★" if mean_s > MF_BASELINE else "below MF"
        print(f"  → {fmt(scores)}  [{status}]")

    print("\n" + "="*55)
    print("=== 22: Beat MF Results (Spearman vs PMI) ===")
    print("="*55)
    print(f"  BPR-MF baseline: {MF_BASELINE}")
    print("-"*40)
    for tag, scores in results.items():
        mean_s = np.mean(scores)
        delta = mean_s - MF_BASELINE
        marker = " ★" if mean_s > MF_BASELINE else ""
        print(f"{tag:<22} {fmt(scores)}  Δ{delta:+.4f}{marker}")

    with open("scripts/gnn/22_results.json", "w") as f:
        json.dump({tag: {"values": v, "mean": float(np.mean(v)), "std": float(np.std(v))}
                   for tag, v in results.items()}, f, indent=2)
    print("\nSaved → scripts/gnn/22_results.json")


if __name__ == "__main__":
    main()
