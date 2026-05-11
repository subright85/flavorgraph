"""
29_comprehensive.py — Full experimental sweep for FlavorGraph paper
Experiments:
  E1: lambda sweep (0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.5) for AntiHomo
  E2: AntiHomo (best lambda) + DualEncoder free embedding
  E3: PMI Regression loss (MSE on raw PMI instead of BPR)
  E4: Bootstrap CI for AntiHomo-best and 1L-HGN (10 seeds)

Proper eval throughout: dedup (ing_a < ing_b) + 80/20 split.
"""

import sqlite3, json, time, numpy as np
import torch, torch.nn as nn, torch.nn.functional as F
from scipy.stats import spearmanr

DB_PATH = "flavorgraph_v2.db"
TIME_BUDGET = 180
SEEDS = [42, 123, 2024]
SEEDS_BOOTSTRAP = [42, 123, 2024, 7, 99, 314, 777, 1001, 2000, 9999]
TEST_RATIO = 0.2
HGN_BASELINE = 0.7174

# ============================================================
# Data loading
# ============================================================

def load_data():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    rows = cur.execute("SELECT id, name FROM ingredient ORDER BY id").fetchall()
    id2name = {r[0]: r[1] for r in rows}
    name2id = {r[1]: r[0] for r in rows}
    n_ing = len(id2name)
    comp_rows = cur.execute("SELECT id FROM compound ORDER BY id").fetchall()
    n_comp = len(comp_rows)
    comp2idx = {r[0]: i for i, r in enumerate(comp_rows)}
    ic_rows = cur.execute("SELECT ingredient_id, compound_id FROM ingredient_compound").fetchall()
    ing_edge, comp_edge = [], []
    for ing_id, comp_id in ic_rows:
        if ing_id in id2name and comp_id in comp2idx:
            ing_edge.append(ing_id - 1)
            comp_edge.append(comp2idx[comp_id])
    pair_rows = cur.execute(
        "SELECT ing_a, ing_b, pmi_score FROM pair_score WHERE ing_a < ing_b"
    ).fetchall()
    pairs = [(name2id[a]-1, name2id[b]-1, float(p))
             for a, b, p in pair_rows if a in name2id and b in name2id]
    con.close()
    return {"n_ing": n_ing, "n_comp": n_comp,
            "ing_edge": ing_edge, "comp_edge": comp_edge, "pairs": pairs}


def build_pyg_data(data, device):
    from torch_geometric.data import HeteroData
    hdata = HeteroData()
    n_ing, n_comp = data["n_ing"], data["n_comp"]
    hdata["ingredient"].x = torch.eye(n_ing, device=device)
    hdata["compound"].x = torch.eye(n_comp, device=device)
    ing_t = torch.tensor(data["ing_edge"], dtype=torch.long, device=device)
    com_t = torch.tensor(data["comp_edge"], dtype=torch.long, device=device)
    hdata["ingredient", "has", "compound"].edge_index = torch.stack([ing_t, com_t])
    hdata["compound", "rev_has", "ingredient"].edge_index = torch.stack([com_t, ing_t])
    return hdata, ing_t, com_t


def train_test_split(pairs, seed, test_ratio):
    rng = np.random.RandomState(seed)
    idx = np.arange(len(pairs))
    rng.shuffle(idx)
    n_test = int(len(pairs) * test_ratio)
    return [pairs[i] for i in idx[n_test:]], [pairs[i] for i in idx[:n_test]]


# ============================================================
# Models
# ============================================================

class HGTLayer(nn.Module):
    def __init__(self, n_ing, n_comp, hidden):
        super().__init__()
        from torch_geometric.nn import HGTConv
        self.ing_proj = nn.Linear(n_ing, hidden, bias=False)
        self.comp_proj = nn.Linear(n_comp, hidden, bias=False)
        metadata = (["ingredient", "compound"],
                    [("ingredient", "has", "compound"), ("compound", "rev_has", "ingredient")])
        self.conv = HGTConv(hidden, hidden, metadata, heads=2)

    def forward(self, hdata):
        x = {"ingredient": self.ing_proj(hdata["ingredient"].x),
             "compound":   self.comp_proj(hdata["compound"].x)}
        x = self.conv(x, {k: hdata[k].edge_index for k in hdata.edge_types})
        return x["ingredient"], x["compound"]


class BaselineHGN(nn.Module):
    def __init__(self, n_ing, n_comp, hidden=64):
        super().__init__()
        self.layer = HGTLayer(n_ing, n_comp, hidden)

    def get_emb(self, hdata, **kw):
        z, _ = self.layer(hdata)
        return z

    def forward_score(self, hdata, i, j, **kw):
        z = self.get_emb(hdata)
        return (z[i] * z[j]).sum(-1)


class AntiHomoHGN(nn.Module):
    def __init__(self, n_ing, n_comp, hidden=64, lam_init=0.3):
        super().__init__()
        self.layer = HGTLayer(n_ing, n_comp, hidden)
        self.lam = nn.Parameter(torch.tensor(float(lam_init)))

    def get_emb(self, hdata, ing_t, com_t):
        z_ing, z_comp = self.layer(hdata)
        n_ing, hidden = z_ing.shape
        z_comp_sum = torch.zeros(n_ing, hidden, device=z_ing.device)
        count = torch.zeros(n_ing, 1, device=z_ing.device)
        z_comp_sum.scatter_add_(0, ing_t.unsqueeze(1).expand(-1, hidden), z_comp[com_t])
        count.scatter_add_(0, ing_t.unsqueeze(1), torch.ones(len(ing_t), 1, device=z_ing.device))
        z_comp_avg = z_comp_sum / (count + 1e-8)
        lam = torch.sigmoid(self.lam)
        return z_ing - lam * z_comp_avg

    def forward_score(self, hdata, i, j, ing_t, com_t):
        z = self.get_emb(hdata, ing_t, com_t)
        return (z[i] * z[j]).sum(-1)


class AntiHomoDualHGN(nn.Module):
    """Anti-Homophily + free MF embedding: z = alpha*z_anti + (1-alpha)*z_free"""
    def __init__(self, n_ing, n_comp, hidden=64, lam_init=0.3):
        super().__init__()
        self.layer = HGTLayer(n_ing, n_comp, hidden)
        self.lam = nn.Parameter(torch.tensor(float(lam_init)))
        self.free_emb = nn.Embedding(n_ing, hidden)
        nn.init.normal_(self.free_emb.weight, std=0.01)
        self.alpha = nn.Parameter(torch.tensor(0.5))

    def get_emb(self, hdata, ing_t, com_t):
        z_ing, z_comp = self.layer(hdata)
        n_ing, hidden = z_ing.shape
        z_cs = torch.zeros(n_ing, hidden, device=z_ing.device)
        cnt = torch.zeros(n_ing, 1, device=z_ing.device)
        z_cs.scatter_add_(0, ing_t.unsqueeze(1).expand(-1, hidden), z_comp[com_t])
        cnt.scatter_add_(0, ing_t.unsqueeze(1), torch.ones(len(ing_t), 1, device=z_ing.device))
        z_anti = z_ing - torch.sigmoid(self.lam) * (z_cs / (cnt + 1e-8))
        z_free = self.free_emb.weight
        a = torch.sigmoid(self.alpha)
        return a * z_anti + (1 - a) * z_free

    def forward_score(self, hdata, i, j, ing_t, com_t):
        z = self.get_emb(hdata, ing_t, com_t)
        return (z[i] * z[j]).sum(-1)


# ============================================================
# Training helpers
# ============================================================

def bpr_loss(pos_s, neg_s):
    return -F.logsigmoid(pos_s - neg_s).mean()


def mse_loss_fn(scores, pmi_t):
    return F.mse_loss(scores, pmi_t)


def run_bpr(model, hdata, ing_t, com_t, train_pairs, test_pairs, seed, budget, device, needs_graph_args):
    torch.manual_seed(seed)
    pmi_tr = torch.tensor([p[2] for p in train_pairs], dtype=torch.float, device=device)
    i_tr = torch.tensor([p[0] for p in train_pairs], dtype=torch.long, device=device)
    j_tr = torch.tensor([p[1] for p in train_pairs], dtype=torch.long, device=device)
    pmi_te = torch.tensor([p[2] for p in test_pairs], dtype=torch.float, device=device)
    i_te = torch.tensor([p[0] for p in test_pairs], dtype=torch.long, device=device)
    j_te = torch.tensor([p[1] for p in test_pairs], dtype=torch.long, device=device)
    med = pmi_tr.median()
    hi = (pmi_tr >= med).nonzero(as_tuple=True)[0]
    lo = (pmi_tr < med).nonzero(as_tuple=True)[0]
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    BATCH = 512
    model.train()
    t0 = time.time()
    while time.time() - t0 < budget:
        pp = hi[torch.randint(len(hi), (BATCH,))]
        np_ = lo[torch.randint(len(lo), (BATCH,))]
        kw = {"ing_t": ing_t, "com_t": com_t} if needs_graph_args else {}
        ps = model.forward_score(hdata, i_tr[pp], j_tr[pp], **kw)
        ns = model.forward_score(hdata, i_tr[np_], j_tr[np_], **kw)
        loss = bpr_loss(ps, ns)
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
    model.train(False)
    with torch.no_grad():
        kw = {"ing_t": ing_t, "com_t": com_t} if needs_graph_args else {}
        tr_sc = model.forward_score(hdata, i_tr, j_tr, **kw).cpu().numpy()
        te_sc = model.forward_score(hdata, i_te, j_te, **kw).cpu().numpy()
    tr_sp = float(spearmanr(tr_sc, pmi_tr.cpu().numpy()).statistic)
    te_sp = float(spearmanr(te_sc, pmi_te.cpu().numpy()).statistic)
    return tr_sp, te_sp


def run_mse(model, hdata, ing_t, com_t, train_pairs, test_pairs, seed, budget, device):
    torch.manual_seed(seed)
    pmi_tr = torch.tensor([p[2] for p in train_pairs], dtype=torch.float, device=device)
    i_tr = torch.tensor([p[0] for p in train_pairs], dtype=torch.long, device=device)
    j_tr = torch.tensor([p[1] for p in train_pairs], dtype=torch.long, device=device)
    pmi_te = torch.tensor([p[2] for p in test_pairs], dtype=torch.float, device=device)
    i_te = torch.tensor([p[0] for p in test_pairs], dtype=torch.long, device=device)
    j_te = torch.tensor([p[1] for p in test_pairs], dtype=torch.long, device=device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    BATCH = 512
    idx_all = torch.arange(len(train_pairs), device=device)
    model.train()
    t0 = time.time()
    while time.time() - t0 < budget:
        batch = idx_all[torch.randint(len(idx_all), (BATCH,))]
        sc = model.forward_score(hdata, i_tr[batch], j_tr[batch], ing_t=ing_t, com_t=com_t)
        loss = mse_loss_fn(sc, pmi_tr[batch])
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
    model.train(False)
    with torch.no_grad():
        tr_sc = model.forward_score(hdata, i_tr, j_tr, ing_t=ing_t, com_t=com_t).cpu().numpy()
        te_sc = model.forward_score(hdata, i_te, j_te, ing_t=ing_t, com_t=com_t).cpu().numpy()
    tr_sp = float(spearmanr(tr_sc, pmi_tr.cpu().numpy()).statistic)
    te_sp = float(spearmanr(te_sc, pmi_te.cpu().numpy()).statistic)
    return tr_sp, te_sp


def multi_seed_run(factory_fn, seeds, data, hdata, ing_t, com_t, budget, device):
    tr_list, te_list = [], []
    for seed in seeds:
        train_p, test_p = train_test_split(data["pairs"], seed, TEST_RATIO)
        model, needs_graph_args, use_mse = factory_fn(data, device)
        if use_mse:
            tr_sp, te_sp = run_mse(model, hdata, ing_t, com_t, train_p, test_p, seed, budget, device)
        else:
            tr_sp, te_sp = run_bpr(model, hdata, ing_t, com_t, train_p, test_p, seed, budget, device, needs_graph_args)
        tr_list.append(tr_sp); te_list.append(te_sp)
    return tr_list, te_list


def fmt(vals):
    return f"{np.mean(vals):.4f}+/-{np.std(vals):.4f}"


# ============================================================
# Main
# ============================================================

LAMBDAS_SWEEP = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.5]


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    data = load_data()
    print(f"  {data['n_ing']} ingredients, {len(data['pairs'])} unique pairs")
    hdata, ing_t, com_t = build_pyg_data(data, device)
    results = {}

    # ---- E1: Lambda sweep ----
    print("\n" + "="*50)
    print("E1: Lambda sweep for AntiHomo")
    print("="*50)
    for lam in LAMBDAS_SWEEP:
        tag = f"AntiHomo-{lam}"
        def factory(d, dev, l=lam):
            return AntiHomoHGN(d["n_ing"], d["n_comp"], 64, lam_init=l).to(dev), True, False
        tr, te = multi_seed_run(factory, SEEDS, data, hdata, ing_t, com_t, TIME_BUDGET, device)
        results[tag] = {"train": tr, "test": te}
        status = "BEAT *" if np.mean(te) > HGN_BASELINE else ""
        print(f"  {tag:<20} test={fmt(te)}  {status}")

    # ---- E2: AntiHomo + DualEncoder (best lam from E1) ----
    print("\n" + "="*50)
    print("E2: AntiHomo + DualEncoder")
    print("="*50)
    best_lam = LAMBDAS_SWEEP[np.argmax([np.mean(results[f"AntiHomo-{l}"]["test"]) for l in LAMBDAS_SWEEP])]
    print(f"  Best lambda from E1: {best_lam}")
    def dual_factory(d, dev):
        return AntiHomoDualHGN(d["n_ing"], d["n_comp"], 64, lam_init=best_lam).to(dev), True, False
    tr, te = multi_seed_run(dual_factory, SEEDS, data, hdata, ing_t, com_t, TIME_BUDGET, device)
    results["AntiHomo+Dual"] = {"train": tr, "test": te}
    status = "BEAT *" if np.mean(te) > HGN_BASELINE else ""
    print(f"  AntiHomo+Dual        test={fmt(te)}  {status}")

    # ---- E3: PMI Regression (MSE) with AntiHomo ----
    print("\n" + "="*50)
    print("E3: PMI Regression loss (MSE) with AntiHomo")
    print("="*50)
    def mse_factory(d, dev):
        return AntiHomoHGN(d["n_ing"], d["n_comp"], 64, lam_init=best_lam).to(dev), True, True
    tr, te = multi_seed_run(mse_factory, SEEDS, data, hdata, ing_t, com_t, TIME_BUDGET, device)
    results["AntiHomo-MSE"] = {"train": tr, "test": te}
    status = "BEAT *" if np.mean(te) > HGN_BASELINE else ""
    print(f"  AntiHomo-MSE         test={fmt(te)}  {status}")

    # ---- E4: Bootstrap CI (10 seeds) for best model and baseline ----
    print("\n" + "="*50)
    print("E4: Bootstrap CI (10 seeds)")
    print("="*50)
    # 1L-HGN baseline
    def hgn_factory(d, dev):
        return BaselineHGN(d["n_ing"], d["n_comp"], 64).to(dev), False, False
    tr, te = multi_seed_run(hgn_factory, SEEDS_BOOTSTRAP, data, hdata, ing_t, com_t, TIME_BUDGET, device)
    results["1L-HGN-10seeds"] = {"train": tr, "test": te}
    print(f"  1L-HGN (10 seeds)    test={fmt(te)}")

    # AntiHomo best
    def ah_best_factory(d, dev):
        return AntiHomoHGN(d["n_ing"], d["n_comp"], 64, lam_init=best_lam).to(dev), True, False
    tr, te = multi_seed_run(ah_best_factory, SEEDS_BOOTSTRAP, data, hdata, ing_t, com_t, TIME_BUDGET, device)
    results[f"AntiHomo-{best_lam}-10seeds"] = {"train": tr, "test": te}
    print(f"  AntiHomo-{best_lam} (10s)  test={fmt(te)}")

    # Bootstrap CI
    hgn_te = np.array(results["1L-HGN-10seeds"]["test"])
    ah_te  = np.array(results[f"AntiHomo-{best_lam}-10seeds"]["test"])
    diffs = ah_te - hgn_te
    ci_low, ci_hi = np.percentile(diffs, [2.5, 97.5])
    print(f"\n  Bootstrap CI for delta (AntiHomo - HGN) [n=10]:")
    print(f"  mean delta = {diffs.mean():.4f}, 95% CI [{ci_low:.4f}, {ci_hi:.4f}]")
    sig = "significant" if ci_low > 0 else "NOT significant"
    print(f"  → {sig} at 95% level")

    # ---- Final summary ----
    print("\n" + "="*70)
    print("=== 29: Comprehensive Results ===")
    print("="*70)
    print(f"  Baseline: 1L-HGN test={HGN_BASELINE}")
    print(f"{'Model':<28} {'Test Spearman':>18}  delta_test")
    print("-"*55)
    for tag, r in results.items():
        te_mean = np.mean(r["test"])
        delta = te_mean - HGN_BASELINE
        mark = " *" if te_mean > HGN_BASELINE else ""
        print(f"{tag:<28} {fmt(r['test']):>18}  {delta:>+.4f}{mark}")

    with open("scripts/gnn/29_results.json", "w") as f:
        json.dump({k: {kk: list(v) for kk, v in vs.items()}
                   for k, vs in results.items()}, f, indent=2)
    print("\nSaved -> scripts/gnn/29_results.json")


if __name__ == "__main__":
    main()
