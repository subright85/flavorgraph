"""
Build PyG HeteroData graph from flavorgraph_v2.db.

Node types:
  - ingredient: 151 nodes, no initial features (will use learnable embeddings)
  - compound: 822 nodes, no initial features

Edge types:
  - ('ingredient', 'pairs_with', 'ingredient'): PMI-weighted co-occurrence (undirected → stored both ways)
  - ('ingredient', 'contains', 'compound'): FooDB membership (binary)
  - ('compound', 'in', 'ingredient'): reverse of above

Output: saves graph.pt to scripts/gnn/
"""

import sqlite3
import torch
from torch_geometric.data import HeteroData
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../flavorgraph_v2.db')
OUT_PATH = os.path.join(os.path.dirname(__file__), 'graph.pt')


def build_graph():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # --- Ingredient nodes ---
    cur.execute("SELECT id, name, category FROM ingredient ORDER BY id")
    ing_rows = cur.fetchall()
    ing_ids = [r[0] for r in ing_rows]
    ing_names = [r[1] for r in ing_rows]
    ing_id_to_idx = {iid: i for i, iid in enumerate(ing_ids)}
    n_ing = len(ing_ids)

    # --- Compound nodes ---
    cur.execute("SELECT id, name FROM compound ORDER BY id")
    cmp_rows = cur.fetchall()
    cmp_ids = [r[0] for r in cmp_rows]
    cmp_names = [r[1] for r in cmp_rows]
    cmp_id_to_idx = {cid: i for i, cid in enumerate(cmp_ids)}
    n_cmp = len(cmp_ids)

    # --- Ingredient ↔ Ingredient edges (PMI) ---
    # Use combined_score as edge weight; deduplicate to one direction then add reverse
    cur.execute("""
        SELECT ing_a, ing_b, pmi_score, combined_score
        FROM pair_score
        WHERE ing_a < ing_b AND combined_score > 0
    """)
    pair_rows = cur.fetchall()

    ii_src, ii_dst, ii_pmi, ii_score = [], [], [], []
    for a_name, b_name, pmi, score in pair_rows:
        # Map name → idx (pair_score uses ingredient names, not ids)
        pass

    # pair_score uses ingredient names — build name→idx
    ing_name_to_idx = {name: i for i, name in enumerate(ing_names)}

    cur.execute("""
        SELECT ing_a, ing_b, pmi_score, combined_score
        FROM pair_score
        WHERE combined_score > 0
    """)
    all_pairs = cur.fetchall()

    seen = set()
    for a_name, b_name, pmi, score in all_pairs:
        if a_name not in ing_name_to_idx or b_name not in ing_name_to_idx:
            continue
        key = (min(a_name, b_name), max(a_name, b_name))
        if key in seen:
            continue
        seen.add(key)
        a_idx = ing_name_to_idx[a_name]
        b_idx = ing_name_to_idx[b_name]
        ii_src.extend([a_idx, b_idx])
        ii_dst.extend([b_idx, a_idx])
        ii_pmi.extend([pmi, pmi])
        ii_score.extend([score, score])

    # --- Ingredient → Compound edges ---
    # ingredient_compound uses integer ids
    cur.execute("SELECT ingredient_id, compound_id FROM ingredient_compound")
    ic_rows = cur.fetchall()

    ic_src, ic_dst = [], []   # ingredient → compound
    ci_src, ci_dst = [], []   # compound → ingredient (reverse)
    for ing_db_id, cmp_db_id in ic_rows:
        if ing_db_id not in ing_id_to_idx or cmp_db_id not in cmp_id_to_idx:
            continue
        i_idx = ing_id_to_idx[ing_db_id]
        c_idx = cmp_id_to_idx[cmp_db_id]
        ic_src.append(i_idx)
        ic_dst.append(c_idx)
        ci_src.append(c_idx)
        ci_dst.append(i_idx)

    conn.close()

    # --- Build HeteroData ---
    data = HeteroData()

    # Nodes: use integer index as num_nodes; no initial features (learnable embeddings in model)
    data['ingredient'].num_nodes = n_ing
    data['compound'].num_nodes = n_cmp

    # Store metadata for downstream use
    data['ingredient'].names = ing_names
    data['compound'].names = cmp_names

    # Ingredient ↔ Ingredient
    data['ingredient', 'pairs_with', 'ingredient'].edge_index = torch.tensor(
        [ii_src, ii_dst], dtype=torch.long
    )
    data['ingredient', 'pairs_with', 'ingredient'].pmi = torch.tensor(ii_pmi, dtype=torch.float)
    data['ingredient', 'pairs_with', 'ingredient'].score = torch.tensor(ii_score, dtype=torch.float)

    # Ingredient → Compound
    data['ingredient', 'contains', 'compound'].edge_index = torch.tensor(
        [ic_src, ic_dst], dtype=torch.long
    )

    # Compound → Ingredient (reverse)
    data['compound', 'in', 'ingredient'].edge_index = torch.tensor(
        [ci_src, ci_dst], dtype=torch.long
    )

    torch.save(data, OUT_PATH)
    print(f"Graph saved to {OUT_PATH}")
    print(f"  ingredient nodes : {n_ing}")
    print(f"  compound nodes   : {n_cmp}")
    print(f"  ing↔ing edges    : {len(ii_src)} (bidirectional, {len(ii_src)//2} unique pairs)")
    print(f"  ing→cmp edges    : {len(ic_src)}")
    print(f"  cmp→ing edges    : {len(ci_src)}")

    return data


if __name__ == '__main__':
    data = build_graph()
    print("\nHeteroData summary:")
    print(data)
