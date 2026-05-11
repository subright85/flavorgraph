#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("chocolate","strawberry","truffle",
     "Chocolate and strawberry share furaneol — sweet-caramel in both — while truffle and strawberry share phenylacetaldehyde, the rosy-fermented compound that earthy fungus and ripe berry produce independently. Chocolate and truffle additionally share dimethyl sulfide, creating a complete three-way compound web that makes this unusual luxury dessert trio chemically precise.",
     "Truffle Strawberry Dark Chocolate Tart",
     ["Make a dark chocolate ganache tart; arrange halved fresh strawberries over the set ganache.", "Glaze with a truffle honey: warm honey with a drizzle of truffle oil until fragrant.", "Drizzle truffle honey over the strawberry tart and shave a little fresh truffle over to serve."]),

    ("chocolate","strawberry","vanilla",
     "Chocolate and strawberry share furaneol — sweet-caramel in both — while chocolate and vanilla share vanillin and furfural, and strawberry and vanilla share linalool and 2-phenylethanol. Every ingredient connects to both others through at least two shared compounds, creating perhaps the most aromatic coherence possible in a classic dessert trio.",
     "Vanilla Strawberry Dark Chocolate Trifle",
     ["Layer dark chocolate sponge with vanilla custard and macerated fresh strawberries in a glass bowl.", "Repeat layers; finish with whipped cream, chocolate curls, and whole strawberries.", "Refrigerate 4 hours before serving; the flavors meld into a classic aromatic unity."]),

    ("chocolate","tomato","truffle",
     "Chocolate, tomato, and truffle all share phenylacetaldehyde and dimethyl sulfide — rosy-fermented and sulfurous compounds spanning cacao, roasted vegetable, and earthy fungal chemistry — creating perhaps the most complete three-way compound alignment outside the caramel-vanilla-strawberry trio. The combination produces an intensely complex savory mole with truffle depth.",
     "Truffle Dark Chocolate Tomato Mole",
     ["Toast dried mulato chilies; blend with roasted tomatoes, dark chocolate, and truffle butter.", "Simmer with stock until thick and aromatic; shave truffle into the hot sauce off heat.", "Serve over duck confit or poached chicken with sesame seeds and warm tortillas."]),

    ("chocolate","tomato","vanilla",
     "Chocolate and tomato share phenylacetaldehyde and pyrazines — rosy-fermented and Maillard-roasted compounds — while chocolate and vanilla share vanillin, and tomato and vanilla share furaneol, creating a chain of two-way compound connections linking all three. The trio drives sophisticated sweet-savory preparations where tomato's umami is deepened by chocolate and sweetened by vanilla.",
     "Vanilla Dark Chocolate Tomato Jam",
     ["Cook ripe tomatoes with sugar and a split vanilla bean until thick and jammy.", "Add a square of dark chocolate and stir until melted; the chocolate deepens and vanilla rounds.", "Cool and jar; serve with cheese or aged meats — an unusual condiment with a complete flavor arc."]),

    ("chocolate","truffle","vanilla",
     "Chocolate and truffle share dimethyl sulfide and phenylacetaldehyde — sulfurous and rosy-fermented compounds — while chocolate and vanilla share vanillin, and truffle and vanilla share vanillin as a key aromatic compound (black truffle producing trace vanillin through enzymatic fermentation). The three-way vanillin connection creates the ultimate earthy-sweet-dark luxury compound.",
     "Truffle Vanilla Dark Chocolate Fondant",
     ["Make dark chocolate fondant batter with truffle butter, eggs, sugar, and vanilla bean seeds.", "Pour into buttered ramekins; bake at 400°F for 10 minutes until just set at edges.", "Serve immediately; the molten center carries truffle and vanilla into the chocolate bitterness."]),

    ("coffee","cucumber","garlic",
     "Coffee's furfural and pyrazines — roasted-bitter Maillard compounds — contrast with cucumber's (E)-2-nonenal clean freshness through a dark-light aromatic opposition, while garlic's dimethyl sulfide provides savory sulfurous grounding that bridges coffee's roasted depth and cucumber's watery brightness into a coherent Middle Eastern-influenced preparation.",
     "Coffee Garlic Cucumber Tzatziki",
     ["Grate cucumber; squeeze dry and mix with yogurt, minced garlic, and cold brew coffee.", "Season with lemon juice, olive oil, and salt; the coffee adds unexpected roasted depth.", "Serve chilled with warm flatbread or as a sauce for grilled lamb and chicken."]),

    ("coffee","cucumber","lamb",
     "Coffee's pyrazines and furfural — roasted Maillard compounds — contrast with lamb's gamey 4-methyloctanoic acid through the bitter-fat modulation seen in coffee-rubbed lamb preparations, while cucumber's (E)-2-nonenal provides clean watery freshness that cuts through both coffee's bitterness and lamb's richness simultaneously.",
     "Espresso Rubbed Lamb with Cucumber Salad",
     ["Rub lamb with ground espresso, garlic, cumin, and olive oil; marinate 2 hours.", "Grill or roast to medium-rare; rest 8 minutes before slicing.", "Serve over a cucumber salad dressed with yogurt, mint, and lemon — the freshness contrasts the coffee crust beautifully."]),

    ("coffee","cucumber","lavender",
     "Coffee's pyrazines provide roasted bitterness while lavender's linalool adds floral warmth — a dark-floral contrast that Provence-inspired café culture has explored — while cucumber's (E)-2-nonenal provides the clean watery freshness that prevents the aromatic coffee-lavender combination from being too heavy. The trio creates a refined cold brew dessert.",
     "Lavender Cucumber Cold Brew",
     ["Make cold brew coffee; steep overnight in the refrigerator with dried lavender flowers.", "Strain; sweeten lightly and add fresh cucumber slices to cold brew for 30 minutes.", "Serve over ice with a lavender sprig and thin cucumber ribbons; the trio is unexpectedly refreshing."]),

    ("coffee","cucumber","lemon",
     "Coffee's furfural and pyrazines — roasted Maillard complexity — are brightened by lemon's citric acid and limonene through acid contrast that cuts bitterness, while cucumber's (E)-2-nonenal provides cool watery freshness that amplifies lemon's brightness and acts as a second palate-cleanser alongside lemon's acidity. The trio creates a refined summer cold brew preparation.",
     "Lemon Cucumber Cold Brew Coffee",
     ["Brew strong cold brew coffee overnight; strain clean and chill.", "Add fresh lemon juice, lemon zest, and thin cucumber slices; steep 20 minutes.", "Serve over ice in tall glasses with a lemon wheel and cucumber ribbon garnish."]),

    ("coffee","cucumber","mint",
     "Coffee's bitter pyrazines contrast with mint's menthol cooling — dark-cool opposition — while cucumber's (E)-2-nonenal amplifies mint's watery-fresh register through shared aqueous freshness. The combination creates a cold coffee drink where double-cooling from mint and cucumber balances coffee's warming bitterness in a refreshing summer beverage.",
     "Mint Cucumber Cold Brew Coffee",
     ["Brew strong cold brew; infuse with fresh mint and cucumber slices overnight in refrigerator.", "Strain; sweeten lightly with simple syrup and add a squeeze of lime.", "Serve over crushed ice with a fresh mint sprig and cucumber wheel garnish."]),

    ("coffee","cucumber","oyster",
     "Coffee's dimethyl sulfide from roasting and oyster's marine dimethyl sulfide share the same sulfurous compound through different production pathways, while cucumber's (E)-2-nonenal provides clean contrast that bridges the dark-roasted and marine registers. The trio creates an avant-garde oyster preparation where a coffee mignonette adds unexpected roasted depth.",
     "Espresso Cucumber Oyster Mignonette",
     ["Reduce brewed espresso with white wine vinegar until concentrated; add minced shallot and cracked pepper.", "Stir in very finely diced cucumber and allow to cool completely.", "Spoon sparingly over freshly shucked raw oysters on ice; the espresso adds startling depth."]),

    ("coffee","cucumber","parmesan",
     "Coffee's dimethyl sulfide connects to Parmesan's dimethyl sulfide — both producing the compound through separate processes — while cucumber's (E)-2-nonenal provides cool watery freshness that cuts through Parmesan's fat and coffee's bitter richness simultaneously. The trio creates a sophisticated savory coffee-cheese application.",
     "Espresso Parmesan Cucumber Crostini",
     ["Brush crostini with a very thin espresso wash; top with shaved Parmesan and cucumber ribbons.", "Drizzle with good olive oil and a grinding of cracked pepper.", "Serve immediately; the coffee adds a roasted note that amplifies Parmesan's umami register."]),

    ("coffee","cucumber","rose",
     "Coffee's pyrazines provide roasted depth while rose's 2-phenylethanol and geraniol add floral warmth — a dark-floral contrast that Middle Eastern café culture has embraced — while cucumber's (E)-2-nonenal provides the cool watery freshness that prevents the intense coffee-rose combination from being too perfumed. The trio creates a refined Turkish coffee-inspired drink.",
     "Rose Cucumber Cold Brew Coffee",
     ["Brew strong cold brew overnight; infuse with dried rose petals in the refrigerator.", "Strain; add cucumber slices and steep 20 more minutes for fresh contrast.", "Serve over ice with rose water, a rose petal garnish, and thin cucumber ribbons."]),

    ("coffee","cucumber","salmon",
     "Coffee's dimethyl sulfide connects to salmon's marine dimethyl sulfide through shared sulfurous chemistry, while cucumber's (E)-2-nonenal provides clean watery freshness that bridges coffee's bitter roasted register and salmon's fatty marine aromatics. Coffee-rubbed salmon with cucumber is a bold preparation that works through sulfurous compound alignment.",
     "Espresso Rubbed Salmon with Cucumber",
     ["Rub salmon fillets with finely ground espresso, brown sugar, and salt; rest 20 minutes.", "Sear skin-side down in a very hot pan until crusted; finish in a 400°F oven 8 minutes.", "Serve over thinly sliced cucumber dressed with rice vinegar and sesame oil."]),

    ("coffee","cucumber","strawberry",
     "Coffee's furfural and pyrazines — Maillard-roasted compounds — share a chemical cousin with strawberry's furaneol (sweet-caramel compound), creating a distant aromatic link while cucumber's (E)-2-nonenal provides cool freshness that bridges the bitter-roasted and sweet-fruit registers. The trio creates a sophisticated summer dessert with unexpected espresso depth.",
     "Strawberry Espresso Cucumber Granita",
     ["Blend fresh strawberries with cold brew coffee and cucumber juice; strain until smooth.", "Sweeten to taste; pour into a shallow pan and freeze, scraping every 30 minutes.", "Serve the granita in chilled glasses with fresh strawberry and a thin cucumber ribbon."]),

    ("coffee","cucumber","tomato",
     "Coffee and tomato share pyrazines and phenylacetaldehyde — Maillard-roasted and rosy-fermented compounds that roasted coffee and roasted tomato both develop — while cucumber's (E)-2-nonenal provides clean watery freshness that bridges the roasted-savory tomato-coffee combination. The trio creates a sophisticated bloody mary or gazpacho with coffee depth.",
     "Espresso Cucumber Tomato Gazpacho",
     ["Blend ripe tomatoes with cucumber, a shot of cold brew, garlic, and olive oil until smooth.", "Strain; season with sherry vinegar, salt, and a drizzle of good olive oil.", "Serve very cold with cucumber ribbons and a drizzle of espresso oil on top."]),

    ("coffee","cucumber","truffle",
     "Coffee and truffle share dimethyl sulfide — the sulfurous compound spanning roasted coffee and earthy fungal fermentation — while cucumber's (E)-2-nonenal provides the clean contrast that prevents the dense dark-roasted-earthy coffee-truffle combination from being overwhelming. The trio creates an elegant luxury preparation where cool freshness lifts heavy aromatics.",
     "Truffle Espresso Cucumber Appetizer",
     ["Slice cucumber thick; top each round with a thin layer of truffle cream cheese.", "Drizzle a tiny amount of cold brew espresso over each and season with fleur de sel.", "Shave fresh truffle over each piece; serve immediately chilled."]),

    ("coffee","cucumber","vanilla",
     "Coffee and vanilla share furfural and vanillin — caramel and lactonic compounds spanning roasted coffee and cured vanilla bean — while cucumber's (E)-2-nonenal provides cool watery freshness that cuts through the sweet-rich coffee-vanilla combination and lifts it into a more refreshing register. The trio creates a refined iced coffee dessert.",
     "Vanilla Cucumber Cold Brew Affogato",
     ["Make a cucumber-vanilla granita: blend cucumber with vanilla syrup; freeze and scrape to granita texture.", "Place a scoop of vanilla ice cream in a cold glass.", "Pour a shot of cold brew espresso over; top with cucumber-vanilla granita immediately."]),

    ("coffee","garlic","lamb",
     "Coffee's pyrazines and furfural — Maillard-roasted compounds — bridge to lamb's dimethyl sulfide through coffee's own roasting sulfurous chemistry, while garlic's allicin adds sharp pungency that converts to sweet-savory roasted garlic notes with heat. The trio is the flavor logic of coffee-rubbed lamb with garlic, creating a bold Mediterranean-North African rub.",
     "Espresso Garlic Rubbed Leg of Lamb",
     ["Make a rub: finely ground espresso, roasted garlic paste, olive oil, cumin, and sumac.", "Coat a leg of lamb generously; marinate overnight in the refrigerator.", "Roast at 325°F for 3 hours until deeply crusted and tender; rest 15 minutes before carving."]),

    ("coffee","garlic","lavender",
     "Coffee's roasted pyrazines and lavender's linalool create a bold dark-floral contrast — the Provençal café register where bitter and floral coexist — while garlic's dimethyl sulfide provides savory sulfurous grounding that anchors both extremes into a coherent savory preparation. The trio drives Provençal coffee-herb preparations for braised meats.",
     "Lavender Espresso Garlic Lamb Rub",
     ["Blend roasted garlic paste with finely ground espresso, dried lavender, olive oil, and herbs.", "Coat lamb or pork and marinate 4 hours at room temperature.", "Roast or grill; the lavender and espresso create a complex floral-bitter crust."]),
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
print(f"Batch 035 done: inserted {len(TRIPLETS)} triplets.")
