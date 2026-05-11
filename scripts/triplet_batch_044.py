#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("garlic","lamb","salmon",
     "Garlic, lamb, and salmon share dimethyl sulfide — the sulfurous compound spanning allium, animal fat, and marine fish through their respective metabolisms — creating a three-way sulfurous alignment that is the basis of surf-and-turf preparations with garlic as the aromatic connector. Garlic's roasted sweetness bridges the gamey and marine registers.",
     "Garlic Lamb and Salmon Surf & Turf",
     ["Make a roasted garlic compound butter: roasted garlic, herbs, and cold butter mashed together.", "Sear lamb chops and salmon fillets separately to proper doneness.", "Plate side by side; top both with a slice of garlic butter melting over each protein."]),

    ("garlic","lamb","strawberry",
     "Garlic and lamb share dimethyl sulfide while strawberry's furaneol sweetness suppresses lamb's gamey 4-methyloctanoic acid through sweet-fat modulation — the same mechanism as fruit in a tagine — and garlic's allicin provides sharp contrast that strawberry's sweetness rounds. The trio appears in Scandinavian lamb with berry preparations.",
     "Strawberry Garlic Lamb Chops",
     ["Make a strawberry-garlic gastrique: cook strawberries with minced garlic, vinegar, and sugar.", "Sear lamb chops until crusted; rest 5 minutes.", "Drizzle the strawberry-garlic sauce over; the sweetness rounds garlic and suppresses lamb's gaminess."]),

    ("garlic","lamb","tomato",
     "Garlic, lamb, and tomato share dimethyl sulfide and acetic acid — sulfurous and tart compounds connecting allium, animal fat, and acid fruit. This is the flavor chemistry of Greek stifado, Italian ragù d'agnello, and Middle Eastern lamb-tomato stews — arguably the most important lamb flavor triangle in Mediterranean cooking.",
     "Lamb Garlic Tomato Stew",
     ["Brown lamb pieces with whole garlic cloves until deeply caramelized.", "Add crushed tomatoes, red wine, and herbs; braise at 325°F for 2 hours until tender.", "Adjust seasoning; serve over orzo or crusty bread with fresh herbs."]),

    ("garlic","lamb","truffle",
     "Garlic, lamb, and truffle all share dimethyl sulfide — the sulfurous compound spanning allium, animal fat, and earthy fungal chemistry — creating the maximum savory sulfurous alignment possible. The combination produces a deeply indulgent luxury lamb preparation where garlic's allium sharpness is rounded by truffle's earthy depth.",
     "Truffle Garlic Rack of Lamb",
     ["Rub rack of lamb with truffle salt, roasted garlic paste, and herbs; press firmly.", "Roast at 425°F for 20 minutes to medium-rare; rest 8 minutes before carving.", "Plate over truffle mashed potato; shave fresh truffle over and drizzle truffle-garlic jus."]),

    ("garlic","lamb","vanilla",
     "Garlic and lamb share dimethyl sulfide while vanilla's vanillin and furaneol sweetness contrasts lamb's gamey acids through sweet-fat modulation — and garlic's roasted sweetness bridges the allium and lactonic-sweet registers. The trio appears in Moroccan lamb preparations where sweet spices and vanilla deepen slow-cooked sauce.",
     "Vanilla Garlic Moroccan Lamb",
     ["Brown lamb with garlic and caramelized onion; add a split vanilla bean, sweet spices, and stock.", "Braise at 300°F for 2 hours; the vanilla deepens garlic's sweetness and rounds the gamey lamb.", "Serve over couscous with toasted almonds and dried apricots."]),

    ("garlic","lavender","lemon",
     "Garlic and lavender create a bold Provençal contrast — allium pungency against floral linalool — while lemon's citric acid moderates both garlic's sharpness through pH adjustment and amplifies lavender's herbal freshness through citrus-terpene alignment. The trio defines classic Provençal herbes de Provence applications.",
     "Lavender Garlic Lemon Roasted Chicken",
     ["Make a rub: roasted garlic paste, dried lavender, lemon zest, olive oil, and flaky salt.", "Rub under and over chicken skin; marinate 4 hours or overnight.", "Roast at 375°F until golden; the lavender and lemon lift garlic's pungency beautifully."]),

    ("garlic","lavender","mint",
     "Garlic, lavender, and mint all share linalool — with lavender and mint sharing the compound as their dominant terpene and garlic producing trace linalool through Maillard transformation when roasted. The three-way linalool alignment bridges allium pungency, floral warmth, and cooling freshness into a complete Provençal herb profile.",
     "Lavender Mint Garlic Lamb Skewers",
     ["Make a marinade: dried lavender, fresh mint, minced garlic, lemon, and olive oil.", "Marinate lamb cubes 4 hours; thread onto skewers.", "Grill over high heat until charred; serve with mint-lavender yogurt and warm pita."]),

    ("garlic","lavender","oyster",
     "Garlic and oyster share dimethyl sulfide — the sulfurous compound in both — while lavender's linalool provides floral bridging between garlic's allium pungency and oyster's marine brine. The trio creates a sophisticated Provençal baked oyster where garlic's savory depth and lavender's floral warmth complement marine umami.",
     "Lavender Garlic Baked Oysters",
     ["Make a compound butter: minced garlic, dried lavender, lemon zest, and cold butter.", "Shuck oysters into shells; top each with a small disc of lavender-garlic butter.", "Bake at 450°F for 5 minutes until butter is melted and oysters just cooked."]),

    ("garlic","lavender","parmesan",
     "Garlic and Parmesan share dimethyl sulfide while lavender's linalool provides floral bridging between garlic's allium pungency and Parmesan's fermented-dairy depth. The Provençal-Italian combination creates a sophisticated garlic-herb bread preparation where lavender's floral note elevates the standard garlic-Parmesan register.",
     "Lavender Garlic Parmesan Bread",
     ["Beat softened butter with roasted garlic, dried lavender, grated Parmesan, and herbs.", "Spread generously on thick sourdough slices; bake at 400°F until bubbling and golden.", "Broil briefly to crisp the top; the lavender lifts garlic-Parmesan into a Provençal register."]),

    ("garlic","lavender","rose",
     "Garlic's allium pungency contrasts with both lavender's linalool floral warmth and rose's 2-phenylethanol perfumed sweetness through a savory-floral opposition, while lavender and rose share linalool and create a double-floral register. Garlic's roasted notes ground the double-floral combination into a coherent savory-aromatic territory.",
     "Rose Lavender Garlic Lamb Tagine",
     ["Brown lamb with garlic; add rose water, dried lavender, saffron, and pomegranate molasses.", "Braise at 300°F for 1.5 hours until tender; the rose-lavender-garlic creates complex floral-savory depth.", "Serve over couscous with rose petals and fresh herbs."]),

    ("garlic","lavender","salmon",
     "Garlic and salmon share dimethyl sulfide while lavender's linalool independently suppresses salmon's trimethylamine through floral aromatic displacement, and garlic's roasted sweetness bridges the allium and marine registers. The trio creates a sophisticated Provençal salmon preparation with double TMA suppression.",
     "Lavender Garlic Salmon",
     ["Rub salmon fillets with dried lavender, garlic, lemon zest, and olive oil; rest 20 minutes.", "Bake at 400°F for 12 minutes; the lavender and garlic create a fragrant aromatic crust.", "Serve with lavender-garlic beurre blanc and a squeeze of fresh lemon."]),

    ("garlic","lavender","strawberry",
     "Garlic's allium pungency and lavender's linalool floral warmth create a bold savory-floral contrast while strawberry's furaneol sweetness provides the contrast element that grounds both — sweet-savory opposition with garlic and sweet-floral connection with lavender. The trio appears in Provençal strawberry-lavender preparations with garlic-herb context.",
     "Strawberry Lavender Garlic Compote",
     ["Cook strawberries with a crushed garlic clove, dried lavender, and a splash of balsamic.", "Remove garlic after 2 minutes of simmering; continue until thick and jammy.", "Cool; serve with cheese or as a gastrique for duck or lamb."]),

    ("garlic","lavender","tomato",
     "Garlic and tomato share acetic acid and dimethyl sulfide — the sulfurous-tart compound foundation of Mediterranean cooking — while lavender's linalool provides Provençal floral bridging that lifts the classic garlic-tomato combination into a more aromatic, Southern French register. The trio is the flavor of tian Provençal.",
     "Lavender Garlic Tomato Tian",
     ["Slice tomatoes and layer in a baking dish with thinly sliced garlic and a sprinkle of dried lavender.", "Drizzle with good olive oil and season with salt; add sprigs of thyme.", "Bake at 325°F for 90 minutes until deeply caramelized and concentrated."]),

    ("garlic","lavender","truffle",
     "Garlic and truffle share dimethyl sulfide — the sulfurous compound in both allium and earthy fungus — while lavender's linalool and anisaldehyde bridge garlic's allium pungency to truffle's anise-adjacent earthy character through floral-herbal aromatic mediation. The trio creates the most complex savory Provençal luxury preparation.",
     "Truffle Lavender Garlic Butter",
     ["Beat softened butter with truffle paste, roasted garlic, dried lavender, and flaky salt.", "Refrigerate in a log until firm; slice into rounds.", "Melt over warm steak, risotto, or scrambled eggs — the lavender bridges allium and earthy truffle."]),

    ("garlic","lavender","vanilla",
     "Garlic's allium pungency contrasts with vanilla's vanillin sweetness through a bold savory-sweet opposition while lavender's linalool provides floral bridging between both extremes. Roasted garlic's sweetness creates an unexpected bridge to vanilla's lactonic warmth, and lavender's linalool connects to vanilla's floral-herbal terpene family.",
     "Vanilla Lavender Roasted Garlic Sauce",
     ["Roast whole garlic heads until soft and sweet; squeeze out cloves into a blender.", "Add cream, a split vanilla bean scraped, and dried lavender; blend smooth.", "Strain; warm gently and serve as a sauce over pasta or roasted vegetables."]),

    ("garlic","lemon","mint",
     "Garlic and lemon share acetic acid while lemon's citric acid moderates garlic's allicin pungency through pH adjustment — the principle behind lemon-garlic dressings — and mint's menthol provides cooling contrast that amplifies lemon's brightness through olfactory cooling. The trio defines Levantine herb sauces and Greek chimichurri-style preparations.",
     "Lemon Mint Garlic Sauce",
     ["Blend garlic, fresh mint, lemon juice, lemon zest, and olive oil until smooth.", "Season with salt; add a splash of water if too thick.", "Serve as a sauce for grilled lamb, chicken, or vegetables — bright, cooling, and pungent."]),

    ("garlic","lemon","oyster",
     "Garlic and oyster share dimethyl sulfide while lemon's citric acid suppresses oyster's trimethylamine marine notes — the lemon-oyster pairing is universal for this reason — and garlic's allicin adds the sharp pungency that makes classic oyster mignonette work. The trio is the foundational flavor of garlic-butter baked oysters with lemon.",
     "Garlic Lemon Baked Oysters",
     ["Make garlic-lemon butter: minced garlic, lemon zest, lemon juice, and cold butter.", "Shuck oysters into half shells; top each with a generous amount of garlic-lemon butter.", "Bake at 450°F for 5-6 minutes until butter is bubbling and edges just curl."]),

    ("garlic","lemon","parmesan",
     "Garlic and Parmesan share dimethyl sulfide while lemon's citric acid cuts Parmesan's butyric fat through acid-fat balance and moderates garlic's allicin through pH adjustment simultaneously. The trio is the precise aromatic chemistry of lemon-garlic pasta with Parmesan — arguably Italian cooking's single most important three-ingredient compound.",
     "Garlic Lemon Parmesan Pasta",
     ["Sauté minced garlic in olive oil; toss with al dente pasta, lemon zest, and lemon juice.", "Off heat add cold butter and grated Parmesan; beat until glossy.", "Plate; finish with more Parmesan, lemon zest, fresh parsley, and cracked black pepper."]),

    ("garlic","lemon","rose",
     "Garlic and lemon share acetic acid while lemon's geraniol directly overlaps with rose's geraniol — sharing a citrus-floral terpene — creating a lemon-rose compound bridge that garlic's savory pungency grounds into a coherent Persian-Mediterranean preparation. The trio drives sophisticated rose water-lemon-garlic marinades.",
     "Rose Lemon Garlic Chicken",
     ["Marinate chicken in rose water, lemon juice, minced garlic, saffron, and olive oil overnight.", "Roast at 375°F until golden; baste with marinade twice while cooking.", "Serve with saffron rice and a garnish of dried rose petals."]),

    ("garlic","lemon","salmon",
     "Garlic and salmon share dimethyl sulfide while lemon's citric acid suppresses salmon's trimethylamine through acid-driven TMA neutralization — lemon's most important function with fish. Garlic's roasted sweetness bridges the allium and marine registers into a complete Mediterranean salmon preparation.",
     "Garlic Lemon Baked Salmon",
     ["Lay salmon in a baking dish; top with sliced garlic, lemon slices, and a drizzle of olive oil.", "Season with herbs and salt; bake at 400°F for 14 minutes until just cooked through.", "Squeeze fresh lemon over immediately on removing from the oven; serve with roasted vegetables."]),
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
print(f"Batch 044 done: inserted {len(TRIPLETS)} triplets.")
