#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("basil","butter","coffee",
     "Butter and coffee share dimethyl sulfide and acetic acid — fat-soluble roasted compounds that butter carries and amplifies — while basil's linalool and eugenol provide herbal brightness that cuts through the heavy fat-roast combination. Together they create a sophisticated café-herb depth used in modern pastry applications.",
     "Basil Brown Butter Coffee Cake",
     ["Brown butter until deeply nutty, cool slightly, then mix into a standard coffee cake batter.","Fold in finely chopped fresh basil and a shot of espresso to the batter.","Bake at 350°F until golden; serve with espresso glaze and a basil garnish."]),

    ("basil","butter","cucumber",
     "Butter and cucumber share hexanal and linalool — green aldehyde and floral terpene compounds — while basil's eugenol and 2-phenylethanol add a warm spiced-herbal layer that bridges butter's fat richness to cucumber's cool, watery freshness. The trio creates a refined summer flavor that reads as both creamy and garden-fresh.",
     "Basil Butter Cucumber Canapés",
     ["Blend softened butter with finely chopped basil, lemon zest, and a pinch of salt.","Spread generously on thin cucumber rounds or crisp crackers.","Top with a small basil leaf and flaky salt; serve immediately chilled."]),

    ("basil","butter","garlic",
     "Butter and garlic share dimethyl sulfide and acetic acid — sulfurous compounds that butter's fat converts from harsh allicin into sweet, round cooked-garlic notes — while basil's linalool and eugenol add the herbal-spice lift that defines classic Italian soffritto. This is the aromatics base of an entire culinary tradition.",
     "Garlic Basil Butter Pasta",
     ["Melt butter over medium heat, add sliced garlic and cook until just golden.","Add al dente pasta and a splash of pasta water, toss to coat completely.","Remove from heat, fold in torn fresh basil, and serve with Parmesan."]),

    ("basil","butter","lamb",
     "Butter and lamb share butyric acid and dimethyl sulfide — connecting dairy fat to animal fat through shared sulfurous-rich compound families — while basil's linalool and eugenol provide the herbal freshness that suppresses lamb's gamey 4-methyloctanoic acid. The trio creates a rich, herbed preparation where butter acts as the aromatic bridge.",
     "Basil Butter Roasted Lamb Rack",
     ["Mix softened butter with chopped basil, garlic, and lemon zest into a compound butter.","Press the herb butter onto the rack of lamb and rest 20 minutes at room temp.","Roast at 425°F to medium-rare; rest 8 minutes before slicing and serving."]),

    ("basil","butter","lavender",
     "Basil and lavender share linalool, linalyl acetate, and 2-phenylethanol at high concentrations — the dominant floral terpene set in both herbs — while butter's fat acts as the ideal solvent, capturing and extending these volatile aromatics far longer on the palate. The combination produces an intensely perfumed yet grounded compound butter.",
     "Lavender Basil Shortbread",
     ["Cream butter with powdered sugar until pale, add dried lavender and chopped basil.","Mix in flour and a pinch of salt until a cohesive dough forms; chill 30 minutes.","Slice into rounds, bake at 325°F until just set at edges — not browned."]),

    ("basil","butter","lemon",
     "Basil and lemon share linalool and trace geraniol — terpene compounds that both plants produce — while butter's fat emulsifies lemon's citric acid and carries basil's volatile eugenol compounds more effectively to the nose. This classic beurre blanc variation achieves the perfect balance of bright citrus, herbal lift, and silky dairy richness.",
     "Lemon Basil Beurre Blanc",
     ["Reduce white wine, shallots, and lemon juice in a small pan until nearly dry.","Whisk cold butter in off heat piece by piece until glossy and emulsified.","Stir in lemon zest and torn basil just before serving over fish or vegetables."]),

    ("basil","butter","mint",
     "Basil and mint share linalool and 1,8-cineole — complementary terpene compounds — while butter's fat moderates menthol's intensity and carries both herbs' volatile aromatics more effectively than a water-based preparation. The combination creates a layered cool-warm herbal butter where mint refreshes and basil grounds.",
     "Mint Basil Pea Butter Toast",
     ["Blend blanched peas with mint, basil, and softened butter until smooth and bright green.","Spread thickly onto toasted sourdough while still warm from the toaster.","Top with pea shoots, flaky salt, and a squeeze of lemon to finish."]),

    ("basil","butter","oyster",
     "Butter and oyster share dimethyl sulfide and acetic acid — sulfurous and tart compounds linking dairy fat to oceanic brine — while basil's benzaldehyde and linalool provide the herbal aromatic lift that bridges dairy richness to marine mineral character. Butter's fat captures oyster's delicate volatile esters and extends the brine on the palate.",
     "Basil Butter Roasted Oysters",
     ["Make a compound butter with softened butter, basil, garlic, and lemon zest.","Place a small knob on each shucked oyster still in its half-shell on a tray.","Broil 3–4 minutes until butter is bubbling and oyster edges just begin to curl."]),

    ("basil","butter","parmesan",
     "Butter and Parmesan share butyric acid, furaneol, and dimethyl sulfide — overlapping dairy compound sets that together produce richer fat-umami than either alone — while basil's linalool and 2-phenylethanol add the herbal-floral lift essential to the classic Italian combination. This trio defines the finish of great risotto and pasta.",
     "Basil Parmesan Butter Risotto",
     ["Cook arborio rice with stock until creamy and al dente, remove from heat.","Add cold diced butter and finely grated Parmesan off heat, stirring vigorously.","Fold in torn fresh basil just before serving; plate immediately."]),

    ("basil","butter","rose",
     "Basil and rose share 2-phenylethanol, linalool, and benzaldehyde — floral-herbal compounds that butter's fat captures and amplifies — while butter provides the rich creamy medium that bridges the delicate flower and the aromatic herb without either dominating. The result is a perfumed, elegant compound butter suitable for both sweet and savory applications.",
     "Rose Basil Butter on Brioche",
     ["Blend softened butter with rose water, fresh basil, and a pinch of flaky salt.","Shape into a log in plastic wrap and refrigerate until firm.","Serve sliced on warm toasted brioche with a drizzle of wildflower honey."]),

    ("basil","butter","salmon",
     "Butter and salmon share dimethyl sulfide, linalool, and acetic acid — fat-soluble aromatic compounds that connect dairy richness to fatty fish — while basil's 2-phenylethanol and eugenol suppress salmon's trimethylamine (fishy compounds) while adding herbal brightness. Together the trio creates the signature flavor of classic French salmon en papillote.",
     "Salmon with Basil Butter en Papillote",
     ["Place salmon on parchment with a knob of basil compound butter and lemon slices.","Fold into a sealed parcel, crimping edges tightly to trap all the aromatics.","Bake at 400°F for 14 minutes; open at the table to release the fragrant steam."]),

    ("basil","butter","strawberry",
     "Butter and strawberry share furaneol — the key caramel-like compound in strawberry's aroma that browned butter also produces — while basil's linalool and 2-phenylethanol amplify strawberry's own floral esters. The trio creates a summer dessert flavor where browning the butter deepens the strawberry's natural sweetness into something more complex.",
     "Strawberry Brown Butter Galette",
     ["Brown butter until nutty, use to make a rough puff pastry as the base.","Toss sliced strawberries with a little sugar and torn basil; pile onto pastry.","Fold edges over loosely and bake at 400°F until golden and bubbling."]),

    ("basil","butter","tomato",
     "Butter and tomato share furaneol and trace hexanal — sweet-caramel and green aldehyde compounds — while basil's linalool and eugenol complete the Mediterranean aromatic triad. The fat in butter suppresses tomato's harsh acidity and rounds its flavor exactly as Marcella Hazan's famous recipe demonstrates, with basil adding the final herbal dimension.",
     "Tomato Basil Butter Sauce",
     ["Simmer whole canned tomatoes with a large knob of butter and a halved onion.","Cook uncovered 45 minutes, pressing tomatoes to break them down gradually.","Remove onion, season, finish with torn fresh basil, toss with pasta."]),

    ("basil","butter","truffle",
     "Butter and truffle share dimethyl sulfide and phenylacetaldehyde — sulfurous and rosy aromatic compounds that butter's fat solubilizes and amplifies far more effectively than water — while basil's linalool and 2-phenylethanol provide herbal brightness that lifts truffle's earthiness into something more vertical and aromatic. This is the principle behind great truffle butter.",
     "Truffle Basil Butter Tagliatelle",
     ["Cook fresh tagliatelle al dente, reserve a generous cup of pasta water.","Toss hot pasta with truffle butter and a splash of pasta water to emulsify.","Finish with torn fresh basil and shaved black truffle; serve immediately."]),

    ("basil","butter","vanilla",
     "Butter and vanilla share vanillin, furaneol, delta-decalactone, and 2-phenylethanol — a nearly complete overlap of sweet lactonic and floral aroma compounds — while basil's eugenol adds a spiced warmth that mirrors vanilla's own anise-adjacent character. Together they create an herb-inflected sweet butter that bridges dessert and savory territory.",
     "Vanilla Basil Brown Butter Financiers",
     ["Brown butter to a deep hazelnut color; cool, then whisk with egg whites and vanilla.","Mix in almond flour, powdered sugar, and finely chopped fresh basil until smooth.","Pour into molds and bake at 400°F for 12 minutes until golden and fragrant."]),

    ("basil","caramel","chocolate",
     "Chocolate and caramel share furaneol and vanillin — Maillard-roasted sweet compounds — while basil's 2-phenylethanol and linalool echo chocolate's own floral fermentation esters, adding a herbal-floral dimension that lifts the heavy caramel-chocolate combination. The trio reads as a refined confection where herb prevents sweetness from becoming one-dimensional.",
     "Basil Caramel Chocolate Tart",
     ["Pour warm salted caramel into a blind-baked chocolate pastry shell and set briefly.","Top with dark chocolate ganache made with basil-infused cream; refrigerate until set.","Garnish with candied basil leaves and flaky salt before slicing."]),

    ("basil","caramel","coffee",
     "Caramel and coffee share furfural, acetic acid, and vanillin — three major Maillard and caramelization reaction products — while basil's linalool and eugenol provide the herbal brightness that lifts the heavy roasted-sweet combination. Together they achieve a sophisticated café flavor where the herb adds an unexpected aromatic dimension.",
     "Basil Coffee Caramel Pots de Crème",
     ["Steep basil in hot cream for 15 minutes, strain, then use to make caramel.","Add strong espresso to the caramel cream, whisk into egg yolks, pour into ramekins.","Bake in a water bath at 325°F until just set; chill 4 hours before serving."]),

    ("basil","caramel","cucumber",
     "Caramel's Maillard sweetness and cucumber's clean (E)-2-nonenal and hexanal create a bold contrast pairing where basil's linalool and benzaldehyde serve as the aromatic bridge between the two extremes. The herbal freshness of basil makes the sweet-cool contrast feel coherent rather than random, adding a garden dimension.",
     "Basil Caramel Cucumber Granita",
     ["Blend cucumber with lime juice and a spoon of salted caramel until smooth; strain.","Sweeten lightly, pour into a shallow freezer pan with torn fresh basil.","Freeze, scraping every 30 minutes until granita; serve with a caramel drizzle."]),

    ("basil","caramel","garlic",
     "Caramel's Maillard sweetness mirrors the sweet vinyl compounds produced when garlic is slowly caramelized — both involve sugar transformation reactions — while basil's linalool and eugenol provide the herbal lift that bridges the sweet and allium registers. This trio is the flavor core of great onion-family tarte tatins and savory caramel glazes.",
     "Caramelized Garlic Basil Tarte Tatin",
     ["Slowly cook whole garlic cloves with butter and sugar until sweet and golden.","Deglaze with balsamic, arrange in a skillet, top with puff pastry.","Bake at 400°F until pastry is golden; invert immediately and scatter fresh basil."]),

    ("basil","caramel","lamb",
     "Caramel's intense Maillard sweetness provides a foil for lamb's gamey 4-methyloctanoic acid — sweet glazes suppress the fatty-acid sharpness — while basil's linalool and eugenol add the herbal brightness that completes the sweet-savory-herbal balance. This is the flavor logic behind Moroccan-style lamb tagines with sweet and aromatic elements.",
     "Caramel Basil Glazed Lamb Chops",
     ["Make a caramel glaze with sugar, soy sauce, garlic, and a handful of torn basil.","Sear lamb chops hard on both sides until a crust forms in a hot cast-iron pan.","Brush with caramel glaze and broil 2 minutes until lacquered; rest before serving."]),
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
print(f"Batch 002 done: inserted {len(TRIPLETS)} triplets.")
