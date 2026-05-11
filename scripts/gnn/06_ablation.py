"""
Ablation study: Hetero GNN vs Homo GNN (no compound nodes).

Homo baseline: ingredient-only graph, same Simple-HGN architecture depth/width.
- Removes compound nodes entirely
- Only ingredient↔ingredient PMI edges remain
- Same hidden_dim, num_layers, num_heads, training procedure

Comparison metrics:
- Cross-signal Spearman (PMI→compound similarity) — key metric
- Hit@10, NDCG@10, MRR on leave-out pairs
- Qualitative: compound-mediated discovery count

Expected result: hetero GNN > homo on cross-signal Spearman,
because compound message passing provides chemical signal.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import sqlite3
import os
import sys
import random
import math
import copy

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

GRAPH_PATH = os.path.join(os.path.dirname(__file__), 'graph.pt')
DB_PATH = os.path.join(os.path.dirname(__file__), '../../flavorgraph_v2.db')


# ── Homo GNN (ingredient-only) ──────────────────────────────────────────────

class HomoGATLayer(nn.Module):
    def __init__(self, in_dim, out_dim, num_heads=4, dropout=0.1):
        super().__init__()
        from torch_geometric.nn import GATConv
        head_dim = out_dim // num_heads
        self.conv = GATConv(in_dim, head_dim, heads=num_heads,
                            dropout=dropout, add_self_loops=False, concat=True)
        self.res = nn.Linear(in_dim, out_dim, bias=False) if in_dim != out_dim else nn.Identity()
        self.norm = nn.LayerNorm(out_dim)
        self.drop = nn.Dropout(dropout)

    def forward(self, x, edge_index):
        h = self.conv(x, edge_index) + self.res(x)
        return self.drop(F.elu(self.norm(h)))


class HomoFlavorGNN(nn.Module):
    """Ingredient-only GAT. No compound nodes, no hetero edges."""

    def __init__(self, n_ingredient, hidden_dim=128, num_layers=2, num_heads=4, dropout=0.1):
        super().__init__()
        self.ing_emb = nn.Embedding(n_ingredient, hidden_dim)
        self.layers = nn.ModuleList([
            HomoGATLayer(hidden_dim, hidden_dim, num_heads, dropout)
            for _ in range(num_layers)
        ])
        self.decoder_W = nn.Parameter(torch.ones(hidden_dim))

    def encode(self, edge_index):
        x = self.ing_emb.weight
        for layer in self.layers:
            x = layer(x, edge_index)
        return F.normalize(x, dim=-1)

    def score_pair(self, emb, ing_i, ing_j):
        return (emb[ing_i] * self.decoder_W * emb[ing_j]).sum(dim=-1)


# ── Shared utilities ─────────────────────────────────────────────────────────

def load_pairs(ing_name_to_idx):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT ing_a, ing_b, combined_score FROM pair_score
        WHERE ing_a < ing_b AND combined_score > 0
        ORDER BY combined_score DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return [(ing_name_to_idx[a], ing_name_to_idx[b], s)
            for a, b, s in rows if a in ing_name_to_idx and b in ing_name_to_idx]


def ndcg_at_k(ranked_rel, k):
    def dcg(rs, k):
        return sum((2**r - 1) / math.log2(i + 2) for i, r in enumerate(rs[:k]))
    ideal = dcg(sorted(ranked_rel, reverse=True), k)
    return 0.0 if ideal == 0 else dcg(ranked_rel, k) / ideal


def ranking_metrics(emb, decoder_W, test_pairs, all_pairs, n_ing, k=10, n_samples=200):
    pos_by_anchor = {}
    for a, b, _ in all_pairs:
        pos_by_anchor.setdefault(a, set()).add(b)
        pos_by_anchor.setdefault(b, set()).add(a)

    hit, ndcg, rr = [], [], []
    for anchor, pos_idx, _ in random.sample(test_pairs, min(n_samples, len(test_pairs))):
        scores = (emb[anchor] * decoder_W * emb).sum(dim=-1)
        scores[anchor] = float('-inf')
        ranked = scores.argsort(descending=True).tolist()
        positives = pos_by_anchor.get(anchor, set())
        ranked_rel = [1 if idx in positives else 0 for idx in ranked[:k]]
        hit.append(1.0 if pos_idx in ranked[:k] else 0.0)
        ndcg.append(ndcg_at_k(ranked_rel, k))
        rank = next((r + 1 for r, idx in enumerate(ranked) if idx == pos_idx), n_ing)
        rr.append(1.0 / rank)

    n = len(hit)
    return {f'Hit@{k}': sum(hit)/n, f'NDCG@{k}': sum(ndcg)/n, 'MRR': sum(rr)/n}


def compound_spearman(emb, decoder_W, ing_names, n_samples=500):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT ing_a, ing_b, shared_count FROM pair_score
        WHERE ing_a < ing_b AND shared_count > 0 LIMIT ?
    """, (n_samples,))
    rows = cur.fetchall()
    conn.close()

    name_to_idx = {n: i for i, n in enumerate(ing_names)}
    gnn_s, cmp_c = [], []
    for a, b, shared in rows:
        if a not in name_to_idx or b not in name_to_idx:
            continue
        score = (emb[name_to_idx[a]] * decoder_W * emb[name_to_idx[b]]).sum().item()
        gnn_s.append(score)
        cmp_c.append(shared)

    n = len(gnn_s)
    if n < 10:
        return float('nan')

    def ranks(lst):
        r = [0]*len(lst)
        for rank, (i, _) in enumerate(sorted(enumerate(lst), key=lambda x: x[1])):
            r[i] = rank+1
        return r

    rx, ry = ranks(gnn_s), ranks(cmp_c)
    mx, my = sum(rx)/n, sum(ry)/n
    num = sum((rx[i]-mx)*(ry[i]-my) for i in range(n))
    den = (sum((rx[i]-mx)**2 for i in range(n))**0.5 * sum((ry[i]-my)**2 for i in range(n))**0.5)
    return round(num/(den+1e-9), 4)


def perturb(model, noise_std=0.01):
    m = copy.deepcopy(model)
    with torch.no_grad():
        for p in m.parameters():
            p.add_(torch.randn_like(p) * noise_std)
    return m


def nt_xent(z1, z2, temp=0.5):
    z1, z2 = F.normalize(z1, dim=-1), F.normalize(z2, dim=-1)
    N = z1.size(0)
    z = torch.cat([z1, z2])
    sim = torch.mm(z, z.T) / temp
    sim.masked_fill_(torch.eye(2*N, dtype=torch.bool), float('-inf'))
    labels = torch.cat([torch.arange(N)+N, torch.arange(N)])
    return F.cross_entropy(sim, labels)


def train_homo(data, all_pairs, test_pairs, ing_names,
               hidden_dim=128, num_layers=2, num_heads=4, dropout=0.1,
               pretrain_epochs=200, finetune_epochs=300, device='cpu'):
    n_ing = data['ingredient'].num_nodes
    edge_index = data['ingredient', 'pairs_with', 'ingredient'].edge_index.to(device)

    model = HomoFlavorGNN(n_ing, hidden_dim, num_layers, num_heads, dropout).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)
    sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=pretrain_epochs)

    print("  [Homo] SimGRACE pre-training...")
    for ep in range(1, pretrain_epochs+1):
        model.train()
        opt.zero_grad()
        z1 = model.encode(edge_index)
        noisy = perturb(model).to(device)
        noisy.train(False)
        with torch.no_grad():
            z2 = noisy.encode(edge_index)
        loss = nt_xent(z1, z2)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        sch.step()
        if ep % 50 == 0:
            print(f"    pretrain ep {ep} | loss {loss.item():.4f}")

    train_sorted = sorted(all_pairs[:int(len(all_pairs)*0.9)], key=lambda x: x[2], reverse=True)
    train_len = len(train_sorted)
    opt2 = torch.optim.Adam(model.parameters(), lr=5e-4, weight_decay=1e-5)
    sch2 = torch.optim.lr_scheduler.CosineAnnealingLR(opt2, T_max=finetune_epochs)
    best_mrr, best_state = 0.0, None

    print("  [Homo] BPR fine-tuning...")
    for ep in range(1, finetune_epochs+1):
        model.train()
        opt2.zero_grad()
        bs = min(256, train_len)
        pos = random.sample(train_sorted[:max(1, train_len//2)], bs)
        neg = random.sample(train_sorted[train_len//2:] or train_sorted, bs)
        emb = model.encode(edge_index)
        pa = torch.tensor([p[0] for p in pos], dtype=torch.long, device=device)
        pb = torch.tensor([p[1] for p in pos], dtype=torch.long, device=device)
        nb = torch.tensor([p[1] for p in neg], dtype=torch.long, device=device)
        loss = -F.logsigmoid(model.score_pair(emb, pa, pb) - model.score_pair(emb, pa, nb)).mean()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt2.step()
        sch2.step()
        if ep % 100 == 0:
            model.train(False)
            with torch.no_grad():
                emb = model.encode(edge_index)
            m = ranking_metrics(emb, model.decoder_W, test_pairs, all_pairs, n_ing)
            if m['MRR'] > best_mrr:
                best_mrr = m['MRR']
                best_state = copy.deepcopy(model.state_dict())
            print(f"    finetune ep {ep} | BPR {loss.item():.4f} | MRR {m['MRR']:.3f}")
            model.train()

    if best_state:
        model.load_state_dict(best_state)
    model.train(False)
    with torch.no_grad():
        emb = model.encode(edge_index)
    return emb, model.decoder_W


def run_ablation():
    print("Loading graph...")
    data = torch.load(GRAPH_PATH, weights_only=False)
    ing_names = data['ingredient'].names
    name_to_idx = {n: i for i, n in enumerate(ing_names)}
    n_ing = data['ingredient'].num_nodes

    all_pairs = load_pairs(name_to_idx)
    random.shuffle(all_pairs)
    split = int(len(all_pairs) * 0.9)
    train_pairs = all_pairs[:split]
    test_pairs = all_pairs[split:]

    # ── Hetero model (load existing finetune.pt) ────────────────────────────
    print("\n=== Hetero GNN (existing checkpoint) ===")
    from scripts.gnn.model import FlavorHGN
    n_cmp = data['compound'].num_nodes
    hetero_model = FlavorHGN(n_ing, n_cmp, hidden_dim=128, num_layers=2, num_heads=4)
    ckpt = os.path.join(os.path.dirname(__file__), 'finetune.pt')
    if os.path.exists(ckpt):
        hetero_model.load_state_dict(torch.load(ckpt, map_location='cpu'))
        print("  Loaded finetune.pt")
    hetero_model.train(False)
    with torch.no_grad():
        hx = hetero_model.encode(data)
        h_emb = hx['ingredient']
        h_W = hetero_model.decoder.W

    hetero_metrics = ranking_metrics(h_emb, h_W, test_pairs, all_pairs, n_ing)
    hetero_spearman = compound_spearman(h_emb, h_W, ing_names)

    # ── Homo model (train from scratch) ────────────────────────────────────
    print("\n=== Homo GNN (ingredient-only, train from scratch) ===")
    homo_emb, homo_W = train_homo(data, train_pairs, test_pairs, ing_names,
                                   pretrain_epochs=200, finetune_epochs=300)
    homo_metrics = ranking_metrics(homo_emb, homo_W, test_pairs, all_pairs, n_ing)
    homo_spearman = compound_spearman(homo_emb, homo_W, ing_names)

    # ── Results ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("ABLATION RESULTS")
    print("=" * 60)
    print(f"{'Metric':<25} {'Hetero GNN':>12} {'Homo GNN':>12} {'Δ':>8}")
    print("-" * 60)
    for key in ['Hit@10', 'NDCG@10', 'MRR']:
        h_val = hetero_metrics[key]
        b_val = homo_metrics[key]
        delta = h_val - b_val
        print(f"{key:<25} {h_val:>12.4f} {b_val:>12.4f} {delta:>+8.4f}")
    print(f"{'Spearman(PMI→cmp)':<25} {hetero_spearman:>12.4f} {homo_spearman:>12.4f} {hetero_spearman-homo_spearman:>+8.4f}")
    print("=" * 60)
    print("\nConclusion:")
    delta_sp = hetero_spearman - homo_spearman
    if delta_sp > 0.05:
        print(f"  Compound nodes improve cross-signal Spearman by +{delta_sp:.3f}")
        print("  → Hetero message passing recovers chemical structure from recipe co-occurrence.")
    else:
        print(f"  Spearman delta = {delta_sp:.3f} — marginal. Check training stability.")


if __name__ == '__main__':
    run_ablation()
