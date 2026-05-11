"""
Clean ablation: training target PMI vs combined_score.

combined_score = 0.8*tfidf + 0.2*pmi, where tfidf is based on FooDB compounds.
So combined_score already contains compound signal.

Q: If we train on pure PMI (no compound info in training target),
   does compound NODE message passing still recover compound similarity?

This is the cleanest version of our main claim:
"Hetero GNN trained on recipe co-occurrence recovers chemical structure
 via compound node message passing"
"""

import torch
import torch.nn.functional as F
import sqlite3, os, sys, random, copy

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from scripts.gnn.model import FlavorHGN

GRAPH_PATH = os.path.join(os.path.dirname(__file__), 'graph.pt')
DB_PATH = os.path.join(os.path.dirname(__file__), '../../flavorgraph_v2.db')


def load_pairs_by_target(name_to_idx, target='pmi'):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    col = 'pmi_score' if target == 'pmi' else 'combined_score'
    cur.execute(f"""
        SELECT ing_a, ing_b, {col}, shared_count
        FROM pair_score
        WHERE ing_a < ing_b AND {col} > 0
    """)
    rows = cur.fetchall()
    conn.close()
    return [(name_to_idx[a], name_to_idx[b], s, sh)
            for a, b, s, sh in rows if a in name_to_idx and b in name_to_idx]


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
    z1, z2 = F.normalize(z1,dim=-1), F.normalize(z2,dim=-1)
    N = z1.size(0)
    z = torch.cat([z1, z2])
    sim = torch.mm(z, z.T) / temp
    sim.masked_fill_(torch.eye(2*N, dtype=torch.bool), float('-inf'))
    labels = torch.cat([torch.arange(N)+N, torch.arange(N)])
    return F.cross_entropy(sim, labels)


def train_and_score(data, pairs, use_hetero_compounds, hidden_dim=64, num_layers=3,
                    epochs=200, seed=42):
    """
    Train GNN and return Spearman(GNN_score, shared_compound).

    use_hetero_compounds: if False, remove compound edges → homo-like behavior
    """
    random.seed(seed)
    torch.manual_seed(seed)

    n_ing = data['ingredient'].num_nodes
    n_cmp = data['compound'].num_nodes

    if not use_hetero_compounds:
        from torch_geometric.data import HeteroData
        data_use = HeteroData()
        data_use['ingredient'].num_nodes = n_ing
        data_use['ingredient'].names = data['ingredient'].names
        data_use['compound'].num_nodes = n_cmp
        data_use['compound'].names = data['compound'].names
        # Remove compound edges
        data_use['ingredient', 'pairs_with', 'ingredient'].edge_index = \
            data['ingredient', 'pairs_with', 'ingredient'].edge_index
        # Keep compound nodes but no edges → compound embeddings unused
        data_use['ingredient', 'contains', 'compound'].edge_index = \
            torch.zeros((2, 0), dtype=torch.long)
        data_use['compound', 'in', 'ingredient'].edge_index = \
            torch.zeros((2, 0), dtype=torch.long)
    else:
        data_use = data

    model = FlavorHGN(n_ing, n_cmp, hidden_dim, num_layers, 4, 0.1)

    # SimGRACE pretrain
    opt = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)
    sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=100)
    for ep in range(100):
        model.train(); opt.zero_grad()
        x1 = model.encode(data_use)
        noisy = perturb(model); noisy.train(False)
        with torch.no_grad():
            x2 = noisy.encode(data_use)
        loss = nt_xent(x1['ingredient'], x2['ingredient'])
        if use_hetero_compounds and x1['compound'].size(0) > 1:
            loss = loss + 0.5 * nt_xent(x1['compound'], x2['compound'])
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step(); sch.step()

    # BPR finetune
    train_sorted = sorted(pairs, key=lambda x: x[2], reverse=True)
    train_len = len(train_sorted)
    opt2 = torch.optim.Adam(model.parameters(), lr=3e-4, weight_decay=1e-5)
    sch2 = torch.optim.lr_scheduler.CosineAnnealingLR(opt2, T_max=epochs)
    for ep in range(epochs):
        model.train(); opt2.zero_grad()
        bs = min(256, train_len)
        pos = random.sample(train_sorted[:max(1,train_len//2)], bs)
        neg = random.sample(train_sorted[train_len//2:] or train_sorted, bs)
        x_dict = model.encode(data_use)
        pa = torch.tensor([p[0] for p in pos], dtype=torch.long)
        pb = torch.tensor([p[1] for p in pos], dtype=torch.long)
        nb = torch.tensor([p[1] for p in neg], dtype=torch.long)
        loss = -F.logsigmoid(model.score_pair(x_dict,pa,pb)-model.score_pair(x_dict,pa,nb)).mean()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt2.step(); sch2.step()

    model.train(False)
    with torch.no_grad():
        x_dict = model.encode(data_use)
        emb, W = x_dict['ingredient'], model.decoder.W

    gnn_s = [(emb[p[0]]*W*emb[p[1]]).sum().item() for p in pairs]
    cmp_s = [p[3] for p in pairs]
    return spearman(gnn_s, cmp_s)


def run():
    data = torch.load(GRAPH_PATH, weights_only=False)
    names = data['ingredient'].names
    name_to_idx = {n: i for i, n in enumerate(names)}

    pmi_pairs = load_pairs_by_target(name_to_idx, 'pmi')
    combined_pairs = load_pairs_by_target(name_to_idx, 'combined')

    print(f"PMI pairs (>0): {len(pmi_pairs)}")
    print(f"Combined pairs (>0): {len(combined_pairs)}")

    print("\n=== Clean Ablation: Training Target × Graph Type ===")
    print(f"  Config: hidden_dim=64, num_layers=3 (optimal from hyperparam search)")
    print(f"  Metric: Spearman(GNN_score, shared_compound_count)\n")

    configs = [
        ("PMI only", pmi_pairs, True,  "hetero (compound edges)"),
        ("PMI only", pmi_pairs, False, "homo  (no compound edges)"),
        ("combined ", combined_pairs, True,  "hetero (compound edges)"),
        ("combined ", combined_pairs, False, "homo  (no compound edges)"),
    ]

    results = []
    print(f"  {'Training target':<14} {'Graph type':<30} {'Spearman':>10}")
    print("  " + "-"*55)
    for target_name, pairs, use_hetero, graph_name in configs:
        sp = train_and_score(data, pairs, use_hetero, hidden_dim=64, num_layers=3, epochs=200)
        print(f"  {target_name:<14} {graph_name:<30} {sp:>10.4f}")
        results.append((target_name, graph_name, sp))

    print("\n  Key comparisons:")
    # PMI hetero vs PMI homo
    pmi_hetero = next(sp for n,g,sp in results if 'PMI' in n and 'hetero' in g)
    pmi_homo   = next(sp for n,g,sp in results if 'PMI' in n and 'homo' in g)
    print(f"  Compound edges on PMI training: {pmi_hetero:.4f} vs {pmi_homo:.4f} → Δ = {pmi_hetero-pmi_homo:+.4f}")
    # combined hetero vs combined homo
    comb_hetero = next(sp for n,g,sp in results if 'combined' in n and 'hetero' in g)
    comb_homo   = next(sp for n,g,sp in results if 'combined' in n and 'homo' in g)
    print(f"  Compound edges on combined training: {comb_hetero:.4f} vs {comb_homo:.4f} → Δ = {comb_hetero-comb_homo:+.4f}")


if __name__ == '__main__':
    run()
