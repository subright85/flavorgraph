#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("coffee","garlic","lemon",
     "Coffee's roasted pyrazines and garlic's allicin both produce pungency — bitter and sharp respectively — while lemon's citric acid acts as the universal moderator for both compounds, reducing perceived bitterness through pH adjustment and converting allicin into less pungent breakdown products with heat. Lemon's limonene also adds brightness that lifts coffee's heavy register.",
     "Espresso Garlic Lemon Marinade",
     ["Whisk together cold brew espresso, minced garlic, lemon juice, lemon zest, and olive oil.", "Add herbs and a pinch of salt; use as a bold marinade for chicken or pork, 2-4 hours.", "Grill or roast; the lemon brightens the espresso while garlic provides savory depth."]),

    ("coffee","garlic","mint",
     "Coffee's bitter pyrazines contrast with mint's menthol cooling through dark-cool opposition — the same mechanism as mocha mint — while garlic's dimethyl sulfide provides savory grounding that anchors the aromatic combination into a coherent savory territory. The trio appears in Middle Eastern-influenced coffee-herb preparations for lamb or chicken.",
     "Espresso Garlic Mint Lamb Marinade",
     ["Blend cold brew coffee with garlic paste, fresh mint, olive oil, and lemon juice.", "Marinate lamb chops 4 hours in the refrigerator; bring to room temperature before grilling.", "Grill over high heat; serve with a mint-yogurt sauce and cucumber."]),

    ("coffee","garlic","oyster",
     "Coffee and oyster share dimethyl sulfide — the sulfurous compound in roasted coffee and marine bivalves — while garlic's allicin and dimethyl sulfide add a second sulfurous layer that bridges the two registers. The trio creates a bold bivalve preparation where coffee's bitter depth amplifies oyster's umami and garlic provides savory sharp contrast.",
     "Espresso Garlic Oyster Pan Sauté",
     ["Sauté minced garlic in butter until golden; add shucked oysters with their liquor.", "Add a shot of brewed espresso and cook 2 minutes until oysters are just cooked through.", "Season with salt, lemon juice, and fresh parsley; serve immediately over toasted sourdough."]),

    ("coffee","garlic","parmesan",
     "Coffee and Parmesan share dimethyl sulfide — sulfurous compounds in roasted coffee and aged dairy — while garlic's allicin adds pungent sharpness that converts to sweet-savory roasted garlic notes, bridging coffee's bitter complexity and Parmesan's salty umami. The unusual trio creates a bold savory espresso-cheese preparation.",
     "Espresso Garlic Parmesan Crostini",
     ["Rub crostini with raw garlic; brush with a thin wash of concentrated cold brew.", "Top with shaved Parmesan and drizzle with good olive oil.", "Broil until Parmesan bubbles and edges crisp; the espresso adds a roasted note beneath the cheese."]),

    ("coffee","garlic","rose",
     "Coffee's roasted pyrazines and rose's 2-phenylethanol create a bold dark-floral contrast — bitter and perfumed — while garlic's dimethyl sulfide provides savory grounding that prevents the combination from being too confectionery and anchors it into a Persian-influenced savory-aromatic territory. The trio appears in sophisticated coffee-rose lamb preparations.",
     "Rose Espresso Garlic Chicken Marinade",
     ["Blend roasted garlic paste with rose water, cold brew coffee, olive oil, and saffron.", "Marinate chicken 6 hours; the rose and espresso create an aromatic depth.", "Grill or roast; garnish with dried rose petals and serve with saffron rice."]),

    ("coffee","garlic","salmon",
     "Coffee and salmon share dimethyl sulfide — sulfurous compounds in both — while garlic's allicin converts to sweet cooked-garlic notes that bridge coffee's roasted bitterness and salmon's fatty richness. The trio creates a bold coffee-crusted salmon preparation where garlic's sweetness rounds the dark-bitter-marine combination.",
     "Espresso Garlic Crusted Salmon",
     ["Make a rub: finely ground espresso, roasted garlic powder, brown sugar, salt, and smoked paprika.", "Press firmly onto salmon fillets; rest 15 minutes.", "Sear skin-side down in a very hot pan 4 minutes; flip and finish 3 minutes until just cooked."]),

    ("coffee","garlic","strawberry",
     "Coffee's furfural shares a Maillard lineage with strawberry's furaneol — both caramel-adjacent compounds — while garlic's dimethyl sulfide provides savory contrast that transforms the coffee-strawberry sweet-bitter combination into a bold gastrique territory. The unusual trio appears in sophisticated strawberry-balsamic-espresso reductions for meat.",
     "Strawberry Espresso Garlic Gastrique",
     ["Cook diced strawberries with garlic, a shot of espresso, and balsamic until thick and jammy.", "Strain; reduce further until syrupy and glossy; season with salt and a pinch of pepper.", "Serve as a bold finishing sauce for duck breast or seared foie gras."]),

    ("coffee","garlic","tomato",
     "Coffee and tomato share pyrazines and phenylacetaldehyde — Maillard-roasted and rosy-fermented compounds that both develop through roasting and fermentation — while garlic's dimethyl sulfide provides the sulfurous savory foundation that Italian cooking has built upon for centuries. The trio is the flavor logic of slow-roasted tomato sauce with espresso depth.",
     "Espresso Garlic Tomato Sauce",
     ["Sauté garlic slowly in olive oil; add crushed tomatoes and a shot of brewed espresso.", "Simmer 30 minutes until thick and concentrated; the espresso deepens the tomato's umami.", "Season with salt and basil; serve over pasta or as a bold pizza sauce."]),

    ("coffee","garlic","truffle",
     "Coffee and truffle share dimethyl sulfide — sulfurous compounds in roasted coffee and earthy fungal fermentation — while garlic's dimethyl sulfide adds a third tier of the same sulfurous compound family, creating a three-way alignment of the same compound at different aromatic intensities. The trio creates a bold Italian-influenced umami preparation.",
     "Truffle Espresso Garlic Pasta",
     ["Sauté minced garlic in truffle butter; add a small shot of espresso and pasta water.", "Toss al dente pasta until glossy; season with salt and cracked pepper.", "Plate; shave fresh truffle generously and dust with espresso-salt to finish."]),

    ("coffee","garlic","vanilla",
     "Coffee and vanilla share furfural and vanillin — caramel and lactonic compounds from roasting and curing — while garlic's allicin provides pungent contrast that roasted garlic converts to sweet-savory notes. The trio appears in bold savory vanilla-coffee preparations where garlic's sweetness bridges the bitter-lactonic coffee-vanilla combination.",
     "Vanilla Espresso Garlic Chicken",
     ["Make a marinade: vanilla bean seeds, roasted garlic paste, cold brew coffee, olive oil, and herbs.", "Marinate chicken 6 hours; grill or roast until deeply caramelized.", "Serve with a vanilla-coffee au jus made from the roasting juices deglazed with espresso."]),

    ("coffee","lamb","lavender",
     "Coffee's pyrazines and furfural — Maillard-roasted compounds — moderate lamb's gamey 4-methyloctanoic acid through the same bitter-fat interaction as in coffee-rubbed meat preparations, while lavender's linalool softens lamb's gameyness through a second floral-aromatic displacement mechanism. Double gamey-note suppression creates the most aromatic lamb preparation possible.",
     "Lavender Espresso Braised Lamb",
     ["Brown lamb shanks; add dried lavender, brewed espresso, garlic, and red wine.", "Braise at 325°F for 3 hours until meltingly tender; reduce sauce until glossy.", "Serve with the coffee-lavender jus and a garnish of fresh lavender and herbs."]),

    ("coffee","lamb","lemon",
     "Coffee's bitter pyrazines interact with lamb's gamey 4-methyloctanoic acid through bitter-fat modulation — coffee suppresses gamey notes in the same mechanism as in meat rubs — while lemon's citric acid brightens both coffee's bitterness and lamb's gameyness through pH-driven aromatic adjustment. The trio creates a bright, acid-lifted coffee-lamb preparation.",
     "Lemon Espresso Lamb Chops",
     ["Make a rub: ground espresso, lemon zest, garlic, oregano, and olive oil.", "Rest lamb chops at room temperature 30 minutes; grill over high heat until charred.", "Serve with a squeeze of fresh lemon and a drizzle of cold brew espresso dressing."]),

    ("coffee","lamb","mint",
     "Coffee's bitter pyrazines add roasted depth to lamb's gamey richness — the same mechanism as espresso-rubbed barbecue — while mint's menthol suppresses lamb's 4-methyloctanoic acid through olfactory masking and provides cooling contrast to coffee's warming bitterness. The trio creates a bold lamb preparation with complete aromatic balance.",
     "Espresso Mint Grilled Lamb",
     ["Make a rub: ground espresso, fresh mint (muddle into the mix), garlic, and olive oil.", "Coat lamb chops and grill over very high heat until charred and fragrant.", "Rest; serve with a mint-espresso yogurt sauce and lemon wedges."]),

    ("coffee","lamb","oyster",
     "Coffee and oyster share dimethyl sulfide — the sulfurous compound in roasted coffee and marine bivalves — while lamb's dimethyl sulfide adds a third expression of the same sulfurous compound family. Coffee's bitter roasted depth bridges the unusual lamb-oyster combination through a shared chemical register that spans animal, marine, and roasted food categories.",
     "Espresso Oyster Sauce Braised Lamb",
     ["Brown lamb shoulder; add oyster sauce, brewed espresso, soy, ginger, and garlic.", "Braise at 325°F for 2.5 hours; the espresso deepens the oyster sauce's umami dramatically.", "Serve over steamed rice with blanched greens and a drizzle of the coffee-oyster jus."]),

    ("coffee","lamb","parmesan",
     "Coffee and Parmesan share dimethyl sulfide — sulfurous compounds in both — while lamb and Parmesan share butyric acid and dimethyl sulfide, creating a chain where coffee deepens Parmesan's fermented-dairy depth and Parmesan's umami amplifies coffee's savory register. The trio creates a sophisticated Italian-influenced lamb preparation with coffee depth.",
     "Espresso Parmesan Braised Lamb Ragu",
     ["Brown ground lamb; add espresso, crushed tomatoes, and red wine; simmer 45 minutes.", "Off heat stir in grated Parmesan to bind and enrich the sauce.", "Toss with pappardelle; finish with more Parmesan and a dusting of ground espresso."]),

    ("coffee","lamb","rose",
     "Coffee's pyrazines provide roasted depth while rose's 2-phenylethanol and geraniol soften lamb's gamey 4-methyloctanoic acid through floral aromatic displacement — a dual gamey-note modulation where coffee suppresses through bitterness and rose through floral displacement. The trio drives Persian-influenced lamb preparations with coffee and rose.",
     "Rose Espresso Persian Lamb Stew",
     ["Brown lamb with onion; add rose water, brewed espresso, saffron, and pomegranate molasses.", "Braise 1.5 hours until tender; the rose and coffee create an aromatic complex jus.", "Serve over saffron rice with dried rose petals, pistachios, and a drizzle of pomegranate."]),

    ("coffee","lamb","salmon",
     "Coffee, lamb, and salmon all share dimethyl sulfide — the sulfurous compound spanning roasted coffee, animal fat, and marine fish metabolism — creating a three-way sulfurous alignment across radically different food categories. In small amounts, coffee's bitterness bridges the surf-and-turf combination through shared aromatic chemistry.",
     "Espresso Glazed Surf and Turf",
     ["Make an espresso-soy glaze: brewed espresso, soy sauce, honey, and rice vinegar reduced together.", "Sear lamb loin and salmon separately to proper doneness; brush both with the glaze.", "Plate side by side; the espresso glaze provides a unified aromatic base across both proteins."]),

    ("coffee","lamb","strawberry",
     "Coffee's furfural shares a Maillard lineage with strawberry's furaneol — both caramel-adjacent compounds from different chemistry — while coffee's bitter pyrazines moderate lamb's gamey 4-methyloctanoic acid and strawberry's sweet furaneol provides additional sweet-fat suppression. The triple attack on gaminess produces the cleanest-tasting coffee-lamb preparation.",
     "Strawberry Espresso Glazed Lamb",
     ["Cook strawberries with espresso, balsamic, and sugar into a rich espresso-strawberry glaze.", "Brush lamb chops and grill over high heat, glazing twice while cooking.", "Rest; serve with sliced fresh strawberry and a cold brew espresso drizzle."]),

    ("coffee","lamb","tomato",
     "Coffee and tomato share pyrazines and phenylacetaldehyde — Maillard-roasted and rosy-fermented compounds — while coffee's bitter compounds interact with lamb's gamey acids through the same bitter-fat modulation seen in coffee-rubbed preparations. Tomato's acidity tenderizes lamb while coffee's depth amplifies the long-braise register.",
     "Espresso Tomato Braised Lamb Shoulder",
     ["Brown lamb shoulder pieces; add garlic, crushed tomatoes, a shot of espresso, and spices.", "Braise at 325°F for 2.5 hours until falling apart; reduce sauce until thick.", "Serve over polenta or pasta with fresh herbs and a final drizzle of good olive oil."]),

    ("coffee","lamb","truffle",
     "Coffee and truffle share dimethyl sulfide — sulfurous compounds in roasted coffee and earthy truffle — while lamb's dimethyl sulfide adds a third tier of the same compound, and coffee's pyrazines interact with lamb's gamey acids through bitter-fat modulation. The trio creates the most complex savory combination possible from these three luxury ingredients.",
     "Truffle Espresso Rack of Lamb",
     ["Rub rack of lamb with ground espresso, truffle salt, and herbs; let rest 30 minutes.", "Roast at 425°F for 20 minutes to medium-rare; rest 8 minutes before carving.", "Plate over a truffle-espresso potato purée; shave truffle and drizzle with espresso jus."]),
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
print(f"Batch 036 done: inserted {len(TRIPLETS)} triplets.")
