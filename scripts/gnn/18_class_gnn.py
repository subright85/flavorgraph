"""
FlavorClass-HGN: class-conditioned GNN with PMI as target metric.
Task: predict ingredient pairing strength (PMI).
Main metric: Spearman(GNN_score, PMI).

Configs:
  A - baseline BPR (one-hot features, combined_score weights)
  B - class-conditioned input [one-hot || flavor_class_vec], BPR
  C - B + complement penalty: max(0, s_redundant - s_syn + margin)
  D - compat-weighted BPR: w = PMI * class_compat(i,j)
"""
import json, sqlite3, random, os
import numpy as np
import torch
import torch.nn.functional as F
from torch_geometric.data import HeteroData
from torch_geometric.nn import HGTConv
from scipy.stats import spearmanr

DB_PATH = "flavorgraph_v2.db"
DATA_DIR = "data"
SEEDS = [42, 123, 2024]
FLAVOR_KEYS = ['alcohol', 'ester', 'sulfur', 'aldehyde', 'nitrogen', 'acid', 'terpene', 'aromatic', 'phenol', 'other']
K = len(FLAVOR_KEYS)


def load_data():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM ingredient ORDER BY id")
    ing_rows = cur.fetchall()
    ing_name2idx = {r[1]: i for i, r in enumerate(ing_rows)}
    n_ing = len(ing_rows)

    cur.execute("SELECT id FROM compound ORDER BY id")
    cmp_rows = cur.fetchall()
    cmp_id2idx = {r[0]: i for i, r in enumerate(cmp_rows)}
    n_cmp = len(cmp_rows)

    cur.execute("""
        SELECT i.name, ic.compound_id
        FROM ingredient_compound ic JOIN ingredient i ON i.id = ic.ingredient_id
    """)
    ic_edges = [(ing_name2idx[r[0]], cmp_id2idx[r[1]])
                for r in cur.fetchall()
                if r[0] in ing_name2idx and r[1] in cmp_id2idx]

    cur.execute("SELECT ing_a, ing_b, combined_score, pmi_score, shared_count FROM pair_score")
    seen, pairs = set(), []
    for r in cur.fetchall():
        key = (min(r[0], r[1]), max(r[0], r[1]))
        if key not in seen and r[0] in ing_name2idx and r[1] in ing_name2idx:
            seen.add(key)
            pairs.append((r[0], r[1], float(r[2] or 0), float(r[3] or 0), float(r[4] or 0)))

    conn.close()
    return ing_name2idx, cmp_id2idx, n_ing, n_cmp, ic_edges, pairs


def load_profiles():
    path = os.path.join(DATA_DIR, "ingredient_flavor_profile.json")
    raw = json.load(open(path)) if os.path.exists(path) else {}
    profiles = {}
    for name, d in raw.items():
        total = d.get('total', 1) or 1
        vec = np.array([d.get(k, 0) / total for k in FLAVOR_KEYS], dtype=np.float32)
        profiles[name] = vec
    return profiles


def build_class_pmi_matrix(pairs, ing_name2idx, profiles):
    sums = np.zeros((K, K), dtype=np.float64)
    cnts = np.zeros((K, K), dtype=np.float64)
    for (n1, n2, _combined, pmi, _shared) in pairs:
        p1 = profiles.get(n1)
        p2 = profiles.get(n2)
        if p1 is None or p2 is None:
            continue
        c1, c2 = int(np.argmax(p1)), int(np.argmax(p2))
        sums[c1, c2] += pmi; sums[c2, c1] += pmi
        cnts[c1, c2] += 1;  cnts[c2, c1] += 1
    with np.errstate(invalid='ignore'):
        mat = np.where(cnts > 0, sums / cnts, 0.0)
    mx = mat.max()
    return (mat / mx).astype(np.float32) if mx > 0 else mat.astype(np.float32)


def compat(n1, n2, profiles, phi):
    p1, p2 = profiles.get(n1), profiles.get(n2)
    if p1 is None or p2 is None:
        return 0.5
    return float(p1 @ phi @ p2)


def build_graph(n_ing, n_cmp, ic_edges, pairs, config, profiles, phi, ing_name2idx, class_feat):
    data = HeteroData()
    data['ingredient'].x = class_feat
    data['compound'].x   = torch.eye(n_cmp)

    if ic_edges:
        src = torch.tensor([e[0] for e in ic_edges])
        dst = torch.tensor([e[1] for e in ic_edges])
        data['ingredient', 'has', 'compound'].edge_index = torch.stack([src, dst])
        data['compound', 'rev_has', 'ingredient'].edge_index = torch.stack([dst, src])

    ii_src, ii_dst, ii_w = [], [], []
    for (n1, n2, combined, pmi, _shared) in pairs:
        if n1 not in ing_name2idx or n2 not in ing_name2idx:
            continue
        i1, i2 = ing_name2idx[n1], ing_name2idx[n2]
        if config == 'D':
            w = pmi * compat(n1, n2, profiles, phi)
        else:
            w = combined
        if w > 0:
            ii_src += [i1, i2]; ii_dst += [i2, i1]; ii_w += [w, w]

    if ii_src:
        data['ingredient', 'pairs', 'ingredient'].edge_index = torch.tensor([ii_src, ii_dst])
        data['ingredient', 'pairs', 'ingredient'].edge_attr  = torch.tensor(ii_w, dtype=torch.float).unsqueeze(1)

    return data


class FlavorClassHGN(torch.nn.Module):
    def __init__(self, ing_feat_dim, n_cmp, hidden=64, layers=3):
        super().__init__()
        self.ing_proj = torch.nn.Linear(ing_feat_dim, hidden)
        self.cmp_proj = torch.nn.Linear(n_cmp, hidden)
        metadata = (
            ['ingredient', 'compound'],
            [('ingredient','has','compound'),
             ('compound','rev_has','ingredient'),
             ('ingredient','pairs','ingredient')]
        )
        self.convs = torch.nn.ModuleList(
            [HGTConv(hidden, hidden, metadata, heads=2) for _ in range(layers)]
        )

    def forward(self, data):
        x_dict = {
            'ingredient': self.ing_proj(data['ingredient'].x),
            'compound':   self.cmp_proj(data['compound'].x),
        }
        ei = {k: data[k].edge_index for k in data.edge_types}
        for conv in self.convs:
            x_dict = conv(x_dict, ei)
            x_dict = {k: F.relu(v) for k, v in x_dict.items()}
        return x_dict['ingredient']


def bpr_loss(emb, pos_i, pos_j, neg_k):
    return -F.logsigmoid((emb[pos_i] * emb[pos_j]).sum(1) - (emb[pos_i] * emb[neg_k]).sum(1)).mean()


def complement_penalty(emb, si, sj, ri, rj, margin=0.2):
    if si is None or ri is None:
        return torch.tensor(0.0)
    s_syn = (emb[si] * emb[sj]).sum(1)
    s_red = (emb[ri] * emb[rj]).sum(1)
    n = min(len(s_syn), len(s_red))
    return F.relu(s_red[:n] - s_syn[:n] + margin).mean()


def sample_batch(pairs, ing_name2idx, n_ing, profiles, phi, batch_size):
    all_pos = [(ing_name2idx[r[0]], ing_name2idx[r[1]], r[3],
                compat(r[0], r[1], profiles, phi))
               for r in pairs if r[0] in ing_name2idx and r[1] in ing_name2idx]
    if not all_pos:
        return [None] * 7

    pmi_med    = np.median([x[2] for x in all_pos])
    compat_med = np.median([x[3] for x in all_pos])
    syn = [(x[0], x[1]) for x in all_pos if x[2] >= pmi_med and x[3] < compat_med]
    red = [(x[0], x[1]) for x in all_pos if x[2] >= pmi_med and x[3] >= compat_med]
    pos = [(x[0], x[1]) for x in all_pos]

    def pick(lst, n):
        if not lst:
            return None, None
        ch = [lst[random.randint(0, len(lst)-1)] for _ in range(n)]
        return torch.tensor([c[0] for c in ch]), torch.tensor([c[1] for c in ch])

    pi, pj = pick(pos, batch_size)
    si, sj = pick(syn, batch_size)
    ri, rj = pick(red, batch_size)
    return pi, pj, torch.randint(0, n_ing, (batch_size,)), si, sj, ri, rj


def score_model(emb_np, pairs, ing_name2idx, profiles, phi):
    gnn_scores, pmis, compats = [], [], []
    for (n1, n2, _combined, pmi, _shared) in pairs:
        if n1 not in ing_name2idx or n2 not in ing_name2idx:
            continue
        i1, i2 = ing_name2idx[n1], ing_name2idx[n2]
        e1, e2 = emb_np[i1], emb_np[i2]
        denom = np.linalg.norm(e1) * np.linalg.norm(e2)
        s = float(np.dot(e1, e2) / denom) if denom > 1e-9 else 0.0
        gnn_scores.append(s)
        pmis.append(pmi)
        compats.append(compat(n1, n2, profiles, phi))
    if len(gnn_scores) < 10:
        return dict(pmi=0.0, compat=0.0)
    return dict(
        pmi   = spearmanr(gnn_scores, pmis).statistic,
        compat = spearmanr(gnn_scores, compats).statistic,
    )


def run(config, ing_name2idx, cmp_id2idx, n_ing, n_cmp, ic_edges, pairs, profiles, phi, seed):
    torch.manual_seed(seed); random.seed(seed); np.random.seed(seed)

    one_hot = torch.eye(n_ing)
    if config in ('B', 'C', 'D'):
        class_vecs = torch.zeros(n_ing, K)
        for name, idx in ing_name2idx.items():
            if name in profiles:
                class_vecs[idx] = torch.tensor(profiles[name])
        class_feat = torch.cat([one_hot, class_vecs], dim=1)
    else:
        class_feat = one_hot

    data  = build_graph(n_ing, n_cmp, ic_edges, pairs, config, profiles, phi, ing_name2idx, class_feat)
    model = FlavorClassHGN(class_feat.shape[1], n_cmp, hidden=64, layers=3)
    optim = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)

    for _ep in range(200):
        model.train(); optim.zero_grad()
        emb = model(data)
        pi, pj, neg_k, si, sj, ri, rj = sample_batch(pairs, ing_name2idx, n_ing, profiles, phi, 512)
        if pi is None:
            break
        loss = bpr_loss(emb, pi, pj, neg_k)
        if config == 'C' and si is not None and ri is not None:
            loss = loss + 0.1 * complement_penalty(emb, si, sj, ri, rj)
        loss.backward(); optim.step()

    model.eval()
    with torch.no_grad():
        emb_np = model(data).numpy()

    return score_model(emb_np, pairs, ing_name2idx, profiles, phi)


def main():
    print("Loading data...")
    ing_name2idx, cmp_id2idx, n_ing, n_cmp, ic_edges, pairs = load_data()
    profiles = load_profiles()
    phi = build_class_pmi_matrix(pairs, ing_name2idx, profiles)

    print(f"Ingredients: {n_ing}, Compounds: {n_cmp}, Pairs: {len(pairs)}")
    print(f"Class PMI matrix nonzero={(phi > 0).sum()}/{K*K}")

    results = {}
    for cfg in ['A', 'B', 'C', 'D']:
        seed_metrics = []
        for seed in SEEDS:
            print(f"  [{cfg}] seed={seed} ...", flush=True)
            m = run(cfg, ing_name2idx, cmp_id2idx, n_ing, n_cmp, ic_edges, pairs, profiles, phi, seed)
            seed_metrics.append(m)
            print(f"    Spear(PMI)={m['pmi']:+.4f}  Spear(compat)={m['compat']:+.4f}")
        results[cfg] = seed_metrics

    print("\n=== FlavorClass-HGN (Main: Spearman(GNN, PMI)) ===\n")
    print(f"{'Cfg':<5} {'Spear(PMI)':>14} {'Spear(compat)':>14}")
    print("-" * 35)
    for cfg, sm in results.items():
        pmi_v = [m['pmi'] for m in sm]
        cmp_v = [m['compat'] for m in sm]
        print(f"{cfg:<5} {np.mean(pmi_v):+.4f}±{np.std(pmi_v):.4f}  {np.mean(cmp_v):+.4f}±{np.std(cmp_v):.4f}")

    with open("scripts/gnn/18_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved → scripts/gnn/18_results.json")


if __name__ == "__main__":
    main()
