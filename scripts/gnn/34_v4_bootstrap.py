"""
34_v4_bootstrap.py -- Bootstrap CI: flavorgraph_v4 (578 ing, 21390 pairs)

Compares 1L-HGN vs AntiHomo-0.2 across 10 seeds.
Baselines: v3 (239/9305), v2 (151/11269)
"""
import json, sqlite3, time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy.stats import spearmanr

DB_PATH = "flavorgraph_v4.db"
TIME_BUDGET = 240
SEEDS = [42, 123, 2024, 7, 99, 314, 777, 1001, 2000, 9999]
TEST_RATIO = 0.2
LAM_INIT = 0.2
device = torch.device("cpu")


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
    pairs = [
        (name2id[a] - 1, name2id[b] - 1, float(p))
        for a, b, p in pair_rows if a in name2id and b in name2id
    ]
    con.close()
    print(f"  {n_ing} ingredients, {n_comp} compounds, {len(pairs)} pairs")
    return {"n_ing": n_ing, "n_comp": n_comp,
            "ing_edge": ing_edge, "comp_edge": comp_edge, "pairs": pairs}


def build_pyg(data):
    from torch_geometric.data import HeteroData
    hdata = HeteroData()
    hdata["ingredient"].x = torch.eye(data["n_ing"], device=device)
    hdata["compound"].x   = torch.eye(data["n_comp"], device=device)
    ing_t = torch.tensor(data["ing_edge"], dtype=torch.long, device=device)
    com_t = torch.tensor(data["comp_edge"], dtype=torch.long, device=device)
    hdata["ingredient", "has", "compound"].edge_index      = torch.stack([ing_t, com_t])
    hdata["compound",  "rev_has", "ingredient"].edge_index = torch.stack([com_t, ing_t])
    return hdata, ing_t, com_t


def do_split(pairs, seed):
    rng = np.random.RandomState(seed)
    idx = np.arange(len(pairs))
    rng.shuffle(idx)
    n_te = int(len(pairs) * TEST_RATIO)
    return [pairs[i] for i in idx[n_te:]], [pairs[i] for i in idx[:n_te]]


class HGTLayer(nn.Module):
    def __init__(self, n_ing, n_comp, hidden):
        super().__init__()
        from torch_geometric.nn import HGTConv
        self.ip = nn.Linear(n_ing, hidden, bias=False)
        self.cp = nn.Linear(n_comp, hidden, bias=False)
        meta = (["ingredient", "compound"],
                [("ingredient", "has", "compound"),
                 ("compound", "rev_has", "ingredient")])
        self.conv = HGTConv(hidden, hidden, meta, heads=2)

    def forward(self, hdata):
        x = {"ingredient": self.ip(hdata["ingredient"].x),
             "compound":   self.cp(hdata["compound"].x)}
        x = self.conv(x, {k: hdata[k].edge_index for k in hdata.edge_types})
        return x["ingredient"], x["compound"]


class BaselineHGN(nn.Module):
    def __init__(self, n_ing, n_comp, hidden=64):
        super().__init__()
        self.layer = HGTLayer(n_ing, n_comp, hidden)

    def forward_score(self, hdata, i, j, **kw):
        z, _ = self.layer(hdata)
        return (z[i] * z[j]).sum(-1)


class AntiHomoHGN(nn.Module):
    def __init__(self, n_ing, n_comp, hidden=64, lam=0.2):
        super().__init__()
        self.layer = HGTLayer(n_ing, n_comp, hidden)
        self.lam   = nn.Parameter(torch.tensor(float(lam)))

    def forward_score(self, hdata, i, j, ing_t, com_t):
        zi, zc = self.layer(hdata)
        n, h   = zi.shape
        zcs = torch.zeros(n, h, device=zi.device)
        cnt = torch.zeros(n, 1, device=zi.device)
        zcs.scatter_add_(0, ing_t.unsqueeze(1).expand(-1, h), zc[com_t])
        cnt.scatter_add_(0, ing_t.unsqueeze(1),
                         torch.ones(len(ing_t), 1, device=zi.device))
        z = zi - torch.sigmoid(self.lam) * (zcs / (cnt + 1e-8))
        return (z[i] * z[j]).sum(-1)


def run_training(model, hdata, ing_t, com_t,
                 train_pairs, test_pairs, seed, budget, needs_graph):
    torch.manual_seed(seed)
    pmi_tr = torch.tensor([p[2] for p in train_pairs], dtype=torch.float, device=device)
    i_tr   = torch.tensor([p[0] for p in train_pairs], dtype=torch.long, device=device)
    j_tr   = torch.tensor([p[1] for p in train_pairs], dtype=torch.long, device=device)
    i_te   = torch.tensor([p[0] for p in test_pairs],  dtype=torch.long, device=device)
    j_te   = torch.tensor([p[1] for p in test_pairs],  dtype=torch.long, device=device)
    pmi_te_np = [p[2] for p in test_pairs]
    pmi_tr_np = [p[2] for p in train_pairs]
    med = pmi_tr.median()
    hi  = (pmi_tr >= med).nonzero(as_tuple=True)[0]
    lo  = (pmi_tr <  med).nonzero(as_tuple=True)[0]
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    model.train()
    t0 = time.time()
    while time.time() - t0 < budget:
        pp  = hi[torch.randint(len(hi),  (512,))]
        nnn = lo[torch.randint(len(lo),  (512,))]
        kw  = {"ing_t": ing_t, "com_t": com_t} if needs_graph else {}
        ps  = model.forward_score(hdata, i_tr[pp],  j_tr[pp],  **kw)
        ns  = model.forward_score(hdata, i_tr[nnn], j_tr[nnn], **kw)
        loss = -F.logsigmoid(ps - ns).mean()
        opt.zero_grad(); loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
    model.train(False)
    with torch.no_grad():
        kw    = {"ing_t": ing_t, "com_t": com_t} if needs_graph else {}
        te_sc = model.forward_score(hdata, i_te, j_te, **kw).cpu().numpy()
        tr_sc = model.forward_score(hdata, i_tr, j_tr, **kw).cpu().numpy()
    return float(spearmanr(tr_sc, pmi_tr_np).statistic), float(spearmanr(te_sc, pmi_te_np).statistic)


def main():
    print("=" * 60)
    print("34: v4 Bootstrap CI (10 seeds)")
    print(f"  DB: {DB_PATH}")
    print("=" * 60)
    data = load_data()
    hdata, ing_t, com_t = build_pyg(data)
    hgn_scores, anti_scores = [], []
    for seed in SEEDS:
        tr_pairs, te_pairs = do_split(data["pairs"], seed)
        m1 = BaselineHGN(data["n_ing"], data["n_comp"]).to(device)
        _, te1 = run_training(m1, hdata, ing_t, com_t,
                              tr_pairs, te_pairs, seed, TIME_BUDGET, False)
        hgn_scores.append(te1)
        m2 = AntiHomoHGN(data["n_ing"], data["n_comp"], lam=LAM_INIT).to(device)
        _, te2 = run_training(m2, hdata, ing_t, com_t,
                              tr_pairs, te_pairs, seed, TIME_BUDGET, True)
        anti_scores.append(te2)
        print(f"  seed={seed:<5}  HGN={te1:.4f}  Anti={te2:.4f}  delta={te2-te1:+.4f}")
    hgn_arr  = np.array(hgn_scores)
    anti_arr = np.array(anti_scores)
    delta    = anti_arr - hgn_arr
    print()
    print(f"  1L-HGN (v4):       {hgn_arr.mean():.4f} +/- {hgn_arr.std():.4f}")
    print(f"  AntiHomo-0.2 (v4): {anti_arr.mean():.4f} +/- {anti_arr.std():.4f}")
    print(f"  delta mean: {delta.mean():+.4f}")
    ci_lo = np.percentile(delta, 2.5)
    ci_hi = np.percentile(delta, 97.5)
    print(f"  95% CI: [{ci_lo:.4f}, {ci_hi:.4f}]")
    sig = "SIGNIFICANT" if (ci_lo > 0 or ci_hi < 0) else "NOT significant"
    print(f"  -> {sig}")
    with open("scripts/gnn/34_results.json", "w") as f:
        json.dump({
            "db": DB_PATH, "n_ing": data["n_ing"], "n_pairs": len(data["pairs"]),
            "seeds": SEEDS, "hgn_scores": hgn_scores, "anti_scores": anti_scores,
            "hgn_mean": float(hgn_arr.mean()), "hgn_std": float(hgn_arr.std()),
            "anti_mean": float(anti_arr.mean()), "anti_std": float(anti_arr.std()),
            "delta_mean": float(delta.mean()),
            "ci_95": [float(ci_lo), float(ci_hi)],
            "significant": bool(ci_lo > 0 or ci_hi < 0),
        }, f, indent=2)
    print(f"\n  Saved -> scripts/gnn/34_results.json")

if __name__ == "__main__":
    main()
