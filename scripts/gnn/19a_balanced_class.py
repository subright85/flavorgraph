"""
19a: Balanced Masked Flavor Class Prediction
Same as 19 but with per-class undersampling to remove alcohol-65% bias.
Random baseline = 1/10 = 0.10
Models: A=class MLP, B=GNN emb, C=compat-GNN emb
"""
import ast, csv, json, random, sqlite3, os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import HeteroData
from torch_geometric.nn import HGTConv
from collections import defaultdict

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
        sums[c1,c2] += pmi; sums[c2,c1] += pmi
        cnts[c1,c2] += 1;   cnts[c2,c1] += 1
    with np.errstate(invalid='ignore'):
        mat = np.where(cnts > 0, sums / cnts, 0.0).astype(np.float32)
    mx = mat.max()
    return mat / mx if mx > 0 else mat


def build_recipe_dataset_balanced(name2idx, profiles, min_match=3):
    random.seed(42)
    by_class = defaultdict(list)
    with open(os.path.join(DATA_DIR, "RAW_recipes.csv")) as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                ings = ast.literal_eval(row['ingredients'])
            except Exception:
                continue
            matched = list(set(name2idx[g.lower()] for g in ings if g.lower() in name2idx))
            matched = [m for m in matched if m in profiles]
            if len(matched) < min_match:
                continue
            target = matched[random.randint(0, len(matched)-1)]
            context = [m for m in matched if m != target]
            cls = int(np.argmax(profiles[target]))
            by_class[cls].append((context, target, cls))

    print("  Class counts before balancing:")
    for cls, samples in sorted(by_class.items()):
        print(f"    {FLAVOR_KEYS[cls]:<12}: {len(samples)}")

    min_count = min(len(v) for v in by_class.values())
    balanced = []
    for cls, samples in by_class.items():
        random.shuffle(samples)
        balanced.extend(samples[:min_count])
    random.shuffle(balanced)
    print(f"  Balanced: {len(balanced)} samples ({min_count} per class)")
    return balanced


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


class GNN(nn.Module):
    def __init__(self, in_dim, n_cmp, hidden=64, layers=3):
        super().__init__()
        self.ing_proj = nn.Linear(in_dim, hidden)
        self.cmp_proj = nn.Linear(n_cmp, hidden)
        metadata = (
            ['ingredient', 'compound'],
            [('ingredient','has','compound'),
             ('compound','rev_has','ingredient'),
             ('ingredient','pairs','ingredient')]
        )
        self.convs = nn.ModuleList(
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


def get_gnn_emb(graph, pairs, name2idx, n_ing, n_cmp, config, seed):
    torch.manual_seed(seed); random.seed(seed)
    in_dim = n_ing if config == 'B' else n_ing + K
    model = GNN(in_dim, n_cmp)
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


def run_clf(model_type, balanced_data, profiles, emb_np, seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    random.shuffle(balanced_data)
    split = int(0.8 * len(balanced_data))
    train_s = balanced_data[:split]
    test_s  = balanced_data[split:]

    def featurize(samples):
        X, y = [], []
        for (ctx, _tgt, cls) in samples:
            if model_type == 'A':
                vecs = [profiles[i] for i in ctx if i in profiles]
                if not vecs: continue
                feat = np.sum(vecs, axis=0)
            else:
                embs = [emb_np[i] for i in ctx]
                if not embs: continue
                feat = np.mean(embs, axis=0)
            X.append(feat); y.append(cls)
        return np.array(X, np.float32), np.array(y, np.int64)

    Xtr, ytr = featurize(train_s)
    Xte, yte = featurize(test_s)
    if len(Xtr) == 0 or len(Xte) == 0:
        return dict(acc1=0.0, acc3=0.0)

    clf = nn.Sequential(nn.Linear(Xtr.shape[1], 64), nn.ReLU(), nn.Linear(64, K))
    opt = torch.optim.Adam(clf.parameters(), lr=1e-3)
    Xt = torch.tensor(Xtr); yt = torch.tensor(ytr)
    for _ep in range(300):
        clf.train(); opt.zero_grad()
        F.cross_entropy(clf(Xt), yt).backward(); opt.step()
    clf.train(False)
    with torch.no_grad():
        logits = clf(torch.tensor(Xte))
        top1 = logits.argmax(1).numpy()
        top3 = logits.topk(3, dim=1).indices.numpy()
    acc1 = float((top1 == yte).mean())
    acc3 = float(np.mean([yte[i] in top3[i] for i in range(len(yte))]))
    return dict(acc1=acc1, acc3=acc3)


def main():
    print("Loading data...")
    name2idx, n_ing, cmp_id2idx, n_cmp, ic_edges, pairs = load_db()
    profiles = load_profiles(name2idx)
    phi = build_class_phi(pairs, name2idx, profiles)

    print("Building balanced dataset...")
    balanced = build_recipe_dataset_balanced(name2idx, profiles, min_match=3)

    results = {}
    for cfg in ['A', 'B', 'C']:
        seed_metrics = []
        for seed in SEEDS:
            print(f"  [{cfg}] seed={seed}...", flush=True)
            if cfg == 'A':
                emb_np = None
            else:
                graph = build_graph(n_ing, n_cmp, ic_edges, pairs, name2idx, profiles, phi, cfg)
                emb_np = get_gnn_emb(graph, pairs, name2idx, n_ing, n_cmp, cfg, seed)
            m = run_clf(cfg, balanced, profiles, emb_np, seed)
            seed_metrics.append(m)
            print(f"    Acc@1={m['acc1']:.4f}  Acc@3={m['acc3']:.4f}")
        results[cfg] = seed_metrics

    print("\n=== 19a: Balanced Class Prediction ===\n")
    print(f"{'Model':<6} {'Acc@1':>12} {'Acc@3':>12}")
    print("-" * 32)
    print(f"{'random':<6} {1/K:.4f}         {3/K:.4f}")
    for cfg, sm in results.items():
        a1 = [m['acc1'] for m in sm]; a3 = [m['acc3'] for m in sm]
        print(f"{cfg:<6} {np.mean(a1):.4f}±{np.std(a1):.4f}  {np.mean(a3):.4f}±{np.std(a3):.4f}")

    with open("scripts/gnn/19a_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved → scripts/gnn/19a_results.json")


if __name__ == "__main__":
    main()
