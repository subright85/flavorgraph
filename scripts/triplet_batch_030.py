#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("chocolate","coffee","cucumber",
     "Chocolate and coffee share pyrazines and furfural — the roasted-bitter and caramel aromatic compounds that make them the most famous bitter-roasted pair in the culinary world — while cucumber's (E)-2-nonenal provides clean watery freshness that contrasts the dark roasted register and provides a cool palate-cleansing quality between bites. The trio appears in avant-garde bistro desserts.",
     "Dark Chocolate Coffee Cucumber Granita",
     ["Make a coffee granita: brew strong espresso, sweeten lightly, freeze, and scrape every 30 minutes.", "Meanwhile make a dark chocolate mousse and a cucumber water by blending and straining cucumber.", "Serve coffee granita over chocolate mousse in a chilled glass; drizzle cucumber water and add mint."]),

    ("chocolate","coffee","garlic",
     "Chocolate and coffee share pyrazines and furfural — roasted bitter compounds from Maillard-driven fermentation — while garlic's dimethyl sulfide and methyl allyl disulfide add sulfurous depth that connects to coffee's minor sulfurous roasting products and chocolate's phenylacetaldehyde. The unusual trio appears in Mexican mole negro where chocolate, coffee, and garlic coexist.",
     "Dark Chocolate Coffee Mole with Garlic",
     ["Toast dried chilies, then blend with garlic, roasted tomato, chocolate, and brewed espresso.", "Cook the mole down with chicken or turkey stock until thick and fragrant; adjust seasoning.", "Serve over turkey or chicken with sesame seeds and warm tortillas."]),

    ("chocolate","coffee","lamb",
     "Chocolate and coffee share pyrazines — roasted bitter compounds from Maillard fermentation — while lamb's dimethyl sulfide creates a sulfurous bridge to coffee's sulfurous roasting byproducts, and chocolate's bitterness contrasts lamb's gamey 4-methyloctanoic acid through the same sweet-bitter-fat interaction as in Mexican mole. The trio drives lamb tagine with bitter chocolate.",
     "Espresso Dark Chocolate Braised Lamb",
     ["Brown lamb shoulder; add garlic, onion, brewed espresso, a square of dark chocolate, and spices.", "Braise at 325°F for 2.5 hours until falling-apart tender; the coffee and chocolate deepen the jus.", "Shred the meat; serve over polenta or couscous with a garnish of fresh herbs."]),

    ("chocolate","coffee","lavender",
     "Chocolate and coffee share pyrazines and furfural — roasted bitter and caramel compounds — while lavender's linalool and linalyl acetate provide a floral counterpoint that softens the double-roasted bitterness through floral aromatic displacement. The trio appears in Provence-influenced truffles and sophisticated mocha preparations where floral lightens the dark register.",
     "Lavender Espresso Dark Chocolate Truffles",
     ["Melt dark chocolate; whisk in hot lavender-infused cream and a shot of espresso until smooth.", "Cool until firm enough to roll; shape into balls with cool hands.", "Roll in cocoa powder mixed with a pinch of dried lavender; store refrigerated and serve at room temperature."]),

    ("chocolate","coffee","lemon",
     "Chocolate and coffee share pyrazines and furfural — the roasted-bitter compound core — while lemon's citric acid and limonene provide the sharp contrast that cuts through double bitterness and adds a brightness that chocolate and coffee both lack. Acidity is the universal brightness agent for bitter compounds, making lemon the perfect aromatic opposite to the bitter-roasted pair.",
     "Dark Chocolate Espresso Lemon Tart",
     ["Make a dark chocolate-espresso ganache: melt chocolate with hot espresso, butter, and lemon zest.", "Pour into a blind-baked tart shell and refrigerate until set and glossy.", "Serve with a lemon curd drizzle, candied lemon peel, and a dusting of cocoa powder."]),

    ("chocolate","coffee","mint",
     "Chocolate and mint is one of the most famous pairings in confectionery — menthol's cooling amplifies chocolate's perceived bitterness intensity through olfactory contrast — while coffee's pyrazines and furfural add roasted depth that gives the chocolate-mint combination more complexity than either achieves alone. The trio is mocha mint in its most complete aromatic form.",
     "Mint Mocha Ice Cream Sandwich",
     ["Make dark chocolate cookies with espresso powder; let cool completely.", "Churn a mint ice cream with a chocolate swirl; sandwich between the coffee-chocolate cookies.", "Freeze firm; serve straight from the freezer with a dusting of cocoa powder and mint garnish."]),

    ("chocolate","coffee","oyster",
     "Chocolate, coffee, and oyster all share dimethyl sulfide — the sulfurous compound produced by dark chocolate fermentation, coffee roasting, and marine bivalves respectively — creating an unusual three-way marine-roasted-earthy sulfurous alignment that appears in avant-garde tasting menus pairing raw oyster with chocolate-coffee mignonette. The combination is extreme but chemically coherent.",
     "Coffee Chocolate Oyster Mignonette",
     ["Brew very strong espresso; dissolve a small amount of dark chocolate into the hot espresso.", "Add sherry vinegar, finely minced shallot, and cracked white pepper; cool completely.", "Spoon a tiny amount over freshly shucked raw oysters; the bitter-sweet-marine trio is startling."]),

    ("chocolate","coffee","parmesan",
     "Chocolate and coffee share pyrazines — Maillard-roasted compounds — while Parmesan and coffee share dimethyl sulfide, and Parmesan's free glutamates interact with chocolate's theobromine bitterness in the same umami-bitter amplification seen in mole. The trio appears in bold savory chocolate preparations where aged dairy rounds bitter roasted notes.",
     "Espresso Dark Chocolate Parmesan Risotto",
     ["Cook arborio risotto with dark stock; off heat stir in a small amount of melted dark chocolate.", "Add cold butter, finely grated Parmesan, and a splash of brewed espresso; beat until glossy.", "Plate; finish with more Parmesan shavings, cracked pepper, and a drizzle of dark chocolate."]),

    ("chocolate","coffee","rose",
     "Chocolate, coffee, and rose all share phenylacetaldehyde — the rosy-fermented compound that cacao fermentation, coffee fermentation, and rose petals produce through separate but parallel biochemical pathways. This three-way shared compound makes the trio one of the most aromatic and aligned pairings in confectionery, driving rosewater mocha and Turkish coffee chocolate.",
     "Rose Mocha Bonbons",
     ["Melt dark chocolate; whisk in hot espresso and rose-infused cream into a smooth ganache.", "Add a splash of rose water; pour into molds and allow to set completely.", "Unmold; dust with cocoa powder and crushed dried rose petals; serve at room temperature."]),

    ("chocolate","coffee","salmon",
     "Chocolate, coffee, and salmon share dimethyl sulfide — the sulfurous compound spanning cacao fermentation, coffee roasting, and marine fish — while chocolate and coffee's shared pyrazines and furfural provide the roasted bitterness that in small amounts acts as an umami amplifier for salmon's fatty richness. The combination appears in bold glazed salmon preparations.",
     "Coffee Dark Chocolate Glazed Salmon",
     ["Make a coffee-chocolate glaze: brewed espresso, dark cocoa, soy sauce, honey, and olive oil.", "Brush salmon fillets; roast at 425°F for 10 minutes, glazing halfway through.", "Serve over black rice; the coffee-chocolate bitterness amplifies salmon's umami register."]),

    ("chocolate","coffee","strawberry",
     "Chocolate and strawberry share furaneol — the sweet-caramel compound in both dark chocolate and ripe strawberry — while coffee and chocolate share pyrazines and furfural, creating a triangle where caramel-sweet, roasted-bitter, and fruit-fresh play against each other in succession. The combination drives chocolate-covered strawberry with espresso ganache.",
     "Espresso Chocolate Covered Strawberries",
     ["Melt dark chocolate with a shot of espresso and a pinch of salt into a smooth dipping ganache.", "Dip ripe whole strawberries and place on parchment to set at room temperature.", "Drizzle with white chocolate and dust with cocoa-espresso powder before fully set."]),

    ("chocolate","coffee","tomato",
     "Chocolate, coffee, and tomato share pyrazines, acetic acid, and phenylacetaldehyde — a roasted-fermented-tart compound cluster that spans three very different foods through parallel Maillard and fermentation chemistry. This triple compound overlap is the flavor science basis of Mexican mole negro where tomato, chocolate, and coffee coexist at depth.",
     "Dark Chocolate Coffee Tomato Mole",
     ["Toast dried mulato and ancho chilies; blend with roasted tomato, garlic, and spices.", "Add dark chocolate and strong brewed coffee; simmer until thick and deeply flavored.", "Adjust salt; serve over roasted chicken or duck with sesame and warm corn tortillas."]),

    ("chocolate","coffee","truffle",
     "Chocolate, coffee, and truffle all share dimethyl sulfide and pyrazines — roasted sulfurous and Maillard compounds spanning cacao fermentation, coffee roasting, and earthy fungal fermentation. This three-way compound alignment creates the most complete dark-roasted-earthy aromatic stack possible, appearing in luxurious truffle-chocolate preparations with espresso.",
     "Truffle Espresso Dark Chocolate Bark",
     ["Melt high-quality dark chocolate; add a shot of espresso and a drizzle of truffle oil; stir well.", "Pour onto a parchment-lined tray; immediately sprinkle with fleur de sel and shaved truffle.", "Let set at room temperature until firm; break into irregular shards and serve with coffee."]),

    ("chocolate","coffee","vanilla",
     "Chocolate, coffee, and vanilla share vanillin and furfural — the lactonic-sweet and caramel compounds spanning cured vanilla bean, dark chocolate fermentation, and coffee roasting. This triple shared-compound alignment is the flavor chemistry basis of mocha, tiramisu, and every classic coffee-vanilla-chocolate dessert combination in European confectionery.",
     "Classic Tiramisu",
     ["Soak ladyfingers in strong espresso mixed with a splash of dark rum or coffee liqueur.", "Layer with mascarpone cream beaten with egg yolks, sugar, and vanilla bean seeds.", "Dust heavily with good-quality cocoa powder; refrigerate overnight before serving."]),

    ("chocolate","cucumber","garlic",
     "Chocolate and cucumber share no direct compound but operate through contrast — chocolate's phenylacetaldehyde fermented-rosy depth against cucumber's (E)-2-nonenal clean freshness — while garlic's dimethyl sulfide provides a savory sulfurous bridge that grounds both extremes into a coherent savory register. The trio appears in bold mole-style preparations with fresh garnish.",
     "Dark Chocolate Mole with Cucumber Garlic Salsa",
     ["Make a simple dark chocolate mole with toasted chilies, garlic, and spices; cook 20 minutes.", "Make a cucumber-garlic salsa: diced cucumber, raw garlic, lime juice, and flaky salt.", "Serve the mole over pork or chicken topped with a generous spoonful of cucumber-garlic salsa."]),

    ("chocolate","cucumber","lamb",
     "Chocolate and lamb share dimethyl sulfide — the sulfurous compound spanning cacao fermentation and animal-fat metabolism — while cucumber's (E)-2-nonenal provides clean watery freshness that cuts through both chocolate's bitterness and lamb's gamey 4-methyloctanoic acid through olfactory cooling. The trio creates an unusual but refreshing lamb preparation.",
     "Dark Chocolate Braised Lamb with Cucumber Raita",
     ["Braise lamb with dark chocolate, spices, and stock until meltingly tender; reduce the sauce.", "Make cucumber raita: grated cucumber, yogurt, mint, and cumin mixed until smooth.", "Serve the chocolate-braised lamb over rice topped with a generous spoonful of cucumber raita."]),

    ("chocolate","cucumber","lavender",
     "Chocolate's phenylacetaldehyde rosy depth and lavender's linalool floral warmth share an aromatic register — both landing in the floral-fermented zone — while cucumber's (E)-2-nonenal provides clean contrast that prevents the floral-bitter combination from becoming heavy. The trio creates a refined summer dessert where cool freshness balances dark aromatic complexity.",
     "Dark Chocolate Lavender Cucumber Cake",
     ["Make a dark chocolate-lavender cake layer; cool completely.", "Whip cream with dried lavender and a tiny amount of cucumber water for subtle freshness.", "Frost the cake with lavender cream; decorate with thinly sliced cucumber and chocolate shavings."]),

    ("chocolate","cucumber","lemon",
     "Chocolate's bitterness and lemon's citric acid both activate similar bitter-tart receptor pathways — they operate in tandem rather than canceling — while cucumber's (E)-2-nonenal provides the neutral fresh contrast that balances both sharp extremes through olfactory cooling. The trio appears in sophisticated dark chocolate and citrus desserts with fresh herbal elements.",
     "Dark Chocolate Lemon Cucumber Tart",
     ["Make a dark chocolate ganache tart; refrigerate until set and glossy.", "Whip cream with lemon zest and a splash of cucumber juice for a subtle fresh flavor.", "Serve the chocolate tart with lemon-cucumber cream, thin cucumber ribbons, and lemon zest."]),

    ("chocolate","cucumber","mint",
     "Chocolate and mint is one of the most celebrated pairings — menthol's cooling amplifies chocolate's perceived intensity through thermal contrast — while cucumber's (E)-2-nonenal reinforces mint's cool-watery freshness through a second compound, creating a double-cool register that balances dark chocolate's bitterness more effectively than mint alone.",
     "Dark Chocolate Mint Cucumber Granita",
     ["Blend fresh cucumber with mint and simple syrup; strain into a clean granita mixture.", "Freeze, scraping every 30 minutes until granita texture; keep in the freezer.", "Serve the cucumber-mint granita beside a portion of rich dark chocolate mousse."]),

    ("chocolate","cucumber","oyster",
     "Chocolate and oyster share dimethyl sulfide — the sulfurous compound spanning cacao fermentation and marine bivalve metabolism — while cucumber's (E)-2-nonenal provides the clean watery freshness that cuts through the unusual chocolate-marine richness and acts as the neutral bridge between two intense flavors. The trio is a daring raw bar concept.",
     "Dark Chocolate Cucumber Oyster Mignonette",
     ["Dissolve a tiny amount of dark chocolate into warm sherry vinegar; add minced shallot and pepper.", "Stir in very finely diced cucumber and a pinch of flaky salt; allow to cool completely.", "Spoon sparingly over freshly shucked raw oysters; the chocolate-cucumber contrast is startling."]),
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
print(f"Batch 030 done: inserted {len(TRIPLETS)} triplets.")
