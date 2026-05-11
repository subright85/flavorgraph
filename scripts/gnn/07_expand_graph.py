"""
Expand ingredient nodes 151 → 1,840 using RAW_recipes.csv PMI.

Graph structure after expansion:
- ingredient nodes: 1,840 (151 with compound links + 1,689 recipe-only)
- compound nodes: 822 (unchanged from FooDB)
- ingredient↔ingredient: PMI from RAW_recipes (231,637 recipes)
- ingredient↔compound: 9,377 links (for the original 151 only)
"""

import csv, math, re, sqlite3, os
import torch
from collections import Counter, defaultdict
from torch_geometric.data import HeteroData

DB_PATH = os.path.join(os.path.dirname(__file__), '../../flavorgraph_v2.db')
RECIPES_PATH = os.path.join(os.path.dirname(__file__), '../../data/RAW_recipes.csv')
OUT_PATH = os.path.join(os.path.dirname(__file__), 'graph_1840.pt')

MIN_COUNT = 100


def parse_ingredients(raw):
    """Parse ingredient list string without using ast — regex on quoted items."""
    return re.findall(r"'([^']+)'", raw)


def build_expanded_graph():
    print("Reading RAW_recipes.csv...")
    ingredient_counter = Counter()
    recipe_ingredients = []

    with open(RECIPES_PATH) as f:
        for row in csv.DictReader(f):
            ings = {i.lower().strip() for i in parse_ingredients(row.get('ingredients', ''))}
            if ings:
                recipe_ingredients.append(ings)
                ingredient_counter.update(ings)

    total_recipes = len(recipe_ingredients)
    print(f"  {total_recipes} recipes loaded")

    # Top-1840 vocabulary
    vocab = [ing for ing, cnt in ingredient_counter.most_common() if cnt >= MIN_COUNT]
    vocab_set = set(vocab)
    ing_to_idx = {ing: i for i, ing in enumerate(vocab)}
    n_ing = len(vocab)
    print(f"  {n_ing} ingredients (>={MIN_COUNT} occurrences)")

    single_count = {ing: ingredient_counter[ing] for ing in vocab}

    print("Computing co-occurrence counts...")
    pair_count = defaultdict(int)
    for recipe_set in recipe_ingredients:
        ings_in_recipe = sorted(vocab_set & recipe_set)
        for i in range(len(ings_in_recipe)):
            for j in range(i + 1, len(ings_in_recipe)):
                pair_count[(ings_in_recipe[i], ings_in_recipe[j])] += 1

    print(f"  {len(pair_count)} unique co-occurring pairs")

    print("Computing PMI...")
    pmi_values = {}
    for (a, b), co_cnt in pair_count.items():
        if co_cnt == 0:
            continue
        p_ab = co_cnt / total_recipes
        p_a = single_count[a] / total_recipes
        p_b = single_count[b] / total_recipes
        pmi = math.log(p_ab / (p_a * p_b))
        if pmi > 0:
            pmi_values[(a, b)] = pmi

    print(f"  {len(pmi_values)} pairs with PMI > 0")
    max_pmi = max(pmi_values.values())
    min_pmi = min(pmi_values.values())
    pmi_range = max_pmi - min_pmi or 1.0
    print(f"  PMI range: [{min_pmi:.3f}, {max_pmi:.3f}]")

    ii_src, ii_dst, ii_pmi = [], [], []
    for (a, b), pmi_raw in pmi_values.items():
        pmi_norm = (pmi_raw - min_pmi) / pmi_range
        ii_src.extend([ing_to_idx[a], ing_to_idx[b]])
        ii_dst.extend([ing_to_idx[b], ing_to_idx[a]])
        ii_pmi.extend([pmi_norm, pmi_norm])

    print("Loading compound data from DB...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM compound ORDER BY id")
    cmp_rows = cur.fetchall()
    cmp_names = [r[1] for r in cmp_rows]
    cmp_id_to_idx = {r[0]: i for i, r in enumerate(cmp_rows)}
    n_cmp = len(cmp_rows)

    cur.execute("""
        SELECT i.name, ic.compound_id
        FROM ingredient_compound ic
        JOIN ingredient i ON i.id = ic.ingredient_id
    """)
    ic_link_rows = cur.fetchall()
    conn.close()

    ic_src, ic_dst, ci_src, ci_dst = [], [], [], []
    for ing_name, cmp_db_id in ic_link_rows:
        ing_key = ing_name.lower().strip()
        if ing_key not in ing_to_idx or cmp_db_id not in cmp_id_to_idx:
            continue
        i_idx = ing_to_idx[ing_key]
        c_idx = cmp_id_to_idx[cmp_db_id]
        ic_src.append(i_idx)
        ic_dst.append(c_idx)
        ci_src.append(c_idx)
        ci_dst.append(i_idx)

    print(f"  ingredient↔compound edges: {len(ic_src)}")

    data = HeteroData()
    data['ingredient'].num_nodes = n_ing
    data['ingredient'].names = vocab
    data['compound'].num_nodes = n_cmp
    data['compound'].names = cmp_names

    data['ingredient', 'pairs_with', 'ingredient'].edge_index = torch.tensor(
        [ii_src, ii_dst], dtype=torch.long)
    data['ingredient', 'pairs_with', 'ingredient'].pmi = torch.tensor(ii_pmi, dtype=torch.float)
    data['ingredient', 'contains', 'compound'].edge_index = torch.tensor(
        [ic_src, ic_dst], dtype=torch.long)
    data['compound', 'in', 'ingredient'].edge_index = torch.tensor(
        [ci_src, ci_dst], dtype=torch.long)

    torch.save(data, OUT_PATH)
    print(f"\nSaved to {OUT_PATH}")
    print(f"  ingredient nodes : {n_ing}")
    print(f"  compound nodes   : {n_cmp}")
    print(f"  ing↔ing edges    : {len(ii_src)} ({len(ii_src)//2} unique pairs)")
    print(f"  ing→cmp edges    : {len(ic_src)}")
    print(f"  compound-linked  : {len(set(ic_src))} ingredients")
    return data


if __name__ == '__main__':
    data = build_expanded_graph()
    print("\nHeteroData summary:")
    print(data)
