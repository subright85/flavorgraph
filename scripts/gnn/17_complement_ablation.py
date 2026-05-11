"""
T4 Complement-Aware BPR Ablation
Configs: A=baseline BPR, B=synergistic-vs-redundant BPR, C=PMI-only BPR
Seeds: [42, 123, 2024] x 3 configs = 9 runs
Metrics: Spearman(GNN, shared_count), (GNN, flavor_sim), (GNN, complement), (GNN, PMI)
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

# ── load graph data ───────────────────────────────────────────────────────────
def load_data():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM ingredient")
    ing_rows = cur.fetchall()
    # name -> idx (pair_score uses names, not ids)
    ing_name2idx = {r[1]: i for i, r in enumerate(ing_rows)}
    n_ing = len(ing_rows)

    cur.execute("SELECT id, name, flavor_class FROM compound")
    cmp_rows = cur.fetchall()
    cmp_id2idx = {r[0]: i for i, r in enumerate(cmp_rows)}
    n_cmp = len(cmp_rows)

    # ingredient-compound edges (use ingredient.name via join)
    cur.execute("""
        SELECT i.name, ic.compound_id
        FROM ingredient_compound ic
        JOIN ingredient i ON i.id = ic.ingredient_id
    """)
    ic_edges = [(ing_name2idx[r[0]], cmp_id2idx[r[1]])
                for r in cur.fetchall()
                if r[0] in ing_name2idx and r[1] in cmp_id2idx]

    # pairings (ing_a, ing_b are names)
    cur.execute("SELECT ing_a, ing_b, combined_score, pmi_score, shared_count FROM pair_score")
    pair_rows_raw = cur.fetchall()
    # deduplicate (table has both directions)
    seen = set()
    pair_rows = []
    for r in pair_rows_raw:
        key = (min(r[0], r[1]), max(r[0], r[1]))
        if key not in seen:
            seen.add(key)
            pair_rows.append((r[0], r[1], r[2], r[3], r[4]))  # name_a, name_b, combined, pmi, shared_count

    conn.close()
    return ing_name2idx, cmp_id2idx, n_ing, n_cmp, ic_edges, pair_rows

# ── flavor similarity from profile ───────────────────────────────────────────
def load_flavor_profiles():
    profile_path = os.path.join(DATA_DIR, "ingredient_flavor_profile.json")
    if not os.path.exists(profile_path):
        return {}
    with open(profile_path) as f:
        return json.load(f)

def profile_to_vec(profile):
    keys = ['alcohol', 'ester', 'sulfur', 'aldehyde', 'nitrogen', 'acid', 'terpene', 'aromatic', 'phenol', 'other']
    total = profile.get('total', 1) or 1
    return [profile.get(k, 0) / total for k in keys]

def cosine_sim(p1, p2):
    a = np.array(profile_to_vec(p1))
    b = np.array(profile_to_vec(p2))
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom > 1e-9 else 0.0

# ── build hetero graph ────────────────────────────────────────────────────────
def build_graph(n_ing, n_cmp, ic_edges, pair_rows, config, flavor_profiles, ing_name2idx):
    data = HeteroData()
    data['ingredient'].x = torch.eye(n_ing)
    data['compound'].x  = torch.eye(n_cmp)

    if ic_edges:
        src = torch.tensor([e[0] for e in ic_edges])
        dst = torch.tensor([e[1] for e in ic_edges])
        data['ingredient', 'has', 'compound'].edge_index = torch.stack([src, dst])
        data['compound', 'rev_has', 'ingredient'].edge_index = torch.stack([dst, src])

    ii_src, ii_dst, ii_w = [], [], []

    for (n1, n2, combined, pmi, _shared) in pair_rows:
        if n1 not in ing_name2idx or n2 not in ing_name2idx:
            continue
        idx1 = ing_name2idx[n1]
        idx2 = ing_name2idx[n2]

        if config == 'A':
            w = float(combined) if combined else 0.0
        elif config == 'B':
            p1 = flavor_profiles.get(n1)
            p2 = flavor_profiles.get(n2)
            fsim = cosine_sim(p1, p2) if (p1 and p2) else 0.5
            pmi_val = float(pmi) if pmi else 0.0
            w = max(0.0, pmi_val * (1.0 - fsim))
        elif config == 'C':
            w = float(pmi) if pmi else 0.0
        else:
            w = 0.0

        if w > 0:
            ii_src += [idx1, idx2]; ii_dst += [idx2, idx1]; ii_w += [w, w]

    if ii_src:
        data['ingredient', 'pairs', 'ingredient'].edge_index = torch.tensor([ii_src, ii_dst])
        data['ingredient', 'pairs', 'ingredient'].edge_attr  = torch.tensor(ii_w, dtype=torch.float).unsqueeze(1)

    return data

# ── HGT encoder ──────────────────────────────────────────────────────────────
class FlavorHGN(torch.nn.Module):
    def __init__(self, n_ing, n_cmp, hidden=64, layers=3):
        super().__init__()
        self.ing_proj = torch.nn.Linear(n_ing, hidden)
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
        edge_index_dict = {k: data[k].edge_index for k in data.edge_types}
        for conv in self.convs:
            x_dict = conv(x_dict, edge_index_dict)
            x_dict = {k: F.relu(v) for k, v in x_dict.items()}
        return x_dict['ingredient']

# ── BPR ───────────────────────────────────────────────────────────────────────
def bpr_loss(emb, pos_i, pos_j, neg_k):
    s_pos = (emb[pos_i] * emb[pos_j]).sum(dim=1)
    s_neg = (emb[pos_i] * emb[neg_k]).sum(dim=1)
    return -F.logsigmoid(s_pos - s_neg).mean()

def sample_bpr(pair_rows, ing_name2idx, n_ing, batch_size):
    positives = [(ing_name2idx[r[0]], ing_name2idx[r[1]])
                 for r in pair_rows if r[0] in ing_name2idx and r[1] in ing_name2idx]
    if not positives:
        return None, None, None
    chosen = [positives[random.randint(0, len(positives)-1)] for _ in range(batch_size)]
    pos_i = torch.tensor([c[0] for c in chosen])
    pos_j = torch.tensor([c[1] for c in chosen])
    neg_k = torch.randint(0, n_ing, (batch_size,))
    return pos_i, pos_j, neg_k

# ── evaluation ────────────────────────────────────────────────────────────────
def evaluate(emb_np, pair_rows, ing_name2idx, flavor_profiles):
    gnn_scores, shared_cnts, fsims, complements, pmis = [], [], [], [], []

    for (n1, n2, _combined, pmi, shared) in pair_rows:
        if n1 not in ing_name2idx or n2 not in ing_name2idx:
            continue
        i1, i2 = ing_name2idx[n1], ing_name2idx[n2]
        e1, e2 = emb_np[i1], emb_np[i2]
        denom = np.linalg.norm(e1) * np.linalg.norm(e2)
        gnn = float(np.dot(e1, e2) / denom) if denom > 1e-9 else 0.0
        gnn_scores.append(gnn)

        shared_cnts.append(float(shared) if shared else 0.0)

        p1 = flavor_profiles.get(n1)
        p2 = flavor_profiles.get(n2)
        fsim = cosine_sim(p1, p2) if (p1 and p2) else 0.5
        fsims.append(fsim)
        complements.append(1.0 - fsim)
        pmis.append(float(pmi) if pmi else 0.0)

    if len(gnn_scores) < 10:
        return dict(shared=0, fsim=0, complement=0, pmi=0)

    return dict(
        shared     = spearmanr(gnn_scores, shared_cnts).statistic,
        fsim       = spearmanr(gnn_scores, fsims).statistic,
        complement = spearmanr(gnn_scores, complements).statistic,
        pmi        = spearmanr(gnn_scores, pmis).statistic,
    )

# ── train one config/seed ─────────────────────────────────────────────────────
def run_config(config_name, ing_name2idx, cmp_id2idx, n_ing, n_cmp, ic_edges, pair_rows, flavor_profiles, seed):
    torch.manual_seed(seed); random.seed(seed); np.random.seed(seed)

    data  = build_graph(n_ing, n_cmp, ic_edges, pair_rows, config_name, flavor_profiles, ing_name2idx)
    model = FlavorHGN(n_ing, n_cmp, hidden=64, layers=3)
    optim = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)

    for _epoch in range(200):
        model.train(); optim.zero_grad()
        emb = model(data)
        pos_i, pos_j, neg_k = sample_bpr(pair_rows, ing_name2idx, n_ing, 512)
        if pos_i is None:
            break
        loss = bpr_loss(emb, pos_i, pos_j, neg_k)
        loss.backward(); optim.step()

    model.eval()
    with torch.no_grad():
        emb_np = model(data).numpy()

    return evaluate(emb_np, pair_rows, ing_name2idx, flavor_profiles)


def main():
    print("Loading data...")
    ing_name2idx, cmp_id2idx, n_ing, n_cmp, ic_edges, pair_rows = load_data()
    flavor_profiles = load_flavor_profiles()
    print(f"Ingredients: {n_ing}, Compounds: {n_cmp}, IC edges: {len(ic_edges)}, Pairs: {len(pair_rows)}")

    configs = {
        'A_baseline':    'A',
        'B_synergistic': 'B',
        'C_pmi_only':    'C',
    }

    results = {}
    for label, cfg in configs.items():
        seed_metrics = []
        for seed in SEEDS:
            print(f"  [{label}] seed={seed} ...", flush=True)
            m = run_config(cfg, ing_name2idx, cmp_id2idx, n_ing, n_cmp, ic_edges, pair_rows, flavor_profiles, seed)
            seed_metrics.append(m)
            print(f"    shared={m['shared']:+.4f}  fsim={m['fsim']:+.4f}  complement={m['complement']:+.4f}  pmi={m['pmi']:+.4f}")
        results[label] = seed_metrics

    print("\n=== T4 Complement-Aware BPR Ablation — Summary ===\n")
    print(f"{'Config':<20} {'Spear(shared)':>14} {'Spear(fsim)':>12} {'Spear(complement)':>18} {'Spear(pmi)':>11}")
    print("-" * 78)
    for label, sm in results.items():
        row = f"{label:<20}"
        for key in ['shared', 'fsim', 'complement', 'pmi']:
            vals = [m[key] for m in sm]
            row += f"  {np.mean(vals):+.4f}±{np.std(vals):.4f}"
        print(row)

    out_path = os.path.join("scripts/gnn", "17_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved → {out_path}")


if __name__ == "__main__":
    main()
