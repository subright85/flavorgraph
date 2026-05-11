"""
33_build_v4.py -- Build flavorgraph_v4.db from 906-ingredient expanded mapping

Uses data/ingredient_expanded_map.json produced by 32_expand_mapping.py.
Schema identical to v3; pmi_score stores PPMI = max(0, NPMI).

Input:
  data/ingredient_expanded_map.json  -- 906 common-name -> botanical-ID mappings
  data/RAW_recipes.csv               -- co-occurrence source
  data/ingr_comp.tsv                 -- ingredient-compound links
  data/comp_info.tsv                 -- compound metadata

Output:
  flavorgraph_v4.db
"""

import csv
import json
import math
import re
import sqlite3
from collections import defaultdict
from itertools import combinations
from pathlib import Path

ROOT   = Path(__file__).parent.parent.parent
DATA   = ROOT / "data"
DB_OUT = ROOT / "flavorgraph_v4.db"

MIN_CO_COUNT = 10

# -- 1. Load expanded mapping --------------------------------------------------
print("Loading ingredient_expanded_map.json...")
with open(DATA / "ingredient_expanded_map.json") as f:
    expanded_map = json.load(f)

common2id = {cn: info["botanical_id"] for cn, info in expanded_map.items()}
print(f"  {len(common2id)} ingredient mappings loaded")

# -- 2. Load ingredient info ---------------------------------------------------
print("Loading ingr_info.tsv...")
id2name, id2cat = {}, {}
with open(DATA / "ingr_info.tsv") as f:
    next(f)
    for line in f:
        parts = line.strip().split("\t")
        iid = int(parts[0]); name = parts[1]; cat = parts[2] if len(parts) > 2 else ""
        id2name[iid] = name; id2cat[iid] = cat

# -- 3. Load compound info ----------------------------------------------------
print("Loading compound info...")
comp_id2name, comp_id2cas = {}, {}
with open(DATA / "comp_info.tsv") as f:
    next(f)
    for line in f:
        parts = line.strip().split("\t")
        cid = int(parts[0]); cname = parts[1]; cas = parts[2] if len(parts) > 2 else ""
        comp_id2name[cid] = cname; comp_id2cas[cid] = cas
print(f"  {len(comp_id2name)} compounds")

# -- 4. Load ingredient-compound links ----------------------------------------
print("Loading ingr_comp.tsv...")
ingr_compounds_by_id = defaultdict(set)
with open(DATA / "ingr_comp.tsv") as f:
    next(f)
    for line in f:
        parts = line.strip().split("\t")
        ingr_compounds_by_id[int(parts[0])].add(int(parts[1]))
print(f"  {len(ingr_compounds_by_id)} botanical IDs have compound data")

# -- 5. Co-occurrence counting ------------------------------------------------
print("Counting co-occurrences from RAW_recipes.csv...")
target = set(common2id.keys())
ing_count  = defaultdict(int)
pair_count = defaultdict(int)
N = 0

with open(DATA / "RAW_recipes.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        N += 1
        if N % 50_000 == 0:
            print(f"  {N:,} recipes...")
        ings = list(set(i for i in re.findall(r"'([^']+)'", row.get("ingredients", "")) if i in target))
        for i in ings:
            ing_count[i] += 1
        for a, b in combinations(sorted(ings), 2):
            pair_count[(a, b)] += 1

print(f"  N={N:,} recipes")
print(f"  Ingredients seen: {len(ing_count)}")
print(f"  Pairs with >=1 co-occurrence: {len(pair_count):,}")

# -- 6. PPMI computation ------------------------------------------------------
print("Computing PPMI...")
pair_scores = {}
for (a, b), co in pair_count.items():
    if co < MIN_CO_COUNT:
        continue
    p_ab = co / N
    p_a  = ing_count[a] / N
    p_b  = ing_count[b] / N
    pmi  = math.log(p_ab / (p_a * p_b))
    npmi = pmi / (-math.log(p_ab))
    pair_scores[(a, b)] = {"npmi": npmi, "co": co}

print(f"  Pairs with PPMI: {len(pair_scores):,}")

active_names = set()
for a, b in pair_scores:
    active_names.add(a); active_names.add(b)
print(f"  Active ingredients: {len(active_names)}")

# -- 7. Shared-compound helper ------------------------------------------------
def get_shared(a_name, b_name):
    ca = ingr_compounds_by_id.get(common2id.get(a_name), set())
    cb = ingr_compounds_by_id.get(common2id.get(b_name), set())
    shared = list(ca & cb)
    return shared, len(shared)

# -- 8. Build database --------------------------------------------------------
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
    id           INTEGER PRIMARY KEY,
    name         TEXT    NOT NULL,
    cas          TEXT,
    flavor_class TEXT
);
CREATE TABLE ingredient_compound (
    ingredient_id INTEGER NOT NULL,
    compound_id   INTEGER NOT NULL,
    PRIMARY KEY (ingredient_id, compound_id)
);
CREATE TABLE pair_score (
    ing_a            TEXT    NOT NULL,
    ing_b            TEXT    NOT NULL,
    tfidf_score      REAL    NOT NULL DEFAULT 0,
    pmi_score        REAL    NOT NULL DEFAULT 0,
    combined_score   REAL    NOT NULL DEFAULT 0,
    shared_count     INTEGER NOT NULL DEFAULT 0,
    shared_compounds TEXT    NOT NULL DEFAULT '[]',
    npmi_score       REAL    NOT NULL DEFAULT 0,
    PRIMARY KEY (ing_a, ing_b)
);
""")

for cname in sorted(active_names):
    bid = common2id.get(cname)
    if bid is not None:
        cur.execute(
            "INSERT OR IGNORE INTO ingredient (name, bio_id, category) VALUES (?,?,?)",
            (cname, bid, id2cat.get(bid, ""))
        )

cur.execute("SELECT id, name FROM ingredient")
name2newid = {row[1]: row[0] for row in cur.fetchall()}

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

pair_rows = []
for (a_name, b_name), sc in pair_scores.items():
    shared_ids, shared_n = get_shared(a_name, b_name)
    npmi     = sc["npmi"]
    ppmi     = max(0.0, npmi)
    combined = ppmi * 0.7 + (shared_n / 50.0) * 0.3
    row = (a_name, b_name, 0.0, ppmi, combined, shared_n, json.dumps(shared_ids), npmi)
    pair_rows.append(row)
    pair_rows.append((b_name, a_name, 0.0, ppmi, combined, shared_n, json.dumps(shared_ids), npmi))

cur.executemany(
    "INSERT OR IGNORE INTO pair_score "
    "(ing_a, ing_b, tfidf_score, pmi_score, combined_score, shared_count, shared_compounds, npmi_score) "
    "VALUES (?,?,?,?,?,?,?,?)",
    pair_rows
)
con.commit()

# -- 9. Summary ---------------------------------------------------------------
cur.execute("SELECT COUNT(*) FROM ingredient")          ; n_ing  = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM compound")            ; n_comp = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM ingredient_compound") ; n_ic   = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM pair_score")          ; n_ps   = cur.fetchone()[0]
unique_pairs = n_ps // 2

print(f"""
=== flavorgraph_v4.db ===
  Ingredients     : {n_ing}   (v3 had 239, v2 had 151)
  Compounds       : {n_comp}
  Ingr-Comp links : {n_ic}
  Unique pairs    : {unique_pairs}  (v3 had 9,305, v2 had 11,269)
  pair_score rows : {n_ps} (both directions)
""")

print("Spot-check pairs:")
checks = [
    ("garlic", "onion"), ("butter", "garlic"), ("garlic cloves", "onions"),
    ("fresh parsley", "garlic"), ("unsalted butter", "garlic cloves"),
]
for a, b in checks:
    cur.execute("SELECT pmi_score, npmi_score, shared_count FROM pair_score WHERE ing_a=? AND ing_b=?", (a, b))
    r = cur.fetchone()
    if r:
        print(f"  {a} + {b}: ppmi={r[0]:.3f}  npmi={r[1]:.3f}  shared={r[2]}")
    else:
        cur.execute("SELECT pmi_score, npmi_score, shared_count FROM pair_score WHERE ing_a=? AND ing_b=?", (b, a))
        r = cur.fetchone()
        if r:
            print(f"  {b} + {a}: ppmi={r[0]:.3f}  npmi={r[1]:.3f}  shared={r[2]}")
        else:
            print(f"  {a} + {b}: NOT FOUND")

con.close()
print(f"\nSaved -> {DB_OUT}")
