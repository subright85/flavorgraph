#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("oyster","strawberry","truffle",
     "Oyster, strawberry, and truffle share phenylacetaldehyde — the rosy-fermented compound produced independently by marine bivalve, ripe fruit, and earthy fungus through three completely separate biochemical pathways — creating the highest triple-phenylacetaldehyde concentration in this entire set. The trio achieves extraordinary rosy-fermented aromatic depth.",
     "Truffle Strawberry Oyster Tartare",
     ["Finely chop oysters; mix with diced strawberry, truffle oil, lemon juice, and fleur de sel.", "Arrange in chilled oyster shells over crushed ice; shave fresh truffle over generously.", "Serve immediately; the phenylacetaldehyde in all three creates a profound rosy-earthy-marine unity."]),

    ("oyster","strawberry","vanilla",
     "Oyster's marine brine and vanilla's vanillin sweetness create the boldest sweet-salt contrast in this set — the salted caramel principle applied to raw shellfish — while strawberry's furaneol sweetness amplifies vanilla's sweet-caramel register and suppresses oyster's marine trimethylamine through fruit-sweet displacement.",
     "Strawberry Vanilla Oyster Granita",
     ["Blend fresh strawberries with vanilla bean seeds, lemon juice, and simple syrup; freeze into a granita.", "Shuck oysters and arrange in their half-shells on crushed ice.", "Top each oyster with strawberry-vanilla granita; serve immediately for maximum sweet-salt contrast."]),

    ("oyster","tomato","truffle",
     "Oyster and tomato share acetic acid and dimethyl sulfide while oyster and truffle share dimethyl sulfide and phenylacetaldehyde — two compound bridges through dimethyl sulfide — making this a triple-dimethyl sulfide combination where the sulfurous marine, vegetable-sweet, and earthy registers combine into a profound savory depth.",
     "Truffle Tomato Oyster Stew",
     ["Sauté garlic; add crushed tomatoes and truffle butter; simmer 10 minutes until rich.", "Add shucked oysters with their liquor; poach 2 minutes until edges just curl.", "Serve in warm bowls with shaved truffle over the top and crusty bread alongside."]),

    ("oyster","tomato","vanilla",
     "Oyster and tomato share acetic acid and dimethyl sulfide while tomato and vanilla share furaneol — the sweet-caramel compound critical to both ripe tomato and cured vanilla beans — making tomato the connector between oyster's marine brine and vanilla's sweet-lactonic register. The trio creates a sophisticated savory-sweet braise.",
     "Vanilla Tomato Oyster Stew",
     ["Sauté garlic in butter; add cherry tomatoes and a split vanilla bean; cook until jammy.", "Add shucked oysters with their liquor; poach 2 minutes until just cooked.", "Remove vanilla pod; finish with a drizzle of vanilla oil and serve with warm crusty bread."]),

    ("oyster","truffle","vanilla",
     "Oyster and truffle share phenylacetaldehyde and dimethyl sulfide — the rosy-fermented and sulfurous luxury compound pair — while vanilla's vanillin sweetness provides the sweetest possible aromatic contrast to the intense marine-earthy combination, and vanilla's furaneol suppresses oyster's trimethylamine. The trio is the most extreme luxury contrast in the set.",
     "Truffle Vanilla Oyster",
     ["Make a vanilla-truffle beurre blanc: reduce cream with vanilla bean and finish with truffle butter.", "Broil shucked oysters in their shells until edges just curl, about 3 minutes.", "Spoon the vanilla-truffle sauce over; shave fresh truffle and serve with champagne."]),

    ("parmesan","rose","salmon",
     "Parmesan and salmon share dimethyl sulfide and butyric acid — the sulfurous and fatty-acid compounds connecting aged dairy and fatty fish — while rose's 2-phenylethanol and geraniol provide the floral aromatic bridge that suppresses salmon's trimethylamine and softens Parmesan's sharpest butyric notes simultaneously. The trio is a refined coastal Italian preparation.",
     "Rose Parmesan Salmon",
     ["Crust salmon fillets with a mixture of grated Parmesan, rose water, and breadcrumbs.", "Bake at 400°F for 12 minutes until the Parmesan crust is golden.", "Serve with a rose-lemon beurre blanc and dried rose petals scattered over the top."]),

    ("parmesan","rose","strawberry",
     "Parmesan and rose share 2-phenylethanol and phenylacetaldehyde — fermented-rosy compounds spanning aged dairy and flower — while strawberry's furaneol sweetness and 2-phenylethanol reinforce rose's dominant compound and soften Parmesan's sharpness. The Italian tradition of aged cheese with strawberries meets the Persian tradition of rose with cheese.",
     "Rose Strawberry Parmesan Tartine",
     ["Spread whipped Parmesan seasoned with rose water on toasted sourdough.", "Top with sliced fresh strawberries and a scatter of dried rose petals.", "Drizzle with rose honey, crack black pepper, and finish with Parmesan shavings."]),

    ("parmesan","rose","tomato",
     "Parmesan and tomato share furaneol and acetic acid — sweet-caramel and tart compounds — while rose's geraniol softens tomato's acidity through floral displacement and rose's 2-phenylethanol reinforces Parmesan's fermentation esters. The trio creates a refined floral-umami tomato tart preparation.",
     "Rose Parmesan Tomato Tarte Fine",
     ["Roll puff pastry thin; scatter grated Parmesan over, then overlap ripe tomato slices.", "Add a few drops of rose water over the tomatoes; bake at 400°F until pastry is golden.", "Serve with dried rose petals and a drizzle of rose-infused olive oil."]),

    ("parmesan","rose","truffle",
     "Parmesan and truffle share phenylacetaldehyde and dimethyl sulfide — the fermented-rosy and sulfurous luxury compound pair — while rose's 2-phenylethanol reinforces the shared phenylacetaldehyde and provides the floral register that lifts the dense Parmesan-truffle umami into a cleaner aromatic space. The trio is the most refined cheese-truffle combination.",
     "Rose Truffle Parmesan Pasta",
     ["Cook fresh pasta al dente; toss with truffle butter and cold Parmesan off heat.", "Add a very small splash of rose water and pasta water; toss until glossy.", "Plate, shave truffle generously, and finish with a dried rose petal and Parmesan shavings."]),

    ("parmesan","rose","vanilla",
     "Parmesan and vanilla share vanillin and butyric acid — the sweet-lactonic and fatty-acid compounds connecting aged dairy and cured spice — while rose's 2-phenylethanol and geraniol provide the floral bridge between vanilla's warm-sweet and Parmesan's savory-funky registers. The trio creates a sophisticated savory-sweet pastry.",
     "Rose Vanilla Parmesan Cheesecake",
     ["Make a savory cheesecake base from cream cheese, Parmesan, vanilla, and lemon.", "Add a splash of rose water to the batter; bake in a water bath at 325°F until just set.", "Refrigerate overnight; serve with rose petal jam and a Parmesan tuile garnish."]),

    ("parmesan","salmon","strawberry",
     "Parmesan and salmon share dimethyl sulfide and butyric acid — the sulfurous and fatty-acid compound family — while strawberry's furaneol sweetness and linalool provide the sweet-floral aromatic displacement of both salmon's trimethylamine and Parmesan's sharpest butyric notes. The trio creates a light Italian salmon salad.",
     "Strawberry Parmesan Salmon Salad",
     ["Pan-sear salmon until just done; cool and flake into large pieces.", "Arrange over arugula with sliced strawberries, shaved Parmesan, and aged balsamic.", "Dress with a strawberry-balsamic vinaigrette; finish with Parmesan shavings and cracked pepper."]),

    ("parmesan","salmon","tomato",
     "Parmesan and salmon share dimethyl sulfide while Parmesan and tomato share furaneol and acetic acid — two compound bridges through Parmesan — making Parmesan the aromatic connector between salmon's marine profile and tomato's sweet-acid register. The trio drives Italian salmon pasta with tomato sauce.",
     "Parmesan Salmon Tomato Pasta",
     ["Cook salmon until just done; flake into pieces. Simmer cherry tomatoes with garlic until jammy.", "Toss pasta with the tomato sauce and pasta water; fold in salmon pieces gently.", "Finish with a generous amount of Parmesan and torn basil; serve immediately."]),

    ("parmesan","salmon","truffle",
     "Parmesan, salmon, and truffle form a triple-dimethyl sulfide and phenylacetaldehyde combination — all three share the sulfurous and rosy-fermented compound pair — creating the most sulfurous-rich dairy-fish-fungal umami preparation in this set. The trio is Italian luxury seafood territory.",
     "Truffle Parmesan Salmon Risotto",
     ["Cook arborio risotto with fish stock until creamy; off heat stir in truffle butter and Parmesan.", "Flake cooked salmon into large pieces; fold gently into the risotto.", "Plate, shave generous truffle over, and finish with Parmesan and cracked pepper."]),

    ("parmesan","salmon","vanilla",
     "Parmesan and salmon share dimethyl sulfide and butyric acid — the sulfurous and fatty-acid compound family — while vanilla's vanillin and furaneol sweetness suppresses both salmon's trimethylamine and Parmesan's sharpest butyric notes through sweet-lactonic displacement. The trio creates a sophisticated French-Italian fusion preparation.",
     "Vanilla Parmesan Salmon Pasta",
     ["Cook pasta; toss with Parmesan, a scrape of vanilla bean, and lemon zest off heat.", "Fold in flaked pan-seared salmon gently; loosen with pasta water until glossy.", "Serve with more Parmesan; the vanilla is subtle but suppresses marine and dairy pungency."]),

    ("parmesan","strawberry","tomato",
     "Parmesan, strawberry, and tomato form a triple-furaneol combination — all three contain the sweet-caramel compound at significant concentrations — creating the richest possible sweet-savory furaneol register. Parmesan's glutamate amplifies the furaneol-sweet base while tomato's acidity and strawberry's floral esters provide contrast.",
     "Strawberry Tomato Parmesan Bruschetta",
     ["Macerate diced strawberries with diced tomato, aged balsamic, and torn basil for 15 minutes.", "Toast thick sourdough until crisp; spread a layer of whipped Parmesan over each.", "Top with the strawberry-tomato mixture; finish with Parmesan shavings and cracked pepper."]),

    ("parmesan","strawberry","truffle",
     "Parmesan and truffle share phenylacetaldehyde and dimethyl sulfide — the fermented-rosy and sulfurous pair — while strawberry and truffle share phenylacetaldehyde through separate biochemical pathways, and Parmesan and strawberry share furaneol. The three-way compound connectivity is extraordinary.",
     "Truffle Strawberry Parmesan Salad",
     ["Slice fresh strawberries; toss with truffle honey and a splash of aged balsamic.", "Arrange on a plate with large Parmesan shavings scattered generously over.", "Shave a small amount of fresh truffle over the top; the phenylacetaldehyde unifies all three."]),

    ("parmesan","strawberry","vanilla",
     "Parmesan, strawberry, and vanilla share furaneol and 2-phenylethanol — the sweet-caramel and rosy-floral compounds connecting aged dairy, ripe fruit, and tropical spice — while vanilla's vanillin provides the sweetest possible aromatic bridge between Parmesan's savory umami and strawberry's fruit register. The trio creates a refined dessert cheese board.",
     "Strawberry Vanilla Parmesan Dessert Board",
     ["Shave aged Parmesan in large pieces; arrange with sliced fresh strawberries and vanilla shortbread.", "Drizzle vanilla bean honey over everything; scatter crystallized sugar.", "Serve as a dessert course; Parmesan's furaneol bridges the vanilla sweetness to the strawberry."]),

    ("parmesan","tomato","truffle",
     "Parmesan and truffle share phenylacetaldehyde and dimethyl sulfide — the fermented-rosy and sulfurous pair — while Parmesan and tomato share furaneol and acetic acid. Two separate compound bridges through Parmesan make it the central aromatic connector between tomato's sweet-acid register and truffle's dense earthiness.",
     "Truffle Tomato Parmesan Risotto",
     ["Cook arborio risotto with stock until creamy; off heat stir in truffle butter and cold Parmesan.", "Fold in roasted cherry tomatoes; the tomato acidity brightens the truffle-Parmesan combination.", "Shave fresh truffle over, finish with Parmesan, and serve immediately."]),

    ("parmesan","tomato","vanilla",
     "Parmesan, tomato, and vanilla share furaneol — the sweet-caramel compound critical to all three — while Parmesan and tomato share acetic acid. The triple-furaneol combination creates the richest possible sweet-savory furaneol register, with vanilla's vanillin providing the sweetest aromatic above the shared caramel base.",
     "Vanilla Tomato Parmesan Sauce",
     ["Simmer crushed tomatoes with garlic until sweet and reduced; add a split vanilla bean.", "Cook 10 more minutes; remove vanilla pod and stir in cold Parmesan until incorporated.", "Toss with pasta; the vanilla amplifies the tomato's furaneol and rounds the Parmesan's sharpness."]),

    ("parmesan","truffle","vanilla",
     "Parmesan and truffle share phenylacetaldehyde and dimethyl sulfide — the fermented-rosy and sulfurous luxury pair — while Parmesan and vanilla share vanillin and butyric acid — the sweet-lactonic and fatty-acid pair — making Parmesan the double-bridge connecting truffle's earthiness and vanilla's sweetness. The trio is the richest compound butter.",
     "Truffle Vanilla Parmesan Compound Butter",
     ["Beat softened butter with truffle paste, vanilla bean seeds, and finely grated Parmesan.", "Add a pinch of flaky salt; mix until completely smooth and thoroughly combined.", "Roll into a log, refrigerate until firm, slice over risotto, pasta, or scrambled eggs."]),
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
print(f"Batch 056 done: inserted {len(TRIPLETS)} triplets.")
