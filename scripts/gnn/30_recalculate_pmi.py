"""
30_recalculate_pmi.py — Expanded PMI from ~272 mapped ingredients

Strategy:
  151 ingredients: ingredient_ahn_map.json  (common name → ingr_info ID)
  121 more:        direct name match RAW_recipes ∩ ingr_info.tsv names
  Combined: ~272 ingredients with both PMI and compound data

  PMI source: data/RAW_recipes.csv  (231,637 recipes, common ingredient names)
  Compound:   data/ingr_comp.tsv via combined name→ID mapping

Output: flavorgraph_v3.db
"""

import csv
import json
import math
import re
import sqlite3
from collections import defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
DATA = ROOT / "data"
DB_OUT = ROOT / "flavorgraph_v3.db"

MIN_CO_COUNT = 10  # pair must co-occur in ≥ 10 recipes

# ── 1. Load ingredient info (botanical IDs) ──────────────────────────────────
print("Loading ingredient info...")
id2name  = {}
id2cat   = {}
name2id  = {}
with open(DATA / "ingr_info.tsv") as f:
    next(f)
    for line in f:
        parts = line.strip().split("\t")
        iid   = int(parts[0])
        name  = parts[1]
        cat   = parts[2] if len(parts) > 2 else ""
        id2name[iid]  = name
        id2cat[iid]   = cat
        name2id[name] = iid

print(f"  {len(id2name)} botanical ingredients loaded")

# ── 2. Load compound info ─────────────────────────────────────────────────────
print("Loading compound info...")
comp_id2name = {}
comp_id2cas  = {}
with open(DATA / "comp_info.tsv") as f:
    next(f)
    for line in f:
        parts = line.strip().split("\t")
        cid   = int(parts[0])
        cname = parts[1]
        cas   = parts[2] if len(parts) > 2 else ""
        comp_id2name[cid] = cname
        comp_id2cas[cid]  = cas

print(f"  {len(comp_id2name)} compounds loaded")

# ── 3. Load ingredient-compound links ─────────────────────────────────────────
print("Loading ingredient-compound links...")
ingr_compounds_by_id = defaultdict(set)  # botanical_id → set of comp_ids
with open(DATA / "ingr_comp.tsv") as f:
    next(f)
    for line in f:
        parts = line.strip().split("\t")
        iid = int(parts[0])
        cid = int(parts[1])
        ingr_compounds_by_id[iid].add(cid)

print(f"  {len(ingr_compounds_by_id)} botanical ingredients have compound data")

# ── 4. Build common-name → botanical-ID mapping ──────────────────────────────
print("Building common-name → botanical-ID mapping...")

# Source A: ingredient_ahn_map.json (151 hand-curated mappings)
with open(DATA / "ingredient_ahn_map.json") as f:
    ahn_map = json.load(f)  # {common_name: {ahn_id: str, compound_count: int}}

common2id = {}
for common_name, info in ahn_map.items():
    ahn_id = info.get("ahn_id")
    if ahn_id is None:
        continue
    bid = int(ahn_id)
    if bid in ingr_compounds_by_id:
        common2id[common_name] = bid

print(f"  From ahn_map: {len(common2id)} ingredients")

# Source B: direct name match (common names that appear verbatim in ingr_info)
direct_matches = 0
with open(DATA / "RAW_recipes.csv") as f:
    reader = csv.DictReader(f)
    counts = defaultdict(int)
    for row in reader:
        raw = row.get("ingredients", "")
        for ing in re.findall(r"'([^']+)'", raw):
            counts[ing] += 1

for name, cnt in counts.items():
    if name not in common2id and name in name2id:
        bid = name2id[name]
        if bid in ingr_compounds_by_id:
            common2id[name] = bid
            direct_matches += 1

print(f"  Direct name matches added: {direct_matches}")
print(f"  Total ingredients with compound mapping: {len(common2id)}")

target = set(common2id.keys())

# ── 5. Count co-occurrences from RAW_recipes ─────────────────────────────────
print("Counting co-occurrences from RAW_recipes.csv...")
ing_count  = defaultdict(int)
pair_count = defaultdict(int)
N = 0

with open(DATA / "RAW_recipes.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        N += 1
        if N % 50_000 == 0:
            print(f"  {N:,} recipes...")
        raw = row.get("ingredients", "")
        ings = list(set(i for i in re.findall(r"'([^']+)'", raw) if i in target))
        for i in ings:
            ing_count[i] += 1
        for a, b in combinations(sorted(ings), 2):
            pair_count[(a, b)] += 1

print(f"  Done. N={N:,} recipes")
print(f"  Ingredients seen in recipes: {len(ing_count)}")
print(f"  Pairs with ≥1 co-occurrence: {len(pair_count):,}")

# ── 6. Compute PMI / NPMI ────────────────────────────────────────────────────
print("Computing PMI / NPMI...")
pair_scores = {}

for (a, b), co in pair_count.items():
    if co < MIN_CO_COUNT:
        continue
    p_ab = co / N
    p_a  = ing_count[a] / N
    p_b  = ing_count[b] / N
    pmi  = math.log(p_ab / (p_a * p_b))
    npmi = pmi / (-math.log(p_ab))
    pair_scores[(a, b)] = {"pmi": pmi, "npmi": npmi, "co": co}

print(f"  Pairs with PMI computed: {len(pair_scores):,}")

# Only keep ingredients that appear in at least one pair
active_names = set()
for a, b in pair_scores:
    active_names.add(a)
    active_names.add(b)

print(f"  Active ingredients (in ≥1 pair): {len(active_names)}")

# ── 7. Shared-compound helper ─────────────────────────────────────────────────
def get_shared(a_name, b_name):
    a_id   = common2id.get(a_name)
    b_id   = common2id.get(b_name)
    if a_id is None or b_id is None:
        return [], 0
    ca     = ingr_compounds_by_id.get(a_id, set())
    cb     = ingr_compounds_by_id.get(b_id, set())
    shared = list(ca & cb)
    return shared, len(shared)

# ── 8. Create flavorgraph_v3.db ──────────────────────────────────────────────
print(f"\nBuilding {DB_OUT}...")
if DB_OUT.exists():
    DB_OUT.unlink()

con = sqlite3.connect(DB_OUT)
cur = con.cursor()

cur.executescript("""
CREATE TABLE ingredient (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT    NOT NULL UNIQUE,
    bio_id   INTEGER NOT NULL DEFAULT 0,
    category TEXT    NOT NULL DEFAULT ''
);
CREATE TABLE compound (
    id          INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL,
    cas         TEXT,
    flavor_class TEXT
);
CREATE TABLE ingredient_compound (
    ingredient_id INTEGER NOT NULL,
    compound_id   INTEGER NOT NULL,
    PRIMARY KEY (ingredient_id, compound_id)
);
CREATE TABLE pair_score (
    ing_a           TEXT    NOT NULL,
    ing_b           TEXT    NOT NULL,
    tfidf_score     REAL    NOT NULL DEFAULT 0,
    pmi_score       REAL    NOT NULL DEFAULT 0,
    combined_score  REAL    NOT NULL DEFAULT 0,
    shared_count    INTEGER NOT NULL DEFAULT 0,
    shared_compounds TEXT   NOT NULL DEFAULT '[]',
    npmi_score      REAL    NOT NULL DEFAULT 0,
    PRIMARY KEY (ing_a, ing_b)
);
""")

# Insert ingredients — name UNIQUE ensures all common names survive even if bio_id overlaps
for cname in sorted(active_names):
    bid = common2id.get(cname)
    if bid is not None:
        cat = id2cat.get(bid, "")
        cur.execute(
            "INSERT OR IGNORE INTO ingredient (name, bio_id, category) VALUES (?,?,?)",
            (cname, bid, cat)
        )

# Build name → new auto-increment id mapping
cur.execute("SELECT id, name, bio_id FROM ingredient")
name2newid = {}
newid2bioid = {}
for row in cur.fetchall():
    name2newid[row[1]] = row[0]
    newid2bioid[row[0]] = row[2]

# Insert compounds (those referenced by active ingredients)
used_cids = set()
for cname in active_names:
    bid = common2id.get(cname)
    if bid:
        used_cids.update(ingr_compounds_by_id.get(bid, set()))

cur.executemany(
    "INSERT OR IGNORE INTO compound (id, name, cas) VALUES (?,?,?)",
    [(cid, comp_id2name[cid], comp_id2cas.get(cid, ""))
     for cid in sorted(used_cids) if cid in comp_id2name]
)

# Insert ingredient-compound links using new auto-increment ingredient.id
ic_rows = [
    (name2newid[cname], cid)
    for cname in sorted(active_names)
    if cname in name2newid and common2id.get(cname)
    for cid in sorted(ingr_compounds_by_id.get(common2id[cname], set()))
    if cid in comp_id2name
]
cur.executemany(
    "INSERT OR IGNORE INTO ingredient_compound (ingredient_id, compound_id) VALUES (?,?)",
    ic_rows
)

# Insert pair_score (both directions)
# pmi_score = PPMI = max(0, npmi)  → [0,1] range, same as v2 ground truth
pair_rows = []
for (a_name, b_name), sc in pair_scores.items():
    shared_ids, shared_n = get_shared(a_name, b_name)
    npmi     = sc["npmi"]
    ppmi     = max(0.0, npmi)          # PPMI: ground truth for GNN (v2-compatible)
    combined = ppmi * 0.7 + (shared_n / 50.0) * 0.3
    shared_str = json.dumps(shared_ids)
    row = (a_name, b_name, 0.0, ppmi, combined, shared_n, shared_str, npmi)
    pair_rows.append(row)
    pair_rows.append((b_name, a_name, 0.0, ppmi, combined, shared_n, shared_str, npmi))

cur.executemany(
    "INSERT OR IGNORE INTO pair_score "
    "(ing_a, ing_b, tfidf_score, pmi_score, combined_score, shared_count, shared_compounds, npmi_score) "
    "VALUES (?,?,?,?,?,?,?,?)",
    pair_rows
)

con.commit()

# ── 9. Summary ───────────────────────────────────────────────────────────────
cur.execute("SELECT COUNT(*) FROM ingredient")          ; n_ing  = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM compound")            ; n_comp = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM ingredient_compound") ; n_ic   = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM pair_score")          ; n_ps   = cur.fetchone()[0]
unique_pairs = n_ps // 2

print(f"""
=== flavorgraph_v3.db ===
  Ingredients     : {n_ing}   (v2 had 151)
  Compounds       : {n_comp}
  Ingr-Comp links : {n_ic}
  Unique pairs    : {unique_pairs}  (v2 had 11,269)
  pair_score rows : {n_ps} (both directions)
""")

print("Spot-check pairs:")
checks = [("garlic", "onion"), ("butter", "garlic"), ("lemon", "garlic"),
          ("olive oil", "garlic"), ("salt", "pepper")]
for a, b in checks:
    cur.execute(
        "SELECT pmi_score, npmi_score, shared_count FROM pair_score WHERE ing_a=? AND ing_b=?",
        (a, b)
    )
    r = cur.fetchone()
    if r:
        print(f"  {a} + {b}: pmi={r[0]:.3f}  npmi={r[1]:.3f}  shared={r[2]}")
    else:
        cur.execute(
            "SELECT pmi_score, npmi_score, shared_count FROM pair_score WHERE ing_a=? AND ing_b=?",
            (b, a)
        )
        r = cur.fetchone()
        if r:
            print(f"  {b} + {a}: pmi={r[0]:.3f}  npmi={r[1]:.3f}  shared={r[2]}")
        else:
            print(f"  {a} + {b}: NOT IN PAIRS (below threshold?)")

# Ahn-style global Spearman check
print("\nGlobal Spearman(shared_count, pmi_score):")
cur.execute(
    "SELECT shared_count, pmi_score FROM pair_score WHERE ing_a < ing_b"
)
rows = cur.fetchall()
if rows:
    n = len(rows)
    sc = [r[0] for r in rows]
    pm = [r[1] for r in rows]
    # rank-based Spearman
    def rank(lst):
        return [sorted(lst).index(x) for x in lst]
    rsc = rank(sc); rpm = rank(pm)
    mean_r = sum(rsc)/n; mean_p = sum(rpm)/n
    num = sum((x-mean_r)*(y-mean_p) for x,y in zip(rsc,rpm))
    den = (sum((x-mean_r)**2 for x in rsc) * sum((y-mean_p)**2 for y in rpm))**0.5
    spearman = num/den if den else 0
    print(f"  N={n} pairs, Spearman = {spearman:.4f}")

con.close()
print("\nDone → flavorgraph_v3.db")
