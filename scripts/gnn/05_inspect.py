"""
Qualitative inspection of learned GNN embeddings.
- Top-k similar ingredients per anchor
- GNN score vs original PMI score comparison
- Compound-mediated pair discovery (pairs GNN ranks high but PMI didn't)
"""

import torch
import sqlite3
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from scripts.gnn.model import FlavorHGN

GRAPH_PATH = os.path.join(os.path.dirname(__file__), 'graph.pt')
FINETUNE_CKPT = os.path.join(os.path.dirname(__file__), 'finetune.pt')
DB_PATH = os.path.join(os.path.dirname(__file__), '../../flavorgraph_v2.db')


def get_pmi_scores():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT ing_a, ing_b, pmi_score, combined_score, shared_count FROM pair_score WHERE ing_a < ing_b")
    rows = cur.fetchall()
    conn.close()
    return {(a, b): (pmi, combined, shared) for a, b, pmi, combined, shared in rows}


def main():
    data = torch.load(GRAPH_PATH, weights_only=False)
    n_ing = data['ingredient'].num_nodes
    n_cmp = data['compound'].num_nodes
    ing_names = data['ingredient'].names

    model = FlavorHGN(n_ing, n_cmp, hidden_dim=128, num_layers=2, num_heads=4)
    model.load_state_dict(torch.load(FINETUNE_CKPT, map_location='cpu'))
    model.train(False)

    with torch.no_grad():
        x_dict = model.encode(data)
        emb = x_dict['ingredient']

    pmi_lookup = get_pmi_scores()

    print("=" * 60)
    print("Top-10 GNN pairs per anchor (vs original PMI)")
    print("=" * 60)
    anchors = ['garlic', 'lemon', 'butter', 'thyme', 'ginger', 'chocolate', 'vanilla', 'tomato']

    for anchor in anchors:
        if anchor not in ing_names:
            print(f"  {anchor}: not in DB")
            continue
        a_idx = ing_names.index(anchor)
        scores = (emb[a_idx] * model.decoder.W * emb).sum(dim=-1)
        scores[a_idx] = float('-inf')
        top_k = scores.argsort(descending=True)[:10].tolist()

        print(f"\n[{anchor}] top-10 by GNN:")
        for rank, idx in enumerate(top_k, 1):
            b_name = ing_names[idx]
            key = (min(anchor, b_name), max(anchor, b_name))
            pmi_data = pmi_lookup.get(key, (0, 0, 0))
            gnn_s = scores[idx].item()
            print(f"  {rank:2d}. {b_name:<25} GNN={gnn_s:.3f}  PMI={pmi_data[0]:.3f}  combined={pmi_data[1]:.3f}  shared_cmp={pmi_data[2]}")

    print("\n" + "=" * 60)
    print("Compound-mediated discoveries: GNN high, PMI low, shared_cmp > 0")
    print("=" * 60)
    all_scores = []
    for i in range(n_ing):
        for j in range(i + 1, n_ing):
            gnn_s = (emb[i] * model.decoder.W * emb[j]).sum().item()
            a, b = ing_names[i], ing_names[j]
            key = (min(a, b), max(a, b))
            pmi_data = pmi_lookup.get(key, (0, 0, 0))
            if pmi_data[0] < 0.3 and pmi_data[2] > 2:  # low PMI, meaningful compound overlap
                all_scores.append((gnn_s, a, b, pmi_data[0], pmi_data[1], pmi_data[2]))

    all_scores.sort(reverse=True)
    print("(low PMI <0.3, shared_compounds >2, high GNN score = compound-driven discovery)")
    for gnn_s, a, b, pmi, combined, shared in all_scores[:15]:
        print(f"  {a:<20} + {b:<20}  GNN={gnn_s:.3f}  PMI={pmi:.3f}  shared_cmp={shared}")


if __name__ == '__main__':
    main()
