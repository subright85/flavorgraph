#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("mint","strawberry","vanilla",
     "Mint, strawberry, and vanilla share linalool, furaneol, and 2-phenylethanol — a three-way compound overlap — while menthol's cooling amplifies strawberry's perceived sweetness and contrasts vanilla's warm-sweet register. Together the trio creates the most aromatic cool-sweet-floral dessert flavor combination in this set.",
     "Mint Strawberry Vanilla Pavlova",
     ["Bake a large meringue until crisp outside and marshmallow inside; cool completely.", "Whip cream with vanilla bean and a touch of mint extract; pile onto the meringue.", "Top with strawberries macerated in vanilla sugar and fresh mint; serve immediately."]),

    ("mint","tomato","truffle",
     "Mint and tomato share hexanal and furaneol while tomato and truffle share dimethyl sulfide and phenylacetaldehyde — double bridges through tomato — while mint's menthol provides the most refreshing aromatic contrast to truffle's dense earthiness. The trio creates an unexpectedly light truffle-tomato preparation.",
     "Mint Truffle Tomato Bruschetta",
     ["Simmer cherry tomatoes with truffle butter until jammy; season well and cool slightly.", "Spread generously on toasted sourdough with a handful of torn fresh mint.", "Shave fresh truffle over each piece; mint's cooling lifts the dense truffle-tomato combination."]),

    ("mint","tomato","vanilla",
     "Mint and tomato share hexanal and furaneol while tomato and vanilla share furaneol — the sweet-caramel compound — creating a triple-furaneol register where mint's cooling and vanilla's warmth provide contrasting registers above the shared sweet-savory base. The unusual trio creates a sophisticated slow-roasted tomato preparation.",
     "Mint Vanilla Roasted Tomatoes",
     ["Halve cherry tomatoes, place with a split vanilla bean and fresh mint bundles in a baking dish.", "Cover with olive oil; roast at 250°F for 90 minutes until jammy and concentrated.", "Serve over burrata; the vanilla-mint amplifies the tomato's natural furaneol sweetness."]),

    ("mint","truffle","vanilla",
     "Mint and vanilla share linalool and 2-phenylethanol while truffle and vanilla share vanillin — and mint and truffle share trace anisaldehyde — creating three separate compound bridges across the trio. Menthol's cooling provides the most dramatic aromatic contrast to truffle's dense earthiness and vanilla's warm-sweet register.",
     "Mint Truffle Vanilla Compound Butter",
     ["Beat softened butter with truffle paste, vanilla bean seeds, and finely chopped fresh mint.", "Add a pinch of flaky salt; mix until completely smooth and taste carefully.", "Roll into a log, refrigerate until firm, and slice over scrambled eggs or warm risotto."]),

    ("oyster","parmesan","rose",
     "Oyster and Parmesan share phenylacetaldehyde and dimethyl sulfide — the rosy-fermented and sulfurous compounds connecting marine brine and aged dairy — while rose's 2-phenylethanol reinforces the shared phenylacetaldehyde and amplifies the rosy register that bridges the luxury marine-dairy combination. The trio creates a refined baked oyster.",
     "Rose Parmesan Baked Oysters",
     ["Mix finely grated Parmesan with rose water, breadcrumbs, and a touch of butter.", "Top shucked oysters in their half-shells; broil 4 minutes until golden.", "Garnish with dried rose petals and serve with champagne; the rose lifts the Parmesan-oyster."]),

    ("oyster","parmesan","salmon",
     "Oyster, Parmesan, and salmon form a triple-dimethyl sulfide combination — all three share the sulfurous compound — creating a rich marine-dairy-fish preparation where each ingredient's sulfurous aromatic reinforces the others. Parmesan's glutamate umami amplifies both seafood proteins through the same savory-binding mechanism.",
     "Parmesan Oyster Salmon Pasta",
     ["Sear salmon until just done; set aside and flake. Sauté shallots in the same pan.", "Add shucked oysters to the pan; cook 2 minutes. Toss with pasta and cold Parmesan.", "Fold salmon in gently off heat; finish with lemon, pasta water, and more Parmesan."]),

    ("oyster","parmesan","strawberry",
     "Oyster and Parmesan share phenylacetaldehyde while Parmesan and strawberry share furaneol — two compound bridges through Parmesan — while strawberry's furaneol sweetness provides the sweet-caramel contrast to oyster's marine brine. The trio creates a bold avant-garde preparation where aged cheese bridges fruit and shellfish.",
     "Strawberry Parmesan Oyster Platter",
     ["Shave aged Parmesan into irregular pieces; arrange alongside freshly shucked oysters.", "Provide a strawberry mignonette: muddled strawberry, white wine vinegar, shallot, and pepper.", "Serve together as a luxury pairing; the Parmesan bridges strawberry's sweetness to oyster's brine."]),

    ("oyster","parmesan","tomato",
     "Oyster and tomato share acetic acid and dimethyl sulfide while Parmesan and tomato share furaneol and acetic acid — double bridges through tomato — making tomato the natural connector between oyster's marine brine and Parmesan's aged dairy umami. The trio creates a refined Italian seafood gratin.",
     "Tomato Parmesan Oyster Gratin",
     ["Make a simple tomato sauce with garlic, crushed tomatoes, and white wine; cool slightly.", "Place shucked oysters in their shells; top with a spoonful of tomato sauce and grated Parmesan.", "Broil 5 minutes until the cheese is golden and the oyster edges just curl."]),

    ("oyster","parmesan","truffle",
     "Oyster, Parmesan, and truffle form an extraordinary triple-phenylacetaldehyde-dimethyl sulfide combination — all three share both the rosy-fermented and sulfurous compound pairs — creating the richest possible marine-dairy-fungal umami register. The three together are arguably the most compound-connected luxury trio in this set.",
     "Truffle Parmesan Oyster",
     ["Make a truffle-Parmesan cream by reducing cream with truffle butter and grated Parmesan.", "Spoon over shucked oysters in their half-shells; broil 3 minutes until just bubbling.", "Shave fresh truffle over immediately and serve; three luxury umami sources unified."]),

    ("oyster","parmesan","vanilla",
     "Oyster's marine brine and vanilla's vanillin sweetness create a bold sweet-salt contrast — the salted caramel logic applied to shellfish — while Parmesan's vanillin from aging provides the savory-sweet bridge between the two extremes, and vanilla's furaneol suppresses oyster's trimethylamine. The trio creates a sophisticated preparation.",
     "Vanilla Parmesan Oyster Custard",
     ["Make a savory custard with cream, eggs, Parmesan, and vanilla bean seeds; strain.", "Fill small ramekins with a shucked oyster each; pour custard over and steam until just set.", "Serve warm; Parmesan's vanillin bridges the vanilla sweetness to the oyster's marine brine."]),

    ("oyster","rose","salmon",
     "Oyster, rose, and salmon all share phenylacetaldehyde — the rosy-floral compound produced independently by bivalve, flower, and fatty fish through separate biochemical pathways — creating a triple-rosy-fermented aromatic connection. The trio achieves the most coherent marine-floral combination possible.",
     "Rose Oyster Salmon Tartare",
     ["Finely dice sushi-grade salmon; season with rose water, shallot, lemon, and sea salt.", "Shuck oysters; arrange alongside the salmon tartare on chilled plates.", "Dress both with a rose-lemon vinaigrette; rose petals connect the two seafood preparations."]),

    ("oyster","rose","strawberry",
     "Oyster, rose, and strawberry share phenylacetaldehyde — the rosy-floral compound produced by all three independently — while rose and strawberry share 2-phenylethanol and furaneol. The triple-rosy compound connection creates an extraordinarily coherent floral-sweet-marine combination.",
     "Rose Strawberry Oyster Mignonette",
     ["Blend muddled fresh strawberry with rose water, white wine vinegar, and minced shallot.", "Add cracked white pepper; strain through a fine sieve for a clean mignonette.", "Spoon over freshly shucked oysters; scatter rose petals and a sliced strawberry garnish."]),

    ("oyster","rose","tomato",
     "Oyster and tomato share acetic acid and dimethyl sulfide while rose and tomato share furaneol and geraniol — two compound bridges through tomato — making tomato the natural connector between oyster's marine brine and rose's floral sweetness. The trio creates a Provençal-inspired oyster braise.",
     "Rose Tomato Oyster Stew",
     ["Sauté garlic in olive oil; add cherry tomatoes and a splash of rose water; cook until jammy.", "Add shucked oysters with their liquor; poach 2 minutes until edges just curl.", "Finish with rose petals, cracked pepper, and a drizzle of rose-infused olive oil."]),

    ("oyster","rose","truffle",
     "Oyster, rose, and truffle share phenylacetaldehyde — the rosy-fermented compound that all three produce independently — creating a triple-rosy-fermented aromatic register with truffle's dimethyl sulfide adding the sulfurous-earthy dimension. The trio represents the most phenylacetaldehyde-concentrated luxury preparation in this set.",
     "Rose Truffle Oyster on the Half Shell",
     ["Mix truffle oil with rose water, minced shallot, white wine vinegar, and cracked pepper.", "Shuck oysters and arrange on crushed ice; spoon a tiny amount of the truffle-rose mignonette over each.", "Garnish with a rose petal; the phenylacetaldehyde in all three creates a unified rosy-earthy-marine note."]),

    ("oyster","rose","vanilla",
     "Oyster's marine brine and vanilla's vanillin sweetness create a bold sweet-salt contrast while rose's 2-phenylethanol provides the floral bridge between vanilla's perfumed sweetness and oyster's minor phenylacetaldehyde floral note. The trio creates a sophisticated beurre blanc preparation.",
     "Rose Vanilla Oyster Beurre Blanc",
     ["Reduce white wine and shallots; whisk cold butter piece by piece until emulsified.", "Add rose water and vanilla bean seeds; strain through a fine sieve.", "Spoon over warm broiled oysters; rose and vanilla create a perfumed sweet contrast to the brine."]),

    ("oyster","salmon","strawberry",
     "Oyster and salmon share trimethylamine, dimethyl sulfide, and (E)-2-nonenal — the fullest marine-compound overlap between two seafoods — while strawberry's furaneol sweetness and linalool provide sweet-floral aromatic displacement that suppresses the marine register of both proteins simultaneously. The trio works as a sweet-briny raw bar concept.",
     "Strawberry Oyster Salmon Shooter",
     ["Blend fresh strawberry with lemon juice, a touch of vinegar, and salt; strain clean.", "Shuck one oyster and slice one piece of sashimi-grade salmon for each shot glass.", "Pour the strawberry liquid over both seafoods; serve immediately chilled."]),

    ("oyster","salmon","tomato",
     "Oyster and salmon share trimethylamine and dimethyl sulfide while both share furaneol and acetic acid with tomato — the sweet-caramel and tart compounds bridging all three — making tomato the natural connector in this double-seafood preparation. The trio drives Italian seafood cioppino and Venetian coastal stews.",
     "Tomato Oyster Salmon Cioppino",
     ["Sauté garlic and fennel in olive oil; add crushed tomatoes, white wine, and fish stock.", "Simmer 15 minutes; add salmon pieces and poach 5 minutes.", "Add shucked oysters for the final 2 minutes; serve in bowls with crusty bread and olive oil."]),

    ("oyster","salmon","truffle",
     "Oyster, salmon, and truffle form a triple-dimethyl sulfide combination — all three share the sulfurous compound that defines their distinct earthy-marine-animal aromatic character — making this the most dimethyl sulfide-concentrated preparation in the set. The combination is the pinnacle of marine-luxury flavor.",
     "Truffle Oyster Salmon Plate",
     ["Sear salmon skin-side down in truffle oil until skin crisps; flip briefly and rest.", "Arrange alongside two freshly shucked raw oysters per portion.", "Shave truffle generously over both; serve with a truffle-lemon vinaigrette."]),

    ("oyster","salmon","vanilla",
     "Oyster, salmon, and vanilla share trimethylamine suppression chemistry — vanilla's furaneol and vanillin suppress the marine-animal amine from both seafoods simultaneously — while vanilla's lactonic sweetness creates the boldest possible sweet-salt-marine contrast. The trio is a sophisticated avant-garde seafood preparation.",
     "Vanilla Oyster Salmon Ceviche",
     ["Dice sushi-grade salmon; cure in lime juice with a scrape of vanilla bean and salt for 5 minutes.", "Add shucked oysters to the mixture; stir gently to combine.", "Serve chilled with diced cucumber, shallot, and a garnish of vanilla seeds over the top."]),

    ("oyster","strawberry","tomato",
     "Oyster and tomato share acetic acid and dimethyl sulfide while tomato and strawberry share furaneol — the sweet-caramel compound critical to both ripe fruits — making tomato the aromatic connector between oyster's marine brine and strawberry's sweet-floral register. The trio creates a bold sweet-briny summer preparation.",
     "Strawberry Tomato Oyster Salsa",
     ["Make a salsa from diced fresh tomato, diced strawberry, shallot, lime juice, and cracked pepper.", "Shuck oysters and arrange on crushed ice in their shells.", "Spoon the strawberry-tomato salsa over each oyster; serve immediately."]),
]

conn = sqlite3.connect(DB)
c = conn.cursor()
for (a, b, cc, desc, title, steps) in TRIPLETS:
    c.execute(
        "INSERT OR REPLACE INTO triplet_info (ing_a, ing_b, ing_c, description, recipe_title, recipe_steps) VALUES (?,?,?,?,?,?)",
        (a, b, cc, desc, title, json.dumps(steps))
    )
conn.commit()
conn.close()
print(f"Batch 055 done: inserted {len(TRIPLETS)} triplets.")
