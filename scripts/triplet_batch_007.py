#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("basil","lavender","rose",
     "Lavender and rose share the highest shared 2-phenylethanol and linalool concentrations of any two culinary plants — both producing rose-floral and herbal terpenes at dominant levels — while basil reinforces this already intense floral-herbal aromatic overlap with its own 2-phenylethanol and linalool. Together the three form the most concentrated floral terpene register possible in cooking.",
     "Rose Lavender Basil Honey Cake",
     ["Make a honey sponge cake flavored with rose water, dried lavender, and finely chopped fresh basil.","Frost with a rose-lavender mascarpone cream flavored with a touch of lemon zest.","Decorate with crystallized rose petals, a sprinkle of dried lavender, and fresh basil leaves."]),

    ("basil","lavender","salmon",
     "Lavender's linalool and linalyl acetate provide floral-herbal softness that suppresses salmon's trimethylamine — the same mechanism as using dill — while basil's 2-phenylethanol and linalool reinforce lavender's dominant compounds and extend the herbal fragrance over the fatty fish. The trio creates an aromatic Provençal salmon preparation.",
     "Provençal Lavender Basil Salmon",
     ["Rub salmon fillets with a paste of dried lavender, fresh basil, garlic, and olive oil.","Rest 20 minutes at room temperature; bake at 400°F for 12 minutes until just opaque.","Finish with a basil-lavender butter and lemon zest drizzled over the top before serving."]),

    ("basil","lavender","strawberry",
     "Lavender and strawberry share linalool and furaneol — floral terpene and sweet-caramel compounds that together create a sophisticated floral-sweet register — while basil's 2-phenylethanol reinforces lavender's floral character and amplifies strawberry's own floral esters. Together the trio creates a refined summer dessert flavor.",
     "Lavender Strawberry Basil Galette",
     ["Make a rough puff pastry; mix sliced strawberries with lavender sugar and torn fresh basil.","Pile onto the pastry, fold edges over loosely, and chill 20 minutes before baking.","Bake at 400°F until golden and bubbling; drizzle with lavender honey while warm."]),

    ("basil","lavender","tomato",
     "Lavender and tomato create a unique Provençal pairing where lavender's linalool contrasts with tomato's furaneol sweetness — the same floral-sweet-umami interplay in Niçoise cooking — while basil's linalool reinforces lavender's terpene and eugenol connects to tomato's Mediterranean aromatic tradition. The trio defines southern French tomato preparations.",
     "Lavender Tomato Basil Tarte Tatin",
     ["Arrange halved cherry tomatoes cut-side up in a buttered tart pan; sprinkle with lavender sugar.","Roast at 375°F for 25 minutes until caramelized; top with puff pastry, tuck edges in.","Bake at 400°F until pastry is golden; invert immediately and scatter fresh basil to serve."]),

    ("basil","lavender","truffle",
     "Lavender and truffle share anisaldehyde — the anise-adjacent aromatic compound that both produce — while basil's linalool bridges lavender's floral-herbal register to truffle's earthy dimethyl sulfide, creating a three-tier aromatic stack of floral, herbal, and earthy. The trio appears in high-end French luxury preparations where aromatic intensity is layered carefully.",
     "Lavender Truffle Basil Scrambled Eggs",
     ["Beat eggs with a pinch of lavender salt and very finely chopped fresh basil.","Scramble slowly in butter over the lowest heat, stirring constantly until just barely set.","Plate immediately, grate fresh truffle over the top generously, and finish with a basil tip."]),

    ("basil","lavender","vanilla",
     "Lavender and vanilla share linalool, linalyl acetate, and trace 2-phenylethanol — overlapping floral-terpene compounds that together produce a perfumed sweet register without added sugar — while basil's eugenol adds spiced warmth that grounds the floral combination and connects to vanilla's anise-adjacent character. The trio creates the most refined dessert herb combination.",
     "Lavender Vanilla Basil Crème Caramel",
     ["Infuse warm cream with split vanilla bean, dried lavender, and fresh basil; steep 30 minutes.","Strain, sweeten, whisk into eggs; pour over dark caramel in ramekins and bake in water bath.","Refrigerate overnight; unmold onto plates — the caramel runs over the perfumed lavender custard."]),

    ("basil","lemon","mint",
     "Lemon and mint share linalool and trace geraniol — the herbal-citrus terpene pair — while basil adds eugenol and 1,8-cineole to mint's menthol, creating a three-herb aromatic where each ingredient's terpene reinforces the others. The trio is the flavor of Middle Eastern lemonade, tabbouleh dressing, and Moroccan preserved citrus herb sauces.",
     "Mint Basil Lemon Tabbouleh",
     ["Cook bulgur wheat in salted water; spread on a tray to cool completely to room temperature.","Fold in finely diced tomato, cucumber, and large quantities of chopped mint, basil, and parsley.","Dress with lemon juice, olive oil, salt, and cracked pepper; rest 15 minutes before serving."]),

    ("basil","lemon","oyster",
     "Lemon's citric acid and geraniol provide a bright citrus-floral lift that directly cuts through oyster's marine trimethylamine — the reason lemon is the universal oyster accompaniment — while basil's linalool and benzaldehyde add herbal depth that connects the citrus brightness to the oceanic mineral register. The trio creates the most refined raw oyster preparation.",
     "Lemon Basil Oyster Granita",
     ["Make a granita from lemon juice, basil-infused syrup, and a pinch of sea salt; freeze and scrape.","Shuck oysters into their half-shells and arrange over crushed ice on a serving platter.","Spoon a small amount of lemon-basil granita onto each oyster; serve immediately."]),

    ("basil","lemon","parmesan",
     "Lemon's citric acid cuts through Parmesan's butyric acid fat — acid-fat balance driving the brightness in Italian pasta finishing — while basil's linalool and geraniol bridge the citrus-herbal connection to Parmesan's fermentation esters, creating the compound logic behind lemon pasta, cacio e pepe finishing, and risotto brightening. The trio defines Italian spring cooking.",
     "Lemon Basil Parmesan Risotto",
     ["Cook arborio rice with stock until creamy and al dente; remove from heat.","Stir in cold butter, finely grated Parmesan, lemon zest, and lemon juice vigorously off heat.","Fold in torn fresh basil just before serving; plate and finish with more Parmesan and lemon."]),

    ("basil","lemon","rose",
     "Lemon and rose share geraniol — the citrus-floral terpene present in both lemon peel and rose petals — while basil's 2-phenylethanol amplifies rose's dominant compound and linalool bridges the herbal connection. Together the trio creates a sophisticated floral-citrus-herbal register used in Turkish and Persian cold desserts.",
     "Rose Lemon Basil Posset",
     ["Simmer heavy cream with sugar, lemon juice, and rose water until slightly thickened; remove from heat.","Stir in very finely chopped fresh basil; pour into glasses and refrigerate 4 hours until set.","Serve topped with rose petals, a basil leaf, and a thin curl of lemon zest."]),

    ("basil","lemon","salmon",
     "Lemon's citric acid suppresses salmon's trimethylamine while geraniol provides floral brightness that complements fatty fish — the reason lemon is the default salmon garnish in every cuisine — while basil's linalool and 2-phenylethanol bridge the citrus-herbal freshness into salmon's own minor floral compounds. The trio is the purest expression of salmon en papillote flavor.",
     "Lemon Basil Baked Salmon",
     ["Lay salmon on parchment; top with lemon slices, torn fresh basil, and a drizzle of olive oil.","Fold into a sealed parcel, bake at 400°F for 14 minutes until just cooked through.","Serve in the parcel; open at the table with a final squeeze of fresh lemon and basil garnish."]),

    ("basil","lemon","strawberry",
     "Strawberry and lemon share furaneol and trace geraniol — sweet-caramel and citrus-floral compounds — while basil's linalool and 2-phenylethanol amplify strawberry's own floral esters, creating a three-way terpene-floral-sweet connection where lemon's acidity sharpens the strawberry's fruit register. The trio is summer dessert at its most coherent.",
     "Strawberry Lemon Basil Shortcakes",
     ["Macerate sliced strawberries with lemon juice, sugar, and torn fresh basil for 30 minutes.","Bake fluffy buttermilk biscuits and split while warm; fill with whipped cream.","Spoon the basil-strawberry mixture generously over each biscuit half and serve immediately."]),

    ("basil","lemon","tomato",
     "Lemon's citric acid brightens tomato's furaneol sweetness through acid-balance — the same principle as adding acid to lift a flat tomato sauce — while basil's linalool and eugenol complete the Mediterranean aromatic triad in its simplest form. The trio drives the flavor of bruschetta al pomodoro, Caprese salad dressing, and every Italian summer antipasto.",
     "Lemon Basil Bruschetta al Pomodoro",
     ["Dice ripe tomatoes, toss with olive oil, lemon juice, lemon zest, salt, and torn fresh basil.","Rest 10 minutes to let flavors develop; meanwhile toast thick slices of sourdough until crisp.","Spoon the tomato mixture generously over toast with a final drizzle of extra-virgin olive oil."]),

    ("basil","lemon","truffle",
     "Truffle's phenylacetaldehyde and dimethyl sulfide meet lemon's citric brightness in a luxury contrast pairing — the principle behind truffle with preserved lemon — while basil's linalool bridges truffle's earthiness to lemon's citrus freshness through herbal terpene compounds. Together they create a light yet intensely aromatic high-end pasta or egg preparation.",
     "Lemon Truffle Basil Tagliolini",
     ["Cook fresh tagliolini al dente; reserve pasta water before draining.","Toss with truffle butter, lemon zest, and pasta water to create a glossy, light sauce.","Fold in torn fresh basil, shave generous truffle over the top, and serve immediately."]),

    ("basil","lemon","vanilla",
     "Lemon's geraniol and citric brightness contrasts with vanilla's vanillin sweetness — the classic sour-sweet pairing of lemon-vanilla desserts — while basil's linalool bridges the herbal connection between lemon's floral citrus and vanilla's lactonic-sweet register. Together the trio creates a sophisticated herb-inflected citrus-vanilla dessert flavor.",
     "Lemon Vanilla Basil Cheesecake",
     ["Make a cheesecake filling with cream cheese, vanilla bean, lemon zest, and juice; fold in chopped basil.","Pour over a graham cracker crust in a springform pan; bake in water bath at 325°F until set.","Cool completely, refrigerate overnight; serve with a basil oil drizzle and lemon curd."]),

    ("basil","mint","oyster",
     "Mint's menthol and 1,8-cineole provide a cooling freshness that directly cuts through oyster's marine trimethylamine — palate-cleansing between each briny bite — while basil's linalool and benzaldehyde bridge the herbal cooling and oceanic mineral registers through shared terpene compounds. The trio creates a sophisticated chilled oyster preparation.",
     "Mint Basil Oyster Shooter",
     ["Combine cucumber juice, lime juice, mint, and basil in a blender; strain until clean and bright.","Season with salt and white pepper; keep very cold.","Shuck oysters, pour a small amount of herb water over each, and serve immediately over ice."]),

    ("basil","mint","parmesan",
     "Mint and Parmesan share trace 1,8-cineole — the cooling terpene that appears in both mint's essential oil and as a minor compound in Parmesan's aromatic profile — while basil bridges the herbal-cooling and aged-dairy registers through its shared linalool presence with mint and 2-phenylethanol connection to Parmesan's fermentation esters. The trio appears in Ligurian pesto variations.",
     "Mint Basil Pesto Pasta",
     ["Blend fresh mint, basil, Parmesan, garlic, pine nuts, and olive oil until smooth but textured.","Cook pasta al dente; reserve pasta water and toss with the herb pesto off heat.","Loosen with pasta water, finish with more Parmesan, mint leaves, and cracked pepper."]),

    ("basil","mint","rose",
     "Mint and rose share 2-phenylethanol and linalool — the rosy-floral and herbal terpene compounds that both produce — while basil reinforces this floral-herbal overlap with its own 2-phenylethanol, creating a triple-floral register where menthol's cool provides contrast against the warm-sweet rose aromatic. The trio is the flavor of Persian cold drinks and Turkish sherbet.",
     "Rose Mint Basil Sherbet",
     ["Make a simple syrup with rose water, fresh mint, and basil; steep 15 minutes and strain.","Combine with cold water and lemon juice to balance sweetness; chill thoroughly.","Serve over crushed ice in tall glasses with a fresh mint sprig and rose petal garnish."]),

    ("basil","mint","salmon",
     "Mint's menthol suppresses salmon's trimethylamine through olfactory masking — a stronger version of the dill-salmon relationship — while basil's linalool provides herbal warmth beneath mint's dominant cool that prevents the combination from tasting flat against the fatty fish. The trio creates a refreshing summer salmon preparation.",
     "Mint Basil Salmon Ceviche",
     ["Dice sushi-grade salmon; cure in lime juice with salt for 5 minutes until opaque at edges.","Drain, toss with finely chopped mint and basil, cucumber, red onion, and a drizzle of olive oil.","Season with salt, serve immediately in chilled glasses with mint-basil oil and lime wedges."]),

    ("basil","mint","strawberry",
     "Mint and strawberry share linalool and furaneol — the herbal terpene and sweet-caramel compound — while basil's 2-phenylethanol amplifies strawberry's floral esters and connects them to mint's herbal freshness through complementary terpene compounds. Menthol's cooling makes the strawberry taste brighter and more intense. The trio is summer dessert perfected.",
     "Mint Basil Strawberry Granita",
     ["Blend fresh strawberries with mint, basil, lime juice, and simple syrup until smooth; strain.","Pour into a shallow freezer pan and freeze, scraping every 30 minutes until granita texture.","Serve in chilled glasses with a fresh mint-basil sprig and a whole strawberry garnish."]),
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
print(f"Batch 007 done: inserted {len(TRIPLETS)} triplets.")
