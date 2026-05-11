#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("basil","garlic","salmon",
     "Garlic and salmon share dimethyl sulfide and acetic acid — sulfurous and tart compounds linking allium pungency to fatty fish — while basil's linalool and 2-phenylethanol suppress salmon's trimethylamine and bridge the herbal-allium register into marine aromatics. This is the flavor logic of Italian aglio e olio applied to salmon, and Japanese salmon with shiso-garlic.",
     "Garlic Basil Salmon en Papillote",
     ["Place salmon on parchment with sliced garlic, torn fresh basil, lemon, and a drizzle of olive oil.","Fold into a sealed parcel, crimping edges tightly; bake at 400°F for 14 minutes.","Open at the table to release the aromatic steam; finish with fresh basil and flaky salt."]),

    ("basil","garlic","strawberry",
     "Garlic's sulfurous allicin creates a sharp pungency that strawberry's furaneol sweetness directly softens through sweet-savory contrast — the principle behind strawberry-garlic balsamic reductions — while basil's linalool and 2-phenylethanol amplify strawberry's floral register and bridge the fruit-allium gap. The trio creates an unexpected summer salsa or gastrique.",
     "Strawberry Garlic Basil Bruschetta",
     ["Macerate diced strawberries with minced garlic, torn fresh basil, and a splash of balsamic for 15 minutes.","Toast thick sourdough slices, rub with a raw garlic clove while still hot.","Pile strawberry mixture on top, finish with olive oil, flaky salt, and more fresh basil."]),

    ("basil","garlic","tomato",
     "Garlic and tomato share acetic acid and dimethyl sulfide — a sulfurous-tart compound foundation that Italian cooking has built upon for centuries — while basil's linalool and eugenol complete the aromatic triad that defines Neapolitan pizza sauce, marinara, and nearly every Italian pasta sauce. This is arguably cooking's most important three-ingredient flavor foundation.",
     "Classic Neapolitan Tomato Sauce",
     ["Gently sauté sliced garlic in olive oil until barely golden; add crushed San Marzano tomatoes.","Simmer uncovered 25 minutes until reduced and sweet; season with salt only.","Remove from heat, tear in a generous amount of fresh basil, and toss with pasta immediately."]),

    ("basil","garlic","truffle",
     "Garlic and truffle share dimethyl sulfide and sulfurous compound families — the reason truffle is often paired with alliums in Italian cooking — while basil's linalool and 2-phenylethanol provide herbal brightness that lifts truffle's earthiness and garlic's pungency into a cleaner, more aromatic register. The trio defines Italian white truffle season preparations.",
     "Truffle Garlic Basil Bruschetta",
     ["Rub thick toasted sourdough with raw garlic; drizzle generously with truffle oil.","Mash good ricotta with roasted garlic, salt, and very finely chopped fresh basil.","Spread ricotta on toast, shave fresh truffle over the top, and finish with a basil leaf."]),

    ("basil","garlic","vanilla",
     "Garlic's allicin and vanilla's vanillin create a bold sweet-savory contrast — the logic behind vanilla-roasted garlic spreads — while basil's eugenol adds a spiced warmth that mirrors vanilla's anise character and bridges the herbal-allium-sweet register. The trio is unconventional but creates a sophisticated compound butter or savory vanilla application.",
     "Vanilla Garlic Basil Compound Butter",
     ["Roast a whole garlic head until sweet and soft; squeeze cloves and mash with softened butter.","Add vanilla bean seeds, finely chopped fresh basil, and a pinch of flaky salt; blend smooth.","Roll into a log in plastic wrap; refrigerate until firm, then slice over grilled steak or bread."]),

    ("basil","lamb","lavender",
     "Lavender and lamb share trace butyric acid and linalool — the first connecting dairy-fat and animal-fat registers, the second providing floral softness that suppresses lamb's gamey 4-methyloctanoic acid — while basil reinforces lavender's linalool and adds eugenol warmth that grounds the herbal-floral combination. The trio is the defining flavor of Provence-style lamb dishes.",
     "Provençal Lavender Basil Lamb Chops",
     ["Rub lamb chops with a paste of olive oil, dried lavender, fresh basil, garlic, and Dijon mustard.","Rest 30 minutes at room temperature; sear in a very hot cast-iron pan until crusted on both sides.","Finish in a 375°F oven for 5 minutes; rest and serve with lavender-basil jus."]),

    ("basil","lamb","lemon",
     "Lamb and lemon share trace acetic acid, and lemon's citric acid directly suppresses lamb's 4-methyloctanoic acid gaminess through pH-driven aromatic modulation — the reason lemon is a universal lamb accompaniment — while basil's linalool and geraniol bridge the citrus freshness into an herbal-Mediterranean aromatic register. The trio defines Greek-style lamb preparation.",
     "Lemon Basil Grilled Lamb Skewers",
     ["Marinate lamb cubes in lemon juice, zest, olive oil, garlic, and torn fresh basil for 2 hours.","Thread onto skewers, season with salt and pepper, and grill over high heat until charred.","Serve with a lemon-basil yogurt sauce and extra fresh basil and lemon wedges."]),

    ("basil","lamb","mint",
     "Mint and lamb is the most classic of all herb-meat combinations: menthol's cooling compounds directly suppress lamb's fatty gamey acids — 4-methyloctanoic acid solubility drops in the mint's aqueous volatiles — while basil's eugenol and linalool add warm herbal depth that prevents the mint from tasting flat or candy-like. The trio refines a classic.",
     "Mint Basil Lamb Meatballs",
     ["Mix ground lamb with finely chopped mint, basil, garlic, cumin, and breadcrumbs; roll into balls.","Brown in olive oil until crusted all over; transfer to a spiced tomato sauce and simmer 15 minutes.","Serve with yogurt, more fresh mint and basil, and warm flatbread to scoop with."]),

    ("basil","lamb","oyster",
     "Lamb and oyster share trimethylamine and dimethyl sulfide — the marine-animal sulfurous compound family that links gamey meat and briny shellfish — while basil's benzaldehyde and linalool provide the herbal lift that bridges these two primal savory registers. The combination appears in Surf-and-Turf preparations and Cantonese braised lamb-oyster sauce dishes.",
     "Oyster Sauce Braised Lamb with Basil",
     ["Brown lamb shoulder pieces in batches; sauté ginger and garlic in the remaining fat.","Return lamb with oyster sauce, soy, star anise, and stock; braise covered at 325°F for 2 hours.","Stir in a generous handful of fresh basil at the end; serve over steamed rice."]),

    ("basil","lamb","parmesan",
     "Lamb and Parmesan share butyric acid and dimethyl sulfide — the fatty-acid and sulfurous compound families spanning animal and dairy fat — while basil's linalool and 2-phenylethanol provide the herbal-floral lift that bridges the rich meat and aged cheese into the Italian-Mediterranean register. The trio is the flavor foundation of lamb-stuffed pasta and Ligurian lamb dishes.",
     "Lamb Parmesan Basil Stuffed Shells",
     ["Brown ground lamb with garlic and herbs; mix with ricotta and Parmesan; stuff large pasta shells.","Arrange in a baking dish over marinara sauce, scatter more Parmesan over the top.","Bake at 375°F until bubbling; garnish with a generous amount of fresh torn basil before serving."]),

    ("basil","lamb","rose",
     "Rose's 2-phenylethanol and geraniol soften lamb's 4-methyloctanoic acid gaminess through floral aromatic displacement — the logic behind Persian rose-water lamb preparations — while basil's 2-phenylethanol reinforces rose's dominant compound, amplifying the floral register and adding herbal warmth to the aromatic balance. The trio defines Iranian and Moroccan lamb cookery.",
     "Rose Basil Persian Lamb Stew",
     ["Brown lamb chunks with onion, add rose water, saffron, and crushed tomatoes.","Simmer 1.5 hours until tender; adjust seasoning with salt and a touch of pomegranate molasses.","Stir in torn fresh basil and dried rose petals just before serving over saffron rice."]),

    ("basil","lamb","salmon",
     "Lamb and salmon share dimethyl sulfide and trimethylamine — animal fat and marine aromatic compounds in the same sulfurous family — while basil's linalool bridges the two proteins through its shared terpene presence with both ingredients' minor floral compounds. The unusual pairing works in surf-and-turf preparations where basil acts as the critical aromatic connector.",
     "Basil-Crusted Lamb and Salmon Platter",
     ["Make a basil-garlic crust from breadcrumbs, basil, Parmesan, and olive oil.","Press crust onto lamb rack and salmon fillets separately; roast together at 400°F until each is done.","Plate side by side with basil oil, lemon, and a cucumber-basil salsa bridging the two proteins."]),

    ("basil","lamb","strawberry",
     "Strawberry's furaneol sweetness provides a direct counterpoint to lamb's gamey 4-methyloctanoic acid — sweet-savory contrast suppressing animal-fat pungency — while basil's linalool and 2-phenylethanol amplify strawberry's floral compounds and bridge fruit-sweetness to herbal meat aromatics. The trio is the flavor logic of Scandinavian lamb with berry-herb preparations.",
     "Strawberry Basil Lamb Tartare",
     ["Finely chop high-quality lamb loin; mix with diced strawberry, shallot, and chopped fresh basil.","Season with flaky salt, olive oil, and a few drops of aged balsamic; mix gently.","Serve immediately on crisp crackers or toast with a basil leaf and strawberry slice garnish."]),

    ("basil","lamb","tomato",
     "Tomato and lamb share furaneol and acetic acid — sweet-caramel and tart compounds that create a natural acid-meat bridge in long braises — while basil's linalool and eugenol complete the Mediterranean aromatic triad essential to Greek moussaka, Italian ragù d'agnello, and Turkish lamb-tomato preparations. Tomato's acidity tenderizes and brightens lamb's rich fat.",
     "Lamb Tomato Basil Ragù",
     ["Brown ground lamb until caramelized; add garlic, crushed tomatoes, and red wine.","Simmer uncovered 45 minutes until thick and rich; season generously with salt and pepper.","Toss with rigatoni, tear in fresh basil at the last moment, and finish with Parmesan."]),

    ("basil","lamb","truffle",
     "Lamb and truffle share dimethyl sulfide and phenylacetaldehyde — the sulfurous-rosy compound family linking animal fat to earthy fungal aromatics — while basil's linalool and 2-phenylethanol provide herbal brightness that lifts truffle's earthiness above lamb's richness into a clean, vertically aromatic register. The combination is a signature of high-end French lamb preparation.",
     "Truffle Basil Rack of Lamb",
     ["Rub rack of lamb with truffle salt, garlic, and a basil-breadcrumb crust; press firmly.","Roast at 425°F for 20 minutes to medium-rare; rest 8 minutes before carving into chops.","Plate over a truffle-Parmesan potato purée with torn fresh basil and a truffle jus drizzle."]),

    ("basil","lamb","vanilla",
     "Vanilla's vanillin and furaneol sweetness contrasts with lamb's gamey butyric and 4-methyloctanoic acids — sweet lactonic compounds suppress animal-fat pungency through aromatic displacement — while basil's eugenol adds spiced herbal warmth that grounds the unexpected sweet-savory combination. The trio appears in Moroccan lamb preparations with sweet spices.",
     "Vanilla Basil Moroccan Lamb Tagine",
     ["Brown lamb with onion, ras el hanout, and a split vanilla bean in a tagine or Dutch oven.","Add dried apricots, preserved lemon, and enough stock to nearly cover; braise 2 hours at 300°F.","Stir in torn fresh basil and toasted almonds just before serving over couscous."]),

    ("basil","lavender","lemon",
     "Lavender and lemon share linalool and trace geraniol — terpene compounds that both Provençal herbs and citrus produce — while basil reinforces this connection with its own linalool, creating a triple-terpene herbal-citrus register grounded by lemon's citric brightness. The trio defines classic Provence-style lemonade and lemon-herb dessert preparations.",
     "Lavender Lemon Basil Shortbread",
     ["Cream butter with powdered sugar, lemon zest, dried lavender, and finely chopped fresh basil.","Mix in flour to form a cohesive dough; chill 30 minutes, then roll and cut into rounds.","Bake at 325°F until just set but not browned; cool and dust with lavender-lemon sugar."]),

    ("basil","lavender","mint",
     "Lavender and mint share linalool and 1,8-cineole — herbal terpenes that both produce in their essential oils — while basil bridges and amplifies these shared compounds, creating a three-herb aromatic stack where each ingredient reinforces the others' terpene profile. Together they form the most concentrated herbal-floral combination in the culinary terpene set.",
     "Lavender Mint Basil Infused Water",
     ["Combine fresh mint, basil, dried lavender, and thinly sliced cucumber in a large pitcher.","Add cold water and a squeeze of lemon; refrigerate 2 hours for the flavors to fully infuse.","Serve over ice, straining into glasses, garnished with a sprig of each herb."]),

    ("basil","lavender","oyster",
     "Lavender's linalool and linalyl acetate provide a floral-terpene counterpoint to oyster's marine dimethyl sulfide — an unusual floral-brine contrast pairing — while basil's benzaldehyde and linalool bridge the herbal-floral and oceanic registers as the aromatic connector. The trio creates a delicate Provençal-style oyster preparation.",
     "Lavender Basil Oyster Mignonette",
     ["Combine white wine vinegar with finely minced shallots, a pinch of dried lavender, and cracked pepper.","Stir in very finely chopped fresh basil and a drop of lavender honey; rest 10 minutes.","Spoon over freshly shucked raw oysters and serve immediately on crushed ice with lemon."]),

    ("basil","lavender","parmesan",
     "Lavender's linalool and linalyl acetate create a perfumed floral register that Parmesan's butyric acid and umami rounds into savory depth — floral against funky-rich dairy — while basil bridges both through its shared linalool with lavender and its herbal-floral 2-phenylethanol connection to Parmesan's fermentation esters. The trio is unusual but precise.",
     "Lavender Basil Parmesan Shortbread",
     ["Blend finely grated Parmesan with cold butter, flour, dried lavender, and chopped fresh basil.","Pulse until the dough just comes together; roll and cut into rounds or press into a tart pan.","Bake at 350°F until golden; these savory shortbreads pair perfectly with wine and honey."]),
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
print(f"Batch 006 done: inserted {len(TRIPLETS)} triplets.")
