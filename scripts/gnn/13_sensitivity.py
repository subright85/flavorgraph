"""
SimGRACE sensitivity + training signal composition sweep.

Questions:
1. Does SimGRACE pretraining help or hurt vs. BPR-only?
2. Temperature (0.1 ~ 1.0) and noise_std (0.001 ~ 0.1) effect.
3. Training signal alpha: combined = alpha*tfidf + (1-alpha)*pmi, alpha in {0, 0.2, 0.5, 0.8, 1.0}.

All use optimal hyperparam: hidden_dim=64, num_layers=3, combined_score training.
Fixed seed=42, 3 seeds averaged for main comparisons.
"""

import torch
import torch.nn.functional as F
import sqlite3, os, sys, random, copy

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from scripts.gnn.model import FlavorHGN

GRAPH_PATH = os.path.join(os.path.dirname(__file__), 'graph.pt')
DB_PATH = os.path.join(os.path.dirname(__file__), '../../flavorgraph_v2.db')


def load_graph():
    return torch.load(GRAPH_PATH, weights_only=False)


def load_pairs(name_to_idx, col='combined_score'):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"""
        SELECT ing_a, ing_b, pmi_score, combined_score, shared_count
        FROM pair_score WHERE ing_a < ing_b AND {col} > 0
    """)
    rows = cur.fetchall()
    conn.close()
    return [(name_to_idx[a], name_to_idx[b], pmi, comb, sh)
            for a, b, pmi, comb, sh in rows if a in name_to_idx and b in name_to_idx]


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


def perturb(model, std=0.01):
    m = copy.deepcopy(model)
    with torch.no_grad():
        for p in m.encoder.parameters():
            p.add_(torch.randn_like(p) * std)
    return m


def nt_xent(z1, z2, temp=0.5):
    z1, z2 = F.normalize(z1, dim=-1), F.normalize(z2, dim=-1)
    N = z1.size(0)
    z = torch.cat([z1, z2])
    sim = torch.mm(z, z.T) / temp
    sim.masked_fill_(torch.eye(2*N, dtype=torch.bool), float('-inf'))
    labels = torch.cat([torch.arange(N)+N, torch.arange(N)])
    return F.cross_entropy(sim, labels)


def train_bpr_only(data, pairs, score_col_idx, hidden_dim=64, num_layers=3,
                   epochs=200, seed=42):
    """BPR-only (no SimGRACE) training."""
    random.seed(seed); torch.manual_seed(seed)
    n_ing = data['ingredient'].num_nodes
    n_cmp = data['compound'].num_nodes
    model = FlavorHGN(n_ing, n_cmp, hidden_dim, num_layers, 4, 0.1)
    opt = torch.optim.Adam(model.parameters(), lr=5e-4, weight_decay=1e-5)
    sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)

    train_sorted = sorted(pairs, key=lambda x: x[score_col_idx], reverse=True)
    train_len = len(train_sorted)
    for _ in range(epochs):
        model.train(); opt.zero_grad()
        bs = min(256, train_len)
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

    gnn_s = [(emb[p[0]]*W*emb[p[1]]).sum().item() for p in pairs]
    cmp_s = [p[4] for p in pairs]  # shared_count
    return spearman(gnn_s, cmp_s)


def train_simgrace_bpr(data, pairs, score_col_idx, hidden_dim=64, num_layers=3,
                       pre_epochs=100, ft_epochs=200, noise_std=0.01, temp=0.5,
                       seed=42):
    """SimGRACE pretrain + BPR finetune."""
    random.seed(seed); torch.manual_seed(seed)
    n_ing = data['ingredient'].num_nodes
    n_cmp = data['compound'].num_nodes
    model = FlavorHGN(n_ing, n_cmp, hidden_dim, num_layers, 4, 0.1)

    # SimGRACE
    opt = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)
    sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=pre_epochs)
    for _ in range(pre_epochs):
        model.train(); opt.zero_grad()
        x1 = model.encode(data)
        noisy = perturb(model, noise_std); noisy.train(False)
        with torch.no_grad():
            x2 = noisy.encode(data)
        loss = nt_xent(x1['ingredient'], x2['ingredient'], temp)
        if x1['compound'].size(0) > 1:
            loss = loss + 0.5 * nt_xent(x1['compound'], x2['compound'], temp)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step(); sch.step()

    # BPR
    train_sorted = sorted(pairs, key=lambda x: x[score_col_idx], reverse=True)
    train_len = len(train_sorted)
    opt2 = torch.optim.Adam(model.parameters(), lr=3e-4, weight_decay=1e-5)
    sch2 = torch.optim.lr_scheduler.CosineAnnealingLR(opt2, T_max=ft_epochs)
    for _ in range(ft_epochs):
        model.train(); opt2.zero_grad()
        bs = min(256, train_len)
        pos = random.sample(train_sorted[:max(1, train_len//2)], bs)
        neg = random.sample(train_sorted[train_len//2:] or train_sorted, bs)
        x_dict = model.encode(data)
        pa = torch.tensor([p[0] for p in pos], dtype=torch.long)
        pb = torch.tensor([p[1] for p in pos], dtype=torch.long)
        nb = torch.tensor([p[1] for p in neg], dtype=torch.long)
        loss = -F.logsigmoid(model.score_pair(x_dict,pa,pb)-model.score_pair(x_dict,pa,nb)).mean()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt2.step(); sch2.step()

    model.train(False)
    with torch.no_grad():
        x_dict = model.encode(data)
        emb, W = x_dict['ingredient'], model.decoder.W

    gnn_s = [(emb[p[0]]*W*emb[p[1]]).sum().item() for p in pairs]
    cmp_s = [p[4] for p in pairs]
    return spearman(gnn_s, cmp_s)


def avg_seeds(fn, seeds=(42, 123, 7)):
    results = [fn(seed=s) for s in seeds]
    return round(sum(results)/len(results), 4), round(min(results), 4), round(max(results), 4)


def run():
    data = load_graph()
    names = data['ingredient'].names
    name_to_idx = {n: i for i, n in enumerate(names)}
    pairs = load_pairs(name_to_idx, 'combined_score')
    # pairs: (i_idx, j_idx, pmi_score, combined_score, shared_count)
    # col idx: 2=pmi, 3=combined, 4=shared

    print("=== 1. SimGRACE vs. BPR-only (hidden=64, layers=3, 3 seeds) ===\n")
    print(f"  {'Method':<30} {'mean':>8} {'min':>8} {'max':>8}")
    print("  " + "-"*58)

    mean, lo, hi = avg_seeds(lambda seed: train_bpr_only(data, pairs, 3, seed=seed))
    print(f"  {'BPR-only':<30} {mean:>8.4f} {lo:>8.4f} {hi:>8.4f}")

    mean, lo, hi = avg_seeds(lambda seed: train_simgrace_bpr(data, pairs, 3, seed=seed))
    print(f"  {'SimGRACE(default)+BPR':<30} {mean:>8.4f} {lo:>8.4f} {hi:>8.4f}")

    print("\n=== 2. SimGRACE Temperature Sensitivity (seed=42) ===\n")
    print(f"  {'temperature':>12} {'Spearman':>10}")
    print("  " + "-"*25)
    for temp in [0.1, 0.2, 0.3, 0.5, 0.7, 1.0]:
        sp = train_simgrace_bpr(data, pairs, 3, temp=temp, seed=42)
        print(f"  {temp:>12.1f} {sp:>10.4f}")

    print("\n=== 3. SimGRACE Noise Std Sensitivity (seed=42) ===\n")
    print(f"  {'noise_std':>12} {'Spearman':>10}")
    print("  " + "-"*25)
    for std in [0.001, 0.005, 0.01, 0.02, 0.05, 0.1]:
        sp = train_simgrace_bpr(data, pairs, 3, noise_std=std, seed=42)
        print(f"  {std:>12.3f} {sp:>10.4f}")

    print("\n=== 4. Training Signal Composition (alpha*tfidf + (1-alpha)*pmi) ===")
    print("  combined_score ≈ 0.8*tfidf + 0.2*pmi (from db)\n")
    print("  alpha=0 → PMI only, alpha=1 → tfidf only\n")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT ing_a, ing_b, pmi_score, combined_score, shared_count
        FROM pair_score WHERE ing_a < ing_b
    """)
    all_rows = cur.fetchall()
    conn.close()

    # Estimate tfidf: combined = 0.8*tfidf + 0.2*pmi → tfidf = (combined - 0.2*pmi) / 0.8
    # Build alpha-parameterized pairs
    def build_alpha_pairs(alpha):
        result = []
        for a, b, pmi, comb, shared in all_rows:
            if a not in name_to_idx or b not in name_to_idx:
                continue
            tfidf_est = (comb - 0.2 * pmi) / 0.8 if comb is not None else 0.0
            score = alpha * tfidf_est + (1 - alpha) * (pmi or 0)
            if score > 0:
                result.append((name_to_idx[a], name_to_idx[b], pmi or 0, score, shared or 0))
        return result

    print(f"  {'alpha (tfidf weight)':>22} {'n_pairs':>8} {'Spearman':>10}")
    print("  " + "-"*43)
    for alpha in [0.0, 0.2, 0.5, 0.8, 1.0]:
        ap = build_alpha_pairs(alpha)
        if len(ap) < 10:
            print(f"  {alpha:>22.1f} {len(ap):>8} {'(too few)':>10}")
            continue
        sp = train_bpr_only(data, ap, 3, seed=42)
        print(f"  {alpha:>22.1f} {len(ap):>8} {sp:>10.4f}")


if __name__ == '__main__':
    run()
