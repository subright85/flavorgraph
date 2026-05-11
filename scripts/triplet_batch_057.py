#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("rose","salmon","strawberry",
     "Rose, salmon, and strawberry share phenylacetaldehyde — the rosy-floral compound produced independently by flower, fatty fish, and ripe fruit — while rose and strawberry share 2-phenylethanol and linalool, and rose's geraniol suppresses salmon's trimethylamine. The triple-phenylacetaldehyde combination creates an extraordinary rosy-marine-floral preparation.",
     "Rose Strawberry Salmon Salad",
     ["Slice sushi-grade salmon paper-thin; arrange with sliced strawberries on a chilled plate.", "Dress with rose water, lemon juice, and olive oil; scatter fleur de sel.", "Garnish with rose petals and a strawberry slice; the shared phenylacetaldehyde unifies all three."]),

    ("rose","salmon","tomato",
     "Rose and salmon share phenylacetaldehyde while rose and tomato share furaneol and geraniol — two compound bridges through rose — making rose the aromatic connector between salmon's marine profile and tomato's sweet-acid register. The trio creates a Provençal-Persian salmon preparation.",
     "Rose Tomato Salmon Provençal",
     ["Marinate salmon with rose water, tomato juice, garlic, and herbs for 30 minutes.", "Bake at 400°F for 12 minutes; simultaneously roast cherry tomatoes with rose water.", "Serve salmon over the roasted rose-tomatoes with dried rose petals and fresh herbs."]),

    ("rose","salmon","truffle",
     "Rose and truffle share phenylacetaldehyde and anisaldehyde — the rosy-fermented and anise-adjacent compound pair — while rose's geraniol suppresses salmon's trimethylamine and truffle's dimethyl sulfide connects to salmon's marine aromatic family. The trio creates a luxury floral-marine-earthy preparation.",
     "Rose Truffle Salmon Fillet",
     ["Sear salmon in truffle butter until the skin is perfectly crisp; flip and finish.", "Make a rose-truffle beurre blanc with rose water, truffle, and cold butter.", "Serve salmon with the sauce, rose petals, and shaved fresh truffle over the top."]),

    ("rose","salmon","vanilla",
     "Rose and vanilla share 2-phenylethanol and linalool — the rosy-floral and herbal terpene pair — while both suppress salmon's trimethylamine through floral and sweet aromatic displacement. Rose's geraniol provides the citrus-floral bridge to salmon's minor floral compounds while vanilla's furaneol creates the sweet-lactonic contrast.",
     "Rose Vanilla Poached Salmon",
     ["Make a court bouillon with rose water, vanilla bean, white wine, and aromatics.", "Poach salmon at barely a simmer for 10 minutes until just opaque.", "Serve with a rose-vanilla beurre blanc and dried rose petals scattered over the fillet."]),

    ("rose","strawberry","tomato",
     "Rose, strawberry, and tomato share furaneol and geraniol — the sweet-caramel and citrus-floral compounds — creating a triple-furaneol-geraniol sweet-floral-savory combination. Rose and strawberry share 2-phenylethanol which amplifies the floral register above the shared sweet-caramel base of all three ingredients.",
     "Rose Strawberry Tomato Gazpacho",
     ["Blend ripe tomatoes with fresh strawberries, a splash of rose water, cucumber, and garlic.", "Season with sherry vinegar, olive oil, salt, and white pepper; strain until silky.", "Serve chilled with rose petals, diced strawberry, and a drizzle of rose-infused olive oil."]),

    ("rose","strawberry","truffle",
     "Rose, strawberry, and truffle share phenylacetaldehyde — the rosy-fermented compound produced by all three independently — while rose and strawberry share 2-phenylethanol and linalool. The triple-phenylacetaldehyde concentration creates the most profound rosy-fermented aromatic possible in a dessert preparation.",
     "Rose Truffle Strawberry Dessert",
     ["Macerate sliced strawberries with rose water and truffle honey; rest 15 minutes.", "Arrange over a rose panna cotta or vanilla cream in chilled glasses.", "Shave a very small amount of fresh truffle over the top; the shared phenylacetaldehyde unifies the trio."]),

    ("rose","strawberry","vanilla",
     "Rose, strawberry, and vanilla share 2-phenylethanol, linalool, and furaneol — the complete three-way floral-sweet compound overlap — creating the most concentrated rosy-sweet aromatic combination in this entire set. Each ingredient's dominant compounds are shared and reinforced by the other two.",
     "Rose Strawberry Vanilla Entremet",
     ["Bake vanilla sponge layers brushed with rose water syrup.", "Fill with strawberry-rose mousse and rose-vanilla cream alternating layers.", "Glaze with rose mirror glaze; decorate with crystallized rose petals and fresh strawberries."]),

    ("rose","tomato","truffle",
     "Rose and truffle share phenylacetaldehyde and anisaldehyde — the rosy-fermented and anise-adjacent pair — while rose and tomato share furaneol and geraniol. Two compound bridges through rose make it the aromatic connector between tomato's sweet-acid register and truffle's dense earthiness. The trio is haute cuisine territory.",
     "Rose Truffle Tomato Sauce",
     ["Simmer crushed tomatoes with garlic and a splash of rose water until reduced and sweet.", "Off heat stir in truffle butter until glossy; season with rose salt and cracked pepper.", "Toss with fresh pasta; shave truffle over and finish with dried rose petals at the table."]),

    ("rose","tomato","vanilla",
     "Rose and tomato share furaneol and geraniol while tomato and vanilla share furaneol — the sweet-caramel compound critical to all three ingredients at high concentrations. The triple-furaneol-geraniol combination creates a sweet-floral-savory preparation where all three ingredients' dominant aromatic compounds reinforce each other.",
     "Rose Vanilla Tomato Confit",
     ["Halve cherry tomatoes; place with rose water, a vanilla bean, and rose petals in a baking dish.", "Cover with olive oil; roast at 250°F for 90 minutes until concentrated and fragrant.", "Serve over burrata; the rose-vanilla amplifies the tomato's natural furaneol sweetness beautifully."]),

    ("rose","truffle","vanilla",
     "Rose and truffle share phenylacetaldehyde and anisaldehyde — the rosy-fermented and anise-adjacent luxury pair — while rose and vanilla share 2-phenylethanol and linalool, and truffle and vanilla share vanillin. Three separate compound bridges make this the most compound-connected trio in the entire set.",
     "Rose Truffle Vanilla Compound Butter",
     ["Beat softened butter with truffle paste, vanilla bean seeds, rose water, and flaky salt.", "Mix until completely smooth; taste carefully — rose water is easy to overdo.", "Roll into a log, refrigerate until firm, and slice over warm brioche or a seared scallop."]),

    ("salmon","strawberry","tomato",
     "Salmon and tomato share dimethyl sulfide and furaneol while strawberry and tomato share furaneol — two compound bridges through tomato — making tomato the natural connector between salmon's marine profile and strawberry's sweet-floral register. The trio creates a summer salmon salsa preparation.",
     "Strawberry Tomato Salmon Ceviche",
     ["Dice sushi-grade salmon; cure in lime juice with salt for 5 minutes; drain.", "Toss with diced strawberry, diced tomato, red onion, cilantro, and a drizzle of olive oil.", "Season with flaky salt; serve immediately chilled — the tomato bridges salmon and strawberry."]),

    ("salmon","strawberry","truffle",
     "Salmon and truffle share dimethyl sulfide — the sulfurous compound linking marine fish and earthy fungus — while strawberry and truffle share phenylacetaldehyde, and strawberry's furaneol sweetness suppresses salmon's trimethylamine. The trio creates a luxury salmon preparation with sweet-earthy contrast.",
     "Truffle Strawberry Salmon Tartare",
     ["Finely dice sushi-grade salmon; season with truffle oil, lemon juice, and fleur de sel.", "Fold in diced fresh strawberry and a drizzle of truffle honey; mix gently.", "Serve on chilled plates with shaved fresh truffle over; strawberry bridges salmon and truffle."]),

    ("salmon","strawberry","vanilla",
     "Salmon and vanilla share furaneol and trace vanillin — caramel-lactonic compounds suppressing trimethylamine — while strawberry and vanilla share furaneol, linalool, and 2-phenylethanol. The three-way furaneol combination with strawberry's additional floral compounds creates the most complete sweet-floral salmon suppression.",
     "Strawberry Vanilla Salmon Glaze",
     ["Make a glaze from strawberry purée, vanilla bean, and a touch of balsamic; reduce until syrupy.", "Brush over salmon fillets; bake at 400°F for 12 minutes, brushing once more halfway.", "Serve with fresh strawberries, vanilla crème fraîche, and a scatter of vanilla seeds."]),

    ("salmon","tomato","truffle",
     "Salmon and tomato share dimethyl sulfide and furaneol while salmon and truffle share dimethyl sulfide — double dimethyl sulfide bridges through salmon — making salmon the aromatic connector between tomato's sweet-acid register and truffle's earthy-luxury profile. The trio drives high-end Italian salmon with truffle and tomato.",
     "Truffle Tomato Salmon Pasta",
     ["Sear salmon until just done; set aside and flake. Simmer cherry tomatoes with truffle butter.", "Toss pasta with the tomato-truffle sauce; fold salmon pieces in gently off heat.", "Shave generous truffle over, finish with lemon and herbs, and serve immediately."]),

    ("salmon","tomato","vanilla",
     "Salmon and tomato share dimethyl sulfide and furaneol while tomato and vanilla share furaneol — two compound bridges through furaneol — with vanilla's vanillin suppressing salmon's trimethylamine and tomato's acidity providing the bright contrast. The trio creates an unusual but chemically precise salmon preparation.",
     "Vanilla Tomato Braised Salmon",
     ["Simmer cherry tomatoes with garlic, white wine, and a split vanilla bean until jammy.", "Add salmon fillets; cover and braise gently for 8 minutes until just opaque.", "Remove vanilla pod; serve salmon over the vanilla-tomato braise with fresh herbs."]),

    ("salmon","truffle","vanilla",
     "Salmon and truffle share dimethyl sulfide — the sulfurous compound linking marine fish and earthy fungus — while salmon and vanilla share furaneol and vanillin suppresses salmon's trimethylamine. The three-way combination achieves maximum aromatic suppression of salmon's marine notes through both sweet-lactonic and earthy pathways.",
     "Truffle Vanilla Salmon en Croûte",
     ["Spread truffle-vanilla compound butter (truffle paste + vanilla bean + butter) over salmon.", "Wrap in puff pastry, seal, brush with egg wash; bake at 400°F for 20 minutes until golden.", "Rest 5 minutes; serve with a truffle-vanilla cream sauce and shaved truffle over each slice."]),

    ("strawberry","tomato","truffle",
     "Strawberry and tomato share furaneol — the sweet-caramel compound critical to both ripe fruits — while tomato and truffle share dimethyl sulfide and phenylacetaldehyde. Two compound bridges through tomato make it the aromatic connector between strawberry's sweet-floral register and truffle's dense earthy luxury.",
     "Truffle Strawberry Tomato Bruschetta",
     ["Roast cherry tomatoes with truffle butter until jammy; cool slightly.", "Dice fresh strawberries; fold gently into the truffle-tomato mixture.", "Serve on toasted sourdough with shaved truffle over; tomato bridges strawberry and truffle perfectly."]),

    ("strawberry","tomato","vanilla",
     "Strawberry, tomato, and vanilla share furaneol — the sweet-caramel compound critical to all three at high concentrations — creating the highest triple-furaneol combination in this entire set. The three ingredients together produce the richest possible caramel-sweet aromatic register in both sweet and savory applications.",
     "Strawberry Vanilla Tomato Jam",
     ["Combine halved cherry tomatoes with sliced strawberries, vanilla bean, and sugar in a saucepan.", "Cook over medium heat until jammy and reduced, about 25 minutes; remove vanilla pod.", "Cool and serve with cheese and crackers — three furaneol sources creating a deep sweet-savory jam."]),

    ("strawberry","truffle","vanilla",
     "Strawberry and truffle share phenylacetaldehyde — the rosy-fermented compound — while strawberry and vanilla share furaneol, linalool, and 2-phenylethanol. Two compound bridges through strawberry make it the connector between truffle's earthy luxury and vanilla's sweet-lactonic register. The trio is a luxury dessert preparation.",
     "Truffle Vanilla Strawberry Tart",
     ["Make a vanilla custard tart; fill a blind-baked shell and refrigerate until set.", "Arrange sliced fresh strawberries macerated with truffle honey over the custard.", "Shave fresh truffle sparingly over the top; vanilla bridges strawberry's sweetness to truffle's earthiness."]),

    ("tomato","truffle","vanilla",
     "Tomato and truffle share dimethyl sulfide and phenylacetaldehyde — the sulfurous and rosy-fermented pair — while tomato and vanilla share furaneol, and truffle and vanilla share vanillin. Three separate compound bridges through all three pairs make this the most compound-connected triplet in the entire FlavorGraph set.",
     "Truffle Vanilla Tomato Risotto",
     ["Cook arborio risotto until creamy; fold in roasted cherry tomato purée and truffle butter.", "Add vanilla bean seeds off heat; stir with cold Parmesan until glossy.", "Plate, shave generous fresh truffle over, and serve — the final triplet in the FlavorGraph."]),
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
print(f"Batch 057 done: inserted {len(TRIPLETS)} triplets.")
