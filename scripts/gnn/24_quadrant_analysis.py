"""
24_quadrant_analysis.py — Substitutability vs Complementarity
Separates negative correlation (shared_count vs PMI) into two mechanisms:
  Q1: High shared + High PMI  → unusual (flavor theory contradicted)
  Q2: Low shared  + High PMI  → complementarity (different flavors pair well)
  Q3: Low shared  + Low PMI   → neutral (different & unused)
  Q4: High shared + Low PMI   → substitutability (same flavor → not used together)
"""

import sqlite3
import numpy as np
from scipy.stats import spearmanr, pearsonr

DB_PATH = "flavorgraph_v2.db"

def load_pairs():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    rows = cur.execute(
        "SELECT ing_a, ing_b, pmi_score, shared_count FROM pair_score WHERE ing_a < ing_b"
    ).fetchall()
    con.close()
    return rows

def main():
    pairs = load_pairs()
    print(f"Total unique pairs: {len(pairs)}")

    shared = np.array([r[3] for r in pairs], dtype=float)
    pmi    = np.array([r[2] for r in pairs], dtype=float)

    # correlation
    sp_r, sp_p = spearmanr(shared, pmi)
    pe_r, pe_p = pearsonr(shared, pmi)
    print(f"\nShared count vs PMI:")
    print(f"  Spearman r = {sp_r:.4f}  (p={sp_p:.2e})")
    print(f"  Pearson  r = {pe_r:.4f}  (p={pe_p:.2e})")

    # quadrant split at medians
    med_shared = np.median(shared)
    med_pmi    = np.median(pmi)
    print(f"\nMedian shared_count = {med_shared:.1f}")
    print(f"Median pmi_score    = {med_pmi:.4f}")

    hi_shared = shared >= med_shared
    hi_pmi    = pmi    >= med_pmi

    Q1 = ( hi_shared &  hi_pmi).sum()   # unusual
    Q2 = (~hi_shared &  hi_pmi).sum()   # complementarity
    Q3 = (~hi_shared & ~hi_pmi).sum()   # neutral
    Q4 = ( hi_shared & ~hi_pmi).sum()   # substitutability
    total = len(pairs)

    print(f"\n=== Quadrant Analysis (median split) ===")
    print(f"Q1  High-shared + High-PMI  (unusual):         {Q1:5d}  ({100*Q1/total:.1f}%)")
    print(f"Q2  Low-shared  + High-PMI  (complementarity): {Q2:5d}  ({100*Q2/total:.1f}%)")
    print(f"Q3  Low-shared  + Low-PMI   (neutral):         {Q3:5d}  ({100*Q3/total:.1f}%)")
    print(f"Q4  High-shared + Low-PMI   (substitutability):{Q4:5d}  ({100*Q4/total:.1f}%)")

    # mechanism dominance
    subst = Q4 / total
    compl = Q2 / total
    print(f"\nDominant mechanism:")
    if subst > compl:
        print(f"  → Substitutability (Q4 {100*subst:.1f}% > Q2 {100*compl:.1f}%)")
    else:
        print(f"  → Complementarity  (Q2 {100*compl:.1f}% > Q4 {100*subst:.1f}%)")

    # off-diagonal ratio: how asymmetric is the negative correlation?
    off_diag = Q2 + Q4
    on_diag  = Q1 + Q3
    print(f"\nOff-diagonal (Q2+Q4): {off_diag}  ({100*off_diag/total:.1f}%)")
    print(f"On-diagonal  (Q1+Q3): {on_diag}   ({100*on_diag/total:.1f}%)")

    # top examples
    print(f"\n=== Top 10 Complementarity Pairs (Low-shared + High-PMI) ===")
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    rows_full = cur.execute(
        "SELECT ing_a, ing_b, pmi_score, shared_count FROM pair_score WHERE ing_a < ing_b ORDER BY pmi_score DESC"
    ).fetchall()
    con.close()
    compl_pairs = [(a, b, p, s) for a, b, p, s in rows_full if s < med_shared]
    print(f"{'ing_a':<20} {'ing_b':<20} {'PMI':>8} {'shared':>8}")
    for a, b, p, s in compl_pairs[:10]:
        print(f"{a:<20} {b:<20} {p:8.4f} {int(s):8d}")

    print(f"\n=== Top 10 Substitutability Pairs (High-shared + Low-PMI) ===")
    subst_pairs = sorted(
        [(a, b, p, s) for a, b, p, s in rows_full if s >= med_shared],
        key=lambda x: x[2]
    )
    print(f"{'ing_a':<20} {'ing_b':<20} {'PMI':>8} {'shared':>8}")
    for a, b, p, s in subst_pairs[:10]:
        print(f"{a:<20} {b:<20} {p:8.4f} {int(s):8d}")

if __name__ == "__main__":
    main()
