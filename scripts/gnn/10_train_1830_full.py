"""
Train FlavorHGN on graph_1830_full.pt (70% compound coverage).

Same pipeline as 08_train_1830.py but uses the expanded compound graph.
Cross-signal Spearman uses FooDB shared_count from pair_score table (151-ingredient subset)
for a fair comparison with previous experiments.
"""

import torch
import torch.nn.functional as F
import sqlite3, os, sys, random, math, copy

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from scripts.gnn.model import FlavorHGN

GRAPH_PATH = os.path.join(os.path.dirname(__file__), 'graph_1830_full.pt')
PRETRAIN_CKPT = os.path.join(os.path.dirname(__file__), 'pretrain_1830_full.pt')
FINETUNE_CKPT = os.path.join(os.path.dirname(__file__), 'finetune_1830_full.pt')
DB_PATH = os.path.join(os.path.dirname(__file__), '../../flavorgraph_v2.db')


def perturb(model, noise_std=0.01):
    m = copy.deepcopy(model)
    with torch.no_grad():
        for p in m.encoder.parameters():
            p.add_(torch.randn_like(p) * noise_std)
    return m


def nt_xent(z1, z2, temp=0.5):
    z1, z2 = F.normalize(z1, dim=-1), F.normalize(z2, dim=-1)
    N = z1.size(0)
    z = torch.cat([z1, z2])
    sim = torch.mm(z, z.T) / temp
    sim.masked_fill_(torch.eye(2 * N, dtype=torch.bool, device=z.device), float('-inf'))
    labels = torch.cat([torch.arange(N, device=z.device) + N, torch.arange(N, device=z.device)])
    return F.cross_entropy(sim, labels)


def ndcg_at_k(ranked_rel, k):
    def dcg(rs, k):
        return sum((2 ** r - 1) / math.log2(i + 2) for i, r in enumerate(rs[:k]))
    ideal = dcg(sorted(ranked_rel, reverse=True), k)
    return 0.0 if ideal == 0 else dcg(ranked_rel, k) / ideal


def ranking_metrics(model, data, test_pairs, all_pairs, n_ing, k=10, n_samples=200, device='cpu'):
    pos_by_anchor = {}
    for a, b, _ in all_pairs:
        pos_by_anchor.setdefault(a, set()).add(b)
        pos_by_anchor.setdefault(b, set()).add(a)

    model.train(False)
    with torch.no_grad():
        x_dict = model.encode(data)
        emb = x_dict['ingredient']
        W = model.decoder.W

    hit, ndcg, rr = [], [], []
    for anchor, pos_idx, _ in random.sample(test_pairs, min(n_samples, len(test_pairs))):
        scores = (emb[anchor] * W * emb).sum(dim=-1)
        scores[anchor] = float('-inf')
        ranked = scores.argsort(descending=True).tolist()
        positives = pos_by_anchor.get(anchor, set())
        ranked_rel = [1 if i in positives else 0 for i in ranked[:k]]
        hit.append(1.0 if pos_idx in ranked[:k] else 0.0)
        ndcg.append(ndcg_at_k(ranked_rel, k))
        rank = next((r + 1 for r, i in enumerate(ranked) if i == pos_idx), n_ing)
        rr.append(1.0 / rank)

    model.train()
    n = len(hit)
    return {f'Hit@{k}': sum(hit) / n, f'NDCG@{k}': sum(ndcg) / n, 'MRR': sum(rr) / n}


def compound_spearman(model, data, device='cpu', n_samples=500):
    """Use DB pair_score shared_count for cross-signal validation (151-ing subset)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT ing_a, ing_b, shared_count FROM pair_score
        WHERE ing_a < ing_b AND shared_count > 0 LIMIT ?
    """, (n_samples,))
    rows = cur.fetchall()
    conn.close()

    name_to_idx = {n.lower(): i for i, n in enumerate(data['ingredient'].names)}

    model.train(False)
    with torch.no_grad():
        x_dict = model.encode(data)
        emb = x_dict['ingredient']
        W = model.decoder.W

    gnn_s, cmp_c = [], []
    for a, b, shared in rows:
        if a.lower() not in name_to_idx or b.lower() not in name_to_idx:
            continue
        score = (emb[name_to_idx[a.lower()]] * W * emb[name_to_idx[b.lower()]]).sum().item()
        gnn_s.append(score)
        cmp_c.append(shared)

    model.train()
    n = len(gnn_s)
    if n < 10:
        return float('nan'), n

    def ranks(lst):
        r = [0] * len(lst)
        for rank, (i, _) in enumerate(sorted(enumerate(lst), key=lambda x: x[1])):
            r[i] = rank + 1
        return r

    rx, ry = ranks(gnn_s), ranks(cmp_c)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    den = (sum((rx[i] - mx) ** 2 for i in range(n)) ** 0.5 *
           sum((ry[i] - my) ** 2 for i in range(n)) ** 0.5)
    return round(num / (den + 1e-9), 4), n


def run(
    hidden_dim=128, num_layers=2, num_heads=4, dropout=0.1,
    pretrain_epochs=200, finetune_epochs=300,
    noise_std=0.01, temperature=0.5, lr_pre=1e-3, lr_ft=5e-4,
    batch_size=512, test_split=0.1, device='cpu',
):
    print("Loading graph_1830_full.pt...")
    data = torch.load(GRAPH_PATH, weights_only=False)
    data = data.to(device)
    n_ing = data['ingredient'].num_nodes
    n_cmp = data['compound'].num_nodes
    print(f"  {n_ing} ingredients, {n_cmp} compounds")
    print(f"  ing↔ing: {data['ingredient','pairs_with','ingredient'].edge_index.size(1)//2} pairs")
    print(f"  ing→cmp: {data['ingredient','contains','compound'].edge_index.size(1)} edges")

    # Build training pairs from graph PMI edges
    ei = data['ingredient', 'pairs_with', 'ingredient'].edge_index
    pmi_vals = data['ingredient', 'pairs_with', 'ingredient'].pmi
    seen, all_pairs = set(), []
    for i in range(ei.size(1)):
        a, b = ei[0, i].item(), ei[1, i].item()
        if a > b:
            continue
        key = (a, b)
        if key in seen:
            continue
        seen.add(key)
        all_pairs.append((a, b, pmi_vals[i].item()))

    random.shuffle(all_pairs)
    split = int(len(all_pairs) * (1 - test_split))
    train_pairs = all_pairs[:split]
    test_pairs = all_pairs[split:]
    print(f"  train {len(train_pairs)} | test {len(test_pairs)}")

    model = FlavorHGN(n_ing, n_cmp, hidden_dim, num_layers, num_heads, dropout).to(device)
    print(f"  model params: {sum(p.numel() for p in model.parameters()):,}")

    # SimGRACE pre-training
    print("\nSimGRACE pre-training...")
    opt = torch.optim.Adam(model.parameters(), lr=lr_pre, weight_decay=1e-5)
    sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=pretrain_epochs)
    best_pre_loss = float('inf')

    for ep in range(1, pretrain_epochs + 1):
        model.train()
        opt.zero_grad()
        x1 = model.encode(data)
        noisy = perturb(model, noise_std).to(device)
        noisy.train(False)
        with torch.no_grad():
            x2 = noisy.encode(data)
        loss = (nt_xent(x1['ingredient'], x2['ingredient'], temperature) +
                0.5 * nt_xent(x1['compound'], x2['compound'], temperature))
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        sch.step()
        if loss.item() < best_pre_loss:
            best_pre_loss = loss.item()
            torch.save(model.state_dict(), PRETRAIN_CKPT)
        if ep % 40 == 0:
            print(f"  ep {ep:3d} | loss {loss.item():.4f}")

    print(f"Pre-training done. Best: {best_pre_loss:.4f}")
    model.load_state_dict(torch.load(PRETRAIN_CKPT, map_location=device))

    # BPR fine-tuning
    print("\nBPR fine-tuning...")
    train_sorted = sorted(train_pairs, key=lambda x: x[2], reverse=True)
    train_len = len(train_sorted)
    opt2 = torch.optim.Adam(model.parameters(), lr=lr_ft, weight_decay=1e-5)
    sch2 = torch.optim.lr_scheduler.CosineAnnealingLR(opt2, T_max=finetune_epochs)
    best_mrr = 0.0

    for ep in range(1, finetune_epochs + 1):
        model.train()
        opt2.zero_grad()
        bs = min(batch_size, train_len)
        pos = random.sample(train_sorted[:max(1, train_len // 2)], bs)
        neg = random.sample(train_sorted[train_len // 2:] or train_sorted, bs)
        x_dict = model.encode(data)
        pa = torch.tensor([p[0] for p in pos], dtype=torch.long, device=device)
        pb = torch.tensor([p[1] for p in pos], dtype=torch.long, device=device)
        nb = torch.tensor([p[1] for p in neg], dtype=torch.long, device=device)
        loss = -F.logsigmoid(model.score_pair(x_dict, pa, pb) -
                             model.score_pair(x_dict, pa, nb)).mean()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt2.step()
        sch2.step()

        if ep % 100 == 0:
            m = ranking_metrics(model, data, test_pairs, all_pairs, n_ing, device=device)
            sp, sp_n = compound_spearman(model, data, device=device)
            if m['MRR'] > best_mrr:
                best_mrr = m['MRR']
                torch.save(model.state_dict(), FINETUNE_CKPT)
            print(f"  ep {ep:3d} | BPR {loss.item():.4f} | "
                  f"Hit@10 {m['Hit@10']:.3f} | MRR {m['MRR']:.3f} | "
                  f"Spearman(cmp) {sp:.3f} (n={sp_n})")

    print(f"\nFine-tuning done. Best MRR: {best_mrr:.4f}")

    print("\n=== Final Metrics (1830-node, 70% compound coverage) ===")
    model.load_state_dict(torch.load(FINETUNE_CKPT, map_location=device))
    final = ranking_metrics(model, data, test_pairs, all_pairs, n_ing, device=device)
    sp_final, sp_n = compound_spearman(model, data, device=device)
    for metric, val in final.items():
        print(f"  {metric}: {val:.4f}")
    print(f"  Cross-signal Spearman: {sp_final:.4f} (n={sp_n})")

    return model


if __name__ == '__main__':
    run()
