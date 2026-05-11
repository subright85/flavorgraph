#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("garlic","lemon","strawberry",
     "Garlic's allicin pungency and strawberry's furaneol sweetness create a bold savory-sweet contrast — the logic behind strawberry-garlic gastrique — while lemon's citric acid moderates garlic's sharpness and amplifies strawberry's brightness through acid-sweet contrast simultaneously. The trio creates a sophisticated summer sauce for duck or chicken.",
     "Strawberry Lemon Garlic Gastrique",
     ["Cook sliced strawberries with minced garlic, lemon juice, and sugar until thick and jammy.", "Strain; reduce until syrupy and season with salt, pepper, and more lemon.", "Serve as a finishing sauce for seared duck breast or grilled chicken thighs."]),

    ("garlic","lemon","tomato",
     "Garlic, lemon, and tomato are the triumvirate of Mediterranean cooking — garlic's dimethyl sulfide and allicin providing allium depth, lemon's citric acid brightening tomato's acidity while moderating garlic's sharpness, and tomato's malic acid creating the tart-savory foundation. The trio drives every Italian pasta sauce, Greek salad dressing, and Middle Eastern salsa.",
     "Garlic Lemon Tomato Bruschetta",
     ["Dice ripe tomatoes; toss with minced garlic, lemon juice, lemon zest, and olive oil.", "Rest 10 minutes to develop flavors; season with salt and fresh basil.", "Pile generously onto grilled sourdough; the lemon and garlic lift tomato's savory register."]),

    ("garlic","lemon","truffle",
     "Garlic and truffle share dimethyl sulfide while lemon's citric acid and limonene lift the intensely earthy garlic-truffle combination through brightness — acid and citrus terpenes preventing the sulfurous-earthy double from being too heavy. The trio creates an elegant light luxury pasta preparation.",
     "Truffle Garlic Lemon Tagliolini",
     ["Sauté sliced garlic in truffle butter; add lemon zest and a splash of pasta water.", "Toss al dente tagliolini until glossy; squeeze lemon juice over off heat.", "Plate; shave fresh truffle generously and finish with lemon zest curls."]),

    ("garlic","lemon","vanilla",
     "Garlic's allium pungency and vanilla's vanillin sweetness create a bold savory-sweet contrast while lemon's citric acid bridges both — moderating garlic's sharpness through pH adjustment and preventing vanilla's sweetness from becoming cloying. The trio appears in sophisticated vanilla-roasted garlic sauces for white meat.",
     "Vanilla Garlic Lemon Chicken",
     ["Make a sauce: roasted garlic, vanilla bean seeds, lemon zest, and cream reduced together.", "Roast chicken until golden; deglaze pan with lemon juice and the vanilla-garlic cream sauce.", "Serve with the pan sauce and steamed vegetables; the vanilla rounds garlic's sharpness beautifully."]),

    ("garlic","mint","oyster",
     "Garlic and oyster share dimethyl sulfide while mint's menthol provides cooling palate-cleansing contrast that cuts through garlic's allium pungency and oyster's marine brine simultaneously. The trio creates a bold Thai-influenced oyster preparation where garlic's savory depth and mint's freshness bracket the marine register.",
     "Garlic Mint Oyster Sauce",
     ["Sauté minced garlic in oil until fragrant; add shucked oysters with their liquor.", "Cook 2 minutes; stir in a generous amount of fresh mint and a squeeze of lime.", "Serve immediately over rice; the garlic deepens and mint freshens the marine flavor."]),

    ("garlic","mint","parmesan",
     "Garlic and Parmesan share dimethyl sulfide while mint's menthol provides cooling contrast that cuts both Parmesan's fat and garlic's pungency through olfactory competition. The trio creates a refreshing savory combination for herb pesto variations where cooling mint bridges allium and aged dairy.",
     "Mint Garlic Parmesan Pesto",
     ["Blend fresh mint, basil, garlic, Parmesan, pine nuts, and olive oil until smooth.", "Season with lemon juice and salt; the mint provides cooling depth that basil alone cannot.", "Toss with pasta; finish with more Parmesan and a drizzle of olive oil."]),

    ("garlic","mint","rose",
     "Garlic's allium pungency contrasts with rose's 2-phenylethanol floral sweetness while mint's menthol provides cooling contrast that moderates both extremes through olfactory competition. The trio drives Persian-influenced preparations where floral and herbal aromatics balance pungent allium in fragrant lamb dishes.",
     "Rose Mint Garlic Yogurt Sauce",
     ["Blend minced garlic into yogurt with rose water and fresh mint; season with lemon and salt.", "The rose softens garlic's sharpness while mint provides cooling refreshment.", "Serve alongside grilled lamb, roasted vegetables, or as a dip with warm flatbread."]),

    ("garlic","mint","salmon",
     "Garlic and salmon share dimethyl sulfide while mint's menthol suppresses salmon's trimethylamine through olfactory masking — a second trimethylamine suppressor alongside garlic's allium transformation during cooking. The duo of TMA suppressors with garlic's savory depth creates a clean-tasting salmon with bold Mediterranean character.",
     "Garlic Mint Salmon",
     ["Make a marinade: minced garlic, fresh mint, lemon juice, and olive oil.", "Marinate salmon 30 minutes; grill or bake at 400°F for 12 minutes.", "Serve with a mint-garlic yogurt sauce and cucumber ribbons."]),

    ("garlic","mint","strawberry",
     "Garlic's allium pungency and strawberry's furaneol sweetness create a savory-sweet opposition while mint's menthol provides cooling freshness that amplifies strawberry's brightness and moderates garlic's harshness through olfactory competition. The trio creates a bold summer salsa or bruschetta with unexpected complexity.",
     "Strawberry Mint Garlic Bruschetta",
     ["Macerate diced strawberries with minced garlic, fresh mint, balsamic, and olive oil 15 minutes.", "Toast sourdough slices; rub with raw garlic while still warm.", "Pile the strawberry mixture generously; the mint and garlic transform a simple bruschetta."]),

    ("garlic","mint","tomato",
     "Garlic, mint, and tomato are the foundation of Levantine cooking — garlic's dimethyl sulfide and allicin, tomato's furaneol and acidity, and mint's menthol cooling that provides the refreshing contrast that prevents the garlic-tomato combination from being too heavy. The trio defines fattoush dressing, shakshuka garnish, and Turkish ezme.",
     "Mint Garlic Tomato Sauce",
     ["Sauté sliced garlic in olive oil; add crushed tomatoes and simmer 20 minutes.", "Off heat, stir in a generous amount of fresh mint; the cooling herb lifts the savory sauce.", "Serve over eggs, pasta, or use as a base for baked feta — the mint refreshes the garlic-tomato."]),

    ("garlic","mint","truffle",
     "Garlic and truffle share dimethyl sulfide while mint's menthol provides cooling contrast that lifts the intensely earthy garlic-truffle combination through olfactory freshness. Menthol's cooling gives truffle's sulfurous earthiness and garlic's allium pungency an unexpected clean finish.",
     "Truffle Garlic Mint Pasta",
     ["Sauté garlic in truffle butter; toss with al dente pasta and a splash of pasta water.", "Off heat, fold in finely chopped fresh mint.", "Plate; shave generous truffle over and finish with lemon zest and fleur de sel."]),

    ("garlic","mint","vanilla",
     "Garlic's allium pungency and vanilla's vanillin sweetness create a bold savory-sweet opposition while mint's menthol provides cooling bridge that moderates both extremes through olfactory competition. The unusual trio appears in sophisticated Middle Eastern dessert preparations where garlic is roasted to sweetness alongside vanilla.",
     "Vanilla Mint Roasted Garlic Dip",
     ["Roast whole garlic heads until sweet and caramelized; squeeze cloves into a bowl.", "Add vanilla bean seeds, fresh mint, and cream cheese; blend until smooth.", "Season with salt and lemon; serve with flatbread — the vanilla and mint transform the roasted garlic."]),

    ("garlic","oyster","parmesan",
     "Garlic, oyster, and Parmesan all share dimethyl sulfide — the sulfurous compound spanning allium, marine bivalve, and aged dairy — while Parmesan and oyster share free glutamates for double umami. The three-way sulfurous-umami alignment creates the most intensely savory possible baked oyster preparation.",
     "Garlic Parmesan Baked Oysters",
     ["Make garlic-Parmesan butter: minced garlic, grated Parmesan, herbs, and cold butter.", "Shuck oysters into shells; top each generously with garlic-Parmesan butter and breadcrumbs.", "Bake at 450°F for 6 minutes until topping is golden and oysters just cooked."]),

    ("garlic","oyster","rose",
     "Garlic and oyster share dimethyl sulfide while rose's 2-phenylethanol and oyster's phenylacetaldehyde share rosy-fermented compound chemistry — rose and oyster connecting through the same compound class. Garlic's savory pungency grounds rose's perfumed floral in a bold luxury oyster preparation.",
     "Rose Garlic Oyster Mignonette",
     ["Combine white wine vinegar, minced garlic, rose water, and finely minced shallot.", "Add cracked pepper and a pinch of flaky salt; rest 5 minutes.", "Spoon over raw oysters on ice; the rose softens garlic's sharpness into a floral-pungent balance."]),

    ("garlic","oyster","salmon",
     "Garlic, oyster, and salmon all share dimethyl sulfide — the sulfurous compound in allium, marine bivalve, and fatty fish through their respective metabolisms — creating a three-way sulfurous alignment that unifies two seafoods and an allium through the same chemical family. Garlic's allium bridges the marine-marine combination.",
     "Garlic Oyster Salmon Stew",
     ["Sauté sliced garlic until golden; add fish stock and shucked oysters with their liquor.", "Add salmon pieces; cook gently 5 minutes until salmon is just opaque.", "Season with herbs and lemon; the garlic ties both seafoods through shared sulfurous chemistry."]),

    ("garlic","oyster","strawberry",
     "Garlic and oyster share dimethyl sulfide while strawberry's furaneol sweetness applies the sweet-salt principle to oyster's brine — the gastrique logic — and garlic's allicin pungency contrasts strawberry's sweetness through savory-sweet opposition. The unusual trio appears in avant-garde raw bar preparations.",
     "Strawberry Garlic Oyster Mignonette",
     ["Blend muddled strawberry with a tiny amount of minced garlic and white wine vinegar.", "Strain; add a pinch of cracked pepper and flaky salt.", "Spoon over freshly shucked oysters on ice; the strawberry-garlic is bold but precise."]),

    ("garlic","oyster","tomato",
     "Garlic, oyster, and tomato share dimethyl sulfide and acetic acid — the sulfurous-tart compound family — while tomato and oyster share free glutamates for a double-umami connection. The trio is the flavor chemistry of Italian seafood brodetto and Spanish marinated oyster with gazpacho.",
     "Garlic Tomato Oyster Stew",
     ["Sauté garlic in olive oil; add crushed tomatoes and simmer 15 minutes until thick.", "Add shucked oysters with their liquor; cook gently 2 minutes.", "Season with salt and parsley; serve over crusty bread with a drizzle of olive oil."]),

    ("garlic","oyster","truffle",
     "Garlic, oyster, and truffle all share dimethyl sulfide — the sulfurous compound spanning allium, marine bivalve, and earthy fungal chemistry — creating a three-way alignment that produces the most complex savory-earthy-marine bivalve preparation possible. The triple umami (garlic allicin amplifiers, oyster glutamates, truffle aroma) compounds intensity.",
     "Truffle Garlic Oyster Tartare",
     ["Shuck and chop oysters; mix with minced garlic, truffle oil, and a pinch of fleur de sel.", "Season with white pepper and a squeeze of lemon; mound in oyster shells over ice.", "Shave fresh truffle over each; serve with cold champagne immediately."]),

    ("garlic","oyster","vanilla",
     "Garlic and oyster share dimethyl sulfide while vanilla's vanillin sweetness applies the sweet-salt principle to oyster's brine and softens garlic's allicin pungency through sweet-compound modulation. The trio creates a refined baked oyster where vanilla bridges allium and marine registers.",
     "Vanilla Garlic Baked Oysters",
     ["Make a vanilla-garlic butter: roasted garlic, vanilla bean seeds, cold butter, and fleur de sel.", "Shuck oysters into shells; top each with vanilla-garlic butter.", "Bake at 450°F for 5 minutes until butter is melted and oysters just cooked; serve immediately."]),

    ("garlic","parmesan","rose",
     "Garlic and Parmesan share dimethyl sulfide while rose's 2-phenylethanol and Parmesan's fermentation esters share rosy-floral compound chemistry — rose connecting to Parmesan through shared phenylacetaldehyde and 2-phenylethanol. Garlic's allium depth grounds rose's floral delicacy into a coherent savory-aromatic preparation.",
     "Rose Garlic Parmesan Flatbread",
     ["Make garlic Parmesan flatbread; top with shaved Parmesan and roasted garlic paste.", "Add dried rose petals and a drizzle of rose-infused olive oil.", "Bake until Parmesan is bubbling; the rose lifts garlic-Parmesan into an unexpected aromatic register."]),
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
print(f"Batch 045 done: inserted {len(TRIPLETS)} triplets.")
