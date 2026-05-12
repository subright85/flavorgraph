"""
36_v6_compound_feat.py -- v6 architecture: GCN on ingredient-ingredient PPMI graph
with compound binary features as node attributes.

Directly tests the Ahn hypothesis: if compound features help predict PPMI
in a PPMI-weighted graph, compound structure is structurally encoded in recipe
co-occurrence signal.

Comparison:
  compound -- GCN with 983-dim binary compound features (Ahn signal)
  identity  -- GCN with 1094-dim one-hot (baseline, equivalent to HGN w/o IC graph)
  random    -- GCN with random 983-dim features (control, lower bound)
"""

import json, sqlite3, time, random
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy.stats import spearmanr
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv

ROOT = Path(__file__).parent.parent.parent
DB   = ROOT / "flavorgraph_v5.db"
OUT  = Path(__file__).parent / "36_results.json"
LOG  = Path(__file__).parent / "36_log.txt"

SEEDS        = [42, 123, 2024, 7, 99, 314, 777, 1001, 2000, 9999]
TIME_BUDGET  = 180
TEST_RATIO   = 0.2
HIDDEN       = 64

with open(LOG, "w") as _f:
    pass

def log(msg):
    print(msg, flush=True)
    with open(LOG, "a") as f:
        f.write(msg + "\n")

# -- Load data ----------------------------------------------------------------
con = sqlite3.connect(DB)
cur = con.cursor()
cur.execute("SELECT id, name FROM ingredient ORDER BY id")
rows_ing = cur.fetchall()
cur.execute("SELECT id FROM compound ORDER BY id")
rows_comp = cur.fetchall()
cur.execute("SELECT ingredient_id, compound_id FROM ingredient_compound")
ic_links = cur.fetchall()
cur.execute("SELECT ing_a, ing_b, npmi_score FROM pair_score WHERE ing_a < ing_b")
pairs_raw = cur.fetchall()
con.close()

id2name  = {r[0]: r[1] for r in rows_ing}
name2id  = {r[1]: r[0] for r in rows_ing}
comp2idx = {r[0]: i for i, r in enumerate(rows_comp)}
n_ing    = len(id2name)
n_comp   = len(comp2idx)
log(f"n_ing={n_ing}, n_comp={n_comp}")

# -- Feature matrices ---------------------------------------------------------
feat_compound = torch.zeros(n_ing, n_comp)
for ing_id, comp_id in ic_links:
    if ing_id in id2name and comp_id in comp2idx:
        feat_compound[ing_id - 1, comp2idx[comp_id]] = 1.0

feat_identity = torch.eye(n_ing)
torch.manual_seed(0)
feat_random = torch.randn(n_ing, n_comp)

# -- Pairs --------------------------------------------------------------------
pairs = [(name2id[a] - 1, name2id[b] - 1, float(p))
         for a, b, p in pairs_raw
         if a in name2id and b in name2id]
log(f"total_pairs={len(pairs)}")

# -- PPMI graph (positive pairs as edges) -------------------------------------
pos_pairs = [(a, b, p) for a, b, p in pairs if p > 0]
edge_i = torch.tensor([p[0] for p in pos_pairs] + [p[1] for p in pos_pairs], dtype=torch.long)
edge_j = torch.tensor([p[1] for p in pos_pairs] + [p[0] for p in pos_pairs], dtype=torch.long)
edge_index = torch.stack([edge_i, edge_j])
log(f"PPMI edges (positive): {len(pos_pairs)}")

# -- Model --------------------------------------------------------------------
class GCN2(nn.Module):
    def __init__(self, in_dim):
        super().__init__()
        self.proj  = nn.Linear(in_dim, HIDDEN, bias=False)
        self.conv1 = GCNConv(HIDDEN, HIDDEN)
        self.conv2 = GCNConv(HIDDEN, HIDDEN)

    def embed(self, node_feats):
        x = self.proj(node_feats)
        x = F.relu(self.conv1(x, edge_index))
        x = self.conv2(x, edge_index)
        return x

    def score(self, node_feats, i, j):
        z = self.embed(node_feats)
        return (z[i] * z[j]).sum(-1)

def run_seed(feat_matrix, seed, train_pairs, test_pairs, label):
    torch.manual_seed(seed)
    model = GCN2(feat_matrix.shape[1])
    opt   = torch.optim.Adam(model.parameters(), lr=1e-3)

    pmi_tr = torch.tensor([p[2] for p in train_pairs], dtype=torch.float)
    i_tr   = torch.tensor([p[0] for p in train_pairs], dtype=torch.long)
    j_tr   = torch.tensor([p[1] for p in train_pairs], dtype=torch.long)

    med = pmi_tr.median()
    hi  = (pmi_tr >= med).nonzero(as_tuple=True)[0]
    lo  = (pmi_tr <  med).nonzero(as_tuple=True)[0]

    i_te    = torch.tensor([p[0] for p in test_pairs], dtype=torch.long)
    j_te    = torch.tensor([p[1] for p in test_pairs], dtype=torch.long)
    pmi_te  = [p[2] for p in test_pairs]

    t0    = time.time()
    steps = 0
    while time.time() - t0 < TIME_BUDGET:
        pp   = hi[torch.randint(len(hi), (512,))]
        neg  = lo[torch.randint(len(lo), (512,))]
        ps   = model.score(feat_matrix, i_tr[pp],  j_tr[pp])
        ns   = model.score(feat_matrix, i_tr[neg], j_tr[neg])
        loss = -F.logsigmoid(ps - ns).mean()
        opt.zero_grad(); loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        steps += 1

    model.train(False)
    with torch.no_grad():
        te_sc = model.score(feat_matrix, i_te, j_te).numpy()

    sr, _ = spearmanr(te_sc, pmi_te)
    log(f"  [{label}] seed={seed} steps={steps} spearman={sr:.4f}")
    return float(sr)

# -- Bootstrap ----------------------------------------------------------------
results = {"compound": [], "identity": [], "random": []}

for seed in SEEDS:
    random.seed(seed)
    indices = list(range(len(pairs)))
    random.shuffle(indices)
    n_test      = int(len(indices) * TEST_RATIO)
    test_pairs  = [pairs[i] for i in indices[:n_test]]
    train_pairs = [pairs[i] for i in indices[n_test:]]
    log(f"\nSeed {seed}: train={len(train_pairs)} test={len(test_pairs)}")

    results["compound"].append(run_seed(feat_compound, seed, train_pairs, test_pairs, "compound"))
    results["identity"].append(run_seed(feat_identity, seed, train_pairs, test_pairs, "identity"))
    results["random"].append(  run_seed(feat_random,   seed, train_pairs, test_pairs, "random"))

# -- Summary ------------------------------------------------------------------
summary = {}
for key, scores in results.items():
    summary[key] = {
        "scores": scores,
        "mean":   float(np.mean(scores)),
        "std":    float(np.std(scores)),
    }

deltas  = [c - i for c, i in zip(results["compound"], results["identity"])]
n       = len(deltas)
mean_d  = float(np.mean(deltas))
se_d    = float(np.std(deltas, ddof=1) / np.sqrt(n))
ci95    = [mean_d - 2.262 * se_d, mean_d + 2.262 * se_d]

summary["delta_compound_vs_identity"] = {
    "mean":        mean_d,
    "std":         float(np.std(deltas)),
    "ci_95":       ci95,
    "significant": not (ci95[0] < 0 < ci95[1]),
}

log("\n=== SUMMARY ===")
for k in ("compound", "identity", "random"):
    v = summary[k]
    log(f"  {k}: mean={v['mean']:.4f} std={v['std']:.4f}")
d = summary["delta_compound_vs_identity"]
log(f"  delta compound-identity: {d['mean']:+.4f} CI=[{d['ci_95'][0]:.4f},{d['ci_95'][1]:.4f}] significant={d['significant']}")

with open(OUT, "w") as f:
    json.dump(summary, f, indent=2)
log(f"\nResults -> {OUT}")
