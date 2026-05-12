"""
37_ahn_linear_probe.py -- Linear probe: can compound features predict PPMI?

Clean test of the Ahn hypothesis without GNN graph leakage.
For each ingredient pair, builds pairwise compound features:
  - shared_count (raw Ahn signal)
  - log(shared_count + 1)
  - cosine_sim (compound binary vectors)
  - jaccard (shared / union)
  - dot product of L2-normalized compound vectors

Trains logistic regression (high vs low PPMI median split) and evaluates
Spearman correlation of predicted score with actual PPMI.

Comparison baselines:
  compound -- actual compound features (Ahn signal)
  random   -- random pairwise features (same dim, control)
  degree   -- ingredient degree in PPMI graph only (graph structure baseline)
"""

import json, sqlite3, random
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).parent.parent.parent
DB   = ROOT / "flavorgraph_v5.db"
OUT  = Path(__file__).parent / "37_results.json"

SEEDS      = [42, 123, 2024, 7, 99, 314, 777, 1001, 2000, 9999]
TEST_RATIO = 0.2

# -- Load data ----------------------------------------------------------------
con = sqlite3.connect(DB)
cur = con.cursor()
cur.execute("SELECT id, name FROM ingredient ORDER BY id")
rows_ing = cur.fetchall()
cur.execute("SELECT id FROM compound ORDER BY id")
rows_comp = cur.fetchall()
cur.execute("SELECT ingredient_id, compound_id FROM ingredient_compound")
ic_links = cur.fetchall()
cur.execute("SELECT ing_a, ing_b, npmi_score, shared_count FROM pair_score WHERE ing_a < ing_b")
pairs_raw = cur.fetchall()
con.close()

id2name  = {r[0]: r[1] for r in rows_ing}
name2id  = {r[1]: r[0] for r in rows_ing}
comp2idx = {r[0]: i for i, r in enumerate(rows_comp)}
n_ing    = len(id2name)
n_comp   = len(comp2idx)

# Compound binary vectors per ingredient
comp_vec = np.zeros((n_ing, n_comp), dtype=np.float32)
for ing_id, comp_id in ic_links:
    if ing_id in id2name and comp_id in comp2idx:
        comp_vec[ing_id - 1, comp2idx[comp_id]] = 1.0

# Normalize for cosine
norms = np.linalg.norm(comp_vec, axis=1, keepdims=True) + 1e-8
comp_norm = comp_vec / norms

# Random control vectors (same dim as compound)
np.random.seed(0)
rand_vec = np.random.randn(n_ing, n_comp).astype(np.float32)
rand_norm = rand_vec / (np.linalg.norm(rand_vec, axis=1, keepdims=True) + 1e-8)

print(f"n_ing={n_ing}, n_comp={n_comp}")

# -- Pairs --------------------------------------------------------------------
pairs = [(name2id[a] - 1, name2id[b] - 1, float(p), int(s))
         for a, b, p, s in pairs_raw
         if a in name2id and b in name2id]
print(f"pairs={len(pairs)}")

def make_features(pair_list, vec, norm_vec, use_random=False):
    """Build pairwise feature matrix from compound vectors."""
    idx_a = np.array([p[0] for p in pair_list])
    idx_b = np.array([p[1] for p in pair_list])
    shared = np.array([p[3] for p in pair_list], dtype=np.float32)

    if use_random:
        # Random pairwise features
        ra, rb = rand_vec[idx_a], rand_vec[idx_b]
        cosine   = (rand_norm[idx_a] * rand_norm[idx_b]).sum(axis=1)
        dot      = (ra * rb).sum(axis=1)
        diff_l2  = np.linalg.norm(ra - rb, axis=1)
        log_sh   = np.log(shared + 1)
        jac = np.zeros(len(pair_list))  # meaningless for random
        feats = np.stack([shared, log_sh, cosine, dot, diff_l2, jac], axis=1)
    else:
        va, vb    = vec[idx_a], vec[idx_b]
        na, nb    = norm_vec[idx_a], norm_vec[idx_b]
        cosine    = (na * nb).sum(axis=1)
        dot       = (va * vb).sum(axis=1)
        diff_l2   = np.linalg.norm(va - vb, axis=1)
        union     = (va + vb).clip(0, 1).sum(axis=1)
        jac       = shared / (union + 1e-8)
        log_sh    = np.log(shared + 1)
        feats     = np.stack([shared, log_sh, cosine, dot, diff_l2, jac], axis=1)
    return feats

def run_probe(pair_list_tr, pair_list_te, vec, norm_vec, label, use_random=False):
    X_tr = make_features(pair_list_tr, vec, norm_vec, use_random=use_random)
    X_te = make_features(pair_list_te, vec, norm_vec, use_random=use_random)
    y_tr = np.array([p[2] for p in pair_list_tr])
    y_te = np.array([p[2] for p in pair_list_te])

    med = np.median(y_tr)
    y_tr_bin = (y_tr >= med).astype(int)

    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X_tr)
    X_te_s = scaler.transform(X_te)

    clf = LogisticRegression(max_iter=200, C=1.0)
    clf.fit(X_tr_s, y_tr_bin)
    prob_te = clf.predict_proba(X_te_s)[:, 1]
    sr, _ = spearmanr(prob_te, y_te)
    print(f"  [{label}] spearman={sr:.4f} (coef: {clf.coef_[0]})")
    return float(sr)

# -- Bootstrap ----------------------------------------------------------------
results = {"compound": [], "random": []}

for seed in SEEDS:
    random.seed(seed)
    indices = list(range(len(pairs)))
    random.shuffle(indices)
    n_test       = int(len(indices) * TEST_RATIO)
    test_pairs   = [pairs[i] for i in indices[:n_test]]
    train_pairs  = [pairs[i] for i in indices[n_test:]]
    print(f"\nSeed {seed}: train={len(train_pairs)} test={len(test_pairs)}")

    results["compound"].append(run_probe(train_pairs, test_pairs, comp_vec, comp_norm, "compound"))
    results["random"].append(  run_probe(train_pairs, test_pairs, rand_vec, rand_norm, "random", use_random=True))

# -- Summary ------------------------------------------------------------------
print("\n=== SUMMARY ===")
for key, scores in results.items():
    mean = np.mean(scores)
    std  = np.std(scores)
    print(f"  {key}: mean={mean:.4f} std={std:.4f} scores={[round(s,4) for s in scores]}")

deltas = [c - r for c, r in zip(results["compound"], results["random"])]
mean_d = float(np.mean(deltas))
se_d   = float(np.std(deltas, ddof=1) / np.sqrt(len(deltas)))
ci95   = [mean_d - 2.262 * se_d, mean_d + 2.262 * se_d]
print(f"  delta compound-random: {mean_d:+.4f} CI=[{ci95[0]:.4f},{ci95[1]:.4f}]")
print(f"  significant: {not (ci95[0] < 0 < ci95[1])}")

summary = {
    "compound": {"mean": float(np.mean(results["compound"])), "std": float(np.std(results["compound"])), "scores": results["compound"]},
    "random":   {"mean": float(np.mean(results["random"])),   "std": float(np.std(results["random"])),   "scores": results["random"]},
    "delta":    {"mean": mean_d, "ci_95": ci95, "significant": not (ci95[0] < 0 < ci95[1])},
}

with open(OUT, "w") as f:
    json.dump(summary, f, indent=2)
print(f"\nResults -> {OUT}")
