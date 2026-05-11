"""
Multi-angle analysis of FlavorHGN embeddings.

1. Compound sharing hypothesis (Ahn et al. 2011):
   Do frequently co-occurring pairs share more compounds?

2. t-SNE embedding visualization (save coordinates)

3. GNN score vs PMI vs compound_sim correlation

4. Category-level clustering (using FooDB ingredient categories)

5. Hyperparameter ablation: hidden_dim, num_layers
"""

import torch
import sqlite3
import os
import sys
import random
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from scripts.gnn.model import FlavorHGN

GRAPH_PATH = os.path.join(os.path.dirname(__file__), 'graph.pt')         # 151-node
FINETUNE_CKPT = os.path.join(os.path.dirname(__file__), 'finetune.pt')    # 151-node best
DB_PATH = os.path.join(os.path.dirname(__file__), '../../flavorgraph_v2.db')
DATA_DIR = os.path.join(os.path.dirname(__file__), '../../data')


def load_model_and_data():
    data = torch.load(GRAPH_PATH, weights_only=False)
    n_ing = data['ingredient'].num_nodes
    n_cmp = data['compound'].num_nodes
    model = FlavorHGN(n_ing, n_cmp, 128, 2, 4)
    model.load_state_dict(torch.load(FINETUNE_CKPT, map_location='cpu'))
    model.train(False)
    with torch.no_grad():
        x_dict = model.encode(data)
    return model, data, x_dict


# ── 1. Compound sharing hypothesis ──────────────────────────────────────────

def compound_sharing_hypothesis():
    """
    Ahn et al. (2011): In Western cuisine, co-occurring ingredient pairs
    share more flavor compounds than expected by chance.

    We test: does PMI correlate with shared compound count?
    """
    print("\n=== 1. Compound Sharing Hypothesis (Ahn et al. 2011) ===")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT ing_a, ing_b, pmi_score, combined_score, shared_count
        FROM pair_score
        WHERE ing_a < ing_b
        ORDER BY combined_score DESC
    """)
    rows = cur.fetchall()
    conn.close()

    pairs_with_cmp = [(a, b, pmi, comb, shared)
                      for a, b, pmi, comb, shared in rows if shared > 0]
    pairs_no_cmp = [(a, b, pmi, comb)
                    for a, b, pmi, comb, shared in rows if shared == 0]

    print(f"Pairs with compound overlap: {len(pairs_with_cmp)}")
    print(f"Pairs without compound overlap: {len(pairs_no_cmp)}")

    # PMI stats: pairs with high compound sharing vs low
    def bucket_stats(pairs_by_shared, buckets):
        results = []
        for lo, hi in buckets:
            bucket = [(p, c) for _, _, p, c, s in pairs_with_cmp if lo <= s < hi]
            if bucket:
                avg_pmi = sum(p for p, c in bucket) / len(bucket)
                avg_comb = sum(c for p, c in bucket) / len(bucket)
                results.append((f"{lo}-{hi}", len(bucket), round(avg_pmi, 4), round(avg_comb, 4)))
        return results

    buckets = [(1, 5), (5, 15), (15, 30), (30, 60), (60, 200)]
    print("\nPMI/Score by shared compound count bucket:")
    print(f"  {'bucket':<10} {'n':>6} {'avg_PMI':>10} {'avg_combined':>14}")
    for bucket, n, avg_pmi, avg_comb in bucket_stats(pairs_with_cmp, buckets):
        print(f"  {bucket:<10} {n:>6} {avg_pmi:>10.4f} {avg_comb:>14.4f}")

    # No-compound pairs
    if pairs_no_cmp:
        avg_pmi_nocmp = sum(p for _, _, p, c in pairs_no_cmp) / len(pairs_no_cmp)
        avg_comb_nocmp = sum(c for _, _, p, c in pairs_no_cmp) / len(pairs_no_cmp)
        print(f"\n  No-compound pairs: avg_PMI={avg_pmi_nocmp:.4f}, avg_combined={avg_comb_nocmp:.4f}")

    # Spearman: shared_count vs PMI
    n = len(pairs_with_cmp)
    pmis = [p for _, _, p, _, _ in pairs_with_cmp]
    shareds = [s for _, _, _, _, s in pairs_with_cmp]

    def ranks(lst):
        r = [0] * len(lst)
        for rank, (i, _) in enumerate(sorted(enumerate(lst), key=lambda x: x[1])):
            r[i] = rank + 1
        return r

    rx, ry = ranks(pmis), ranks(shareds)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    den = (sum((rx[i] - mx) ** 2 for i in range(n)) ** 0.5 *
           sum((ry[i] - my) ** 2 for i in range(n)) ** 0.5)
    sp_pmi_cmp = round(num / (den + 1e-9), 4)
    print(f"\nSpearman(PMI, shared_count): {sp_pmi_cmp}")
    print("→ positive = compound sharing correlates with recipe co-occurrence (Ahn hypothesis)")


# ── 2. t-SNE visualization ───────────────────────────────────────────────────

def tsne_analysis():
    print("\n=== 2. t-SNE Embedding Analysis ===")
    model, data, x_dict = load_model_and_data()
    emb = x_dict['ingredient'].numpy()
    names = data['ingredient'].names

    from sklearn.manifold import TSNE
    from sklearn.decomposition import PCA

    # PCA first for speed
    pca_emb = PCA(n_components=50).fit_transform(emb)
    tsne_emb = TSNE(n_components=2, perplexity=30, random_state=42).fit_transform(pca_emb)

    # Save to file for plotting
    import json
    out = [{'name': names[i], 'x': float(tsne_emb[i, 0]), 'y': float(tsne_emb[i, 1])}
           for i in range(len(names))]
    out_path = os.path.join(os.path.dirname(__file__), 'tsne_151.json')
    with open(out_path, 'w') as f:
        json.dump(out, f)
    print(f"  Saved t-SNE coords to {out_path}")

    # Check nearest neighbors for key ingredients
    from sklearn.metrics.pairwise import cosine_similarity
    cos_sim = cosine_similarity(emb)

    anchors = ['garlic', 'lemon', 'butter', 'thyme', 'ginger', 'vanilla', 'cocoa powder']
    print("\nNearest neighbors (cosine similarity in embedding space):")
    for anchor in anchors:
        if anchor not in names:
            continue
        a_idx = names.index(anchor)
        sims = [(cos_sim[a_idx][i], names[i]) for i in range(len(names)) if i != a_idx]
        sims.sort(reverse=True)
        top5 = [f"{n}({s:.3f})" for s, n in sims[:5]]
        print(f"  [{anchor}] → {', '.join(top5)}")


# ── 3. GNN vs PMI vs compound_sim triple correlation ────────────────────────

def triple_correlation():
    print("\n=== 3. GNN Score vs PMI vs Compound Similarity Correlation ===")
    model, data, x_dict = load_model_and_data()
    emb = x_dict['ingredient']
    W = model.decoder.W
    names = data['ingredient'].names
    name_to_idx = {n: i for i, n in enumerate(names)}

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT ing_a, ing_b, pmi_score, combined_score, shared_count
        FROM pair_score WHERE ing_a < ing_b AND pmi_score > 0
    """)
    rows = cur.fetchall()
    conn.close()

    gnn_s, pmi_s, comb_s, cmp_s = [], [], [], []
    for a, b, pmi, comb, shared in rows:
        if a not in name_to_idx or b not in name_to_idx:
            continue
        gnn = (emb[name_to_idx[a]] * W * emb[name_to_idx[b]]).sum().item()
        gnn_s.append(gnn)
        pmi_s.append(pmi)
        comb_s.append(comb)
        cmp_s.append(shared)

    def spearman(xs, ys):
        n = len(xs)
        def ranks(lst):
            r = [0]*n
            for rank, (i, _) in enumerate(sorted(enumerate(lst), key=lambda x: x[1])):
                r[i] = rank + 1
            return r
        rx, ry = ranks(xs), ranks(ys)
        mx, my = sum(rx)/n, sum(ry)/n
        num = sum((rx[i]-mx)*(ry[i]-my) for i in range(n))
        den = (sum((rx[i]-mx)**2 for i in range(n))**0.5 *
               sum((ry[i]-my)**2 for i in range(n))**0.5)
        return round(num/(den+1e-9), 4)

    print(f"  n = {len(gnn_s)} pairs")
    print(f"  Spearman(GNN, PMI):      {spearman(gnn_s, pmi_s)}")
    print(f"  Spearman(GNN, combined): {spearman(gnn_s, comb_s)}")
    print(f"  Spearman(GNN, shared_cmp): {spearman(gnn_s, cmp_s)}")
    print(f"  Spearman(PMI, shared_cmp): {spearman(pmi_s, cmp_s)}")
    print(f"  Spearman(combined, shared_cmp): {spearman(comb_s, cmp_s)}")


# ── 4. Hyperparameter ablation ───────────────────────────────────────────────

def hyperparameter_ablation():
    """Test hidden_dim and num_layers effect on cross-signal Spearman."""
    print("\n=== 4. Hyperparameter Ablation ===")
    import torch.nn.functional as F
    import copy

    data = torch.load(GRAPH_PATH, weights_only=False)
    n_ing = data['ingredient'].num_nodes
    n_cmp = data['compound'].num_nodes
    names = data['ingredient'].names
    name_to_idx = {n: i for i, n in enumerate(names)}

    # Load pairs
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT ing_a, ing_b, combined_score, shared_count
        FROM pair_score WHERE ing_a < ing_b AND combined_score > 0
    """)
    rows = cur.fetchall()
    conn.close()

    all_pairs = [(name_to_idx[a], name_to_idx[b], s, sh)
                 for a, b, s, sh in rows if a in name_to_idx and b in name_to_idx]

    def spearman(xs, ys):
        n = len(xs)
        def ranks(lst):
            r=[0]*n
            for rank,(i,_) in enumerate(sorted(enumerate(lst),key=lambda x:x[1])): r[i]=rank+1
            return r
        rx,ry=ranks(xs),ranks(ys)
        mx,my=sum(rx)/n,sum(ry)/n
        num=sum((rx[i]-mx)*(ry[i]-my) for i in range(n))
        den=(sum((rx[i]-mx)**2 for i in range(n))**0.5*sum((ry[i]-my)**2 for i in range(n))**0.5)
        return round(num/(den+1e-9),4)

    def quick_train_and_spearman(hidden_dim, num_layers, epochs=150):
        model = FlavorHGN(n_ing, n_cmp, hidden_dim, num_layers, 4, 0.1)
        opt = torch.optim.Adam(model.parameters(), lr=5e-4, weight_decay=1e-5)
        train_sorted = sorted(all_pairs, key=lambda x: x[2], reverse=True)
        train_len = len(train_sorted)

        for ep in range(1, epochs+1):
            model.train(); opt.zero_grad()
            bs = min(256, train_len)
            pos = random.sample(train_sorted[:max(1,train_len//2)], bs)
            neg = random.sample(train_sorted[train_len//2:] or train_sorted, bs)
            x_dict = model.encode(data)
            pa = torch.tensor([p[0] for p in pos], dtype=torch.long)
            pb = torch.tensor([p[1] for p in pos], dtype=torch.long)
            nb = torch.tensor([p[1] for p in neg], dtype=torch.long)
            loss = -F.logsigmoid(model.score_pair(x_dict,pa,pb)-model.score_pair(x_dict,pa,nb)).mean()
            loss.backward(); opt.step()

        model.train(False)
        with torch.no_grad():
            x_dict = model.encode(data)
            emb, W = x_dict['ingredient'], model.decoder.W
        gnn_s = [(emb[p[0]]*W*emb[p[1]]).sum().item() for p in all_pairs]
        cmp_s = [p[3] for p in all_pairs]
        return spearman(gnn_s, cmp_s)

    configs = [
        (64, 1), (64, 2), (64, 3),
        (128, 1), (128, 2), (128, 3),
        (256, 1), (256, 2), (256, 3),
    ]

    print(f"  {'hidden_dim':>10} {'num_layers':>10} {'Spearman':>10}")
    print("  " + "-"*35)
    for hd, nl in configs:
        sp = quick_train_and_spearman(hd, nl, epochs=150)
        marker = " ←" if hd == 128 and nl == 2 else ""
        print(f"  {hd:>10} {nl:>10} {sp:>10.4f}{marker}")


if __name__ == '__main__':
    compound_sharing_hypothesis()
    tsne_analysis()
    triple_correlation()
    hyperparameter_ablation()
