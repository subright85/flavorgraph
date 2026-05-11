"""
21_baseline_comparison.py — Baseline comparison for FlavorGraph-HGN
Metric: Spearman(score, pmi_score) — all baselines use same evaluation.

Baselines:
  1. Random — null baseline
  2. Ahn et al. — shared_count (no training)
  3. Jaccard — compound set overlap (no training)
  4. Node2Vec — general graph embedding
  5. BPR-MF — matrix factorization, no graph
  6. 1L-HGN — our method (config B)
"""

import sqlite3, json, time, os, numpy as np
import torch, torch.nn as nn, torch.nn.functional as F
from scipy.stats import spearmanr

DB_PATH = "flavorgraph_v2.db"
TIME_BUDGET = 180  # 3 min per trainable baseline
SEEDS = [42, 123, 2024]

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
    pairs = []
    for a, b, pmi, sc in pair_rows:
        if a in name2id and b in name2id:
            pairs.append((name2id[a]-1, name2id[b]-1, float(pmi), int(sc)))

    con.close()
    return {
        "n_ing": n_ing, "n_comp": n_comp,
        "ing_edge": ing_edge, "comp_edge": comp_edge,
        "ing_compounds": ing_compounds,
        "pairs": pairs, "name2id": name2id,
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


# ============================================================
# Evaluation helper
# ============================================================

def spearman(scores, pmi_vals):
    r, _ = spearmanr(scores, pmi_vals)
    return float(r)


# ============================================================
# Baselines (no training)
# ============================================================

def baseline_random(pairs):
    scores = np.random.randn(len(pairs))
    pmi = np.array([p[2] for p in pairs])
    return spearman(scores, pmi)


def baseline_ahn(pairs):
    """Ahn et al. (2011): shared compound count as pairing score."""
    scores = np.array([float(p[3]) for p in pairs])  # shared_count
    pmi = np.array([p[2] for p in pairs])
    return spearman(scores, pmi)


def baseline_jaccard(pairs, ing_compounds):
    """Jaccard similarity of compound sets."""
    scores = []
    for i, j, pmi, sc in pairs:
        ci, cj = ing_compounds[i], ing_compounds[j]
        u = len(ci | cj)
        jac = sc / u if u > 0 else 0.0
        scores.append(jac)
    pmi = np.array([p[2] for p in pairs])
    return spearman(np.array(scores), pmi)


# ============================================================
# SVD Spectral Embedding (replaces Node2Vec — no extra deps)
# ============================================================

def run_svd_spectral(data):
    """SVD on ingredient×compound binary adjacency → ingredient embeddings."""
    n_ing = data["n_ing"]
    n_comp = data["n_comp"]
    A = np.zeros((n_ing, n_comp), dtype=np.float32)
    for ii, ci in zip(data["ing_edge"], data["comp_edge"]):
        A[ii, ci] = 1.0
    # Truncated SVD — top 64 components
    from numpy.linalg import svd
    U, S, Vt = np.linalg.svd(A, full_matrices=False)
    k = min(64, len(S))
    z = U[:, :k] * S[:k]  # (n_ing, k)

    pairs = data["pairs"]
    scores = np.array([float(np.dot(z[p[0]], z[p[1]])) for p in pairs])
    pmi = np.array([p[2] for p in pairs])
    return spearman(scores, pmi)


# ============================================================
# BPR-MF
# ============================================================

class BPRMF(nn.Module):
    def __init__(self, n_ing, dim=64):
        super().__init__()
        self.emb = nn.Embedding(n_ing, dim)
        nn.init.normal_(self.emb.weight, std=0.01)

    def score(self, i, j):
        return (self.emb(i) * self.emb(j)).sum(-1)


def run_bprmf(data, seed, time_budget, device):
    torch.manual_seed(seed)
    pairs = data["pairs"]
    n_ing = data["n_ing"]
    pmi_t = torch.tensor([p[2] for p in pairs], dtype=torch.float, device=device)
    pos_i = torch.tensor([p[0] for p in pairs], dtype=torch.long, device=device)
    pos_j = torch.tensor([p[1] for p in pairs], dtype=torch.long, device=device)

    med = pmi_t.median()
    high_idx = (pmi_t >= med).nonzero(as_tuple=True)[0]
    low_idx  = (pmi_t < med).nonzero(as_tuple=True)[0]

    model = BPRMF(n_ing, dim=64).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    BATCH = 512

    t0 = time.time()
    while time.time() - t0 < time_budget:
        pp = high_idx[torch.randint(len(high_idx), (BATCH,))]
        np_ = low_idx[torch.randint(len(low_idx), (BATCH,))]
        ps = model.score(pos_i[pp], pos_j[pp])
        ns = model.score(pos_i[np_], pos_j[np_])
        loss = -F.logsigmoid(ps - ns).mean()
        opt.zero_grad(); loss.backward(); opt.step()

    model.eval()
    with torch.no_grad():
        scores = model.score(pos_i, pos_j).cpu().numpy()
    return spearman(scores, pmi_t.cpu().numpy())


# ============================================================
# 1L-HGN (config B reuse from 20_autoresearch)
# ============================================================

class HGTEncoder(nn.Module):
    def __init__(self, n_ing, n_comp, hidden, n_layers):
        super().__init__()
        from torch_geometric.nn import HGTConv
        self.ing_proj = nn.Linear(n_ing, hidden, bias=False)
        self.comp_proj = nn.Linear(n_comp, hidden, bias=False)
        self.convs = nn.ModuleList()
        metadata = (
            ["ingredient", "compound"],
            [("ingredient", "has", "compound"), ("compound", "rev_has", "ingredient")]
        )
        for _ in range(n_layers):
            self.convs.append(HGTConv(hidden, hidden, metadata, heads=2))

    def forward(self, hdata):
        x_dict = {
            "ingredient": self.ing_proj(hdata["ingredient"].x),
            "compound": self.comp_proj(hdata["compound"].x),
        }
        edge_index_dict = {k: hdata[k].edge_index for k in hdata.edge_types}
        for conv in self.convs:
            x_dict = conv(x_dict, edge_index_dict)
        return x_dict["ingredient"]


def run_hgn(data, seed, time_budget, device):
    torch.manual_seed(seed)
    hdata = build_pyg_data(data, device)
    pairs = data["pairs"]
    n_ing, n_comp = data["n_ing"], data["n_comp"]
    pmi_t = torch.tensor([p[2] for p in pairs], dtype=torch.float, device=device)
    pos_i = torch.tensor([p[0] for p in pairs], dtype=torch.long, device=device)
    pos_j = torch.tensor([p[1] for p in pairs], dtype=torch.long, device=device)

    med = pmi_t.median()
    high_idx = (pmi_t >= med).nonzero(as_tuple=True)[0]
    low_idx  = (pmi_t < med).nonzero(as_tuple=True)[0]

    model = HGTEncoder(n_ing, n_comp, hidden=64, n_layers=1).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    BATCH = 512

    t0 = time.time()
    while time.time() - t0 < time_budget:
        pp = high_idx[torch.randint(len(high_idx), (BATCH,))]
        np_ = low_idx[torch.randint(len(low_idx), (BATCH,))]
        z = model(hdata)
        ps = (z[pos_i[pp]] * z[pos_j[pp]]).sum(-1)
        ns = (z[pos_i[np_]] * z[pos_j[np_]]).sum(-1)
        loss = -F.logsigmoid(ps - ns).mean()
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()

    model.eval()
    with torch.no_grad():
        z = model(hdata)
        scores = (z[pos_i] * z[pos_j]).sum(-1).cpu().numpy()
    return spearman(scores, pmi_t.cpu().numpy())


# ============================================================
# Main
# ============================================================

def fmt(vals):
    return f"{np.mean(vals):.4f}±{np.std(vals):.4f}"


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    print("Loading data...")
    data = load_data()
    pairs = data["pairs"]
    pmi = np.array([p[2] for p in pairs])
    print(f"  {data['n_ing']} ingredients, {len(pairs)} pairs")

    results = {}

    # --- Analytical baselines (no training, single pass) ---
    np.random.seed(42)
    r_random = np.mean([baseline_random(pairs) for _ in range(3)])
    results["Random"] = ([r_random], "analytical")
    print(f"\nRandom:  Spearman={r_random:.4f}")

    r_ahn = baseline_ahn(pairs)
    results["Ahn (shared_count)"] = ([r_ahn], "analytical")
    print(f"Ahn:     Spearman={r_ahn:.4f}")

    r_jac = baseline_jaccard(pairs, data["ing_compounds"])
    results["Jaccard"] = ([r_jac], "analytical")
    print(f"Jaccard: Spearman={r_jac:.4f}")

    # --- SVD spectral (analytical, no training) ---
    print("\nSVD Spectral:")
    r_svd = run_svd_spectral(data)
    results["SVD Spectral"] = ([r_svd], "analytical")
    print(f"  Spearman={r_svd:.4f}")

    print("\nBPR-MF:")
    mf_scores = []
    for seed in SEEDS:
        r = run_bprmf(data, seed, TIME_BUDGET, device)
        mf_scores.append(r)
        print(f"  seed={seed}  Spearman={r:.4f}")
    results["BPR-MF"] = (mf_scores, "trainable")
    print(f"  → {fmt(mf_scores)}")

    print("\n1L-HGN (ours):")
    hgn_scores = []
    for seed in SEEDS:
        r = run_hgn(data, seed, TIME_BUDGET, device)
        hgn_scores.append(r)
        print(f"  seed={seed}  Spearman={r:.4f}")
    results["1L-HGN"] = (hgn_scores, "trainable")
    print(f"  → {fmt(hgn_scores)}")

    # --- Summary ---
    print("\n" + "="*55)
    print("=== 21: Baseline Comparison (Spearman vs PMI) ===")
    print("="*55)
    print(f"{'Method':<22} {'Spearman':>14}")
    print("-"*38)
    for name, (vals, kind) in results.items():
        marker = " ★" if name == "1L-HGN" else ""
        if len(vals) == 1:
            print(f"{name:<22} {vals[0]:.4f}      {marker}")
        else:
            print(f"{name:<22} {fmt(vals)}{marker}")

    out = {name: {"values": vals, "mean": float(np.mean(vals)), "std": float(np.std(vals))}
           for name, (vals, _) in results.items()}
    with open("scripts/gnn/21_results.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nSaved → scripts/gnn/21_results.json")


if __name__ == "__main__":
    main()
