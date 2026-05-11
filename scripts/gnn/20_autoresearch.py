"""
20_autoresearch.py — FlavorGraph Class-Conditioned Relation Decoder
Inspired by karpathy/autoresearch: fixed time budget, single metric, auto keep/discard.

Core algorithm: s(i,j) = z(i)^T R[c(i), c(j)] z(j)
R: (8, 8, hidden, hidden) relation matrices initialized from class PMI matrix Phi.
This overcomes DistMult's single-metric limitation and encodes class-level pairing knowledge.

Metric: Spearman(GNN_score, PMI) — higher is better.
Time budget: TIME_BUDGET seconds per experiment.
"""

import sqlite3, json, time, os, sys, csv
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy.stats import spearmanr

DB_PATH = "flavorgraph_v2.db"
TIME_BUDGET = 180  # 3 min per experiment (6 configs ~ 18 min total)
RESULTS_TSV = "scripts/gnn/20_results.tsv"
N_SEEDS = 3
SEEDS = [42, 123, 2024]
N_CLASS = 8

# ============================================================
# EDITABLE: Experiment configs
# ============================================================
CONFIGS = [
    # tag, hidden, layers, n_epochs_cap, lambda_r, r_init, dropout
    dict(tag="A_baseline",  hidden=64,  layers=3, lambda_r=0.0, r_init="eye",  dropout=0.0),  # original HGT, no relation decoder
    dict(tag="B_1layer",    hidden=64,  layers=1, lambda_r=0.0, r_init="eye",  dropout=0.0),  # fix oversmoothing: 1 layer
    dict(tag="C_rel_phi",   hidden=64,  layers=1, lambda_r=0.1, r_init="phi",  dropout=0.0),  # class-conditioned + phi init
    dict(tag="D_rel_eye",   hidden=64,  layers=1, lambda_r=0.1, r_init="eye",  dropout=0.0),  # class-conditioned + eye init
    dict(tag="E_rel_phi_d", hidden=64,  layers=1, lambda_r=0.1, r_init="phi",  dropout=0.1),  # + dropout
    dict(tag="F_rel_h128",  hidden=128, layers=1, lambda_r=0.1, r_init="phi",  dropout=0.0),  # larger hidden
]

# ============================================================
# FIXED HARNESS (do not modify below for experiments)
# ============================================================

def load_data():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # Ingredients
    rows = cur.execute("SELECT id, name FROM ingredient ORDER BY id").fetchall()
    id2name = {r[0]: r[1] for r in rows}
    name2id = {r[1]: r[0] for r in rows}
    n_ing = len(id2name)

    # Compounds
    comp_rows = cur.execute("SELECT id FROM compound ORDER BY id").fetchall()
    n_comp = len(comp_rows)
    comp_ids = [r[0] for r in comp_rows]
    comp2idx = {cid: i for i, cid in enumerate(comp_ids)}

    # Edges: ingredient <-> compound
    ic_rows = cur.execute("SELECT ingredient_id, compound_id FROM ingredient_compound").fetchall()
    ing_edge, comp_edge = [], []
    for ing_id, comp_id in ic_rows:
        if ing_id in id2name and comp_id in comp2idx:
            ing_edge.append(ing_id - 1)  # 0-indexed
            comp_edge.append(comp2idx[comp_id])

    # Pair scores (PMI proxy)
    pair_rows = cur.execute("SELECT ing_a, ing_b, pmi_score FROM pair_score").fetchall()
    pairs = []
    for a, b, s in pair_rows:
        if a in name2id and b in name2id:
            pairs.append((name2id[a] - 1, name2id[b] - 1, float(s)))

    # Flavor profiles → class assignment (argmax)
    with open("data/ingredient_flavor_profile.json") as f:
        profiles = json.load(f)
    CLASS_KEYS = ["sulfur","ester","alcohol","aldehyde","nitrogen","acid","terpene","other"]
    class_labels = np.zeros(n_ing, dtype=np.int64)
    for name, vec in profiles.items():
        if name in name2id:
            idx = name2id[name] - 1
            vals = [vec.get(k, 0.0) for k in CLASS_KEYS]
            class_labels[idx] = int(np.argmax(vals))

    con.close()
    return {
        "n_ing": n_ing, "n_comp": n_comp,
        "ing_edge": ing_edge, "comp_edge": comp_edge,
        "pairs": pairs, "class_labels": class_labels,
        "profiles": profiles, "name2id": name2id, "CLASS_KEYS": CLASS_KEYS,
    }


def compute_phi(data):
    """Class PMI matrix Phi[k,l] = mean PMI for class-k x class-l pairs."""
    cl = data["class_labels"]
    phi = np.zeros((N_CLASS, N_CLASS))
    cnt = np.zeros((N_CLASS, N_CLASS))
    for i, j, s in data["pairs"]:
        k, l = int(cl[i]), int(cl[j])
        phi[k, l] += s
        phi[l, k] += s
        cnt[k, l] += 1
        cnt[l, k] += 1
    cnt = np.maximum(cnt, 1)
    phi = phi / cnt
    # Normalize to [0, 1]
    phi = (phi - phi.min()) / (phi.max() - phi.min() + 1e-8)
    return phi.astype(np.float32)


def build_pyg_data(data, device):
    """Build PyG HeteroData for HGT."""
    from torch_geometric.data import HeteroData
    n_ing = data["n_ing"]
    n_comp = data["n_comp"]

    hdata = HeteroData()
    hdata["ingredient"].x = torch.eye(n_ing, device=device)
    hdata["compound"].x = torch.eye(n_comp, device=device)

    ing_t = torch.tensor(data["ing_edge"], dtype=torch.long, device=device)
    com_t = torch.tensor(data["comp_edge"], dtype=torch.long, device=device)
    edge_index = torch.stack([ing_t, com_t])
    hdata["ingredient", "has", "compound"].edge_index = edge_index
    hdata["compound", "rev_has", "ingredient"].edge_index = torch.stack([com_t, ing_t])
    return hdata


# ============================================================
# Model
# ============================================================

class HGTEncoder(nn.Module):
    def __init__(self, n_ing, n_comp, hidden, n_layers, dropout=0.0):
        super().__init__()
        from torch_geometric.nn import HGTConv, Linear
        self.ing_proj = nn.Linear(n_ing, hidden, bias=False)
        self.comp_proj = nn.Linear(n_comp, hidden, bias=False)
        self.convs = nn.ModuleList()
        metadata = (
            ["ingredient", "compound"],
            [("ingredient", "has", "compound"), ("compound", "rev_has", "ingredient")]
        )
        for _ in range(n_layers):
            self.convs.append(HGTConv(hidden, hidden, metadata, heads=2))
        self.dropout = dropout

    def forward(self, hdata):
        x_dict = {
            "ingredient": self.ing_proj(hdata["ingredient"].x),
            "compound": self.comp_proj(hdata["compound"].x),
        }
        edge_index_dict = {k: hdata[k].edge_index for k in hdata.edge_types}
        for conv in self.convs:
            x_dict = conv(x_dict, edge_index_dict)
            if self.dropout > 0:
                x_dict = {k: F.dropout(v, p=self.dropout, training=self.training) for k, v in x_dict.items()}
        return x_dict["ingredient"]  # (n_ing, hidden)


class RelationDecoder(nn.Module):
    """Class-Conditioned Relation Decoder: s(i,j) = z_i^T R[c_i, c_j] z_j"""
    def __init__(self, hidden, n_class, phi=None, r_init="phi"):
        super().__init__()
        # R: (n_class, n_class, hidden, hidden)
        R = torch.zeros(n_class, n_class, hidden, hidden)
        if r_init == "phi" and phi is not None:
            # Initialize each R[k,l] = phi[k,l] * I
            phi_t = torch.tensor(phi)
            for k in range(n_class):
                for l in range(n_class):
                    R[k, l] = phi_t[k, l] * torch.eye(hidden)
        else:
            # Eye init
            for k in range(n_class):
                for l in range(n_class):
                    R[k, l] = torch.eye(hidden) * 0.1
        self.R = nn.Parameter(R)

    def score(self, z, i_idx, j_idx, class_labels):
        ci = class_labels[i_idx]  # (batch,)
        cj = class_labels[j_idx]
        # Gather relation matrices for each pair
        R_ij = self.R[ci, cj]  # (batch, hidden, hidden)
        zi = z[i_idx]  # (batch, hidden)
        zj = z[j_idx]
        # s = z_i^T R z_j
        s = torch.einsum("bi,bij,bj->b", zi, R_ij, zj)
        return s


class DotDecoder(nn.Module):
    """Baseline DistMult-style dot product."""
    def score(self, z, i_idx, j_idx, class_labels=None):
        return (z[i_idx] * z[j_idx]).sum(dim=-1)


class FlavorHGN(nn.Module):
    def __init__(self, n_ing, n_comp, hidden, n_layers, n_class, phi, r_init, dropout):
        super().__init__()
        self.encoder = HGTEncoder(n_ing, n_comp, hidden, n_layers, dropout)
        if r_init == "eye" and False:  # force relation decoder always for config C-F
            self.decoder = DotDecoder()
            self.use_relation = False
        else:
            self.decoder = RelationDecoder(hidden, n_class, phi, r_init)
            self.use_relation = True

    def forward(self, hdata):
        return self.encoder(hdata)

    def score(self, z, i_idx, j_idx, class_labels):
        if self.use_relation:
            return self.decoder.score(z, i_idx, j_idx, class_labels)
        return self.decoder.score(z, i_idx, j_idx)


class BaselineHGN(nn.Module):
    """Original HGT + dot product (config A)."""
    def __init__(self, n_ing, n_comp, hidden, n_layers, dropout):
        super().__init__()
        self.encoder = HGTEncoder(n_ing, n_comp, hidden, n_layers, dropout)
        self.decoder = DotDecoder()

    def forward(self, hdata):
        return self.encoder(hdata)

    def score(self, z, i_idx, j_idx, class_labels=None):
        return self.decoder.score(z, i_idx, j_idx)


# ============================================================
# Training
# ============================================================

def bpr_loss(pos_scores, neg_scores):
    return -F.logsigmoid(pos_scores - neg_scores).mean()


def run_experiment(config, data, phi, seed, time_budget, device):
    torch.manual_seed(seed)
    np.random.seed(seed)

    hdata = build_pyg_data(data, device)
    n_ing = data["n_ing"]
    n_comp = data["n_comp"]
    hidden = config["hidden"]
    n_layers = config["layers"]
    dropout = config["dropout"]
    r_init = config["r_init"]
    lambda_r = config["lambda_r"]
    cl = torch.tensor(data["class_labels"], dtype=torch.long, device=device)

    # Build model
    if config["tag"].startswith("A"):
        model = BaselineHGN(n_ing, n_comp, hidden, n_layers, dropout).to(device)
    else:
        model = FlavorHGN(n_ing, n_comp, hidden, n_layers, N_CLASS, phi, r_init, dropout).to(device)

    opt = torch.optim.Adam(model.parameters(), lr=1e-3)

    # Pair tensors
    pairs = data["pairs"]
    n_pairs = len(pairs)
    pos_i = torch.tensor([p[0] for p in pairs], dtype=torch.long, device=device)
    pos_j = torch.tensor([p[1] for p in pairs], dtype=torch.long, device=device)
    pmi_vals = torch.tensor([p[2] for p in pairs], dtype=torch.float, device=device)

    # High/low PMI split for BPR
    med = pmi_vals.median()
    high_mask = pmi_vals >= med
    high_idx = high_mask.nonzero(as_tuple=True)[0]
    low_idx  = (~high_mask).nonzero(as_tuple=True)[0]

    BATCH = 512
    t0 = time.time()
    step = 0
    model.train()

    while time.time() - t0 < time_budget:
        # Sample BPR batch: pos from high-PMI, neg from low-PMI
        perm_p = high_idx[torch.randint(len(high_idx), (BATCH,))]
        perm_n = low_idx[torch.randint(len(low_idx), (BATCH,))]

        z = model(hdata)

        pos_s = model.score(z, pos_i[perm_p], pos_j[perm_p], cl)
        neg_s = model.score(z, pos_i[perm_n], pos_j[perm_n], cl)

        loss = bpr_loss(pos_s, neg_s)

        # Optional: relation regularization (penalize large R deviation from init)
        if lambda_r > 0 and hasattr(model, 'decoder') and isinstance(model.decoder, RelationDecoder):
            reg = model.decoder.R.pow(2).mean()
            loss = loss + lambda_r * reg

        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        step += 1

    elapsed = time.time() - t0

    # Evaluate: Spearman(GNN_score, PMI)
    model.eval()
    with torch.no_grad():
        z = model(hdata)
        gnn_scores = model.score(z, pos_i, pos_j, cl).cpu().numpy()
    pmi_np = pmi_vals.cpu().numpy()
    spear, _ = spearmanr(gnn_scores, pmi_np)

    return {"spearman": float(spear), "steps": step, "elapsed": elapsed}


# ============================================================
# Main
# ============================================================

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    print("Loading data...")
    data = load_data()
    phi_np = compute_phi(data)
    phi_t = torch.tensor(phi_np, device=device)
    print(f"  {data['n_ing']} ingredients, {data['n_comp']} compounds, {len(data['pairs'])} pairs")
    print(f"  Class PMI matrix Phi computed ({N_CLASS}x{N_CLASS})")

    # Init results TSV
    write_header = not os.path.exists(RESULTS_TSV)
    tsv_f = open(RESULTS_TSV, "a", newline="")
    writer = csv.writer(tsv_f, delimiter="\t")
    if write_header:
        writer.writerow(["tag", "seed", "spearman", "steps", "elapsed_s", "hidden", "layers", "r_init", "lambda_r"])
        tsv_f.flush()

    best_mean = -999.0
    summary_rows = []

    for cfg in CONFIGS:
        tag = cfg["tag"]
        spears = []
        print(f"\n--- {tag} (h={cfg['hidden']}, L={cfg['layers']}, r_init={cfg['r_init']}, λ={cfg['lambda_r']}) ---")
        for seed in SEEDS:
            t0 = time.time()
            res = run_experiment(cfg, data, phi_np, seed, TIME_BUDGET, device)
            spears.append(res["spearman"])
            print(f"  seed={seed}  Spearman={res['spearman']:.4f}  steps={res['steps']}  t={res['elapsed']:.0f}s")
            writer.writerow([tag, seed, f"{res['spearman']:.4f}", res["steps"],
                             f"{res['elapsed']:.1f}", cfg["hidden"], cfg["layers"],
                             cfg["r_init"], cfg["lambda_r"]])
            tsv_f.flush()

        mean_s = float(np.mean(spears))
        std_s  = float(np.std(spears))
        status = "keep" if mean_s > best_mean else "discard"
        if mean_s > best_mean:
            best_mean = mean_s
        print(f"  → mean={mean_s:.4f}±{std_s:.4f}  [{status}]")
        summary_rows.append((tag, mean_s, std_s, status))

    tsv_f.close()

    print("\n" + "="*55)
    print("=== 20: Class-Conditioned Relation Decoder Results ===")
    print("="*55)
    print(f"{'Config':<16} {'Spearman':>12}  Status")
    print("-"*40)
    for tag, mean_s, std_s, status in summary_rows:
        marker = " ★" if status == "keep" and mean_s == best_mean else ""
        print(f"{tag:<16} {mean_s:.4f}±{std_s:.4f}  {status}{marker}")

    # Save JSON summary
    result_json = {cfg_tag: {"mean": m, "std": s, "status": st}
                   for cfg_tag, m, s, st in summary_rows}
    with open("scripts/gnn/20_results.json", "w") as f:
        json.dump(result_json, f, indent=2)
    print("\nSaved → scripts/gnn/20_results.json")
    print(f"TSV log → {RESULTS_TSV}")


if __name__ == "__main__":
    main()
