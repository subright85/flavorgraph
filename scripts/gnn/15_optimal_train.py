"""
Final optimal training: hidden=64, layers=3, BPR-only, combined_score target.

Findings from sensitivity analysis:
- SimGRACE pretrain hurts (-0.02 Spearman) — dropped
- alpha=0.8 tfidf + 0.2 PMI (combined_score) optimal
- Temperature/noise_std don't matter for SimGRACE

Runs 5 seeds, reports mean ± std.
Saves best checkpoint as finetune_optimal.pt.
Also reports full ranking metrics (Hit@10, MRR) + cross-signal Spearman.
"""

import torch
import torch.nn.functional as F
import sqlite3, os, sys, random, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from scripts.gnn.model import FlavorHGN

GRAPH_PATH = os.path.join(os.path.dirname(__file__), 'graph.pt')
CKPT_PATH  = os.path.join(os.path.dirname(__file__), 'finetune_optimal.pt')
DB_PATH    = os.path.join(os.path.dirname(__file__), '../../flavorgraph_v2.db')

HIDDEN = 64
LAYERS = 3
HEADS  = 4
DROPOUT = 0.1
EPOCHS  = 300
LR      = 5e-4
BATCH   = 256
TEST_SPLIT = 0.1
SEEDS = [42, 123, 7, 2024, 99]


def spearman(xs, ys):
    n = len(xs)
    def ranks(lst):
        r = [0]*n
        for rank, (i, _) in enumerate(sorted(enumerate(lst), key=lambda x: x[1])):
            r[i] = rank+1
        return r
    rx, ry = ranks(xs), ranks(ys)
    mx, my = sum(rx)/n, sum(ry)/n
    num = sum((rx[i]-mx)*(ry[i]-my) for i in range(n))
    den = (sum((rx[i]-mx)**2 for i in range(n))**0.5 *
           sum((ry[i]-my)**2 for i in range(n))**0.5)
    return round(num/(den+1e-9), 4)


def ndcg_at_k(ranked_rel, k):
    def dcg(rs, k):
        return sum((2**r-1)/math.log2(i+2) for i,r in enumerate(rs[:k]))
    ideal = dcg(sorted(ranked_rel, reverse=True), k)
    return 0.0 if ideal == 0 else dcg(ranked_rel, k)/ideal


def ranking_metrics(model, data, test_pairs, all_pairs, n_ing, k=10, n_samples=300):
    pos_by_anchor = {}
    for a, b, _ in all_pairs:
        pos_by_anchor.setdefault(a, set()).add(b)
        pos_by_anchor.setdefault(b, set()).add(a)

    model.train(False)
    with torch.no_grad():
        x_dict = model.encode(data)
        emb, W = x_dict['ingredient'], model.decoder.W

    hit, ndcg_vals, rr = [], [], []
    for anchor, pos_idx, _ in random.sample(test_pairs, min(n_samples, len(test_pairs))):
        scores = (emb[anchor] * W * emb).sum(dim=-1)
        scores[anchor] = float('-inf')
        ranked = scores.argsort(descending=True).tolist()
        positives = pos_by_anchor.get(anchor, set())
        ranked_rel = [1 if i in positives else 0 for i in ranked[:k]]
        hit.append(1.0 if pos_idx in ranked[:k] else 0.0)
        ndcg_vals.append(ndcg_at_k(ranked_rel, k))
        rank = next((r+1 for r,i in enumerate(ranked) if i == pos_idx), n_ing)
        rr.append(1.0/rank)

    n = len(hit)
    return {f'Hit@{k}': round(sum(hit)/n, 4),
            f'NDCG@{k}': round(sum(ndcg_vals)/n, 4),
            'MRR': round(sum(rr)/n, 4)}


def train_one_seed(data, all_pairs, train_pairs, test_pairs, seed):
    random.seed(seed); torch.manual_seed(seed)
    n_ing = data['ingredient'].num_nodes
    n_cmp = data['compound'].num_nodes

    model = FlavorHGN(n_ing, n_cmp, HIDDEN, LAYERS, HEADS, DROPOUT)
    opt = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=1e-5)
    sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=EPOCHS)

    train_sorted = sorted(train_pairs, key=lambda x: x[2], reverse=True)
    train_len = len(train_sorted)

    for ep in range(EPOCHS):
        model.train(); opt.zero_grad()
        bs = min(BATCH, train_len)
        pos = random.sample(train_sorted[:max(1, train_len//2)], bs)
        neg = random.sample(train_sorted[train_len//2:] or train_sorted, bs)
        x_dict = model.encode(data)
        pa = torch.tensor([p[0] for p in pos], dtype=torch.long)
        pb = torch.tensor([p[1] for p in pos], dtype=torch.long)
        nb = torch.tensor([p[1] for p in neg], dtype=torch.long)
        loss = -F.logsigmoid(model.score_pair(x_dict,pa,pb)-model.score_pair(x_dict,pa,nb)).mean()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step(); sch.step()

    model.train(False)
    with torch.no_grad():
        x_dict = model.encode(data)
        emb, W = x_dict['ingredient'], model.decoder.W

    # Cross-signal Spearman
    gnn_s = [(emb[p[0]]*W*emb[p[1]]).sum().item() for p in all_pairs]
    cmp_s = [p[3] for p in all_pairs]  # shared_count
    sp = spearman(gnn_s, cmp_s)

    # Ranking
    m = ranking_metrics(model, data, test_pairs, [(a,b,s) for a,b,s,_ in all_pairs], n_ing)

    return model, sp, m


def run():
    data = torch.load(GRAPH_PATH, weights_only=False)
    names = data['ingredient'].names
    name_to_idx = {n: i for i, n in enumerate(names)}
    n_ing = data['ingredient'].num_nodes

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

    # Fixed 90/10 split (seed=0 for reproducibility of split)
    rng = random.Random(0)
    shuffled = list(all_pairs)
    rng.shuffle(shuffled)
    split = int(len(shuffled) * (1 - TEST_SPLIT))
    train_pairs = shuffled[:split]
    test_pairs_raw = shuffled[split:]
    test_pairs = [(a, b, s) for a, b, s, _ in test_pairs_raw]

    print(f"Graph: {n_ing} ingredients, {data['compound'].num_nodes} compounds")
    print(f"Pairs: {len(all_pairs)} total, {len(train_pairs)} train, {len(test_pairs)} test")
    print(f"Config: hidden={HIDDEN}, layers={LAYERS}, epochs={EPOCHS}, lr={LR}")
    print(f"Seeds: {SEEDS}\n")
    print(f"  {'Seed':>6} {'Spearman':>10} {'Hit@10':>8} {'NDCG@10':>9} {'MRR':>7}")
    print("  " + "-"*45)

    sps, hits, mrrs = [], [], []
    best_sp, best_model = 0, None
    for seed in SEEDS:
        model, sp, m = train_one_seed(data, all_pairs, train_pairs, test_pairs, seed)
        sps.append(sp)
        hits.append(m['Hit@10'])
        mrrs.append(m['MRR'])
        print(f"  {seed:>6} {sp:>10.4f} {m['Hit@10']:>8.4f} {m['NDCG@10']:>9.4f} {m['MRR']:>7.4f}")
        if sp > best_sp:
            best_sp = sp
            best_model = model

    def s(lst): return round(sum(lst)/len(lst), 4), round((sum((x-sum(lst)/len(lst))**2 for x in lst)/len(lst))**0.5, 4)

    sp_mean, sp_std = s(sps)
    hit_mean, hit_std = s(hits)
    mrr_mean, mrr_std = s(mrrs)
    print("  " + "-"*45)
    print(f"  {'mean':>6} {sp_mean:>10.4f} {hit_mean:>8.4f} {'':>9} {mrr_mean:>7.4f}")
    print(f"  {'std':>6} {sp_std:>10.4f} {hit_std:>8.4f} {'':>9} {mrr_std:>7.4f}")

    torch.save(best_model.state_dict(), CKPT_PATH)
    print(f"\nSaved best checkpoint → finetune_optimal.pt (Spearman={best_sp:.4f})")
    print(f"\nFinal summary:")
    print(f"  Cross-signal Spearman: {sp_mean:.4f} ± {sp_std:.4f}")
    print(f"  Hit@10:  {hit_mean:.4f} ± {hit_std:.4f}")
    print(f"  MRR:     {mrr_mean:.4f} ± {mrr_std:.4f}")


if __name__ == '__main__':
    run()
