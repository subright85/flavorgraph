"""
NPMI-based DB score rebuild.
Formula: combined_score = max(0, npmi_norm) * 0.7 + compound_score * 0.3
"""
import ast, csv, sqlite3, math, json
from collections import defaultdict
from itertools import combinations

DB_PATH = "/Users/sukim/Documents/Github/flavorgraph/flavorgraph_v2.db"
RECIPES_PATH = "/Users/sukim/Documents/Github/flavorgraph/data/RAW_recipes.csv"
MIN_CO_COUNT = 10

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

# Get our 151 target ingredients
cur.execute("SELECT name FROM ingredient")
target = set(r[0] for r in cur.fetchall())
print(f"Target ingredients: {len(target)}")

# Pass 1: count co-occurrences and ingredient frequencies
print("Pass 1: counting co-occurrences from 231k recipes...")
ing_count = defaultdict(int)
pair_count = defaultdict(int)
N = 0

with open(RECIPES_PATH) as f:
    reader = csv.DictReader(f)
    for row in reader:
        N += 1
        if N % 50000 == 0:
            print(f"  {N} recipes processed...")
        try:
            ings = ast.literal_eval(row['ingredients'])
        except:
            continue
        # Only keep target ingredients
        ings_filtered = list(set(i for i in ings if i in target))
        for ing in ings_filtered:
            ing_count[ing] += 1
        for a, b in combinations(sorted(ings_filtered), 2):
            pair_count[(a, b)] += 1

print(f"Done. N={N}, unique target ing appearances: {len(ing_count)}")
print(f"Pairs with co-occurrence: {len(pair_count)}")

# Pass 2: compute NPMI for all pairs
print("\nPass 2: computing NPMI...")
npmi_scores = {}

for (a, b), co in pair_count.items():
    if co < MIN_CO_COUNT:
        continue
    p_ab = co / N
    p_a = ing_count[a] / N
    p_b = ing_count[b] / N
    if p_a == 0 or p_b == 0 or p_ab == 0:
        continue
    pmi = math.log(p_ab / (p_a * p_b))
    npmi = pmi / (-math.log(p_ab))
    npmi_scores[(a, b)] = max(0, npmi)  # PPMI: floor at 0

print(f"Pairs with NPMI computed: {len(npmi_scores)}")

# Print some examples
for pair in [("lemon","garlic"), ("butter","garlic"), ("garlic","onion"), ("garlic","thyme"), ("olive oil","garlic")]:
    a, b = min(pair), max(pair)
    npmi = npmi_scores.get((a,b)) or npmi_scores.get((b,a))
    co = pair_count.get((a,b)) or pair_count.get((b,a), 0)
    npmi_str = f"{npmi:.4f}" if npmi is not None else "N/A"
    print(f"  {pair[0]} + {pair[1]}: co={co} npmi={npmi_str}")

# Pass 3: update DB
print("\nPass 3: updating pair_score table...")

# Add npmi_score column if not exists
try:
    cur.execute("ALTER TABLE pair_score ADD COLUMN npmi_score REAL NOT NULL DEFAULT 0")
    con.commit()
    print("Added npmi_score column")
except sqlite3.OperationalError:
    print("npmi_score column already exists")

updated = 0
for (a, b), npmi in npmi_scores.items():
    # combined_score = npmi * 0.7 + compound_score * 0.3
    cur.execute(
        "UPDATE pair_score SET npmi_score=?, combined_score=? + shared_count/50.0*0.3 WHERE (ing_a=? AND ing_b=?) OR (ing_a=? AND ing_b=?)",
        (npmi, npmi * 0.7, a, b, b, a)
    )
    updated += cur.rowcount

con.commit()
print(f"Updated {updated} rows")

# Verify
print("\nVerification:")
for pair in [("lemon","garlic"), ("butter","garlic"), ("garlic","onion"), ("garlic","thyme")]:
    cur.execute("SELECT npmi_score, shared_count, combined_score FROM pair_score WHERE (ing_a=? AND ing_b=?) OR (ing_a=? AND ing_b=?)", (*pair, *reversed(pair)))
    r = cur.fetchone()
    if r:
        print(f"  {pair[0]} + {pair[1]}: npmi={r[0]:.3f} shared={r[1]} combined={r[2]:.3f} → {round(r[2]*100)}pts")

con.close()
print("\nDone!")
