#!/usr/bin/env python3
"""Seed pair descriptions batch 2: chocolate through garlic pairs (54 pairs)"""
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

PAIRS = [
    # ── chocolate (15 pairs) ──
    ("chocolate","coffee",
     "Chocolate and coffee share vanillin, phenylacetaldehyde, acetic acid, and dimethyl sulfide — four Maillard-roasted compounds that make them near-identical in chemical terms despite tasting very different. Coffee's bitter chlorogenic acids amplify chocolate's roasted polyphenols, creating a depth that neither achieves alone.",
     "Mocha Flourless Cake",
     ["Melt dark chocolate and butter together, cool slightly before adding eggs.","Whisk in sugar, a shot of espresso, and a pinch of salt — no flour.","Bake at 350°F in a water bath 25 minutes; it firms as it cools."]),

    ("chocolate","cucumber",
     "Chocolate and cucumber share hexanal and trace linalool — green aldehyde notes that, surprisingly, occur during cacao fermentation alongside the roasted compounds. Cucumber's clean (E)-2-nonenal acts as a palate-refresher that resets the richness of dark chocolate between bites.",
     "Cucumber Dark Chocolate Gazpacho",
     ["Blend cucumber with water, mint, lime juice, and a small square of dark chocolate.","Chill overnight; the chocolate emulsifies into the cucumber liquid as it rests.","Serve very cold in small glasses with a chocolate-dipped cucumber slice."]),

    ("chocolate","garlic",
     "Chocolate and garlic share dimethyl sulfide — a sulfurous compound present in both roasted cacao and cooked garlic. While counterintuitive, deeply roasted garlic's diallyl disulfide transforms into sweet vinyl compounds that echo chocolate's complex aromatic depth in savory preparations.",
     "Mole Negro",
     ["Toast dried chiles, blend with roasted garlic, tomato, and Mexican chocolate.","Simmer with chicken stock until the mole thickens and turns very deep brown.","Adjust salt and sugar balance, serve over roasted chicken with sesame."]),

    ("chocolate","lamb",
     "Chocolate and lamb share dimethyl sulfide and phenylacetaldehyde — connecting roasted cacao and animal fat through shared sulfurous-floral compounds. Dark chocolate's bitter polyphenols cut through lamb's fatty 4-methyloctanoic acid in the same way that a red wine does.",
     "Lamb Shanks with Dark Chocolate Mole",
     ["Brown lamb shanks well on all sides in a heavy pot over high heat.","Add mole sauce made with dried chiles, spices, and 70% dark chocolate.","Braise covered at 325°F for 3 hours until falling off the bone."]),

    ("chocolate","lavender",
     "Chocolate and lavender share linalool — a floral terpene compound that occurs in cacao's fermentation profile and is lavender's dominant aroma. Lavender's linalyl acetate bridges cacao's fruity ester notes (from fermentation) into something perfumed and distinctly Provençal.",
     "Lavender Dark Chocolate Truffles",
     ["Steep dried lavender in hot cream 15 minutes, strain, use to make ganache.","Melt in dark chocolate until smooth, cool until scoopable in the fridge.","Roll into balls, coat in cocoa powder, and refrigerate until firm."]),

    ("chocolate","lemon",
     "Chocolate and lemon share acetic acid and trace linalool — tart-floral compounds that connect citrus brightness to cacao's fermentation-derived acidity. Lemon's citral cuts through chocolate's dense fat and amplifies its fruit esters, making the chocolate taste more complex rather than just bitter.",
     "Dark Chocolate Lemon Tart",
     ["Make a dark chocolate ganache tart filling with lemon zest in the cream.","Pour into a blind-baked shell and refrigerate until set, about 2 hours.","Finish with candied lemon peel and flaky salt across the top."]),

    ("chocolate","mint",
     "Chocolate and mint share linalool and trace acetic acid — but this pairing works primarily through contrast: menthol's cooling sensation creates a thermal contrast with the warmth of dark chocolate, while mint's camphor-like compounds contrast cacao's earthy depth to create a clean, refreshing finish.",
     "Thin Mint Bark",
     ["Melt dark chocolate and spread thin on parchment, about 3mm thick.","Scatter crushed peppermint candy canes across the wet chocolate evenly.","Refrigerate until fully set, then break into irregular shards to serve."]),

    ("chocolate","oyster",
     "Chocolate and oyster share phenylacetaldehyde and dimethyl sulfide — connecting the roasted depth of dark chocolate to the briny minerality of oysters. This is a celebrated pairing in molecular gastronomy: chocolate's tannins mirror the astringency of oyster liquor, while both share complex fermentation-derived aromatics.",
     "Dark Chocolate Oyster Mignonette",
     ["Melt a small piece of dark chocolate into a warm shallot-vinegar mignonette.","Cool until just above room temperature — it should remain liquid, barely.","Spoon a few drops onto freshly shucked oysters; serve immediately."]),

    ("chocolate","parmesan",
     "Chocolate and Parmesan share phenylacetaldehyde and dimethyl sulfide — compounds found in aged dairy fermentation and cacao roasting alike. Parmesan's crystalline glutamate amplifies dark chocolate's savory umami undertones, making the combination taste more complex and less sweet.",
     "Chocolate Parmesan Crackers",
     ["Mix almond flour, grated Parmesan, cocoa powder, and a pinch of salt.","Bind with cold butter, roll thin, cut into squares, and chill 30 minutes.","Bake at 350°F until crisp; serve warm with aged cheese and honey."]),

    ("chocolate","rose",
     "Chocolate and rose share 2-phenylethanol and linalool — floral compounds that cacao fermentation produces alongside its fruit esters, and which constitute the primary aroma of rose petals. The rose amplifies cacao's hidden floral notes, making the chocolate taste more complex and less one-dimensional.",
     "Rose Chocolate Mousse",
     ["Melt dark chocolate, fold in rose water with whipped cream in two stages.","Beat egg whites to stiff peaks, fold gently into the chocolate-cream mixture.","Chill in cups at least 2 hours, top with a candied rose petal to serve."]),

    ("chocolate","salmon",
     "Chocolate and salmon share linalool and dimethyl sulfide — a floral-sulfurous thread connecting fatty fish and roasted cacao. While counterintuitive, the bittersweet compounds in dark chocolate cut through salmon's rich omega-3 fats in the same way that teriyaki or miso glazes do.",
     "Mole-Glazed Salmon",
     ["Make a simple mole with dark chocolate, ancho chile, garlic, and cumin.","Brush generously onto salmon fillets and marinate 30 minutes.","Broil 8 minutes until the mole lacquers and the salmon is just cooked."]),

    ("chocolate","strawberry",
     "Chocolate and strawberry share furaneol, linalool, 2-phenylethanol, and vanillin — four of the most significant volatile aroma compounds in both ingredients. This near-perfect compound overlap explains why the pairing feels effortless: they are essentially the same flavor family in different expressions.",
     "Strawberry Chocolate Pavlova",
     ["Whip meringue to stiff peaks, fold in cocoa powder gently at the end.","Bake at 250°F for 90 minutes until crisp outside and marshmallowy inside.","Top with whipped cream, sliced strawberries, and a dark chocolate drizzle."]),

    ("chocolate","tomato",
     "Chocolate and tomato share furaneol, acetic acid, and hexanal — the same sweet-tart-green volatile compounds that both develop during ripening and roasting. This is the basis of mole's secret: tomato's beta-ionone (violet-like) and lycopene-derived compounds deepen chocolate's complexity dramatically.",
     "Chocolate Tomato Soup",
     ["Roast tomatoes and shallots at 400°F until deeply caramelized and jammy.","Blend smooth with stock, finish by melting in a square of dark chocolate.","Adjust seasoning, serve with sourdough and a swirl of crème fraîche."]),

    ("chocolate","truffle",
     "Chocolate and truffle share phenylacetaldehyde, dimethyl sulfide, and anisaldehyde — three of the most powerful aromatic compounds in gastronomy. Both are fermentation products (cacao bean ferment; truffle mycorrhiza); together their earthy-roasted-floral profiles amplify each other into something intensely luxurious.",
     "Truffle Chocolate Ganache",
     ["Heat cream with a tiny amount of truffle oil (or shaved fresh truffle).","Pour over chopped 70% dark chocolate, stir until smooth and glossy.","Use as a sauce over vanilla ice cream with shaved truffle on top."]),

    ("chocolate","vanilla",
     "Chocolate and vanilla share vanillin, 2-phenylethanol, furaneol, and linalool — vanilla is literally what cacao fermentation produces alongside its chocolate compounds. This is why every good chocolate recipe includes vanilla: vanilla's pure vanillin rounds chocolate's harsh bitter edges into something coherent.",
     "Classic Chocolate Chip Cookies",
     ["Cream butter and sugars, add eggs and vanilla extract until fluffy.","Fold in flour, salt, baking soda, and chocolate chips — chill dough 1 hour.","Bake at 375°F until just golden; pull while centers look slightly underdone."]),

    # ── coffee (14 pairs) ──
    ("coffee","cucumber",
     "Coffee and cucumber share linalool and hexanal — floral and green aldehyde compounds that create an unexpected bridge between roasted depth and fresh garden character. Cucumber's (E)-2-nonenal is used by perfumers as a 'freshener' that cuts through dense, dark notes — exactly what it does for coffee.",
     "Cold Brew Cucumber Spritz",
     ["Brew strong cold brew coffee concentrate overnight, strain through fine mesh.","Blend cucumber with lime juice and a pinch of salt until smooth, strain.","Mix cold brew concentrate with cucumber water over ice, top with sparkling water."]),

    ("coffee","garlic",
     "Coffee and garlic share dimethyl sulfide and acetic acid — pungent, sulfurous compounds that connect roasted and allium flavors. Coffee's bitter compounds and garlic's harsh allicin both mellow dramatically with heat; combined in a rub, they create a complex savory crust unlike any single-note seasoning.",
     "Coffee-Garlic Dry Rub Brisket",
     ["Mix finely ground coffee, minced garlic, smoked paprika, salt, and brown sugar.","Rub aggressively all over a trimmed brisket and rest overnight in the fridge.","Smoke or oven-roast at 250°F for 8–10 hours until deeply dark and tender."]),

    ("coffee","lamb",
     "Coffee and lamb share dimethyl sulfide, acetic acid, and phenylacetaldehyde — a sulfurous-fermented-floral compound set that connects roasted coffee to the complex fatty acids of lamb. Coffee's bitter compounds work like tannins in red wine, cutting through lamb's fat and suppressing gaminess.",
     "Coffee-Rubbed Lamb Leg",
     ["Mix ground espresso, cumin, coriander, garlic, salt, and smoked paprika together.","Rub the whole lamb leg aggressively and marinate overnight refrigerated.","Roast at 325°F 2.5–3 hours until pulling-tender, rest well before carving."]),

    ("coffee","lavender",
     "Coffee and lavender share linalool — a floral terpene compound in coffee's roasting-derived volatiles and lavender's primary aromatic compound. Coffee's guaiacol (a smoky phenol) grounds lavender's sometimes soapy notes into something earthy and sophisticated.",
     "Lavender Cortado",
     ["Make a lavender simple syrup by heating equal parts sugar and water with dried lavender.","Pull a double shot of espresso directly over a spoonful of lavender syrup.","Add an equal volume of warm steamed whole milk and serve immediately."]),

    ("coffee","lemon",
     "Coffee and lemon share acetic acid and trace linalool — tart, bright compounds that connect roasted bitterness to citrus freshness. A splash of lemon juice in cold brew or espresso is a traditional technique in parts of Italy: the citric acid cuts bitterness while the oils of the peel add complexity.",
     "Espresso Romano",
     ["Pull a fresh double shot of espresso into a warm, pre-heated demitasse cup.","Add a thin slice of fresh lemon peel to the espresso, stir once gently.","Drink immediately — the lemon cuts the bitterness and adds a bright finish."]),

    ("coffee","mint",
     "Coffee and mint share linalool and limonene at trace levels — terpene compounds that coffee produces during roasting and mint in its essential oils. Menthol's cooling sensation contrasts with coffee's heat and bitterness, creating a refreshing polarity that makes the combination feel palate-cleansing.",
     "Mint Espresso Granita",
     ["Brew strong espresso, sweeten lightly, pour into a shallow freezer-safe dish.","Steep fresh mint in the hot espresso before freezing to infuse completely.","Freeze, scraping every 30 minutes with a fork until granita consistency."]),

    ("coffee","oyster",
     "Coffee and oyster share phenylacetaldehyde and dimethyl sulfide — compounds connecting the Maillard-roasted world of coffee with the microbial brine world of oysters. Coffee's acidity mirrors the mineral acidity of oyster liquor; together they create a marine-meets-roasted depth unusual in pairing.",
     "Oysters with Espresso Mignonette",
     ["Reduce espresso with shallots and red wine vinegar until slightly syrupy.","Cool to room temperature, season with cracked pepper and a pinch of sugar.","Spoon a small amount onto freshly shucked oysters on the half shell."]),

    ("coffee","parmesan",
     "Coffee and Parmesan share phenylacetaldehyde, dimethyl sulfide, and acetic acid — a roasted-fermented-pungent compound thread that bridges two of the most complex umami-rich foods in the world. Coffee's bitter polyphenols amplify Parmesan's glutamate into an intensely savory finish.",
     "Parmesan Espresso Risotto",
     ["Sauté shallots in butter, toast arborio, deglaze with white wine until absorbed.","Add warm stock gradually, stirring, until creamy and al dente.","Finish off heat with a shot of espresso and generous grated Parmesan."]),

    ("coffee","rose",
     "Coffee and rose share 2-phenylethanol and linalool — floral compounds produced both by rose petals and by coffee during roasting. Rose's geraniol lifts coffee's sometimes bitter, ashy notes into something more aromatic and perfumed without adding sweetness.",
     "Rose Cold Brew Tonic",
     ["Make a 24-hour cold brew concentrate with medium-roast coffee grounds.","Add a few drops of rose water to a glass with ice and tonic water.","Pour cold brew concentrate over top gently so layers form visibly."]),

    ("coffee","salmon",
     "Coffee and salmon share dimethyl sulfide, linalool, and acetic acid — connecting roasted volatiles to the fatty acids of salmon. Coffee's bitter chlorogenic acids act as a counterbalance to salmon's rich omega-3 fat, creating a crust that adds savory complexity without overpowering delicate fish flavor.",
     "Coffee-Crusted Salmon",
     ["Mix finely ground coffee, brown sugar, smoked paprika, salt, and a pinch of cayenne.","Press the rub firmly onto salmon skin side and flesh side, rest 15 minutes.","Sear skin-side down in a hot pan, flip once, finish in a 400°F oven 5 minutes."]),

    ("coffee","strawberry",
     "Coffee and strawberry share linalool, acetic acid, and vanillin — fermented and roasted volatiles that connect the two ingredients through their respective processing histories. Coffee's bitterness amplifies strawberry's sweetness through contrast; together they taste more vivid than either alone.",
     "Strawberry Cold Brew Smoothie",
     ["Blend frozen strawberries with cold brew coffee concentrate and a banana.","Add a splash of cream and a pinch of salt to round the flavor.","Serve immediately over ice in a tall glass with a fresh strawberry garnish."]),

    ("coffee","tomato",
     "Coffee and tomato share furaneol, acetic acid, and hexanal — sweet-tart-green compounds connecting two fermentation-forward foods. Coffee's roasted compounds add umami depth to tomato sauces in the same way anchovy paste does; a tablespoon of espresso in a bolognese is a professional chef's secret.",
     "Espresso Bolognese",
     ["Brown ground beef and pork in batches, deglaze each batch with red wine.","Add crushed tomatoes, a shot of espresso, and simmer 90 minutes uncovered.","Finish with cold butter stirred in off heat, serve over fresh tagliatelle."]),

    ("coffee","truffle",
     "Coffee and truffle share phenylacetaldehyde, dimethyl sulfide, and guaiacol — three of the most powerful savory-earthy aromatic compounds in food. Both are defined by fermentation and microbial transformation; together their roasted-earthy-pungent profiles amplify each other into something extraordinarily complex.",
     "Truffle Coffee Sauce for Steak",
     ["Make a reduction with espresso, beef stock, and shallots until syrupy.","Whisk in cold butter in pieces off the heat to create a glossy sauce.","Finish with a few drops of truffle oil and shaved truffle over the steak."]),

    ("coffee","vanilla",
     "Coffee and vanilla share vanillin, linalool, 2-phenylethanol, and 4-vinylguaiacol — a near-complete overlap of sweet-floral roasted volatiles. Vanilla was historically added to early chocolate-and-coffee drinks because its vanillin rounds bitter compounds; this is why café de olla and many espresso drinks include a touch of vanilla.",
     "Vanilla Bean Cold Brew",
     ["Grind coffee coarse, combine with cold water and a split vanilla bean in a jar.","Steep 18–24 hours in the refrigerator, strain through a fine mesh filter.","Serve over ice with a splash of whole milk and a tiny pinch of salt."]),

    # ── cucumber (13 pairs) ──
    ("cucumber","garlic",
     "Cucumber and garlic share dimethyl sulfide and hexanal — an unlikely but effective pair that defines Greek tzatziki and countless Eastern European cold salads. Garlic's pungency is moderated by cucumber's water content and its (E)-2-nonenal, which pushes the combination toward refreshing rather than sharp.",
     "Classic Tzatziki",
     ["Grate cucumber, squeeze out all excess moisture through a clean towel.","Mix with Greek yogurt, minced garlic, dill, lemon juice, and olive oil.","Rest at least 1 hour before serving cold with warm pita."]),

    ("cucumber","lamb",
     "Cucumber and lamb share hexanal and linalool — green and floral aldehyde compounds that bridge the cooling freshness of cucumber with lamb's complex fatty character. Cucumber's (E,Z)-2,6-nonadienal (melon-watermelon note) directly suppresses the harsh 4-methyloctanoic acid that makes lamb gamey.",
     "Lamb Kofta with Cucumber Yogurt",
     ["Mix ground lamb with cumin, coriander, garlic, and fresh herbs, form into cylinders.","Grill on skewers over high heat until charred outside and just cooked through.","Serve in flatbread with grated cucumber yogurt sauce and sliced tomato."]),

    ("cucumber","lavender",
     "Cucumber and lavender share linalool — a floral terpene that cucumber contains as a minor compound and lavender in dominant concentration. Cucumber's clean hexanal and (E)-2-nonenal create a green freshness that prevents lavender from reading as soapy, grounding the floral into something crisp.",
     "Lavender Cucumber Gin Cooler",
     ["Make lavender syrup, cool, combine with cucumber juice and fresh lemon.","Add gin, stir with ice until well chilled, strain into a coupe glass.","Garnish with a cucumber ribbon and a small sprig of fresh lavender."]),

    ("cucumber","lemon",
     "Cucumber and lemon share linalool and trace geraniol — terpene compounds that create a mutually reinforcing freshness. Both contain compounds in the 'clean and bright' aldehyde family; together they amplify each other's lightness rather than competing for aromatic space.",
     "Cucumber Lemon Agua Fresca",
     ["Blend peeled cucumber with cold water, lemon juice, and a pinch of salt.","Strain through a fine sieve, sweeten lightly with simple syrup to taste.","Serve immediately over ice with mint and thin lemon wheels."]),

    ("cucumber","mint",
     "Cucumber and mint share linalool and benzaldehyde — terpene and aldehyde compounds that combine the cooling freshness of both ingredients into something that reads as almost refrigeratingly cold even at room temperature. Menthol and (E)-2-nonenal together create the most perceived 'cooling' flavor pairing in food.",
     "Cucumber Mint Raita",
     ["Grate cucumber, salt, rest 10 minutes, squeeze out all moisture.","Mix with plain yogurt, chopped mint, cumin, and a squeeze of lemon.","Serve chilled alongside spiced dishes or as a cooling dip."]),

    ("cucumber","oyster",
     "Cucumber and oyster share hexanal and benzaldehyde — green aldehyde and mild aromatic compounds that connect the garden freshness of cucumber to the subtle sweetness beneath oyster brine. Cucumber's high water content dilutes and refreshes the mineral intensity of raw oyster.",
     "Oysters with Cucumber Mignonette",
     ["Finely dice cucumber, combine with rice wine vinegar and minced shallot.","Add fresh dill, cracked pepper, and a pinch of sugar, chill 20 minutes.","Spoon a small amount onto freshly shucked oysters and serve immediately."]),

    ("cucumber","parmesan",
     "Cucumber and Parmesan share hexanal and linalool at trace levels — a pairing that works through contrast: cucumber's watery freshness and Parmesan's concentrated crystalline umami create a textural and flavor polarity that makes both ingredients taste more defined alongside each other.",
     "Cucumber Parmesan Salad",
     ["Shave Parmesan into thin sheets with a vegetable peeler over sliced cucumber.","Dress with lemon juice, olive oil, and cracked pepper — nothing more.","Serve immediately on a cold plate while the Parmesan is still crisp."]),

    ("cucumber","rose",
     "Cucumber and rose share 2-phenylethanol, geraniol, linalool, and benzaldehyde — four compounds that make these two among the most aromatic 'fresh' ingredients in food and perfumery. Together they create a floral-green aromatic that is the basis of many Middle Eastern drink and dessert traditions.",
     "Rose Cucumber Lassi",
     ["Blend yogurt with diced cucumber, rose water, and a little honey.","Add cold water to thin to a pourable consistency, season with salt.","Serve in chilled glasses with a sprinkle of ground cardamom on top."]),

    ("cucumber","salmon",
     "Cucumber and salmon share hexanal and linalool — green aldehyde and floral terpene compounds that create a bridge between the freshness of raw cucumber and the delicate floral notes in quality salmon. Cucumber's high water content also cleanses the fat from salmon between bites.",
     "Salmon Cucumber Tartare",
     ["Dice sashimi-grade salmon fine, mix with soy, sesame oil, and lime juice.","Fold in finely diced cucumber and scallion just before serving.","Serve immediately on cucumber rounds or rice crackers."]),

    ("cucumber","strawberry",
     "Cucumber and strawberry share linalool and benzaldehyde — terpene and almond-adjacent aromatic compounds that create an unexpectedly coherent fresh-sweet pairing. The (E)-2-nonenal in cucumber acts as a flavor enhancer that makes strawberry's ethyl butanoate (its primary fruity ester) read as more intense.",
     "Strawberry Cucumber Salad",
     ["Slice strawberries and cucumber thinly, toss with balsamic vinegar and honey.","Let rest 10 minutes for the juices to release and combine.","Finish with torn basil and a crack of black pepper just before serving."]),

    ("cucumber","tomato",
     "Cucumber and tomato share hexanal, furaneol, and linalool — the volatile set that defines 'fresh garden.' Both contain beta-ionone (violet-like) and green aldehyde compounds in similar ratios, making them one of the highest-overlap pairs in this dataset and the basis of every summer salad.",
     "Panzanella",
     ["Tear stale sourdough into rough chunks, toss with olive oil and salt.","Combine with diced tomatoes, cucumber, red onion, and torn basil.","Dress with good olive oil and red wine vinegar, rest 20 minutes before serving."]),

    ("cucumber","truffle",
     "Cucumber and truffle share anisaldehyde and trace phenylacetaldehyde — aromatic aldehyde compounds connecting cucumber's clean freshness to truffle's deep earthy complexity. The contrast between cucumber's aqueous lightness and truffle's dense aromatic weight creates a vivid high-low pairing.",
     "Truffle Cucumber Carpaccio",
     ["Slice cucumber paper-thin on a mandoline and arrange on a cold plate.","Drizzle with white truffle oil and a few drops of lemon juice.","Shave fresh black or white truffle generously across the top, serve immediately."]),

    ("cucumber","vanilla",
     "Cucumber and vanilla share linalool and 2-phenylethanol — terpene and rose-alcohol compounds that create an elegant, floral-fresh bridge between cool vegetable and warm sweet spice. This unexpected pairing is the basis of several haute-cuisine desserts and Nordic cuisine preparations.",
     "Vanilla Cucumber Granita",
     ["Split a vanilla bean into cold simple syrup, steep in fridge overnight.","Add fresh cucumber juice to the syrup, pour into a shallow freezer pan.","Freeze, scraping every 30 minutes until granita texture, serve with mint."]),

    # ── garlic (12 pairs) ──
    ("garlic","lamb",
     "Garlic and lamb share dimethyl sulfide and acetic acid — sulfurous and acidic compounds that deepen together into intense savory richness. Garlic's allicin is chemically transformed by lamb's own fatty acids during slow cooking, producing sweet, complex sulfide compounds that suppress gaminess perfectly.",
     "Slow-Roasted Garlic Lamb Shoulder",
     ["Stud lamb shoulder with whole garlic cloves pushed deep into slits all over.","Rub with olive oil, rosemary, salt, and more crushed garlic on the surface.","Roast covered at 300°F for 4–5 hours, uncover last 30 minutes to brown."]),

    ("garlic","lavender",
     "Garlic and lavender share linalool and dimethyl sulfide — a floral-sulfurous compound thread that sounds strange but underlies the Herbes de Provence tradition of pairing both with lamb and pork. Lavender's linalyl acetate balances garlic's pungent allicin by introducing a clean terpene freshness.",
     "Herbes de Provence Roasted Chicken",
     ["Mix dried lavender, garlic, thyme, rosemary, and olive oil into a paste.","Rub under and over the skin of the chicken and rest 2 hours or overnight.","Roast at 400°F breast-side up until golden and cooked through, about 60 min."]),

    ("garlic","lemon",
     "Garlic and lemon share acetic acid and trace linalool — but the pairing works primarily through contrast: lemon's citric acid reacts with garlic's allicin to partially convert its harsh pungency into milder, sweeter compounds. This is why aioli always contains lemon: the acid softens the raw garlic.",
     "Lemon Garlic Aioli",
     ["Whisk egg yolks with Dijon, lemon juice, and minced garlic until pale.","Slowly drizzle in neutral oil while whisking constantly until thick.","Season with salt, finish with more lemon juice to taste; chill before serving."]),

    ("garlic","mint",
     "Garlic and mint share dimethyl sulfide and linalool — a sulfurous-floral compound thread that defines Middle Eastern cooking, particularly with lamb and yogurt dishes. Mint's menthol provides a refreshing counterpoint that makes garlic's pungency feel cleaner and more aromatic rather than harsh.",
     "Mint Garlic Lamb Meatballs",
     ["Mix ground lamb with minced garlic, fresh mint, cumin, and a touch of yogurt.","Roll into balls and pan-fry until golden on the outside and just cooked through.","Serve with extra yogurt, warm flatbread, and a scatter of chopped mint."]),

    ("garlic","oyster",
     "Garlic and oyster share dimethyl sulfide — the primary sulfurous compound in both cooked garlic and raw oyster. Garlic's allicin is transformed by the brine and heat to create sweet vinyl sulfides that amplify rather than overwhelm oyster's delicate marine character.",
     "Garlic Butter Roasted Oysters",
     ["Make a compound butter with roasted garlic, parsley, lemon zest, and salt.","Place a small knob on each oyster in its half-shell on a baking sheet.","Broil 3–4 minutes until butter is bubbling and oyster edges just begin to curl."]),

    ("garlic","parmesan",
     "Garlic and Parmesan share dimethyl sulfide, acetic acid, and phenylacetaldehyde — a pungent-umami compound thread that defines one of the most beloved flavor combinations in Mediterranean cooking. Parmesan's glutamate amplifies garlic's savory intensity in a classic positive feedback loop.",
     "Parmesan Garlic Roasted Asparagus",
     ["Toss asparagus with olive oil, minced garlic, salt, and cracked pepper.","Roast at 425°F for 12–15 minutes until tips are slightly charred.","Remove from oven, immediately shower with finely grated Parmesan to melt."]),

    ("garlic","rose",
     "Garlic and rose share 2-phenylethanol — the same floral alcohol compound present in both rose essential oil and the metabolic byproducts of garlic fermentation. In Middle Eastern cuisine, garlic and rose water are combined in several dessert-adjacent savory dishes for exactly this aromatic reason.",
     "Rose-Scented Garlic Yogurt Sauce",
     ["Roast a whole head of garlic until the cloves are sweet and very soft.","Squeeze out cloves, blend with yogurt, a few drops of rose water, and lemon.","Season with salt, drizzle with olive oil; serve alongside grilled meats."]),

    ("garlic","salmon",
     "Garlic and salmon share dimethyl sulfide, linalool, and acetic acid — sulfurous and floral compounds that connect the allium world to fatty fish. Garlic's harsh allicin is neutralized by salmon's omega-3 fat, converting into sweet cooked-garlic compounds that complement rather than overwhelm the fish.",
     "Garlic Herb Salmon en Papillote",
     ["Place salmon on parchment with sliced garlic, lemon wheels, and fresh dill.","Fold into a sealed parcel, ensuring the edges are tightly crimped all around.","Bake at 400°F for 12–15 minutes; open at the table to release the aromatics."]),

    ("garlic","strawberry",
     "Garlic and strawberry share linalool and trace acetic acid — an unexpected volatile bridge that makes a small amount of roasted garlic work as a flavor enhancer in strawberry-based savory preparations. The Maillard compounds from caramelized garlic echo strawberry's furaneol, creating a sweet-savory unity.",
     "Strawberry Balsamic with Roasted Garlic",
     ["Roast whole garlic head, squeeze soft cloves into a pan with sliced strawberries.","Add balsamic vinegar and a touch of sugar, cook until syrupy and jammy.","Serve warm over vanilla ice cream or alongside aged cheese on a board."]),

    ("garlic","tomato",
     "Garlic and tomato share dimethyl sulfide, acetic acid, and furaneol — sulfurous and sweet-tart compounds that together form the aromatic backbone of Mediterranean cooking. Garlic's allicin transforms in the presence of tomato's acid into sweet diallyl compounds that round the sauce into something deeply savory.",
     "Simple Tomato Sauce",
     ["Slowly cook minced garlic in olive oil until golden and fragrant, not brown.","Add crushed canned tomatoes, season with salt, simmer 25 minutes uncovered.","Finish with fresh basil and a thread of good olive oil just before serving."]),

    ("garlic","truffle",
     "Garlic and truffle share dimethyl sulfide, phenylacetaldehyde, and 2,4-dithiapentane — intensely sulfurous and aromatic compounds that amplify each other's depth dramatically. Professional truffle preparations almost always include garlic for this reason: garlic's allium base makes truffle's volatile sulfides more persistent and defined.",
     "Truffle Garlic Scrambled Eggs",
     ["Very gently beat eggs with cream and season lightly, no rushing this.","Cook over the lowest heat in a pan with truffle butter, stirring constantly.","Remove still slightly loose, top with shaved truffle and toasted baguette."]),

    ("garlic","vanilla",
     "Garlic and vanilla share trace 2-phenylethanol and dimethyl sulfide — a floral-sulfurous bridge that sounds improbable but underlies certain haute-cuisine preparations. Vanilla's vanillin actually suppresses garlic's harsh allicin compounds while amplifying its sweeter cooked notes — the result is startlingly savory-sweet.",
     "Vanilla Garlic Roasted Shrimp",
     ["Combine olive oil, roasted garlic, a tiny amount of vanilla, lemon, and chili.","Toss with large shrimp and roast at 425°F for 8–10 minutes until curled.","Serve immediately with crusty bread to soak up the aromatic oil."]),
]

conn = sqlite3.connect(DB)
c = conn.cursor()
inserted = 0
for (a, b, desc, title, steps) in PAIRS:
    a, b = sorted([a, b])
    c.execute(
        "INSERT OR REPLACE INTO pair_info (ing_a, ing_b, description, recipe_title, recipe_steps) VALUES (?, ?, ?, ?, ?)",
        (a, b, desc, title, json.dumps(steps))
    )
    inserted += 1
conn.commit()
conn.close()
print(f"Batch 2 done: inserted {inserted} pairs.")
