"""
Higher-order pairing analysis — beyond pairwise PMI.

성철 question: "페어로는 설명이 안되는 코릴레이션이 있을거 같은데"

1. Triplet PMI: P(A,B,C) / (P(A)*P(B)*P(C)) — 3자 공출현 강도
2. Context-conditioned pairing: given anchor C, does (A,B) PMI change?
3. GNN embedding captures triplet structure?
   — Is the GNN score on (A,B) predicted by context of C?
4. Complement vs. similar: pairs with low compound overlap but high GNN score
   (flavor contrast pairing — East Asian pattern)
5. Cuisine-stratified: filter by recipe title keywords (italian, chinese, thai, french)
   and compare PMI ↔ compound_sim slope
"""

import csv, re, os, sys, sqlite3, math, random
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

DATA_DIR = os.path.join(os.path.dirname(__file__), '../../data')
RECIPES_PATH = os.path.join(DATA_DIR, 'RAW_recipes.csv')
DB_PATH = os.path.join(os.path.dirname(__file__), '../../flavorgraph_v2.db')
GRAPH_PATH = os.path.join(os.path.dirname(__file__), 'graph.pt')


def parse_ingredients(raw):
    return re.findall(r"'([^']+)'", raw)


def load_recipes_and_vocab(min_count=100):
    ingredient_counter = Counter()
    recipe_data = []
    with open(RECIPES_PATH) as f:
        for row in csv.DictReader(f):
            ings = {i.lower().strip() for i in parse_ingredients(row.get('ingredients', ''))}
            tags = row.get('tags', '').lower()
            name = row.get('name', '').lower()
            if ings:
                recipe_data.append({'ings': ings, 'tags': tags, 'name': name})
                ingredient_counter.update(ings)

    vocab = [ing for ing, cnt in ingredient_counter.most_common() if cnt >= min_count]
    vocab_set = set(vocab)
    ing_to_idx = {ing: i for i, ing in enumerate(vocab)}
    total = len(recipe_data)
    single_count = {ing: ingredient_counter[ing] for ing in vocab}
    return recipe_data, vocab_set, ing_to_idx, single_count, total


# ── 1. Triplet PMI ───────────────────────────────────────────────────────────

def triplet_analysis(recipe_data, vocab_set, ing_to_idx, single_count, total):
    print("\n=== 1. Triplet PMI Analysis ===")
    print("  Pointwise Mutual Information of 3-ingredient combos\n")

    triple_count = defaultdict(int)
    pair_count = defaultdict(int)

    for recipe in recipe_data:
        ings = sorted(vocab_set & recipe['ings'])
        for i in range(len(ings)):
            for j in range(i+1, len(ings)):
                pair_count[(ings[i], ings[j])] += 1
                for k in range(j+1, len(ings)):
                    triple_count[(ings[i], ings[j], ings[k])] += 1

    print(f"  Total unique triplets observed: {len(triple_count):,}")

    # Triplet PMI: log P(A,B,C) / (P(A)*P(B)*P(C))
    triplet_pmis = []
    for (a, b, c), cnt in triple_count.items():
        if cnt < 50:
            continue
        pmi3 = math.log((cnt/total) / ((single_count[a]/total) *
                                        (single_count[b]/total) *
                                        (single_count[c]/total)))
        pmi_ab = math.log((pair_count[(a,b)]/total) / ((single_count[a]/total)*(single_count[b]/total))) if pair_count[(a,b)] > 0 else 0
        pmi_ac = math.log((pair_count[(a,c)]/total) / ((single_count[a]/total)*(single_count[c]/total))) if pair_count[(a,c)] > 0 else 0
        pmi_bc = math.log((pair_count[(b,c)]/total) / ((single_count[b]/total)*(single_count[c]/total))) if pair_count[(b,c)] > 0 else 0
        avg_pair_pmi = (pmi_ab + pmi_ac + pmi_bc) / 3
        # Synergy: how much triplet exceeds sum of pair PMIs?
        synergy = pmi3 - avg_pair_pmi
        triplet_pmis.append((a, b, c, cnt, pmi3, avg_pair_pmi, synergy))

    triplet_pmis.sort(key=lambda x: x[6], reverse=True)  # sort by synergy

    print(f"  Triplets with count≥50: {len(triplet_pmis)}\n")
    print(f"  Top 10 synergistic triplets (triplet PMI >> avg pair PMI):")
    print(f"  {'ingredients':<40} {'count':>6} {'pmi3':>7} {'avg_pair':>9} {'synergy':>8}")
    print("  " + "-"*75)
    for a, b, c, cnt, pmi3, avg_pair, syn in triplet_pmis[:10]:
        label = f"{a} + {b} + {c}"
        print(f"  {label:<40} {cnt:>6} {pmi3:>7.3f} {avg_pair:>9.3f} {syn:>8.3f}")

    print(f"\n  Bottom 10 (pairs suggest pairing, but triplet doesn't work):")
    print(f"  {'ingredients':<40} {'count':>6} {'pmi3':>7} {'avg_pair':>9} {'synergy':>8}")
    print("  " + "-"*75)
    for a, b, c, cnt, pmi3, avg_pair, syn in triplet_pmis[-10:]:
        label = f"{a} + {b} + {c}"
        print(f"  {label:<40} {cnt:>6} {pmi3:>7.3f} {avg_pair:>9.3f} {syn:>8.3f}")

    return triple_count, pair_count, triplet_pmis


# ── 2. Complement pairing — high GNN score, low compound overlap ─────────────

def complement_analysis():
    print("\n=== 2. Complement Pairing Analysis ===")
    print("  High GNN score + LOW compound overlap = flavor contrast pairing\n")

    import torch
    from scripts.gnn.model import FlavorHGN

    data = torch.load(GRAPH_PATH, weights_only=False)
    finetune_ckpt = os.path.join(os.path.dirname(__file__), 'finetune.pt')
    names = data['ingredient'].names
    name_to_idx = {n: i for i, n in enumerate(names)}

    n_ing, n_cmp = data['ingredient'].num_nodes, data['compound'].num_nodes
    model = FlavorHGN(n_ing, n_cmp, 128, 2, 4)
    model.load_state_dict(torch.load(finetune_ckpt, map_location='cpu'))
    model.train(False)

    with torch.no_grad():
        x_dict = model.encode(data)
        emb, W = x_dict['ingredient'], model.decoder.W

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT ing_a, ing_b, pmi_score, shared_count
        FROM pair_score WHERE ing_a < ing_b
    """)
    rows = cur.fetchall()
    conn.close()

    similar, complement = [], []
    for a, b, pmi, shared in rows:
        if a not in name_to_idx or b not in name_to_idx:
            continue
        gnn = (emb[name_to_idx[a]] * W * emb[name_to_idx[b]]).sum().item()
        entry = (a, b, pmi or 0, shared or 0, gnn)
        if shared >= 20:
            similar.append(entry)
        elif shared == 0:
            complement.append(entry)

    # Top GNN score from complement (low overlap) pairs
    complement.sort(key=lambda x: x[4], reverse=True)
    similar.sort(key=lambda x: x[4], reverse=True)

    print(f"  High compound overlap pairs (≥20 shared): {len(similar)}")
    print(f"  Zero compound overlap pairs: {len(complement)}")

    print(f"\n  Top 15 complement pairs (PMI=any, shared=0, high GNN):")
    print(f"  {'pair':<35} {'PMI':>7} {'shared':>7} {'GNN':>8}")
    print("  " + "-"*60)
    for a, b, pmi, shared, gnn in complement[:15]:
        label = f"{a} + {b}"
        print(f"  {label:<35} {pmi:>7.3f} {shared:>7} {gnn:>8.3f}")

    # Compound-similar pairs with low PMI — flavoring pairing candidates
    low_pmi_similar = [(a,b,pmi,sh,gnn) for a,b,pmi,sh,gnn in similar if pmi < 0.5]
    low_pmi_similar.sort(key=lambda x: x[3], reverse=True)
    print(f"\n  High compound overlap + low PMI (pairing candidates not in common recipes):")
    print(f"  {'pair':<35} {'PMI':>7} {'shared':>7} {'GNN':>8}")
    print("  " + "-"*60)
    for a, b, pmi, shared, gnn in low_pmi_similar[:15]:
        label = f"{a} + {b}"
        print(f"  {label:<35} {pmi:>7.3f} {shared:>7} {gnn:>8.3f}")


# ── 3. Cuisine-stratified analysis ────────────────────────────────────────────

CUISINE_KEYWORDS = {
    'italian':   ['italian', 'pasta', 'risotto', 'pizza', 'parmesan', 'marinara'],
    'french':    ['french', 'provencal', 'beurre', 'coq au vin', 'bouillabaisse'],
    'east_asian':['chinese', 'japanese', 'korean', 'thai', 'asian', 'stir fry', 'stir-fry', 'soy sauce'],
    'mexican':   ['mexican', 'tex mex', 'enchilada', 'taco', 'salsa', 'tamale'],
}


def cuisine_analysis(recipe_data, vocab_set, single_count, total):
    print("\n=== 3. Cuisine-Stratified PMI vs Compound Similarity ===")
    print("  Ahn et al. (2011): Western = compound sharing, East Asian = compound contrast\n")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT ing_a, ing_b, shared_count FROM pair_score WHERE ing_a < ing_b")
    shared_lookup = {(a, b): sh for a, b, sh in cur.fetchall()}
    conn.close()

    def spearman_corr(xs, ys):
        n = len(xs)
        if n < 10:
            return float('nan'), n
        def ranks(lst):
            r = [0]*n
            for rank, (i, _) in enumerate(sorted(enumerate(lst), key=lambda x: x[1])):
                r[i] = rank+1
            return r
        rx, ry = ranks(xs), ranks(ys)
        mx, my = sum(rx)/n, sum(ry)/n
        num = sum((rx[i]-mx)*(ry[i]-my) for i in range(n))
        den = (sum((rx[i]-mx)**2 for i in range(n))**0.5 *
               sum((ry[i]-my)**2 for i in range(n))**0.5)
        return round(num/(den+1e-9), 4), n

    cuisine_pair_counts = {c: defaultdict(int) for c in CUISINE_KEYWORDS}
    cuisine_recipe_counts = {c: 0 for c in CUISINE_KEYWORDS}

    for recipe in recipe_data:
        ings = sorted(vocab_set & recipe['ings'])
        text = recipe['tags'] + ' ' + recipe['name']
        matched = [c for c, kws in CUISINE_KEYWORDS.items() if any(k in text for k in kws)]
        for c in matched:
            cuisine_recipe_counts[c] += 1
            for i in range(len(ings)):
                for j in range(i+1, len(ings)):
                    cuisine_pair_counts[c][(ings[i], ings[j])] += 1

    print(f"  {'Cuisine':<12} {'Recipes':>8} {'Pairs':>8} {'Spearman(PMI,shared)':>22}")
    print("  " + "-"*55)
    for cuisine, kws in CUISINE_KEYWORDS.items():
        pc = cuisine_pair_counts[cuisine]
        rc = cuisine_recipe_counts[cuisine]
        if rc < 50:
            print(f"  {cuisine:<12} {rc:>8} {'(too few)':>8}")
            continue

        pmi_list, shared_list = [], []
        for (a, b), cnt in pc.items():
            if cnt < 5:
                continue
            shared = shared_lookup.get((a,b), shared_lookup.get((b,a), 0))
            if shared == 0:
                continue
            pmi_raw = math.log((cnt/rc) / ((single_count.get(a,1)/total) * (single_count.get(b,1)/total)))
            pmi_list.append(pmi_raw)
            shared_list.append(shared)

        sp, n = spearman_corr(pmi_list, shared_list)
        print(f"  {cuisine:<12} {rc:>8} {len(pmi_list):>8} {sp:>22.4f}")

    print("\n  Interpretation: positive = food pairing hypothesis (Western), negative = contrast pairing (East Asian)")


def run():
    print("Loading recipes...")
    recipe_data, vocab_set, ing_to_idx, single_count, total = load_recipes_and_vocab()
    print(f"  {total:,} recipes, {len(vocab_set)} ingredient vocab\n")

    triplet_analysis(recipe_data, vocab_set, ing_to_idx, single_count, total)
    complement_analysis()
    cuisine_analysis(recipe_data, vocab_set, single_count, total)


if __name__ == '__main__':
    run()
