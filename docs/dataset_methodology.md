# FlavorGraph Dataset Construction Methodology

**Version**: v5 (current main dataset)  
**Generated**: 2026-05-10  
**Database**: `flavorgraph_v5.db`

---

## 1. Data Sources

| Source | Description | Records |
|--------|-------------|---------|
| **RecipeNLG** | Large-scale recipe corpus | 231,637 recipes |
| **FlavorDB** | Ingredient–flavor compound database | 1,525 botanical entries, 1,107 compounds |

**RecipeNLG** provides the co-occurrence signal: which ingredients appear together in real recipes. We extract ingredient lists as raw text strings (e.g., `"2 cups all-purpose flour"`, `"3 cloves garlic"`), tokenizing via the bracketed-list format in `RAW_recipes.csv`.

**FlavorDB** provides the structural signal: which flavor compounds each botanical ingredient contains. Each botanical entry links to a set of flavor compounds (e.g., garlic → 279 compounds including allicin, diallyl sulfide). Of 1,525 botanical entries, **1,525 have compound data** available.

---

## 2. Ingredient–Botanical Mapping Pipeline

A key challenge is the vocabulary mismatch: RecipeNLG uses 14,915 unique common-language ingredient strings (e.g., `"fresh ground black pepper"`, `"boneless skinless chicken breast halves"`) while FlavorDB uses 1,525 normalized botanical names (e.g., `"black_pepper"`, `"chicken"`). We bridge this gap through a four-phase mapping pipeline.

### Phase 1: Hand-Curated Seed Map

We start from `ingredient_ahn_map.json`, a hand-curated mapping of 150 common cooking ingredients to their botanical FlavorDB identifiers, sourced from prior work (Ahn et al., 2011). Only entries with compound coverage in FlavorDB are retained.

**Output**: 150 mappings

### Phase 2: Exact Name Match

For each unmatched recipe ingredient string, we attempt exact string match against the FlavorDB botanical vocabulary.

**Output**: +135 mappings (cumulative: 285)

### Phase 3: Normalization Match

Recipe ingredient strings often use spaces where FlavorDB uses underscores (e.g., `"black pepper"` → `"black_pepper"`). We apply space→underscore normalization with case folding and attempt a second match.

**Output**: +118 mappings (cumulative: 403)

### Phase 3.5: Rule-Based Preparation Stripping

Recipe strings frequently include preparation descriptors that do not affect botanical identity. We strip:

**Prep prefixes** (26 patterns): `fresh`, `dried`, `ground`, `minced`, `chopped`, `diced`, `sliced`, `shredded`, `grated`, `whole`, `extra`, `pure`, `raw`, `frozen`, `canned`, `cooked`, `crushed`, `packed`, `unsalted`, `granulated`, `powdered`, `smoked`, `roasted`, `toasted`, `marinated`, `salted`

**Prep suffixes** (12 patterns): `cloves`, `clove`, `leaves`, `leaf`, `seeds`, `seed`, `pods`, `pod`, `stalks`, `stalk`, `flakes`, `extract`

**Depluralization**: terminal `s` removal for strings longer than 3 characters

After each stripping operation, the result is re-matched against the botanical vocabulary (exact, then underscore-normalized).

**Output**: +503 mappings (cumulative: 906)

### Phase 4.manual: Knowledge-Based Batch Review

The top 600 remaining unmatched ingredients (by recipe frequency) were split into 12 batches of 50 and reviewed against the botanical vocabulary using culinary and food-science knowledge. Mappings were applied where a clear botanical identity could be established:

- Ingredient variants → base botanical (e.g., `"lean ground beef"`, `"ground chuck"`, `"beef brisket"` → `beef`)
- Preparation variants → base ingredient (e.g., `"dark sesame oil"` → `sesame_oil`)
- Semantic equivalents (e.g., `"ricotta cheese"` → `cottage_cheese` as closest whey-based dairy)
- Compound dishes → primary botanical (e.g., `"tabasco sauce"` → `tabasco_pepper`)

Ambiguous or non-botanical ingredients (salt, water, sugar, baking soda, brand-name products) were intentionally excluded.

**Output**: +541 mappings (cumulative: 1,447)

---

## 3. Database Construction

### 3.1 Co-occurrence Counting

For each recipe in RecipeNLG, we extract ingredient mentions and normalize using the mapping above. For each pair (a, b) of co-occurring mapped ingredients, we count the number of recipes in which they both appear.

**Minimum co-occurrence threshold**: 10 recipes (pairs below this threshold are discarded as statistically unreliable).

### 3.2 PPMI Computation

For each ingredient pair (a, b) surviving the threshold, we compute Positive Pointwise Mutual Information:

```
PMI(a,b)  = log[ P(a,b) / (P(a) x P(b)) ]
NPMI(a,b) = PMI(a,b) / (-log P(a,b))       in [-1, +1]
PPMI(a,b) = max(0, NPMI(a,b))              in [0, +1]
```

where P(a,b) = co-occurrence count / N, P(a) = ingredient frequency / N, N = total recipes.

PPMI serves as the ground-truth affinity score for ingredient pairing evaluation.

### 3.3 Ingredient–Compound Links

Each mapped ingredient's botanical ID is resolved against FlavorDB's `ingr_comp.tsv` to retrieve its set of flavor compounds. The bipartite ingredient–compound (IC) graph is constructed from these links.

### 3.4 Combined Score

The stored `combined_score` is a weighted blend:
```
combined_score = 0.7 x PPMI + 0.3 x (shared_compound_count / 50)
```
This was retained for compatibility with prior versions but is not used in the HGN experiments (which use PPMI directly).

---

## 4. Dataset Statistics

### 4.1 Mapping Pipeline Summary

| Phase | Method | Mappings Added | Cumulative |
|-------|--------|---------------|------------|
| Phase 1 | Hand-curated (Ahn et al.) | 150 | 150 |
| Phase 2 | Exact string match | 135 | 285 |
| Phase 3 | Normalization (space→underscore) | 118 | 403 |
| Phase 3.5 | Rule-based prep stripping | 503 | 906 |
| Phase 4.manual | Knowledge-based batch review | 541 | **1,447** |

### 4.2 Graph Statistics (flavorgraph_v5.db)

| Metric | Value |
|--------|-------|
| Total mapped ingredient strings | 1,447 |
| Active ingredients (>=10 co-occurrence pairs) | **1,094** |
| Unique botanical IDs covered | 301 |
| Average common names per botanical ID | 3.63x |
| Flavor compounds indexed | 983 |
| Ingredient–compound (IC) links | 66,169 |
| Average compounds per ingredient | 60.5 |
| Unique co-occurrence pairs (PPMI >= 0, count >= 10) | **66,295** |
| Average shared compounds per pair | 10.17 |
| Maximum shared compounds per pair | 199 |
| Total recipes used | 231,637 |

### 4.3 Version Comparison

| Version | Ingredients | Unique Botanicals | Ratio | Pairs | AntiHomo Delta | 95% CI |
|---------|-------------|-------------------|-------|-------|----------------|--------|
| v2 | 151 | ~100 | ~1.5x | 11,269 | +0.0015 | [-0.016, +0.016] |
| v3 | 239 | 191 | 1.25x | 9,305 | +0.0048 | [-0.013, +0.013] |
| v4 | 578 | 289 | 2.00x | 21,390 | **+0.0101** | [-0.008, +0.023] |
| v5 | 1,094 | 301 | 3.63x | 66,295 | -0.0073 | [-0.012, -0.002] |

---

## 5. Key Observations

### 5.1 Mapping Quality vs. Quantity

The anti-homophily correction (AntiHomo) depends on the precision of the compound-center representation. Each ingredient's compound center is derived from its botanical ID's compound set. When multiple common-name ingredients map to the same botanical ID (high many-to-one ratio), they share identical compound centers, reducing the correction's discriminative power.

**v4 to v5 transition**: Adding 516 new active ingredients via Phase 4.manual expanded ingredient coverage by 89% but added only 12 new unique botanical IDs (289 to 301). The many-to-one ratio increased from 2.00x to 3.63x. As a result, AntiHomo delta flipped from +0.0101 (v4) to -0.0073 (v5): the correction became harmful.

**Implication**: Naive expansion of common-name coverage without discovering new botanical entities does not improve—and can degrade—the anti-homophily signal. Future work should prioritize expanding *unique botanical coverage* over synonym coverage.

### 5.2 Scale of Co-occurrence Pairs

The pair count grew 3.1x from v4 to v5 (21,390 to 66,295) due to the larger ingredient set enabling more pair combinations. This demonstrates that even synonymous expansions substantially increase the training signal for co-occurrence modeling.

### 5.3 Excluded Ingredient Categories

The following ingredient categories were deliberately excluded as they lack meaningful botanical identity in FlavorDB:

- **Pure chemicals**: salt, sugar, water, baking soda, baking powder
- **Brand names**: Bisquick, Cool Whip, Velveeta, Crisco, Splenda
- **Compound preparations with no dominant botanical**: Italian seasoning (blend), poultry seasoning (blend)
- **Cooking process artifacts**: cooking spray, nonstick spray

---

## 6. Reproducibility

All pipeline scripts are under `scripts/gnn/`:

| Script | Purpose |
|--------|---------|
| `32_expand_mapping.py` | Phases 1 through 3.5 mapping pipeline |
| `33_build_v4.py` | Database construction (v5 uses identical schema) |
| `34_v4_bootstrap.py` | Bootstrap CI for v4 |
| `35_v5_bootstrap.py` | Bootstrap CI for v5 |

Mapping data: `data/ingredient_expanded_map.json` (1,447 entries, JSON, sorted by recipe frequency)
Database: `flavorgraph_v5.db` (SQLite3)

**Random seeds for bootstrap**: [42, 123, 2024, 7, 99, 314, 777, 1001, 2000, 9999]
**Bootstrap evaluation metric**: Spearman correlation between model scores and PPMI on held-out 20% test pairs
