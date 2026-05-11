"""
Expand compound coverage to 1,830-ingredient graph using FooDB TSV data.

Strategy:
1. Load FooDB ingr_info.tsv (1,530 ingredients) + comp_info.tsv (1,107 compounds) + ingr_comp.tsv
2. Fuzzy match RAW_recipes vocab (1,830 ings) → FooDB ingredient names
   - Exact match first
   - Substring: FooDB name is a substring of recipe name (≥4 chars)
3. Build extended graph with ~70% compound coverage
4. Save as graph_1830_full.pt
"""

import csv, re, os, sys, sqlite3
import torch
from collections import Counter, defaultdict
from torch_geometric.data import HeteroData
import math

DATA_DIR = os.path.join(os.path.dirname(__file__), '../../data')
RECIPES_PATH = os.path.join(DATA_DIR, 'RAW_recipes.csv')
OUT_PATH = os.path.join(os.path.dirname(__file__), 'graph_1830_full.pt')

MIN_COUNT = 100


def parse_ingredients(raw):
    return re.findall(r"'([^']+)'", raw)


def load_foodb():
    """Load FooDB ingredient info, compound info, and links from TSV files."""
    foodb_id_to_name = {}
    foodb_name_to_id = {}
    with open(os.path.join(DATA_DIR, 'ingr_info.tsv')) as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                fid = parts[0]
                name = parts[1].replace('_', ' ').lower()
                foodb_id_to_name[fid] = name
                foodb_name_to_id[name] = fid

    comp_id_to_name = {}
    with open(os.path.join(DATA_DIR, 'comp_info.tsv')) as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                comp_id_to_name[parts[0]] = parts[1].replace('_', ' ')

    ing_comp_links = []
    with open(os.path.join(DATA_DIR, 'ingr_comp.tsv')) as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                ing_comp_links.append((parts[0], parts[1]))

    return foodb_name_to_id, comp_id_to_name, ing_comp_links


def fuzzy_match(vocab_1830, foodb_name_to_id):
    """Match recipe ingredient names to FooDB names."""
    foodb_names = list(foodb_name_to_id.keys())

    matched = {}
    for ing in vocab_1830:
        if ing in foodb_name_to_id:
            matched[ing] = foodb_name_to_id[ing]
            continue
        # Substring: longest FooDB name that appears in recipe name (≥4 chars)
        best, best_len = None, 0
        for fn in foodb_names:
            if fn in ing and len(fn) > best_len and len(fn) >= 4:
                best = fn
                best_len = len(fn)
        if best:
            matched[ing] = foodb_name_to_id[best]

    return matched


def build_graph():
    print("Loading FooDB data...")
    foodb_name_to_id, comp_id_to_name, ing_comp_links = load_foodb()
    print(f"  FooDB: {len(foodb_name_to_id)} ingredients, {len(comp_id_to_name)} compounds, "
          f"{len(ing_comp_links)} links")

    # Build compound vocabulary from FooDB
    all_comp_ids = sorted(set(comp_id_to_name.keys()))
    comp_id_to_idx = {cid: i for i, cid in enumerate(all_comp_ids)}
    comp_names = [comp_id_to_name[cid] for cid in all_comp_ids]
    n_cmp = len(all_comp_ids)
    print(f"  Compound vocab: {n_cmp}")

    # Build FooDB ingr_id → compound_ids lookup
    foodb_ing_to_comps = defaultdict(set)
    for ing_id, cmp_id in ing_comp_links:
        if cmp_id in comp_id_to_idx:
            foodb_ing_to_comps[ing_id].add(cmp_id)

    print("\nReading RAW_recipes.csv...")
    ingredient_counter = Counter()
    recipe_ingredients = []
    with open(RECIPES_PATH) as f:
        for row in csv.DictReader(f):
            ings = {i.lower().strip() for i in parse_ingredients(row.get('ingredients', ''))}
            if ings:
                recipe_ingredients.append(ings)
                ingredient_counter.update(ings)

    total_recipes = len(recipe_ingredients)
    vocab = [ing for ing, cnt in ingredient_counter.most_common() if cnt >= MIN_COUNT]
    vocab_set = set(vocab)
    ing_to_idx = {ing: i for i, ing in enumerate(vocab)}
    n_ing = len(vocab)
    print(f"  {total_recipes} recipes, {n_ing} ingredients")

    # Fuzzy match recipe vocab → FooDB
    print("\nFuzzy matching recipe ingredients → FooDB...")
    ing_to_foodb = fuzzy_match(vocab, foodb_name_to_id)
    print(f"  Matched: {len(ing_to_foodb)}/{n_ing} ({100*len(ing_to_foodb)/n_ing:.1f}%)")

    # Build ingredient↔compound edges
    ic_src, ic_dst = [], []
    ci_src, ci_dst = [], []
    for ing_name, foodb_ing_id in ing_to_foodb.items():
        if ing_name not in ing_to_idx:
            continue
        i_idx = ing_to_idx[ing_name]
        for cmp_id in foodb_ing_to_comps.get(foodb_ing_id, []):
            c_idx = comp_id_to_idx[cmp_id]
            ic_src.append(i_idx)
            ic_dst.append(c_idx)
            ci_src.append(c_idx)
            ci_dst.append(i_idx)

    print(f"  ing→cmp edges: {len(ic_src)} (avg {len(ic_src)/max(1,len(ing_to_foodb)):.1f} per matched ing)")
    print(f"  Ingredients with compound data: {len(set(ic_src))}")

    # Build ingredient↔ingredient PMI edges
    print("\nComputing PMI...")
    single_count = {ing: ingredient_counter[ing] for ing in vocab}
    pair_count = defaultdict(int)
    for recipe_set in recipe_ingredients:
        ings_in_recipe = sorted(vocab_set & recipe_set)
        for i in range(len(ings_in_recipe)):
            for j in range(i + 1, len(ings_in_recipe)):
                pair_count[(ings_in_recipe[i], ings_in_recipe[j])] += 1

    pmi_values = {}
    for (a, b), co_cnt in pair_count.items():
        if co_cnt == 0:
            continue
        pmi = math.log((co_cnt / total_recipes) /
                       ((single_count[a] / total_recipes) * (single_count[b] / total_recipes)))
        if pmi > 0:
            pmi_values[(a, b)] = pmi

    max_pmi = max(pmi_values.values())
    min_pmi = min(pmi_values.values())
    pmi_range = max_pmi - min_pmi or 1.0

    ii_src, ii_dst, ii_pmi = [], [], []
    for (a, b), pmi_raw in pmi_values.items():
        pmi_norm = (pmi_raw - min_pmi) / pmi_range
        ii_src.extend([ing_to_idx[a], ing_to_idx[b]])
        ii_dst.extend([ing_to_idx[b], ing_to_idx[a]])
        ii_pmi.extend([pmi_norm, pmi_norm])

    print(f"  PMI pairs: {len(ii_src)//2}")

    # Build HeteroData
    data = HeteroData()
    data['ingredient'].num_nodes = n_ing
    data['ingredient'].names = vocab
    data['compound'].num_nodes = n_cmp
    data['compound'].names = comp_names

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
    print(f"  ing↔ing edges    : {len(ii_src)//2} unique pairs")
    print(f"  ing→cmp edges    : {len(ic_src)}")
    print(f"  compound coverage: {len(set(ic_src))}/{n_ing} = {100*len(set(ic_src))/n_ing:.1f}%")

    return data


if __name__ == '__main__':
    build_graph()
