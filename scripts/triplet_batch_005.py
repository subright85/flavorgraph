#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("basil","cucumber","garlic",
     "Cucumber and garlic share hexanal and dimethyl sulfide — green aldehyde and sulfurous compounds that create a raw summer freshness — while basil's linalool and eugenol provide the herbal-spice lift that bridges cucumber's cool watery character and garlic's allium pungency. The trio is the flavor foundation of tzatziki and Persian herb-cucumber salads.",
     "Garlic Basil Cucumber Tzatziki",
     ["Grate cucumber and squeeze dry; mix with Greek yogurt, minced garlic, and olive oil.","Fold in finely chopped fresh basil and season with salt, lemon juice, and cracked pepper.","Rest 30 minutes for flavors to develop; serve with warm pita and a basil garnish."]),

    ("basil","cucumber","lamb",
     "Cucumber's hexanal and (E)-2-nonenal provide the cool, watery-green freshness that directly counteracts lamb's gamey 4-methyloctanoic acid — the contrast basis of mint-cucumber lamb preparations — while basil's linalool and eugenol add spiced herbal depth that bridges the cool vegetable and the rich meat. This is Greek and Levantine lamb accompaniment logic.",
     "Lamb Kofta with Basil Cucumber Raita",
     ["Mix ground lamb with garlic, cumin, coriander, and finely chopped fresh basil; form into koftas.","Grill over high heat, turning to char on all sides, until cooked through but still juicy.","Serve with a raita of grated cucumber, basil, garlic, and yogurt alongside warm flatbread."]),

    ("basil","cucumber","lavender",
     "Cucumber and lavender share linalool as a shared terpene — the same compound dominant in lavender appears in minor quantities in cucumber's fresh aroma — while basil reinforces this connection with its own linalool, creating a triple-herbal-floral register over cucumber's clean hexanal base. The trio produces a delicate Provençal spa-food flavor profile.",
     "Lavender Basil Cucumber Agua Fresca",
     ["Blend cucumber with lavender syrup, fresh basil, and a squeeze of lemon until smooth; strain.","Taste and adjust sweetness; pour over ice in a tall pitcher with a handful of fresh basil.","Serve in chilled glasses garnished with a cucumber round and a small sprig of lavender."]),

    ("basil","cucumber","lemon",
     "Cucumber and lemon share hexanal and trace geraniol — green aldehyde and citrus-adjacent terpene compounds — while basil's linalool and geraniol reinforce this connection, adding a herbal dimension to the clean citrus-cucumber register. The trio creates a hydrating summer flavor that reads as simultaneously refreshing and aromatic.",
     "Lemon Basil Cucumber Salad",
     ["Thinly slice English cucumber on a mandoline; toss with lemon juice, zest, and a pinch of salt.","Let rest 5 minutes to draw out liquid; drain, then toss with good olive oil and torn fresh basil.","Finish with cracked pepper, a final drizzle of lemon oil, and flaky salt before serving."]),

    ("basil","cucumber","mint",
     "Cucumber and mint share (E)-2-nonenal and linalool — clean watery-green and terpene compounds — that together produce the iconic cool-fresh flavor, while basil's eugenol adds a warm herbal-spice counterpoint to mint's dominant menthol that prevents the combination from tasting flat. The trio is the aromatic backbone of nearly every Middle Eastern green herb salad.",
     "Mint Basil Cucumber Lassi",
     ["Blend yogurt with fresh mint, basil, peeled cucumber, a pinch of salt, and cumin until smooth.","Taste and adjust seasoning; thin with cold water to a pourable, drinkable consistency.","Serve over ice in tall glasses with a dusting of cumin and a fresh mint-basil garnish."]),

    ("basil","cucumber","oyster",
     "Cucumber's hexanal and (E)-2-nonenal mirror oyster's own clean aquatic and green-aldehyde compounds — both ingredients share a cool, watery oceanic freshness — while basil's linalool and benzaldehyde add the herbal aromatic lift that bridges vegetable cool and marine mineral. The trio creates a clean mignonette or aquatic appetizer flavor.",
     "Basil Cucumber Oyster Mignonette",
     ["Finely dice peeled cucumber, mix with white wine vinegar, shallots, and cracked white pepper.","Stir in very finely chopped fresh basil and a pinch of salt; chill 10 minutes to meld.","Spoon over freshly shucked raw oysters on ice and serve immediately with lemon."]),

    ("basil","cucumber","parmesan",
     "Cucumber and Parmesan create an unusual cool-umami contrast — cucumber's (E)-2-nonenal provides fresh green freshness against Parmesan's butyric acid and furaneol — while basil's linalool bridges the green vegetable and aged dairy through its herbal-floral compounds. The trio produces a sophisticated Italian summer salad flavor.",
     "Parmesan Basil Cucumber Ribbon Salad",
     ["Use a peeler to make long cucumber ribbons; toss with good olive oil and a pinch of salt.","Arrange on a plate with torn fresh basil and shave Parmesan over with a vegetable peeler.","Finish with cracked pepper, lemon zest, and a drizzle of aged balsamic to serve."]),

    ("basil","cucumber","rose",
     "Cucumber and rose share linalool and (E)-2-nonenal — floral terpene and green aldehyde compounds — creating a cool floral-green register, while basil's 2-phenylethanol amplifies rose's dominant rosy compound, adding a herbal-floral dimension to cucumber's clean watery freshness. The trio is the flavor logic of Persian rose-cucumber cold drinks.",
     "Rose Basil Cucumber Sorbet",
     ["Blend peeled cucumber with rose water, fresh basil, and a little sugar until smooth; strain.","Adjust sweetness and acidity with a squeeze of lemon; churn in an ice cream maker.","Freeze until firm; serve scooped with fresh basil leaves and a drizzle of rose syrup."]),

    ("basil","cucumber","salmon",
     "Cucumber and salmon share (E)-2-nonenal — the clean watery-green compound in both cucumber's aroma and fresh salmon's marine-green notes — while basil's linalool and 2-phenylethanol bridge the cool vegetable and fatty fish through shared terpene-floral chemistry. The trio is the flavor backbone of Nordic smørrebrød and Japanese salmon cucumber rolls.",
     "Basil Cucumber Salmon Tartare",
     ["Finely dice sushi-grade salmon; mix with cucumber, lemon zest, capers, and chopped fresh basil.","Season with flaky salt, white pepper, and a drizzle of good olive oil; mix gently to combine.","Serve in cucumber cups or on crisp crackers immediately with extra basil and lemon wedges."]),

    ("basil","cucumber","strawberry",
     "Strawberry's furaneol sweetness contrasts with cucumber's clean hexanal freshness in a summer-garden pairing where basil's linalool and 2-phenylethanol bridge both through their shared terpene-floral presence in strawberry's own aroma. The combination reads as a sophisticated garden salad where fruit, vegetable, and herb occupy distinct but harmonious registers.",
     "Strawberry Basil Cucumber Salad",
     ["Slice strawberries and cucumber thinly; arrange alternating on a chilled platter.","Drizzle with a dressing of white balsamic, olive oil, a pinch of salt, and shredded fresh basil.","Top with burrata or whipped ricotta and torn basil; serve immediately while cold."]),

    ("basil","cucumber","tomato",
     "Cucumber and tomato share hexanal and linalool — the green aldehyde and herbal terpene compounds at the core of summer salad freshness — while basil's eugenol and linalool complete the Mediterranean flavor triad of the classic Caprese. The trio is arguably the most eaten flavor combination in the world during summer months.",
     "Classic Caprese with Basil Oil",
     ["Slice ripe tomatoes and cucumber into even rounds; layer alternating on a platter.","Scatter torn fresh basil generously over the top with good mozzarella if desired.","Dress with cold-pressed olive oil, flaky salt, cracked pepper, and balsamic glaze."]),

    ("basil","cucumber","truffle",
     "Truffle's dimethyl sulfide and anisaldehyde create an earthy-anise richness that contrasts directly with cucumber's clean (E)-2-nonenal freshness — luxury earthiness against vegetable cool — while basil's linalool and 2-phenylethanol bridge the two extremes through their herbal-floral compounds. The trio produces a refined amuse-bouche flavor profile.",
     "Truffle Basil Cucumber Canapés",
     ["Spread whipped cream cheese or ricotta on cucumber rounds; drizzle each with truffle oil.","Top with a tiny fresh basil leaf and a shaving of black truffle or truffle salt.","Arrange on a chilled tray; serve immediately as an elegant passed appetizer."]),

    ("basil","cucumber","vanilla",
     "Vanilla's vanillin and furaneol sweetness provides a counterpoint to cucumber's clean hexanal freshness — sweet-floral against green-watery — while basil's linalool bridges through its shared terpene presence with vanilla's floral character and cucumber's herbal notes. The trio creates a subtle, elegant flavor suitable for refined cold desserts and spa cuisine.",
     "Vanilla Basil Cucumber Panna Cotta",
     ["Warm cream with split vanilla bean and fresh basil; steep 20 minutes, strain, dissolve gelatin.","Pour into molds and refrigerate until set; make a cucumber-basil water for the sauce.","Unmold, spoon cold cucumber sauce around the base, and garnish with a basil leaf."]),

    ("basil","garlic","lamb",
     "Garlic and lamb share dimethyl sulfide and allicin-derived sulfurous compounds — allium and animal fat meeting in the same sulfurous family — while basil's linalool and eugenol provide the herbal-spice brightness that suppresses lamb's 4-methyloctanoic acid gaminess. This is the defining flavor triad of roasted leg of lamb across every Mediterranean cuisine.",
     "Garlic Basil Roast Leg of Lamb",
     ["Stud the leg with slivers of garlic; make a paste of olive oil, basil, garlic, and rosemary.","Rub the paste all over, refrigerate overnight; bring to room temp 1 hour before roasting.","Roast at 425°F for 20 minutes, then 325°F for 1.5 hours to medium; rest 20 minutes before carving."]),

    ("basil","garlic","lavender",
     "Garlic and lavender share trace linalool and sulfurous compounds that lavender's terpene chemistry mildly suppresses through a pleasant aromatic displacement — the principle behind Herbes de Provence — while basil reinforces lavender's linalool to create a layered herbal-allium-floral register. The trio defines the aromatic profile of southern French cuisine.",
     "Provençal Garlic Lavender Basil Chicken",
     ["Marinate chicken thighs in olive oil, minced garlic, dried lavender, and torn fresh basil overnight.","Sear skin-side down until deeply golden; add white wine and roast at 375°F for 30 minutes.","Rest 5 minutes; serve with the pan jus, fresh basil, and crusty bread for the sauce."]),

    ("basil","garlic","lemon",
     "Garlic and lemon share acetic acid and trace geraniol — tart compounds that both allium and citrus produce — while basil's linalool and geraniol reinforce the lemon-herbal connection and soften garlic's allicin harshness into a bright, aromatic register. The trio is gremolata: the classic Italian garnish that defines braised meat and risotto finishing.",
     "Gremolata Garlic Basil Linguine",
     ["Make gremolata with finely chopped basil, garlic, and lemon zest; mix with good olive oil.","Cook linguine al dente; drain, toss immediately with gremolata, and add pasta water to emulsify.","Finish with a generous squeeze of fresh lemon juice and more gremolata on top to serve."]),

    ("basil","garlic","mint",
     "Garlic and mint share trace menthol-adjacent compounds that together create a cooling-pungent interplay — the basis of Middle Eastern mint-garlic sauce traditions — while basil's linalool and 1,8-cineole bridge the herbal-allium gap with complementary terpene compounds. The trio defines the flavor of Lebanese toum, chimichurri, and Persian herb plates.",
     "Mint Garlic Basil Chimichurri",
     ["Blend fresh mint, basil, garlic, red wine vinegar, and olive oil in a food processor until coarse.","Season with salt, red pepper flakes, and a squeeze of lemon; rest 15 minutes before serving.","Spoon generously over grilled meats, charred vegetables, or use as a flatbread dressing."]),

    ("basil","garlic","oyster",
     "Garlic and oyster share dimethyl sulfide and acetic acid — sulfurous and tart compounds linking allium pungency to marine brine — while basil's benzaldehyde and linalool provide the herbal aromatic lift that bridges allium and oceanic registers. The combination drives Chinese oyster with black bean sauce and French beurre d'escargot flavor logic.",
     "Garlic Basil Butter Oysters",
     ["Blend softened butter with minced garlic, fresh basil, lemon zest, and white wine; chill to firm.","Place a knob of compound butter on each shucked oyster in its half-shell on a baking sheet.","Broil 4 minutes until butter is bubbling and the oyster edges just begin to curl; serve with crusty bread."]),

    ("basil","garlic","parmesan",
     "Garlic and Parmesan share dimethyl sulfide and acetic acid — the sulfurous-tart compound pair that defines Italian umami — while basil's linalool and 2-phenylethanol provide the herbal-floral lift essential to pesto, the world's most famous Italian sauce built on this exact trio. Olive oil and pine nuts support, but the three core aromatics are garlic, Parmesan, and basil.",
     "Classic Basil Pesto Pasta",
     ["Blend basil, garlic, Parmesan, pine nuts, and olive oil in a food processor until smooth.","Cook pasta al dente; reserve a cup of pasta water before draining.","Toss pasta with pesto and enough pasta water to create a glossy sauce; serve immediately."]),

    ("basil","garlic","rose",
     "Garlic's sulfurous allicin and rose's delicate 2-phenylethanol create a bold contrast pairing where garlic's pungency is softened by rose's floral sweetness — the logic behind Persian rose-garlic lamb marinades — while basil's 2-phenylethanol reinforces rose's dominant compound and bridges the floral-allium tension through its herbal warmth.",
     "Rose Garlic Basil Flatbread",
     ["Make a dough with olive oil, roasted garlic, and a drizzle of rose water worked into the flour.","Roll thin, brush with garlic-basil oil, and bake at 500°F until golden and charred at the edges.","Scatter fresh basil and rose petals as soon as it comes out of the oven; serve immediately."]),
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
print(f"Batch 005 done: inserted {len(TRIPLETS)} triplets.")
