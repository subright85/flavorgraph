"""
32_expand_mapping.py — Expand common-name -> botanical-ID mapping via phased rules

Phase 1: ingredient_ahn_map.json (150 hand-curated)
Phase 2: exact name match (RAW_recipes name verbatim in ingr_info.tsv)
Phase 3: space->underscore normalization match
Phase 3.5: rule-based prep prefix/suffix stripping + depluralization
Phase 4: LLM batch matching (claude-haiku-4-5) for top unmatched by frequency

Output:
  data/ingredient_expanded_map.json  -- all accepted mappings
  data/ingredient_llm_review.json    -- low-confidence LLM results for manual review
"""

import csv
import json
import re
import time
from collections import defaultdict
from pathlib import Path

import anthropic

ROOT = Path(__file__).parent.parent.parent
DATA = ROOT / "data"

LLM_TOP_N       = 2000   # top N unmatched ingredients to send to LLM
BATCH_SIZE      = 40     # ingredients per LLM call
AUTO_THRESHOLD  = 0.85   # confidence >= this -> auto-accept
REVIEW_THRESHOLD = 0.5   # confidence < this -> discard; between -> review file

# -- Load base data ------------------------------------------------------------
print("Loading ingr_info.tsv...")
ingr_id2name = {}
ingr_name2id = {}
ingr_id2cat  = {}
with open(DATA / "ingr_info.tsv") as f:
    next(f)
    for line in f:
        parts = line.strip().split("\t")
        iid   = int(parts[0])
        name  = parts[1]
        cat   = parts[2] if len(parts) > 2 else ""
        ingr_id2name[iid]  = name
        ingr_name2id[name] = iid
        ingr_id2cat[iid]   = cat

print(f"  {len(ingr_name2id)} botanical names loaded")

print("Loading ingr_comp.tsv (compound coverage)...")
has_comp = set()
with open(DATA / "ingr_comp.tsv") as f:
    next(f)
    for line in f:
        has_comp.add(int(line.strip().split("\t")[0]))
print(f"  {len(has_comp)} botanical IDs have compound data")

print("Scanning RAW_recipes.csv for ingredient frequencies...")
counts = defaultdict(int)
with open(DATA / "RAW_recipes.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        for ing in re.findall(r"'([^']+)'", row.get("ingredients", "")):
            counts[ing] += 1
print(f"  {len(counts)} unique ingredients found")

# -- Phase 1: ahn_map ---------------------------------------------------------
print("\nPhase 1: ahn_map...")
with open(DATA / "ingredient_ahn_map.json") as f:
    ahn_map = json.load(f)

common2id = {}  # common_name -> botanical_id
sources   = {}  # common_name -> source label

for common_name, info in ahn_map.items():
    ahn_id = info.get("ahn_id")
    if ahn_id is None:
        continue
    bid = int(ahn_id)
    if bid in has_comp:
        common2id[common_name] = bid
        sources[common_name] = "ahn_map"

print(f"  Phase 1: {len(common2id)} mapped")

# -- Phase 2: exact name match ------------------------------------------------
print("Phase 2: exact name match...")
for name in counts:
    if name in common2id:
        continue
    if name in ingr_name2id:
        bid = ingr_name2id[name]
        if bid in has_comp:
            common2id[name] = bid
            sources[name] = "exact"

print(f"  After Phase 2: {len(common2id)} mapped")

# -- Phase 3: space->underscore normalization ----------------------------------
print("Phase 3: normalization match...")
for common in list(counts.keys()):
    if common in common2id:
        continue
    norm = common.lower().strip().replace(" ", "_").replace("-", "_")
    if norm in ingr_name2id:
        bid = ingr_name2id[norm]
        if bid in has_comp:
            common2id[common] = bid
            sources[common] = "normalized"

print(f"  After Phase 3: {len(common2id)} mapped")

# -- Phase 3.5: rule-based prep prefix/suffix stripping + depluralization -----
print("Phase 3.5: rule-based stripping...")

PREP_PREFIXES = [
    "fresh", "dried", "ground", "minced", "chopped", "diced", "sliced",
    "shredded", "grated", "whole", "extra", "pure", "raw", "frozen",
    "canned", "cooked", "crushed", "packed", "unsalted", "granulated",
    "powdered", "smoked", "roasted", "toasted", "pickled", "salted",
]
PREP_SUFFIXES = [
    "cloves", "clove", "leaves", "leaf", "seeds", "seed",
    "pods", "pod", "stalks", "stalk", "flakes", "extract",
]


def lookup_name(name):
    if name in ingr_name2id:
        bid = ingr_name2id[name]
        if bid in has_comp:
            return bid
    norm = name.replace(" ", "_")
    if norm in ingr_name2id:
        bid = ingr_name2id[norm]
        if bid in has_comp:
            return bid
    return None


for common in list(counts.keys()):
    if common in common2id:
        continue
    lower = common.lower().strip()
    matched = False

    for p in PREP_PREFIXES:
        if lower.startswith(p + " "):
            base = lower[len(p) + 1:].strip()
            bid = lookup_name(base)
            if bid:
                common2id[common] = bid
                sources[common] = f"rule:prefix:{p}"
                matched = True
                break

    if matched:
        continue

    for s in PREP_SUFFIXES:
        if lower.endswith(" " + s):
            base = lower[:-(len(s) + 1)].strip()
            bid = lookup_name(base)
            if bid:
                common2id[common] = bid
                sources[common] = f"rule:suffix:{s}"
                matched = True
                break

    if matched:
        continue

    if lower.endswith("s") and len(lower) > 3:
        base = lower[:-1]
        bid = lookup_name(base)
        if bid:
            common2id[common] = bid
            sources[common] = "rule:deplural"

print(f"  After Phase 3.5: {len(common2id)} mapped")

# -- Phase 4: LLM batch matching ----------------------------------------------
print(f"\nPhase 4: LLM batch matching (top {LLM_TOP_N} unmatched)...")

unmapped = [(name, cnt) for name, cnt in counts.items() if name not in common2id]
unmapped.sort(key=lambda x: -x[1])
unmapped_top = unmapped[:LLM_TOP_N]
print(f"  {len(unmapped)} total unmatched, processing top {len(unmapped_top)}")

botanical_list = sorted(ingr_name2id.keys())
botanical_str  = "\n".join(botanical_list)

client = anthropic.Anthropic()

llm_results = {}
review_items = []


def run_batch(batch_names):
    names_str = "\n".join(f"- {n}" for n in batch_names)
    prompt = f"""You are matching recipe ingredient names (common English cooking terms) to a controlled botanical/food ingredient vocabulary.

BOTANICAL VOCABULARY (one per line, use underscore notation):
{botanical_str}

RECIPE INGREDIENTS TO MATCH:
{names_str}

For each recipe ingredient, find the BEST matching botanical name from the vocabulary above.
Rules:
- Match semantically (e.g., "garlic cloves" -> "garlic", "all-purpose flour" -> "wheat_flour")
- If a variant/preparation of an ingredient (e.g., "minced garlic", "garlic powder"), map to the base ingredient
- If no reasonable match exists, output null
- Confidence: 1.0 = exact/obvious match, 0.8 = clear semantic match, 0.6 = plausible but uncertain, below 0.5 = skip

Respond with ONLY a JSON array, one object per ingredient:
[
  {{"input": "garlic cloves", "botanical": "garlic", "confidence": 0.95, "reason": "garlic cloves is a form of garlic"}},
  {{"input": "mystery ingredient", "botanical": null, "confidence": 0.0, "reason": "no match found"}}
]"""

    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    text = resp.content[0].text.strip()
    m = re.search(r'\[.*\]', text, re.DOTALL)
    if not m:
        return []
    return json.loads(m.group())


batch_names = [n for n, _ in unmapped_top]
n_batches = (len(batch_names) + BATCH_SIZE - 1) // BATCH_SIZE
print(f"  Running {n_batches} LLM batches...")

for i in range(n_batches):
    batch = batch_names[i * BATCH_SIZE:(i + 1) * BATCH_SIZE]
    if i % 5 == 0:
        print(f"  Batch {i+1}/{n_batches}...")
    try:
        results = run_batch(batch)
        for item in results:
            inp    = item.get("input", "")
            bot    = item.get("botanical")
            conf   = float(item.get("confidence", 0))
            reason = item.get("reason", "")

            if not bot or conf < REVIEW_THRESHOLD:
                continue

            if bot not in ingr_name2id:
                bot_norm = bot.replace(" ", "_")
                if bot_norm in ingr_name2id:
                    bot = bot_norm
                else:
                    continue

            bid = ingr_name2id[bot]
            if bid not in has_comp:
                continue

            llm_results[inp] = {
                "botanical": bot,
                "botanical_id": bid,
                "confidence": conf,
                "reason": reason,
            }

            if conf >= AUTO_THRESHOLD:
                if inp not in common2id:
                    common2id[inp] = bid
                    sources[inp] = f"llm:{conf:.2f}"
            else:
                review_items.append({
                    "common_name": inp,
                    "botanical": bot,
                    "botanical_id": bid,
                    "confidence": conf,
                    "reason": reason,
                    "frequency": counts.get(inp, 0),
                })

    except Exception as e:
        print(f"  Batch {i+1} error: {e}")
        time.sleep(2)

print(f"\nAfter Phase 4:")
print(f"  Auto-accepted (confidence >= {AUTO_THRESHOLD}): {sum(1 for v in sources.values() if v.startswith('llm'))}")
print(f"  Needs review: {len(review_items)}")
print(f"  Total mapped: {len(common2id)}")

# -- Save outputs -------------------------------------------------------------
expanded_map = {}
for common_name, bid in common2id.items():
    expanded_map[common_name] = {
        "botanical_id": bid,
        "botanical_name": ingr_id2name.get(bid, ""),
        "category": ingr_id2cat.get(bid, ""),
        "source": sources.get(common_name, "unknown"),
        "frequency": counts.get(common_name, 0),
    }

expanded_map_sorted = dict(
    sorted(expanded_map.items(), key=lambda x: -x[1]["frequency"])
)

out_map    = DATA / "ingredient_expanded_map.json"
out_review = DATA / "ingredient_llm_review.json"

with open(out_map, "w") as f:
    json.dump(expanded_map_sorted, f, indent=2)

review_sorted = sorted(review_items, key=lambda x: -x["confidence"])
with open(out_review, "w") as f:
    json.dump(review_sorted, f, indent=2)

# -- Summary ------------------------------------------------------------------
source_counts = defaultdict(int)
for s in sources.values():
    key = s.split(":")[0]
    source_counts[key] += 1

print(f"""
=== Mapping Summary ===
  ahn_map:    {source_counts['ahn_map']}
  exact:      {source_counts['exact']}
  normalized: {source_counts['normalized']}
  rule:       {source_counts['rule']}
  llm:        {source_counts['llm']}
  ─────────────────────
  Total auto: {len(common2id)}
  For review: {len(review_items)}

  Saved -> {out_map}
  Review -> {out_review}
""")
