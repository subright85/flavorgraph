"""
19b: Ingredient-Level Recipe Completion via MRR
Task: given recipe context (n-1 ingredients), rank all 151 ingredients, measure MRR/Hit@K.
Method: mean(GNN_embedding(context)) -> cosine sim with all ingredient embeddings -> rank.
Models: A=random, B=FlavorHGN baseline, C=FlavorClass-HGN (compat-weighted).
"""
import ast, csv, json, random, sqlite3, os
import numpy as np
import torch
import torch.nn.functional as F
from torch_geometric.data import HeteroData
from torch_geometric.nn import HGTConv

DB_PATH = "flavorgraph_v2.db"
DATA_DIR = "data"
SEEDS = [42, 123, 2024]
FLAVOR_KEYS = ['alcohol', 'ester', 'sulfur', 'aldehyde', 'nitrogen',
               'acid', 'terpene', 'aromatic', 'phenol', 'other']
K = len(FLAVOR_KEYS)


def load_db():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT id, name FROM ingredient ORDER BY id").fetchall()
    name2idx = {r[1].lower(): i for i, r in enumerate(rows)}
    n_ing = len(rows)
    cmp_rows = conn.execute("SELECT id FROM compound ORDER BY id").fetchall()
    cmp_id2idx = {r[0]: i for i, r in enumerate(cmp_rows)}
    n_cmp = len(cmp_rows)
    ic_raw = conn.execute("""
        SELECT i.name, ic.compound_id FROM ingredient_compound ic
        JOIN ingredient i ON i.id = ic.ingredient_id
    """).fetchall()
    ic_edges = [(name2idx[r[0].lower()], cmp_id2idx[r[1]])
                for r in ic_raw if r[0].lower() in name2idx and r[1] in cmp_id2idx]
    pairs_raw = conn.execute(
        "SELECT ing_a, ing_b, combined_score, pmi_score FROM pair_score"
    ).fetchall()
    seen, pairs = set(), []
    for r in pairs_raw:
        key = (min(r[0], r[1]), max(r[0], r[1]))
        if key not in seen and r[0].lower() in name2idx and r[1].lower() in name2idx:
            seen.add(key)
            pairs.append((r[0].lower(), r[1].lower(), float(r[2] or 0), float(r[3] or 0)))
    conn.close()
    return name2idx, n_ing, cmp_id2idx, n_cmp, ic_edges, pairs


def load_profiles(name2idx):
    raw = json.load(open(os.path.join(DATA_DIR, "ingredient_flavor_profile.json")))
    profiles = {}
    for name, d in raw.items():
        if name.lower() in name2idx:
            total = d.get('total', 1) or 1
            vec = np.array([d.get(k, 0) / total for k in FLAVOR_KEYS], dtype=np.float32)
            profiles[name2idx[name.lower()]] = vec
    return profiles


def build_class_phi(pairs, name2idx, profiles):
    sums = np.zeros((K, K)); cnts = np.zeros((K, K))
    for n1, n2, _, pmi in pairs:
        i1, i2 = name2idx.get(n1), name2idx.get(n2)
        if i1 is None or i2 is None: continue
        p1, p2 = profiles.get(i1), profiles.get(i2)
        if p1 is None or p2 is None: continue
        c1, c2 = int(np.argmax(p1)), int(np.argmax(p2))
        sums[c1, c2] += pmi; sums[c2, c1] += pmi
        cnts[c1, c2] += 1;   cnts[c2, c1] += 1
    with np.errstate(invalid='ignore'):
        mat = np.where(cnts > 0, sums / cnts, 0.0).astype(np.float32)
    mx = mat.max()
    return mat / mx if mx > 0 else mat


def build_graph(n_ing, n_cmp, ic_edges, pairs, name2idx, profiles, phi, config):
    data = HeteroData()
    one_hot = torch.eye(n_ing)
    if config == 'C':
        cv = torch.zeros(n_ing, K)
        for idx, vec in profiles.items():
            cv[idx] = torch.tensor(vec)
        data['ingredient'].x = torch.cat([one_hot, cv], dim=1)
    else:
        data['ingredient'].x = one_hot
    data['compound'].x = torch.eye(n_cmp)

    if ic_edges:
        src = torch.tensor([e[0] for e in ic_edges])
        dst = torch.tensor([e[1] for e in ic_edges])
        data['ingredient', 'has', 'compound'].edge_index = torch.stack([src, dst])
        data['compound', 'rev_has', 'ingredient'].edge_index = torch.stack([dst, src])

    ii_src, ii_dst, ii_w = [], [], []
    for n1, n2, combined, pmi in pairs:
        i1, i2 = name2idx.get(n1), name2idx.get(n2)
        if i1 is None or i2 is None: continue
        if config == 'C':
            p1, p2 = profiles.get(i1), profiles.get(i2)
            c_score = float(p1 @ phi @ p2) if (p1 is not None and p2 is not None) else 0.0
            w = pmi * c_score
        else:
            w = combined
        if w > 0:
            ii_src += [i1, i2]; ii_dst += [i2, i1]; ii_w += [w, w]

    if ii_src:
        data['ingredient', 'pairs', 'ingredient'].edge_index = torch.tensor([ii_src, ii_dst])
        data['ingredient', 'pairs', 'ingredient'].edge_attr  = torch.tensor(ii_w, dtype=torch.float).unsqueeze(1)
    return data


class FlavorHGN(torch.nn.Module):
    def __init__(self, in_dim, n_cmp, hidden=64, layers=3):
        super().__init__()
        self.ing_proj = torch.nn.Linear(in_dim, hidden)
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


def train_gnn(graph, pairs, name2idx, n_ing, n_cmp, config, seed):
    torch.manual_seed(seed); random.seed(seed)
    in_dim = n_ing if config == 'B' else n_ing + K
    model = FlavorHGN(in_dim, n_cmp)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)
    pos = [(name2idx[r[0]], name2idx[r[1]]) for r in pairs if r[0] in name2idx and r[1] in name2idx]
    for _ep in range(200):
        model.train(); opt.zero_grad()
        emb = model(graph)
        chosen = [pos[random.randint(0, len(pos)-1)] for _ in range(512)]
        pi = torch.tensor([c[0] for c in chosen])
        pj = torch.tensor([c[1] for c in chosen])
        nk = torch.randint(0, n_ing, (512,))
        loss = -F.logsigmoid((emb[pi]*emb[pj]).sum(1) - (emb[pi]*emb[nk]).sum(1)).mean()
        loss.backward(); opt.step()
    model.train(False)
    with torch.no_grad():
        return model(graph).numpy()


def load_recipes(name2idx, min_match=3, max_recipes=30000):
    random.seed(42)
    out = []
    with open(os.path.join(DATA_DIR, "RAW_recipes.csv")) as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                ings = ast.literal_eval(row['ingredients'])
            except Exception:
                continue
            matched = list(set(name2idx[g.lower()] for g in ings if g.lower() in name2idx))
            if len(matched) < min_match:
                continue
            out.append(matched)
            if len(out) >= max_recipes:
                break
    return out


def mrr_hits(emb_np, recipes, n_ing, seed):
    random.seed(seed)
    rr_list = []
    hits5, hits10 = [], []
    for matched in recipes:
        target = matched[random.randint(0, len(matched)-1)]
        context = [m for m in matched if m != target]
        if not context:
            continue
        ctx_emb = np.mean(emb_np[context], axis=0)
        ctx_norm = ctx_emb / (np.linalg.norm(ctx_emb) + 1e-9)
        sims = emb_np @ ctx_norm  # (n_ing,)
        # exclude context from ranking
        for c in context:
            sims[c] = -999.0
        rank = int(np.sum(sims > sims[target])) + 1
        rr_list.append(1.0 / rank)
        hits5.append(1 if rank <= 5 else 0)
        hits10.append(1 if rank <= 10 else 0)
    return dict(
        mrr   = float(np.mean(rr_list)),
        hit5  = float(np.mean(hits5)),
        hit10 = float(np.mean(hits10)),
    )


def random_baseline(n_ing, n_recipes=10000):
    ranks = [random.randint(1, n_ing) for _ in range(n_recipes)]
    rr = [1/r for r in ranks]
    return dict(
        mrr   = float(np.mean(rr)),
        hit5  = float(sum(r <= 5 for r in ranks) / n_recipes),
        hit10 = float(sum(r <= 10 for r in ranks) / n_recipes),
    )


def main():
    print("Loading data...")
    name2idx, n_ing, cmp_id2idx, n_cmp, ic_edges, pairs = load_db()
    profiles = load_profiles(name2idx)
    phi = build_class_phi(pairs, name2idx, profiles)

    print("Loading recipes...")
    recipes = load_recipes(name2idx, min_match=3, max_recipes=30000)
    print(f"  Recipes: {len(recipes)}")

    rand = random_baseline(n_ing)
    print(f"Random baseline: MRR={rand['mrr']:.4f}  Hit@5={rand['hit5']:.4f}  Hit@10={rand['hit10']:.4f}")

    results = {}
    for cfg in ['B', 'C']:
        seed_metrics = []
        for seed in SEEDS:
            print(f"  [{cfg}] seed={seed} training GNN...", flush=True)
            graph = build_graph(n_ing, n_cmp, ic_edges, pairs, name2idx, profiles, phi, cfg)
            emb_np = train_gnn(graph, pairs, name2idx, n_ing, n_cmp, cfg, seed)
            m = mrr_hits(emb_np, recipes, n_ing, seed)
            seed_metrics.append(m)
            print(f"    MRR={m['mrr']:.4f}  Hit@5={m['hit5']:.4f}  Hit@10={m['hit10']:.4f}")
        results[cfg] = seed_metrics

    print("\n=== 19b: Ingredient-Level Recipe Completion (MRR) ===\n")
    print(f"{'Model':<8} {'MRR':>10} {'Hit@5':>10} {'Hit@10':>10}")
    print("-" * 42)
    print(f"{'random':<8} {rand['mrr']:.4f}      {rand['hit5']:.4f}      {rand['hit10']:.4f}")
    for cfg, sm in results.items():
        m_v  = [m['mrr']  for m in sm]
        h5   = [m['hit5'] for m in sm]
        h10  = [m['hit10'] for m in sm]
        print(f"{cfg:<8} {np.mean(m_v):.4f}±{np.std(m_v):.4f}  {np.mean(h5):.4f}±{np.std(h5):.4f}  {np.mean(h10):.4f}±{np.std(h10):.4f}")

    with open("scripts/gnn/19b_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved → scripts/gnn/19b_results.json")


if __name__ == "__main__":
    main()
