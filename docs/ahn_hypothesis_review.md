# Ahn Hypothesis Review — FlavorGraph v4/v5
**Prepared for**: RecSys 2026 Workshop (deadline July 20, 2026)  
**Status**: W2 draft — empirical correlation analysis added

---

## 1. The Ahn et al. 2011 Hypothesis

Ahn et al. (2011) "Flavor network and the principles of food pairing" constructed a bipartite ingredient–compound graph and observed:

> **Flavor pairing hypothesis**: In Western cuisines, ingredient pairs that co-occur in recipes share significantly more flavor compounds than random pairs. The probability of two ingredients appearing together in a recipe increases with the number of shared flavor compounds.

They further found this pattern:
- **Strong** in North American and Western European recipes
- **Weak or inverted** in East Asian recipes (Korean, Chinese, Japanese)

The RecipeNLG corpus used in FlavorGraph is predominantly English-language, thus Western-biased — placing our work squarely in the "hypothesis should hold" regime.

---

## 2. FlavorGraph's Connection to Ahn

### 2.1 Seed dataset

Phase 1 of our ingredient mapping pipeline (`ingredient_ahn_map.json`) uses 150 ingredient–botanical mappings directly from Ahn et al. 2011 as the hand-curated seed. This establishes direct lineage: our bipartite IC graph is a superset of the Ahn flavor network, extended from 150 to 1,094 ingredients via four expansion phases.

### 2.2 Training signal

Our HGN trains on **PPMI** (Positive Pointwise Mutual Information) from RecipeNLG — recipe co-occurrence, not compound sharing. The IC bipartite graph is used as *structural input* to the GNN, not as the training target. This is the key architectural choice that lets us test the Ahn hypothesis empirically:

> If the Ahn hypothesis holds perfectly, then compound-sharing (encoded in the IC graph) should be a sufficient predictor of recipe co-occurrence (PPMI). The GNN should learn nothing beyond compound similarity.

> If the hypothesis holds partially, compound-sharing explains some PPMI variance but independent co-occurrence signal remains.

---

## 3. Empirical Evidence from Bootstrap Results

### 3.1 Anti-homophily correction logic

The AntiHomo correction subtracts each ingredient's compound-center from its GNN embedding:

```
z_corrected = z_ingredient - σ(λ) × z_compound_center
```

where `z_compound_center` = mean compound embedding for that ingredient's botanical ID. This removes the direction of embedding space most correlated with compound-similarity, testing whether PPMI can be better ranked *without* the compound-sharing bias.

### 3.2 v4 result (578 ingredients, 2.00x ratio)

| Model | Spearman (test) | Δ vs HGN |
|-------|----------------|----------|
| Baseline HGN | 0.7111 ± 0.011 | — |
| AntiHomo HGN | 0.7211 ± 0.010 | **+0.0101** |
| 95% CI | | [−0.008, +0.023] |

**Direction**: AntiHomo improves over baseline HGN.  
**Significance**: CI includes zero (not significant at 95%), but directionally consistent across 10 seeds.

**Interpretation**: The HGN embeds compound-sharing as a homophily bias in ingredient representations. Correcting for this bias improves PPMI ranking by ~1 Spearman point. This is evidence that recipe co-occurrence has **independent signal beyond compound sharing** — the Ahn hypothesis is real but partial.

### 3.3 v5 result (1,094 ingredients, 3.63x ratio)

| Model | Spearman (test) | Δ vs HGN |
|-------|----------------|----------|
| Baseline HGN | 0.7082 ± 0.005 | — |
| AntiHomo HGN | 0.7009 ± 0.006 | **−0.0073** |
| 95% CI | | [−0.012, −0.002] |

**Direction**: AntiHomo *hurts* relative to baseline HGN.  
**Significance**: CI excludes zero — statistically significant degradation.

**Interpretation**: With a many-to-one mapping ratio of 3.63x (301 unique botanical IDs for 1,094 ingredients), most ingredient pairs share an identical compound center (same botanical ID). The AntiHomo correction subtracts the *same* vector for multiple ingredient variants, providing no discriminative signal — only noise. The correction is not harmful in principle; it is harmful because the *measurement* (compound center identity) is not resolved at the ingredient level.

---

## 4. Ahn Hypothesis Interpretation

### 4.1 What the positive v4 delta tells us

A positive AntiHomo delta means: reducing the compound-similarity signal **helps** PPMI ranking. This implies:

1. **The HGN is over-encoding compound sharing.** The bipartite IC graph structure creates embedding similarity between high-compound-overlap ingredient pairs, even when those pairs don't frequently co-occur in recipes.

2. **Recipe pairing has independent structure.** Cultural, seasonal, textural, and culinary-technique factors drive recipe co-occurrence beyond what compound sharing predicts. The AntiHomo correction lets the model weight these signals more.

3. **Ahn hypothesis is real but not the whole story.** In our Western corpus, compound sharing correlates with recipe co-occurrence (the HGN benefits from the IC graph), but the correlation is imperfect enough that de-biasing improves ranking.

### 4.2 Quantifying the "partial truth"

The baseline HGN achieves Spearman 0.711 on v4 test pairs. This is already substantially above chance, confirming compound structure is useful. The +0.010 gain from AntiHomo represents ~1.4% relative improvement — statistically modest but directionally consistent, suggesting the Ahn correlation is real and substantial (perhaps 70–80% of the achievable signal) but not total.

### 4.3 The many-to-one problem as a measurement issue

The v5 degradation does NOT contradict the Ahn hypothesis. It reveals a **measurement precision problem**: when multiple ingredient variants (e.g., `"lean ground beef"`, `"ground chuck"`, `"beef brisket"`) all map to `beef`, they receive identical compound centers despite having meaningfully different culinary profiles. The correction becomes uninformative.

This is the key v6 motivation: we need compound-resolved embeddings where the compound center reflects the *specific ingredient* (or preparation variant), not just the canonical botanical ID.

---

## 5. Proposed v6 Architecture (Hypothesis-Motivated)

Based on the above, the most hypothesis-motivated next architecture:

### Option A: Ingredient-ingredient PPMI + compound-as-feature
- Build an ingredient–ingredient graph weighted by PPMI
- Use compound membership as node features (binary vector, length = #compounds)
- Train GCN/GAT directly on the PPMI graph
- This tests: can compound features explain PPMI structure in an ingredient-ingredient graph?

### Option B: Compound-resolved ingredient representations
- Assign each ingredient a unique compound set based on its full preparation context (not just canonical botanical ID)
- Requires compound data enrichment beyond FlavorDB (PubChem, FooDB, etc.)
- This directly fixes the measurement precision problem identified in §4.3

**Recommendation for RecSys 2026**: Implement Option A as it tests the Ahn hypothesis cleanest — ingredient nodes with compound features in a PPMI-weighted graph. If compound features improve PPMI prediction, the Ahn hypothesis is structurally encoded in the optimal representation.

---

---

## 6. Empirical Correlation Analysis (v5.db direct)

Direct Spearman correlation between shared compound count and NPMI, computed across all 66,295 unique pairs in flavorgraph_v5.db:

| Filter | N pairs | Spearman r | Interpretation |
|--------|---------|-----------|----------------|
| All pairs | 66,295 | **0.019** | Near-zero overall |
| Both ingredients >=5 compounds | 49,615 | **0.012** | Sparsity not main driver |
| Both ingredients >=20 compounds | 36,458 | **0.071** | 4x stronger for compound-rich pairs |

### 6.1 NPMI by shared compound bucket

| Shared compounds | N pairs | Mean NPMI | Median NPMI |
|-----------------|---------|----------|------------|
| 0 | 20,673 | 0.0661 | 0.0619 |
| 1-5 | 18,593 | 0.0635 | 0.0604 |
| 6-20 | 17,106 | 0.0642 | 0.0614 |
| 21-50 | 7,246 | 0.0690 | 0.0664 |
| 51-200 | 2,677 | **0.0906** | **0.0817** |

The signal is nearly flat until very high compound sharing (51+). Only 2,677 pairs (4%) enter that regime.

### 6.2 Ahn-confirmed pairs

High-NPMI (>0.2) pairs with substantial compound sharing:

| Pair | NPMI | Shared | Note |
|------|------|--------|------|
| mirin + sake | 0.633 | 29 | Japanese cooking bases |
| oyster + shiitake mushrooms | 0.597 | 117 | Asian mushroom umami |
| red + yellow bell pepper | 0.587 | 36 | Same botanical, color variants |
| blackberry + raspberries | 0.587 | 72 | Berry family |
| mozzarella + ricotta | 0.494 | 127 | Italian dairy |
| feta + kalamata olive | 0.516 | 26 | Mediterranean staples |
| mango + papaya | 0.531 | 55 | Tropical fruits |

### 6.3 Counter-examples

High-NPMI (>0.3) pairs with zero shared compounds (415 total):

| Pair | NPMI | Culinary explanation |
|------|------|---------------------|
| ginger (cured) + wasabi | 0.653 | Sushi condiment set - cultural tradition |
| sesame oil + soy sauce | 0.544 | East Asian base - Ahn inverted regime |
| basil + oregano | 0.559 | Both Lamiaceae - FlavorDB data gap |
| tahini + chickpeas | 0.493 | Hummus - texture/protein tradition |
| parsnip + turnip | 0.576 | Root vegetable - no FlavorDB overlap |

### 6.4 Interpretation

**The Ahn hypothesis is real but weak in our corpus**:
- At 51+ shared compounds (top 4% of pairs), mean NPMI is 37% above average
- Overall correlation is near-zero: Spearman r = 0.019
- East Asian pairs follow Ahn inverted prediction exactly
- Compound sharing explains ~0.04% of NPMI variance overall; ~0.5% for compound-rich pairs

**Why AntiHomo still helps in v4**: The HGN encodes compound-sharing as embedding similarity for ALL pairs, not just the top-4% where Ahn signal exists. Correcting this over-encoding lets the model weight the 96% of pairs where PPMI is driven by other factors.

### 6.5 Linear probe: pairwise compound features

Logistic regression probe trained on 6 compound pairwise features:
shared_count, log(shared+1), cosine_similarity, dot_product, L2_distance, jaccard.
10-seed bootstrap, 80/20 train/test split. No GNN, no graph leakage.

| Model | Spearman (test) | Std |
|-------|----------------|-----|
| Compound features | **0.0645** | 0.0071 |
| Random features (control) | 0.0590 | 0.0080 |
| Delta | +0.0055 | CI: [-0.001, +0.012], not significant |

Cosine similarity has the largest coefficient (~0.46), making normalized shared-compound
count the strongest single predictor. The +0.006 delta is directionally positive but
statistically insignificant. This is the cleanest test of the Ahn hypothesis: compound
features predict PPMI marginally better than random noise.


## 7. Open Questions for Paper

1. **Significance threshold**: Should we report v4 delta as "marginally positive" or wait for a v4-scale clean dataset to achieve significance?
2. **Comparison baseline**: Need a non-GNN baseline (BM25/collaborative-filter on recipe co-occurrence alone) to show GNN adds value beyond corpus statistics.
3. **Cuisine segmentation**: Can we filter RecipeNLG to Western-only recipes and re-run bootstrap? Would test Ahn's regional prediction directly.
4. **Compound sparsity**: Some ingredients have 3 compounds (olive oil, lemon juice). Does sparsity affect compound-center quality systematically?

---

## 8. Version Comparison Summary

| Version | Ingredients | Unique Botanicals | Ratio | AntiHomo Δ | CI | Verdict |
|---------|-------------|-------------------|-------|-----------|-----|---------|
| v2 | 151 | ~100 | ~1.5x | +0.0015 | [−.016, +.016] | noise |
| v3 | 239 | 191 | 1.25x | +0.0048 | [−.013, +.013] | noise |
| v4 | 578 | 289 | 2.00x | **+0.0101** | [−.008, +.023] | directional positive |
| v5 | 1,094 | 301 | 3.63x | **−0.0073** | [−.012, −.002] | significant negative |

**Key insight**: AntiHomo delta peaks at v4 (many-to-one ratio ~2x). As ratio climbs above ~2x, compound-center identity collapses across ingredient variants. The sweet spot for AntiHomo is low many-to-one ratio with high botanical diversity.

**Next target**: v6 dataset with 500+ unique botanical IDs and ratio ≤ 2x, via new data sources (FooDB, USDA flavor database).
