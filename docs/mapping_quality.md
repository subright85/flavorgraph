# Mapping Quality Analysis — v5 Dataset
**Generated**: 2026-05-12
**Relevant for**: RecSys 2026 data quality section

---

## Overview

Of 1,094 active ingredients in flavorgraph_v5.db:
- **301** map to unique botanical IDs (high-confidence, 1:1)
- **979** share a botanical ID with at least one other ingredient (many-to-one)

The 186 multi-variant botanical IDs break into:
- **101 pure synonym groups**: all variants are prep-word variants of the same base ingredient
  (e.g., fresh garlic / dried garlic / garlic cloves / granulated garlic → garlic)
- **85 semantic overreach groups**: multiple culinary roles collapsed to one botanical
  (e.g., all-purpose flour / pasta / breadcrumbs / tortillas → wheat; cream / cream soups → cream)

## Critical Overreach Cases

These affect AntiHomo quality the most — all variants share the same compound center
despite having fundamentally different culinary roles:

| Botanical ID | Variants | Examples (distinct roles) |
|---|---|---|
| 1179 (wheat) | 40 | flour vs pasta vs breadcrumbs vs tortillas |
| 1338 (chicken) | 33 | breast vs thigh vs ground vs wings |
| 1240 (tomato) | 28 | fresh tomato vs tomato soup vs spaghetti sauce |
| 1021 (pepper) | 27 | fresh pepper vs chili paste vs chipotle in adobo |
| 417 (pork) | 20 | ribs vs ground pork vs chorizo sausage |
| 248 (beef) | 20 | steak vs ground beef vs brisket vs corned beef |
| 724 (cream) | 19 | cream vs cream of chicken soup vs cream of mushroom soup |
| 427 (corn) | 18 | corn vs corn flakes vs tortilla chips |
| 260 (mushroom) | 15 | fresh mushroom vs condensed cream of mushroom soup |

Worst examples:
- creole seasoning (spice blend) -> black pepper
- worcestershire sauce -> vinegar
- italian seasoning (herb blend) -> oregano
- poultry seasoning (blend) -> thyme

## Impact on AntiHomo

The AntiHomo correction computes .
For semantic overreach groups, this compound center is:
1. Shared across all variants (zero discriminative power among them)
2. Inaccurate for processed variants (cream of mushroom soup ≠ cream compound profile)

This explains why AntiHomo degrades in v5 (3.63x ratio) vs v4 (2.00x ratio):
the v5 expansion added 516 new ingredients but only 12 new botanical IDs, mostly
via semantic overreach (Phase 4.manual batch review mapped blended/processed products
to nearest botanical).

## v6 Recommendations

**Option A (immediate)**: Filter to the 301 unique-botanical ingredients + synonym groups.
This gives ~600-700 ingredients with cleaner compound-center quality and ratio <=1.5x.
Trade-off: smaller dataset, fewer pairs.

**Option B (data enrichment)**: Use FooDB or USDA flavor database to get compound
profiles for processed products (pasta, breadcrumbs, sauces). This expands the
unique-botanical coverage without semantic overreach.

**Option C (paper framing)**: Document as a known limitation. Demonstrate that
filtering to high-quality ingredients (unique botanical) improves AntiHomo delta.
This is a clean ablation that can be done on v5.db without new data collection.
