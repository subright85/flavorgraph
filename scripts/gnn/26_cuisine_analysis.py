"""
26_cuisine_analysis.py — Cuisine-stratified Ahn hypothesis analysis
Computes Spearman(shared_count, pmi_score) per cuisine.
Also computes Ahn disagreement case studies (complementarity vs substitutability).
"""

import sqlite3, json, numpy as np
from scipy.stats import spearmanr

DB_PATH = "flavorgraph_v2.db"

def load_data():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # Check available tables and columns
    tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print("Tables:", [t[0] for t in tables])

    # pair_score columns
    pair_cols = [r[1] for r in cur.execute("PRAGMA table_info(pair_score)").fetchall()]
    print("pair_score columns:", pair_cols)

    # Check for recipe or cuisine table
    has_recipe = any(t[0] in ("recipe", "recipe_ingredient") for t in tables)
    print("Has recipe/cuisine tables:", has_recipe)

    rows = cur.execute("SELECT ing_a, ing_b, pmi_score, shared_count FROM pair_score WHERE ing_a < ing_b").fetchall()
    pairs = [(a, b, float(p), int(s)) for a, b, p, s in rows]

    con.close()
    return pairs, has_recipe, con


def main():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    pair_rows = cur.execute(
        "SELECT ing_a, ing_b, pmi_score, shared_count FROM pair_score WHERE ing_a < ing_b"
    ).fetchall()
    pairs = [(a, b, float(p), int(s)) for a, b, p, s in pair_rows]

    shared = np.array([p[3] for p in pairs])
    pmi    = np.array([p[2] for p in pairs])

    sp_r, sp_p = spearmanr(shared, pmi)
    print(f"Global Spearman(shared_count, PMI) = {sp_r:.4f}  (p={sp_p:.2e}, N={len(pairs)})")

    # Check if cuisine column exists in pair_score
    pair_cols = [r[1] for r in cur.execute("PRAGMA table_info(pair_score)").fetchall()]

    # Check tables for cuisine info
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print(f"\nAvailable tables: {tables}")

    cuisine_col = None
    if "cuisine" in pair_cols:
        cuisine_col = "cuisine"
    elif "cuisine_type" in pair_cols:
        cuisine_col = "cuisine_type"

    if cuisine_col:
        # cuisine-stratified analysis directly from pair_score
        cuisines = cur.execute(f"SELECT DISTINCT {cuisine_col} FROM pair_score").fetchall()
        print(f"\n=== Cuisine-stratified Spearman ===")
        for (c,) in sorted(cuisines):
            rows = cur.execute(
                f"SELECT shared_count, pmi_score FROM pair_score WHERE {cuisine_col}=? AND ing_a < ing_b",
                (c,)
            ).fetchall()
            if len(rows) < 10:
                continue
            sh = np.array([r[0] for r in rows], dtype=float)
            pm = np.array([r[1] for r in rows], dtype=float)
            r_c, p_c = spearmanr(sh, pm)
            sig = "*" if p_c < 0.05 else ""
            print(f"  {c:<15} N={len(rows):5d}  Spearman={r_c:+.4f}  p={p_c:.3f}{sig}")
    else:
        print("\nNo cuisine column in pair_score — checking recipe tables...")

        # Try recipe_ingredient or similar
        if "recipe" in tables:
            rcols = [r[1] for r in cur.execute("PRAGMA table_info(recipe)").fetchall()]
            print(f"  recipe columns: {rcols}")
        if "recipe_ingredient" in tables:
            ricols = [r[1] for r in cur.execute("PRAGMA table_info(recipe_ingredient)").fetchall()]
            print(f"  recipe_ingredient columns: {ricols}")

        # Fallback: use flavor class as proxy for cuisine-like grouping
        print("\n=== Flavor Class-stratified Spearman (cuisine proxy) ===")
        print("(No cuisine data — using flavor class of ing_a as proxy)")

        # Load flavor profiles
        with open("data/ingredient_flavor_profile.json") as f:
            raw_profiles = json.load(f)

        CLASS_KEYS = ["alcohol","ester","sulfur","aldehyde","nitrogen","acid","terpene","aromatic","phenol","other"]

        # Map ingredient name to dominant class
        ing_rows = cur.execute("SELECT id, name FROM ingredient ORDER BY id").fetchall()
        name2id = {r[1]: r[0] for r in ing_rows}
        ing_class = {}  # name -> class
        for name, vec in raw_profiles.items():
            total = max(float(vec.get("total", 1)), 1.0)
            vals = [float(vec.get(k, 0.0)) / total for k in CLASS_KEYS]
            ing_class[name] = CLASS_KEYS[int(np.argmax(vals))]

        # Group pairs by class of ing_a
        class_pairs = {k: [] for k in CLASS_KEYS}
        for a, b, pmi, sc in pairs:
            # Find name by id
            pass

        # Actually build id->name
        id2name = {r[0]: r[1] for r in ing_rows}

        # Re-map from pair names (pair_score uses names not ids)
        pair_full = cur.execute(
            "SELECT ing_a, ing_b, pmi_score, shared_count FROM pair_score WHERE ing_a < ing_b"
        ).fetchall()

        class_groups = {k: [] for k in CLASS_KEYS}
        for a, b, pmi, sc in pair_full:
            cls = ing_class.get(a, None)
            if cls:
                class_groups[cls].append((float(pmi), int(sc)))

        print(f"{'Class':<12} {'N':>6}  {'Spearman':>10}  {'p-value':>10}")
        print("-" * 45)
        for cls in CLASS_KEYS:
            g = class_groups[cls]
            if len(g) < 10:
                continue
            pm = np.array([x[0] for x in g])
            sh = np.array([x[1] for x in g])
            r_c, p_c = spearmanr(sh, pm)
            sig = "*" if p_c < 0.05 else " "
            print(f"{cls:<12} {len(g):>6}  {r_c:>+10.4f}  {p_c:>10.3f}{sig}")

    # ============================================================
    # Ahn disagreement case studies
    # ============================================================
    med_shared = float(np.median(shared))
    med_pmi = float(np.median(pmi))

    print(f"\n=== Ahn Disagreement: Complementarity Pairs ===")
    print("(Low shared_count + High PMI — different flavor, used together)")
    compl = sorted(
        [(a, b, p, s) for a, b, p, s in pair_rows if s < med_shared and p > med_pmi],
        key=lambda x: -x[2]
    )
    print(f"{'ing_a':<22} {'ing_b':<22} {'PMI':>8} {'shared':>8}")
    for a, b, p, s in compl[:10]:
        print(f"{a:<22} {b:<22} {float(p):8.4f} {int(s):8d}")

    print(f"\n=== Ahn Disagreement: Substitutability Pairs ===")
    print("(High shared_count + Low PMI — similar flavor, not used together)")
    subst = sorted(
        [(a, b, p, s) for a, b, p, s in pair_rows if s >= med_shared and p < med_pmi],
        key=lambda x: (-x[3], x[2])
    )
    print(f"{'ing_a':<22} {'ing_b':<22} {'PMI':>8} {'shared':>8}")
    for a, b, p, s in subst[:10]:
        print(f"{a:<22} {b:<22} {float(p):8.4f} {int(s):8d}")

    # Cases where Ahn is most wrong (high shared, high PMI — Ahn would predict, and it works)
    print(f"\n=== Ahn-Aligned: High Shared + High PMI ===")
    print("(compound-sharing pairs that DO pair well — Ahn was right here)")
    aligned = sorted(
        [(a, b, p, s) for a, b, p, s in pair_rows if s >= med_shared and p > med_pmi],
        key=lambda x: (-x[2], -x[3])
    )
    print(f"{'ing_a':<22} {'ing_b':<22} {'PMI':>8} {'shared':>8}")
    for a, b, p, s in aligned[:10]:
        print(f"{a:<22} {b:<22} {float(p):8.4f} {int(s):8d}")

    con.close()


if __name__ == "__main__":
    main()
