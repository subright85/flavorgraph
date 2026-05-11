"""
Pairwise ranking fine-tune + BPR loss.

Training data: pair_score table (combined_score as target ranking signal)
- Positive pair (a, b): high combined_score
- Hard negative: same-category ingredient (if available), else random

BPR loss: log σ(score_pos - score_neg) — model learns relative ordering.

Two automated checks:
1. Leave-out recipe validation: hold out 10% pairs, compute NDCG@10, Hit@10, MRR
2. Cross-signal check: Spearman corr between GNN scores and compound similarity
"""

import torch
import torch.nn.functional as F
import sqlite3
import os
import sys
import random
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from scripts.gnn.model import FlavorHGN

GRAPH_PATH = os.path.join(os.path.dirname(__file__), 'graph.pt')
PRETRAIN_CKPT = os.path.join(os.path.dirname(__file__), 'pretrain.pt')
FINETUNE_CKPT = os.path.join(os.path.dirname(__file__), 'finetune.pt')
DB_PATH = os.path.join(os.path.dirname(__file__), '../../flavorgraph_v2.db')


def load_pairs(ing_name_to_idx):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT ing_a, ing_b, combined_score
        FROM pair_score
        WHERE ing_a < ing_b AND combined_score > 0
        ORDER BY combined_score DESC
    """)
    rows = cur.fetchall()
    conn.close()
    pairs = []
    for a, b, score in rows:
        if a in ing_name_to_idx and b in ing_name_to_idx:
            pairs.append((ing_name_to_idx[a], ing_name_to_idx[b], score))
    return pairs


def dcg_at_k(sorted_scores, k):
    return sum(
        (2 ** rel - 1) / math.log2(rank + 2)
        for rank, rel in enumerate(sorted_scores[:k])
    )


def ndcg_at_k(ranked_relevance, k):
    ideal = sorted(ranked_relevance, reverse=True)
    idcg = dcg_at_k(ideal, k)
    return 0.0 if idcg == 0 else dcg_at_k(ranked_relevance, k) / idcg


def compute_ranking_metrics(model, data, test_pairs, all_pairs_list, n_ing, k=10, n_samples=200):
    model.train(False)
    with torch.no_grad():
        x_dict = model.encode(data)
        emb = x_dict['ingredient']

    hit_list, ndcg_list, rr_list = [], [], []
    positives_by_anchor = {}
    for a, b, _ in all_pairs_list:
        positives_by_anchor.setdefault(a, set()).add(b)
        positives_by_anchor.setdefault(b, set()).add(a)

    sample = random.sample(test_pairs, min(n_samples, len(test_pairs)))
    for anchor_idx, pos_idx, _ in sample:
        anchor_emb = emb[anchor_idx].unsqueeze(0)
        scores = (anchor_emb * model.decoder.W * emb).sum(dim=-1)
        scores[anchor_idx] = float('-inf')

        sorted_idxs = scores.argsort(descending=True).tolist()
        positives = positives_by_anchor.get(anchor_idx, set())
        ranked_rel = [1 if idx in positives else 0 for idx in sorted_idxs[:k]]

        hit_list.append(1.0 if pos_idx in sorted_idxs[:k] else 0.0)
        ndcg_list.append(ndcg_at_k(ranked_rel, k))
        rank_of_pos = next((r + 1 for r, idx in enumerate(sorted_idxs) if idx == pos_idx), n_ing)
        rr_list.append(1.0 / rank_of_pos)

    model.train()
    n = len(hit_list)
    return {
        f'Hit@{k}': sum(hit_list) / n,
        f'NDCG@{k}': sum(ndcg_list) / n,
        'MRR': sum(rr_list) / n,
    }


def compound_correlation(model, data, n_samples=500):
    """Spearman corr: GNN score (trained on PMI) vs shared compound count (FooDB)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT ing_a, ing_b, shared_count
        FROM pair_score
        WHERE ing_a < ing_b AND shared_count > 0
        LIMIT ?
    """, (n_samples,))
    rows = cur.fetchall()
    conn.close()

    name_to_idx = {n: i for i, n in enumerate(data['ingredient'].names)}

    model.train(False)
    with torch.no_grad():
        x_dict = model.encode(data)
        emb = x_dict['ingredient']

    gnn_scores, cmp_counts = [], []
    for a_name, b_name, shared in rows:
        if a_name not in name_to_idx or b_name not in name_to_idx:
            continue
        a_idx = name_to_idx[a_name]
        b_idx = name_to_idx[b_name]
        score = (emb[a_idx] * model.decoder.W * emb[b_idx]).sum().item()
        gnn_scores.append(score)
        cmp_counts.append(shared)

    model.train()

    n = len(gnn_scores)
    if n < 10:
        return {'spearman_r': float('nan'), 'n': n}

    def rank_list(lst):
        ranked = [0] * len(lst)
        for rank, (idx, _) in enumerate(sorted(enumerate(lst), key=lambda x: x[1])):
            ranked[idx] = rank + 1
        return ranked

    rx, ry = rank_list(gnn_scores), rank_list(cmp_counts)
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    den = (sum((rx[i] - mean_rx) ** 2 for i in range(n)) ** 0.5 *
           sum((ry[i] - mean_ry) ** 2 for i in range(n)) ** 0.5)
    return {'spearman_r': round(num / (den + 1e-9), 4), 'n': n}


def finetune(
    hidden_dim=128,
    num_layers=2,
    num_heads=4,
    dropout=0.1,
    lr=5e-4,
    epochs=300,
    test_split=0.1,
    device='cpu',
    verbose=True,
):
    data = torch.load(GRAPH_PATH, weights_only=False)
    data = data.to(device)

    n_ing = data['ingredient'].num_nodes
    n_cmp = data['compound'].num_nodes
    ing_names = data['ingredient'].names
    ing_name_to_idx = {n: i for i, n in enumerate(ing_names)}

    model = FlavorHGN(n_ing, n_cmp, hidden_dim, num_layers, num_heads, dropout).to(device)

    if os.path.exists(PRETRAIN_CKPT):
        model.load_state_dict(torch.load(PRETRAIN_CKPT, map_location=device))
        print("Loaded pre-trained weights.")
    else:
        print("No pre-trained weights — training from scratch.")

    all_pairs = load_pairs(ing_name_to_idx)
    print(f"Total pairs: {len(all_pairs)}")

    random.shuffle(all_pairs)
    split = int(len(all_pairs) * (1 - test_split))
    train_pairs = all_pairs[:split]
    test_pairs = all_pairs[split:]
    print(f"Train: {len(train_pairs)} | Test: {len(test_pairs)}")

    train_sorted = sorted(train_pairs, key=lambda x: x[2], reverse=True)
    train_len = len(train_sorted)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    best_mrr = 0.0
    for epoch in range(1, epochs + 1):
        model.train()
        optimizer.zero_grad()

        batch_size = min(256, train_len)
        pos_sample = random.sample(train_sorted[:max(1, train_len // 2)], batch_size)
        neg_pool = train_sorted[train_len // 2:] or train_sorted
        neg_sample = random.sample(neg_pool, batch_size)

        x_dict = model.encode(data)
        pos_a = torch.tensor([p[0] for p in pos_sample], dtype=torch.long, device=device)
        pos_b = torch.tensor([p[1] for p in pos_sample], dtype=torch.long, device=device)
        neg_b = torch.tensor([p[1] for p in neg_sample], dtype=torch.long, device=device)

        score_pos = model.score_pair(x_dict, pos_a, pos_b)
        score_neg = model.score_pair(x_dict, pos_a, neg_b)
        loss = -F.logsigmoid(score_pos - score_neg).mean()

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        scheduler.step()

        if epoch % 50 == 0:
            metrics = compute_ranking_metrics(model, data, test_pairs, all_pairs, n_ing)
            cs = compound_correlation(model, data)
            if metrics['MRR'] > best_mrr:
                best_mrr = metrics['MRR']
                torch.save(model.state_dict(), FINETUNE_CKPT)
            if verbose:
                print(f"Epoch {epoch:3d} | BPR {loss.item():.4f} | "
                      f"Hit@10 {metrics['Hit@10']:.3f} | NDCG@10 {metrics['NDCG@10']:.3f} | "
                      f"MRR {metrics['MRR']:.3f} | Spearman(cmp) {cs['spearman_r']:.3f}")

    print(f"\nFine-tuning done. Best MRR: {best_mrr:.4f}")

    print("\n=== Final Metrics ===")
    model.load_state_dict(torch.load(FINETUNE_CKPT, map_location=device))
    final = compute_ranking_metrics(model, data, test_pairs, all_pairs, n_ing, k=10)
    cs_final = compound_correlation(model, data)
    for metric, val in final.items():
        print(f"  {metric}: {val:.4f}")
    print(f"  Cross-signal Spearman (PMI→compound): {cs_final['spearman_r']:.4f} (n={cs_final['n']})")

    return model


if __name__ == '__main__':
    finetune(epochs=300, verbose=True)
