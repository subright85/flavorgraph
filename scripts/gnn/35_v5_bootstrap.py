"""
35_v5_bootstrap.py -- Bootstrap CI for AntiHomo on flavorgraph_v5.db
Architecture mirrors 34_v4_bootstrap.py exactly.
Identity features + linear projections + HGTConv.
Training: BPR within positive pairs (hi-PPMI vs lo-PPMI).
"""
import json, sqlite3, time, math
from pathlib import Path
import numpy as np
import torch, torch.nn as nn, torch.nn.functional as F
from scipy.stats import spearmanr
from torch_geometric.data import HeteroData
from torch_geometric.nn import HGTConv

ROOT = Path(__file__).parent.parent.parent
DB   = ROOT / "flavorgraph_v5.db"
OUT  = Path(__file__).parent / "35_results.json"
LOG  = Path(__file__).parent / "35_bootstrap_log.txt"

SEEDS       = [42, 123, 2024, 7, 99, 314, 777, 1001, 2000, 9999]
TIME_BUDGET = 240    # seconds per model per seed
TEST_RATIO  = 0.2
LAM_INIT    = 0.2
HIDDEN      = 64

with open(LOG, "w") as _f:
    pass

def log(msg):
    print(msg, flush=True)
    with open(LOG, "a") as f:
        f.write(msg + "\n")

# -- Load data -----------------------------------------------------------------
con = sqlite3.connect(DB)
cur = con.cursor()
cur.execute("SELECT id, name FROM ingredient ORDER BY id")
rows_ing = cur.fetchall()
cur.execute("SELECT id FROM compound ORDER BY id")
rows_comp = cur.fetchall()
cur.execute("SELECT ingredient_id, compound_id FROM ingredient_compound")
ic_links = cur.fetchall()
cur.execute("SELECT ing_a, ing_b, pmi_score FROM pair_score WHERE ing_a < ing_b")
pairs_raw = cur.fetchall()
con.close()

id2name = {r[0]: r[1] for r in rows_ing}
name2id = {r[1]: r[0] for r in rows_ing}
n_ing   = len(id2name)
comp2idx = {r[0]: i for i,r in enumerate(rows_comp)}
n_comp  = len(comp2idx)

ing_edge = [r[0] - 1 for r in ic_links if r[0] in id2name and r[1] in comp2idx]
comp_edge = [comp2idx[r[1]] for r in ic_links if r[0] in id2name and r[1] in comp2idx]

pairs = [(name2id[a] - 1, name2id[b] - 1, float(p))
         for a,b,p in pairs_raw if a in name2id and b in name2id]

log(f"n_ing={n_ing}, n_comp={n_comp}, pairs={len(pairs)}, ic={len(ing_edge)}")

# -- PyG HeteroData -----------------------------------------------------------
hdata = HeteroData()
hdata["ingredient"].x = torch.eye(n_ing)
hdata["compound"].x   = torch.eye(n_comp)
ing_t = torch.tensor(ing_edge, dtype=torch.long)
com_t = torch.tensor(comp_edge, dtype=torch.long)
hdata["ingredient","has","compound"].edge_index      = torch.stack([ing_t, com_t])
hdata["compound","rev_has","ingredient"].edge_index  = torch.stack([com_t, ing_t])
meta = (["ingredient","compound"],
        [("ingredient","has","compound"),("compound","rev_has","ingredient")])

# -- Models -------------------------------------------------------------------
class HGTLayer(nn.Module):
    def __init__(self):
        super().__init__()
        self.ip   = nn.Linear(n_ing,  HIDDEN, bias=False)
        self.cp   = nn.Linear(n_comp, HIDDEN, bias=False)
        self.conv = HGTConv(HIDDEN, HIDDEN, meta, heads=2)
    def forward(self):
        x = {"ingredient": self.ip(hdata["ingredient"].x),
             "compound":   self.cp(hdata["compound"].x)}
        out = self.conv(x, {k: hdata[k].edge_index for k in hdata.edge_types})
        return out["ingredient"], out["compound"]

class BaselineHGN(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer = HGTLayer()
    def forward_score(self, i, j):
        zi, _ = self.layer()
        return (zi[i] * zi[j]).sum(-1)

class AntiHomoHGN(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer = HGTLayer()
        self.lam   = nn.Parameter(torch.tensor(float(LAM_INIT)))
    def forward_score(self, i, j):
        zi, zc = self.layer()
        zcs = torch.zeros(n_ing, HIDDEN)
        cnt = torch.zeros(n_ing, 1)
        zcs.scatter_add_(0, ing_t.unsqueeze(1).expand(-1,HIDDEN), zc[com_t])
        cnt.scatter_add_(0, ing_t.unsqueeze(1), torch.ones(len(ing_t),1))
        z = zi - torch.sigmoid(self.lam) * (zcs / (cnt + 1e-8))
        return (z[i] * z[j]).sum(-1)

def train_and_eval(ModelClass, seed, train_pairs, test_pairs):
    torch.manual_seed(seed)
    model = ModelClass()
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    
    pmi_tr = torch.tensor([p[2] for p in train_pairs], dtype=torch.float)
    i_tr = torch.tensor([p[0] for p in train_pairs], dtype=torch.long)
    j_tr = torch.tensor([p[1] for p in train_pairs], dtype=torch.long)
    
    med = pmi_tr.median()
    hi  = (pmi_tr >= med).nonzero(as_tuple=True)[0]
    lo  = (pmi_tr <  med).nonzero(as_tuple=True)[0]
    
    i_te = torch.tensor([p[0] for p in test_pairs], dtype=torch.long)
    j_te = torch.tensor([p[1] for p in test_pairs], dtype=torch.long)
    pmi_te_np = [p[2] for p in test_pairs]
    pmi_tr_np = [p[2] for p in train_pairs]
    
    t0 = time.time()
    while time.time() - t0 < TIME_BUDGET:
        pp  = hi[torch.randint(len(hi), (512,))]
        nn_ = lo[torch.randint(len(lo), (512,))]
        ps  = model.forward_score(i_tr[pp], j_tr[pp])
        ns  = model.forward_score(i_tr[nn_], j_tr[nn_])
        loss = -F.logsigmoid(ps - ns).mean()
        opt.zero_grad(); loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
    
    model.eval()
    with torch.no_grad():
        te_sc = model.forward_score(i_te, j_te).numpy()
        tr_sc = model.forward_score(i_tr, j_tr).numpy()
    return float(spearmanr(tr_sc, pmi_tr_np).statistic), float(spearmanr(te_sc, pmi_te_np).statistic)

def do_split(pairs, seed):
    rng = np.random.RandomState(seed)
    idx = np.arange(len(pairs))
    rng.shuffle(idx)
    n_te = int(len(pairs) * TEST_RATIO)
    return [pairs[i] for i in idx[n_te:]], [pairs[i] for i in idx[:n_te]]

# -- Bootstrap ----------------------------------------------------------------
log(f"\n=== v5 Bootstrap ({len(SEEDS)} seeds) ===")
log(f"HIDDEN={HIDDEN}, TIME_BUDGET={TIME_BUDGET}s, LAM_INIT={LAM_INIT}")

hgn_scores, anti_scores = [], []
for seed in SEEDS:
    t0 = time.time()
    tr, te = do_split(pairs, seed)
    
    tr1, te1 = train_and_eval(BaselineHGN, seed, tr, te)
    hgn_scores.append(te1)
    
    tr2, te2 = train_and_eval(AntiHomoHGN, seed, tr, te)
    anti_scores.append(te2)
    
    elapsed = time.time() - t0
    log(f"  seed={seed:<5}  HGN={te1:.4f}  Anti={te2:.4f}  delta={te2-te1:+.4f}  ({elapsed:.0f}s)")

hgn_arr  = np.array(hgn_scores)
anti_arr = np.array(anti_scores)
deltas   = anti_arr - hgn_arr
from scipy import stats as sc_stats
se     = deltas.std(ddof=1) / math.sqrt(len(SEEDS))
t_crit = sc_stats.t.ppf(0.975, df=len(SEEDS)-1)
ci     = [deltas.mean() - t_crit*se, deltas.mean() + t_crit*se]
sig    = ci[0] > 0

log(f"""
=== v5 Bootstrap Results ===
  HGN:       {hgn_arr.mean():.4f} ± {hgn_arr.std():.4f}
  AntiHomo:  {anti_arr.mean():.4f} ± {anti_arr.std():.4f}
  Delta:     {deltas.mean():+.4f}
  95% CI:    [{ci[0]:+.4f}, {ci[1]:+.4f}]
  Significant (CI lower > 0): {sig}
""")

result = {
    "n_ing": n_ing, "n_comp": n_comp, "n_pairs": len(pairs),
    "hgn_mean": float(hgn_arr.mean()), "hgn_std": float(hgn_arr.std()),
    "anti_mean": float(anti_arr.mean()), "anti_std": float(anti_arr.std()),
    "delta_mean": float(deltas.mean()),
    "ci_95": [float(ci[0]), float(ci[1])],
    "significant": bool(sig),
    "seeds": SEEDS,
    "hgn_scores": [float(x) for x in hgn_scores],
    "anti_scores": [float(x) for x in anti_scores],
}
with open(OUT, "w") as f:
    json.dump(result, f, indent=2)
log(f"Saved -> {OUT}")
