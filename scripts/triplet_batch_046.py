#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("garlic","parmesan","salmon",
     "Garlic, Parmesan, and salmon all share dimethyl sulfide — the sulfurous compound spanning allium, aged dairy, and marine fish — creating a three-way alignment that is the flavor foundation of Italian garlic-Parmesan crusted salmon. Garlic's allium sharpness is rounded by Parmesan's umami while both suppress salmon's trimethylamine.",
     "Garlic Parmesan Crusted Salmon",
     ["Mix grated Parmesan with minced garlic, breadcrumbs, lemon zest, and olive oil.", "Press firmly onto salmon fillets; bake at 400°F for 12 minutes until crust is golden.", "Serve with lemon and garlic aioli; the Parmesan-garlic crust creates intense savory depth."]),

    ("garlic","parmesan","strawberry",
     "Garlic and Parmesan share dimethyl sulfide while Parmesan and strawberry share furaneol — the sweet-caramel compound in both aged cheese and ripe strawberry. Garlic's allium pungency contrasts strawberry's sweetness through savory-sweet opposition while Parmesan bridges both through its dual compound connections.",
     "Strawberry Garlic Parmesan Bruschetta",
     ["Macerate sliced strawberries with minced garlic, balsamic, and a pinch of salt 10 minutes.", "Toast sourdough; top with Parmesan shavings and the strawberry-garlic mixture.", "The garlic's pungency and Parmesan's umami give the sweet strawberry unexpected savory depth."]),

    ("garlic","parmesan","tomato",
     "Garlic, Parmesan, and tomato together form the foundational flavor of Italian cooking — garlic and tomato share dimethyl sulfide and acetic acid, Parmesan and tomato share furaneol and acetic acid — creating overlapping compound connections through the entire trio. This is the chemistry of marinara, pizza, bruschetta, and every Italian pasta sauce.",
     "Classic Garlic Parmesan Tomato Pasta",
     ["Sauté sliced garlic in olive oil; add crushed San Marzano tomatoes and simmer 25 minutes.", "Toss with al dente pasta; off heat stir in cold butter and generous Parmesan.", "Tear in fresh basil; plate with more Parmesan and a final drizzle of olive oil."]),

    ("garlic","parmesan","truffle",
     "Garlic, Parmesan, and truffle all share dimethyl sulfide — the sulfurous compound in allium, aged dairy, and earthy fungus — while Parmesan and truffle additionally share phenylacetaldehyde. The double-overlap creates the most complete umami-earthy-allium preparation, driving Italian white truffle pasta with garlic and Parmesan.",
     "Truffle Garlic Parmesan Pasta",
     ["Sauté minced garlic in truffle butter until fragrant; add pasta water.", "Toss al dente pasta in the truffle-garlic sauce; off heat beat in cold Parmesan.", "Plate; shave generous fresh truffle and grate more Parmesan over immediately."]),

    ("garlic","parmesan","vanilla",
     "Garlic and Parmesan share dimethyl sulfide while Parmesan and vanilla share vanillin and furaneol — the sweet-lactonic compounds in aged cheese and cured vanilla bean. Garlic's roasted sweetness bridges the allium and vanilla registers when cooked long, creating an unexpected savory-sweet compound butter.",
     "Vanilla Garlic Parmesan Compound Butter",
     ["Beat softened butter with roasted garlic, vanilla bean seeds, finely grated Parmesan, and salt.", "Refrigerate in a log; slice into rounds.", "Melt over pasta, risotto, or grilled chicken — the vanilla rounds garlic and Parmesan into a cohesive whole."]),

    ("garlic","rose","salmon",
     "Garlic and salmon share dimethyl sulfide while rose's 2-phenylethanol and geraniol suppress salmon's trimethylamine through floral displacement — a second TMA suppressor alongside garlic's allium transformation. Garlic's roasted sweetness grounds rose's floral delicacy into a coherent Persian-Mediterranean salmon preparation.",
     "Rose Garlic Salmon",
     ["Marinate salmon with rose water, garlic, saffron, and lemon; bake at 400°F for 12 minutes.", "Make a rose-garlic sauce from the marinade reduced with cream.", "Serve garnished with dried rose petals; the garlic anchors rose's perfume into savory territory."]),

    ("garlic","rose","strawberry",
     "Garlic's allium pungency contrasts with rose's 2-phenylethanol and strawberry's furaneol sweetness — savory against double-sweet-floral — while garlic's roasted sweetness creates an unexpected bridge to both floral registers when cooked until caramelized. The trio appears in Persian-style strawberry-rose preparations with garlic depth.",
     "Strawberry Rose Garlic Gastrique",
     ["Cook strawberries with roasted garlic, rose water, and balsamic until jammy and thick.", "Strain; reduce until syrupy and season with salt and pepper.", "Serve as a finishing sauce for duck breast or seared foie gras."]),

    ("garlic","rose","tomato",
     "Garlic and tomato share dimethyl sulfide and acetic acid — the Mediterranean cooking foundation — while rose's 2-phenylethanol softens tomato's acidity through floral aromatic displacement. Garlic grounds rose's delicate perfume into a coherent savory-floral tomato preparation appearing in Turkish rose-tomato preparations.",
     "Rose Garlic Tomato Jam",
     ["Cook ripe tomatoes with sliced garlic and sugar until thick; add rose water off heat.", "Simmer briefly; the rose softens the tomato-garlic savory combination into a perfumed jam.", "Cool and jar; serve with cheese or use as a glaze for roasted meats."]),

    ("garlic","rose","truffle",
     "Garlic and truffle share dimethyl sulfide while rose and truffle share phenylacetaldehyde — the rosy-fermented compound in both — creating a compound chain where garlic's allium depth and rose's floral sweetness both connect to truffle's earthy complexity. The trio creates a bold luxury preparation.",
     "Rose Truffle Garlic Butter",
     ["Beat softened butter with truffle paste, roasted garlic, rose water, and flaky salt.", "Refrigerate in a log; slice into rounds.", "Melt over warm risotto or grilled steak — the rose and garlic bracket truffle's earthiness."]),

    ("garlic","rose","vanilla",
     "Garlic's allium pungency contrasts with both rose's 2-phenylethanol floral sweetness and vanilla's vanillin warmth while garlic's roasted sweetness bridges both registers when caramelized. Rose and vanilla share linalool and 2-phenylethanol, creating a double-floral connection that garlic grounds into savory territory.",
     "Vanilla Rose Roasted Garlic Spread",
     ["Roast garlic until sweet and caramelized; squeeze cloves into a bowl.", "Add vanilla bean seeds, rose water, and cream cheese; blend smooth.", "Season with salt; serve with flatbread or crackers — the trio creates an aromatic sweet-savory dip."]),

    ("garlic","salmon","strawberry",
     "Garlic and salmon share dimethyl sulfide while strawberry's furaneol sweetness suppresses salmon's trimethylamine and garlic's cooked sweetness bridges the allium and fruit registers. The trio creates a bold glazed salmon preparation where garlic's savory depth and strawberry's sweetness work in tandem against marine notes.",
     "Strawberry Garlic Glazed Salmon",
     ["Cook strawberries with garlic, balsamic, and honey into a thick glaze.", "Brush salmon fillets; bake at 425°F for 10 minutes, glazing halfway through.", "Garnish with fresh strawberry; the garlic's savory depth prevents the sweet glaze from being cloying."]),

    ("garlic","salmon","tomato",
     "Garlic, salmon, and tomato share dimethyl sulfide and acetic acid — the sulfurous-tart compound family — creating a Mediterranean flavor alignment that drives Italian salmon al pomodoro, Greek fish plaki, and Spanish salmon with tomato and garlic. Tomato's acidity suppresses salmon's TMA while garlic adds allium depth.",
     "Garlic Tomato Braised Salmon",
     ["Sauté garlic in olive oil; add crushed tomatoes and simmer 10 minutes.", "Nestle salmon fillets into the sauce; cover and cook gently 8 minutes.", "Serve with fresh basil and crusty bread; the garlic-tomato sauce suppresses marine notes perfectly."]),

    ("garlic","salmon","truffle",
     "Garlic, salmon, and truffle all share dimethyl sulfide — the sulfurous compound spanning allium, marine fish, and earthy fungus — creating a three-way alignment that drives Italian black truffle salmon preparations where garlic provides the allium bridge. The combination is intensely savory and aromatic.",
     "Truffle Garlic Salmon",
     ["Make truffle-garlic sauce: sauté garlic in truffle butter, add white wine and cream; reduce.", "Sear salmon skin-side down until crisp; finish in the oven 8 minutes.", "Plate over the truffle-garlic sauce; shave fresh truffle over generously."]),

    ("garlic","salmon","vanilla",
     "Garlic and salmon share dimethyl sulfide while vanilla's vanillin sweetness suppresses salmon's trimethylamine and vanilla's furaneol bridges to garlic's roasted-sweet register when caramelized. The trio creates an elegant French-technique salmon where vanilla's unexpected sweetness rounds allium sharpness.",
     "Vanilla Garlic Poached Salmon",
     ["Make a court bouillon with garlic, split vanilla bean, white wine, and aromatics.", "Poach salmon at barely a simmer for 10 minutes until just cooked.", "Serve with a vanilla-garlic beurre blanc; the vanilla softens garlic and suppresses marine notes."]),

    ("garlic","strawberry","tomato",
     "Garlic and tomato share dimethyl sulfide and acetic acid while strawberry and tomato share furaneol — the sweet-caramel compound in both ripe fruit and ripe tomato. Garlic's allium pungency contrasts strawberry's sweetness while both tomato and strawberry share the furaneol compound that unifies the fruit-vegetable combination.",
     "Strawberry Garlic Tomato Salsa",
     ["Dice ripe tomatoes and strawberries; toss with minced garlic, lime juice, and cilantro.", "Season with salt and a pinch of sugar if tomatoes are acidic.", "Serve with corn chips or over grilled fish; the garlic ties tomato and strawberry into savory territory."]),

    ("garlic","strawberry","truffle",
     "Garlic and truffle share dimethyl sulfide while strawberry and truffle share phenylacetaldehyde through separate fermentation chemistry. Garlic's allium grounds the unusual fruity-earthy truffle-strawberry combination into savory territory, creating a sophisticated luxury gastrique.",
     "Strawberry Truffle Garlic Sauce",
     ["Cook strawberries with garlic and a drizzle of truffle oil until jammy.", "Add aged balsamic and reduce to a syrupy consistency; season with salt.", "Serve over seared duck or foie gras; the garlic and truffle transform strawberry into a savory sauce."]),

    ("garlic","strawberry","vanilla",
     "Garlic's allium pungency contrasts with both strawberry's furaneol and vanilla's vanillin sweetness — savory against double-sweet — while garlic's roasted sweetness when caramelized creates a bridge to both fruit and spice registers. The unusual trio drives sophisticated savory-sweet preparations.",
     "Vanilla Strawberry Roasted Garlic Dip",
     ["Roast garlic until sweet; blend with cream cheese, vanilla bean seeds, and macerated strawberry.", "Season with salt and lemon; the sweetness rounds garlic's sharpness into a creamy dip.", "Serve with flatbread and fresh strawberries for dipping — unexpected but aromatic."]),

    ("garlic","tomato","truffle",
     "Garlic, tomato, and truffle all share dimethyl sulfide and phenylacetaldehyde — the sulfurous and rosy-fermented compound pair connecting allium, ripe vegetable, and earthy fungus. This three-way overlap drives Italian truffle-tomato pasta where garlic provides the allium bridge that ties tomato's savory acidity to truffle's earthy depth.",
     "Truffle Garlic Tomato Pasta",
     ["Sauté garlic in truffle butter; add crushed San Marzano tomatoes and simmer 20 minutes.", "Toss with al dente pasta; shave truffle over generously off heat.", "The garlic bridges tomato's acidity and truffle's earthiness into a complete savory register."]),

    ("garlic","tomato","vanilla",
     "Garlic and tomato share dimethyl sulfide and acetic acid while tomato and vanilla share furaneol — the sweet-caramel compound in both ripe tomato and cured vanilla bean. Garlic's allium pungency grounds vanilla's sweetness while tomato's furaneol bridges the two through the shared sweet-caramel compound.",
     "Vanilla Garlic Tomato Sauce",
     ["Sauté garlic slowly in olive oil; add crushed tomatoes and a split vanilla bean.", "Simmer 25 minutes until thick; remove vanilla bean and season with salt.", "Serve over pasta; the vanilla amplifies tomato's natural sweetness and rounds garlic's pungency."]),

    ("garlic","truffle","vanilla",
     "Garlic and truffle share dimethyl sulfide while truffle and vanilla share vanillin — the lactonic-sweet compound that black truffle produces through enzymatic fermentation. Garlic's allium pungency grounds vanilla's sweetness and truffle's earthiness into a rich savory compound with unexpected lactonic depth.",
     "Truffle Vanilla Garlic Pasta",
     ["Sauté garlic in truffle butter with vanilla bean seeds; toss with al dente pasta.", "Add pasta water; beat until glossy and season with salt.", "Shave fresh truffle; finish with a curl of vanilla bean pod — allium, earthy, and sweet simultaneously."]),
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
print(f"Batch 046 done: inserted {len(TRIPLETS)} triplets.")
