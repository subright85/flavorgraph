#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("basil","caramel","lavender",
     "Caramel and lavender share linalyl acetate and furaneol — a sweet floral compound overlap — while basil's linalool reinforces lavender's dominant terpene to create a triple-layered herbal-sweet-floral register. The trio achieves Provençal dessert elegance: caramel's warmth rounded by two herbs sharing the same primary aromatic compound.",
     "Lavender Caramel Basil Crème Brûlée",
     ["Steep dried lavender and fresh basil in hot cream 20 minutes; strain and use for custard base.","Whisk into egg yolks with caramelized sugar, pour into ramekins, bake in water bath at 325°F until just set.","Chill overnight, top with sugar, torch to a crackled caramel just before serving with a fresh basil sprig."]),

    ("basil","caramel","lemon",
     "Caramel's diacetyl and furaneol sweetness is sharpened by lemon's citric acid — the acid-caramel tension that drives salted-caramel tartness — while basil's linalool and geraniol bridge the citrus-herbal register into the sweet-roasted base. Together they achieve a sophisticated sour-sweet-herbal balance used in modern French pâtisserie.",
     "Lemon Basil Caramel Tart",
     ["Make a dry caramel, deglaze with fresh lemon juice and cream, whisk until smooth and glossy.","Pour into a blind-baked tart shell and let set 30 minutes at room temperature.","Finish with lemon zest, torn fresh basil, and a sprinkle of flaky salt before slicing."]),

    ("basil","caramel","mint",
     "Caramel's Maillard sweetness and mint's menthol create the classic mint-toffee confection pairing — contrasting warm and cool in a single compound register — while basil's eugenol adds a spiced herbal depth beneath the menthol that prevents the mint from tasting flat. The trio creates a layered cool-warm-herbal sweet that reads as more refined than mint alone.",
     "Mint Basil Caramel Sauce",
     ["Make a dark caramel, cool slightly, then whisk in cream infused with mint and basil; strain herbs.","Return to low heat and whisk until smooth, glossy, and pourable consistency.","Serve warm over vanilla ice cream, drizzled with fresh mint oil and a torn basil leaf."]),

    ("basil","caramel","oyster",
     "Caramel's intense Maillard sweetness provides a counterpoint to oyster's marine trimethylamine and dimethyl sulfide — sweet-brine contrast at its most direct — while basil's linalool and benzaldehyde bridge the gap as a herbal aromatic connector between the caramelized and oceanic registers. The trio parallels Korean sweet-soy glazed seafood flavor logic.",
     "Caramel Glazed Oysters with Basil",
     ["Make a light caramel with soy sauce, mirin, and ginger; reduce until syrupy and glossy.","Shuck oysters, brush each with caramel glaze, and place on a sheet pan over rock salt.","Broil 3 minutes until edges curl and glaze caramelizes; garnish with torn fresh basil and serve."]),

    ("basil","caramel","parmesan",
     "Caramel and Parmesan share furaneol and butyric acid — sweet-lactonic and fatty dairy compounds that together create deep savory-sweet umami — while basil's linalool and 2-phenylethanol provide the herbal-floral lift that bridges cheese funk and caramelized sweetness. The trio is the flavor logic behind Parmesan caramel crisps and refined savory cheeseboards.",
     "Caramel Parmesan Basil Crisps",
     ["Mix finely grated Parmesan with a drizzle of dark caramel and a pinch of cayenne; fold in chopped basil.","Drop spoonfuls onto a parchment-lined tray and spread into thin rounds.","Bake at 375°F for 8 minutes until golden and lacy; cool until crisp before lifting."]),

    ("basil","caramel","rose",
     "Rose and caramel share 2-phenylethanol and furaneol — the floral-rosy and sweet-caramel compound pair at the heart of Turkish delight confections — while basil's linalool and 2-phenylethanol reinforce rose's dominant floral compound, amplifying the perfumed register before caramel's warmth grounds it. Together they create a Middle Eastern–inflected dessert flavor.",
     "Rose Basil Caramel Panna Cotta",
     ["Warm cream with caramelized sugar and a splash of rose water; dissolve gelatin and strain.","Stir in finely chopped fresh basil; pour into molds and refrigerate until set, at least 4 hours.","Unmold onto plates, drizzle with salted caramel, and garnish with crystallized rose petals."]),

    ("basil","caramel","salmon",
     "Caramel's Maillard glaze suppresses salmon's trimethylamine through sweet-savory contrast while adding a lacquered crust that seals in moisture — the same logic as teriyaki sauce — while basil's linalool and 2-phenylethanol provide the herbal lift that bridges sweet glaze and fatty fish aromatics. Together they create a polished restaurant-style salmon preparation.",
     "Caramel Glazed Salmon with Basil",
     ["Make a caramel with brown sugar, soy sauce, garlic, and ginger; reduce to a syrupy glaze.","Sear salmon skin-side down in a hot pan until crispy, then flip and brush generously with glaze.","Finish under the broiler 2 minutes until lacquered; plate with fresh basil oil and lemon wedges."]),

    ("basil","caramel","strawberry",
     "Strawberry and caramel share furaneol at exceptionally high concentrations — the same sweet-caramel compound dominating both — creating a self-amplifying sweet register that basil's linalool and 2-phenylethanol lift with herbal-floral brightness before the combination becomes cloying. The trio achieves the most cohesive compound overlap of any three-ingredient dessert combination.",
     "Strawberry Caramel Basil Pavlova",
     ["Whip meringue to stiff peaks and bake at 250°F for 90 minutes; cool completely in oven.","Macerate sliced strawberries with a spoon of salted caramel and torn fresh basil for 20 minutes.","Top meringue with whipped cream and the basil-caramel strawberries just before serving."]),

    ("basil","caramel","tomato",
     "Tomato and caramel share furaneol — the ripe sweet-caramel compound in both ingredients — creating a natural sweet-umami bridge when tomatoes are caramelized, while basil's linalool and eugenol complete the Mediterranean aromatic triad. The combination is the flavor logic behind slow-roasted tomato preparations that taste sweeter and more complex than fresh.",
     "Caramelized Tomato Basil Bruschetta",
     ["Roast halved cherry tomatoes with olive oil and brown sugar at 375°F for 35 minutes until jammy.","Deglaze the pan with balsamic, scrape up all caramelized bits, and toss tomatoes to coat.","Pile onto toasted sourdough with a generous handful of torn fresh basil and flaky salt."]),

    ("basil","caramel","truffle",
     "Truffle's dimethyl sulfide and phenylacetaldehyde meet caramel's Maillard furaneol in a savory-sweet luxury register — the same logic that makes truffle honey a classic pairing — while basil's linalool and 2-phenylethanol provide the herbal brightness that prevents the earthy-sweet combination from becoming too heavy. Together they define modern high-end Italian dessert-savory crossover.",
     "Truffle Caramel Basil Risotto",
     ["Cook arborio rice with stock until creamy; in a separate pan make a light caramel with shallots and white wine.","Combine caramel base into risotto off heat, stir in Parmesan and cold butter until glossy.","Finish with shaved black truffle, torn fresh basil, and a drizzle of truffle caramel to serve."]),

    ("basil","caramel","vanilla",
     "Caramel and vanilla share vanillin, furaneol, and diacetyl — an extensive sweet-lactonic compound overlap that makes them the two most naturally compatible dessert flavors — while basil's eugenol adds a spiced warmth that mirrors vanilla's own anise-adjacent character without competing. The trio achieves a refined herb-inflected sweet where basil elevates without disrupting.",
     "Vanilla Caramel Basil Ice Cream",
     ["Make a caramel custard base with brown sugar, egg yolks, cream, and split vanilla bean; steep and strain.","Churn in ice cream maker until thick and creamy; in the last 2 minutes fold in finely chopped fresh basil.","Freeze until firm; serve with a caramel drizzle and a single basil leaf garnish."]),

    ("basil","chocolate","coffee",
     "Chocolate and coffee share furfural, acetic acid, phenylacetaldehyde, and dimethyl sulfide — the most complete overlap of Maillard-roasted compounds in the culinary world — while basil's linalool and 2-phenylethanol echo chocolate's floral fermentation esters, adding a herbal dimension that lifts the intense roasted-bitter combination. The trio creates the backbone of sophisticated mocha pastry.",
     "Basil Mocha Flourless Cake",
     ["Melt dark chocolate with espresso butter, cool slightly, then whisk in eggs and sugar until smooth.","Fold in finely chopped fresh basil and a pinch of salt; pour into a buttered springform pan.","Bake at 325°F until just set in the center; serve warm with coffee cream and a basil oil drizzle."]),

    ("basil","chocolate","cucumber",
     "Dark chocolate's phenylacetaldehyde and rosy fermentation esters contrast with cucumber's clean hexanal and (E)-2-nonenal — a bold sweet-green contrast pairing — while basil's linalool bridges the two through its shared terpene presence with both cucumber's herbal freshness and chocolate's floral character. The combination creates a surprisingly coherent garden-dessert flavor.",
     "Dark Chocolate Basil Cucumber Sorbet",
     ["Blend peeled cucumber with a tablespoon of good dark cocoa and a handful of fresh basil; strain well.","Sweeten with simple syrup, add a squeeze of lime, and churn in an ice cream maker until smooth.","Freeze until firm; serve scooped with a few shards of dark chocolate and a basil leaf."]),

    ("basil","chocolate","garlic",
     "Dark chocolate and garlic share dimethyl sulfide — the sulfurous compound that roasting transforms from harsh allicin into sweet, round garlic — and phenylacetaldehyde, linking the roasted-fermented and allium registers, while basil's eugenol and linalool provide the herbal-spice bridge that channels this bold pairing into the savory mole tradition. The trio defines complex New World sauce flavor.",
     "Dark Chocolate Garlic Basil Mole",
     ["Toast dried chiles, blend with roasted garlic, tomatoes, and a square of dark chocolate until smooth.","Simmer with stock, cumin, and cinnamon until thick and glossy, adjusting seasoning carefully.","Finish with a generous handful of torn fresh basil; serve over grilled chicken or enchiladas."]),

    ("basil","chocolate","lamb",
     "Chocolate and lamb share phenylacetaldehyde and dimethyl sulfide — linking roasted fermented dairy character to animal fat — while basil's linalool and eugenol provide the herbal brightness that lifts lamb's gamey 4-methyloctanoic acid and connects it to chocolate's dark bitter register. The trio drives North African tagine flavor logic: sweet spice, dark depth, and fresh herbal finish.",
     "Dark Chocolate Lamb Basil Tagine",
     ["Brown lamb shoulder in batches, set aside; sauté onion with ras el hanout and a square of dark chocolate.","Return lamb with crushed tomatoes and stock; braise covered at 325°F for 2 hours until tender.","Stir in a handful of torn fresh basil just before serving; plate over couscous with toasted almonds."]),

    ("basil","chocolate","lavender",
     "Chocolate's fermentation-derived linalool and 2-phenylethanol align with lavender's dominant terpene compounds — creating an unusually high shared floral aromatic overlap for a chocolate pairing — while basil reinforces this shared linalool set, amplifying the perfumed register before chocolate's roasted bitterness grounds it. The trio creates an intensely aromatic, Provençal-inflected dark chocolate confection.",
     "Lavender Basil Dark Chocolate Ganache",
     ["Heat cream with dried lavender and fresh basil until steaming; steep 15 minutes then strain well.","Pour the hot infused cream over finely chopped dark chocolate and stir until smooth and glossy.","Pour into a lined tray, refrigerate until firm, then cut into squares and dust with cocoa powder."]),

    ("basil","chocolate","lemon",
     "Dark chocolate's acidity and tannin structure are sharpened by lemon's citric acid — the same principle behind chocolate-orange confections — while basil's linalool and geraniol bridge the citrus-herbal gap into chocolate's floral fermentation register. The trio creates a bright, high-acidity chocolate preparation where each ingredient's acid contribution reinforces the others.",
     "Lemon Basil Dark Chocolate Tart",
     ["Make a ganache with dark chocolate, heavy cream, lemon zest, and finely chopped fresh basil; pour into a baked shell.","Refrigerate until set, about 2 hours; meanwhile make a lemon curd for the top layer.","Spread a thin lemon curd layer over the set ganache; garnish with candied lemon peel and basil."]),

    ("basil","chocolate","mint",
     "Chocolate and mint share 1,8-cineole as a minor compound — the cooling terpene that aligns menthol's refreshing character with chocolate's subtle aromatics — while basil's eugenol adds a spiced herbal depth beneath the menthol that gives the classic pairing a more complex, less candy-like register. Together the trio elevates mint-chocolate from confection to refined after-dinner flavor.",
     "Mint Basil Dark Chocolate Truffles",
     ["Steep fresh mint and basil in warm cream 20 minutes; strain and pour over chopped dark chocolate.","Stir until smooth, add a pinch of flaky salt, and refrigerate ganache until firm enough to roll.","Shape into balls, roll in cocoa powder, and press a tiny fresh basil leaf onto each before serving."]),

    ("basil","chocolate","oyster",
     "Dark chocolate and oyster share phenylacetaldehyde and dimethyl sulfide — the rosy-fermented and marine-sulfurous compound family that connects fermented cacao to oceanic brine — while basil's benzaldehyde and linalool provide the herbal aromatic lift that bridges the intense contrast between dark bitter-roast and briny marine. The trio is a bold umami pairing used in avant-garde seafood applications.",
     "Dark Chocolate Oyster Basil Mignonette",
     ["Finely grate dark chocolate (70%+) and mix with red wine vinegar, shallots, and cracked pepper.","Stir in very finely chopped fresh basil and a pinch of flaky salt; let rest 10 minutes to meld.","Spoon a small amount onto freshly shucked raw oysters and serve immediately over crushed ice."]),

    ("basil","chocolate","parmesan",
     "Dark chocolate and Parmesan share phenylacetaldehyde and furaneol — rosy-fermented and sweet-caramel compounds spanning both aged dairy and roasted cacao — while basil's linalool and 2-phenylethanol provide herbal-floral brightness that prevents the umami-roasted combination from becoming too dense. The trio creates a sophisticated savory-sweet register used in Italian chocolate-cheese preparations.",
     "Dark Chocolate Parmesan Basil Crisps",
     ["Melt dark chocolate and spread thinly on parchment; immediately scatter finely grated Parmesan over top.","Press very finely chopped fresh basil into the surface before chocolate sets completely.","Break into irregular shards once fully cooled; serve with wine or as a cheese board accent."]),
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
print(f"Batch 003 done: inserted {len(TRIPLETS)} triplets.")
