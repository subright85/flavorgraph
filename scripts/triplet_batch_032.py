#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("chocolate","lamb","lemon",
     "Chocolate and lamb share dimethyl sulfide — the sulfurous compound spanning cacao fermentation and animal-fat chemistry — while lemon's citric acid modulates both chocolate's bitterness and lamb's gamey 4-methyloctanoic acid through pH-driven aromatic shift. Lemon's dual function as bitterness-reducer and gamey-fat cutter makes it the ideal bridge in this bold trio.",
     "Lemon Dark Chocolate Braised Lamb",
     ["Brown lamb shanks; add preserved lemon, a square of dark chocolate, red wine, and herbs.", "Braise at 325°F for 3 hours until meltingly tender; reduce the sauce until glossy.", "Serve with the reduced chocolate-lemon jus, gremolata of lemon zest, and fresh parsley."]),

    ("chocolate","lamb","mint",
     "Chocolate and mint is a celebrated confectionery pairing — menthol's cooling amplifies chocolate's bitterness through thermal contrast — while mint's menthol simultaneously suppresses lamb's gamey 4-methyloctanoic acid through olfactory masking, giving a double suppression. The trio creates a refined Moroccan-inflected lamb preparation with chocolate depth.",
     "Dark Chocolate Mint Braised Lamb",
     ["Brown lamb with garlic and onion; add dark chocolate, ras el hanout, and a large bunch of fresh mint.", "Braise at 300°F for 2.5 hours; remove mint stems and reduce sauce until glossy.", "Serve over bulgur with fresh mint leaves and a chocolate-mint drizzle."]),

    ("chocolate","lamb","oyster",
     "Chocolate, lamb, and oyster share dimethyl sulfide — the sulfurous compound spanning cacao fermentation, animal-fat metabolism, and marine bivalve chemistry — creating a three-way sulfurous alignment that bridges vastly different food categories. The combination appears in Cantonese-influenced braised lamb with oyster sauce deepened by dark chocolate.",
     "Oyster Sauce Dark Chocolate Braised Lamb",
     ["Brown lamb shoulder; add oyster sauce, a square of dark chocolate, soy, and stock.", "Braise at 325°F for 2.5 hours until tender; the chocolate deepens the oyster sauce's umami.", "Serve over steamed rice with blanched greens and a drizzle of the reduced chocolate-oyster jus."]),

    ("chocolate","lamb","parmesan",
     "Chocolate, lamb, and Parmesan share phenylacetaldehyde and dimethyl sulfide — fermented-rosy and sulfurous compounds spanning cacao, animal fat, and aged dairy — creating a three-way compound alignment that appears in sophisticated Italian braised lamb preparations where Parmesan adds dairy umami and chocolate deepens the long-cooked sauce.",
     "Dark Chocolate Parmesan Braised Lamb Ragù",
     ["Brown ground lamb; add garlic, crushed tomatoes, a square of dark chocolate, and red wine.", "Simmer 1 hour until thick and rich; off heat stir in grated Parmesan to bind the sauce.", "Toss with pappardelle; finish with more Parmesan and a grating of dark chocolate."]),

    ("chocolate","lamb","rose",
     "Chocolate and rose share phenylacetaldehyde — the rosy-fermented compound that cacao fermentation and rose petals both produce — while rose's 2-phenylethanol and geraniol independently soften lamb's gamey 4-methyloctanoic acid through floral aromatic displacement. The combination creates a Persian-influenced chocolate-lamb preparation of unusual refinement.",
     "Rose Dark Chocolate Persian Lamb",
     ["Brown lamb with onion; add rose water, dark chocolate, saffron, and dried rose petals.", "Braise at 300°F for 2 hours; the rose and chocolate create a complex sweet-floral-bitter sauce.", "Serve over saffron rice with fresh rose petals and toasted pistachios."]),

    ("chocolate","lamb","salmon",
     "Chocolate, lamb, and salmon share dimethyl sulfide — the sulfurous compound spanning cacao fermentation, animal-fat chemistry, and marine fish metabolism — creating a three-way alignment that is unusual but chemically precise. In small amounts chocolate bridges two proteins that share this compound family, creating a surf-and-turf preparation with Peruvian mole overtones.",
     "Dark Chocolate Mole Surf and Turf",
     ["Make a thin dark chocolate mole with chili, spices, and lamb stock.", "Sear lamb loin and salmon fillet separately to proper doneness.", "Plate side by side; spoon the chocolate mole over both and garnish with sesame and cilantro."]),

    ("chocolate","lamb","strawberry",
     "Chocolate and strawberry share furaneol — the sweet-caramel compound in both dark chocolate and ripe strawberry — while chocolate's bitterness contrasts lamb's gamey 4-methyloctanoic acid through the bitter-fat suppression mechanism seen in mole negro. Strawberry's furaneol reinforces chocolate's sweetness and adds fruit brightness that rounds the bold trio.",
     "Strawberry Dark Chocolate Lamb Salad",
     ["Grill lamb loin to medium-rare; rest and slice thin.", "Make a chocolate-strawberry dressing: dark chocolate, strawberry vinegar, and olive oil whisked smooth.", "Arrange lamb over arugula with sliced strawberries; drizzle with the chocolate-strawberry dressing."]),

    ("chocolate","lamb","tomato",
     "Chocolate, lamb, and tomato share phenylacetaldehyde and dimethyl sulfide — rosy-fermented and sulfurous compounds — creating the exact compound alignment of Mexican mole negro with lamb, where tomato provides the savory acid backbone and chocolate deepens the long-braise sauce. The trio is the flavor logic of the most complex lamb braise possible.",
     "Dark Chocolate Tomato Braised Lamb",
     ["Brown lamb pieces; add crushed tomatoes, dark chocolate, dried chilies, and garlic.", "Braise at 325°F for 2.5 hours until tender; reduce sauce to a glossy intensity.", "Serve over polenta or rice; finish with fresh tomato, herbs, and a grating of chocolate."]),

    ("chocolate","lamb","truffle",
     "Chocolate, lamb, and truffle all share dimethyl sulfide — the sulfurous compound spanning cacao fermentation, animal-fat metabolism, and earthy fungal fermentation. This three-way alignment creates the deepest possible dark, earthy, animal aromatic stack, appearing in ultra-luxury tasting menus where truffle, chocolate, and lamb jus combine into a single complex sauce.",
     "Truffle Dark Chocolate Rack of Lamb",
     ["Roast a rack of lamb with truffle salt and herbs to medium-rare; rest before carving.", "Make a jus: deglaze pan with red wine, add dark chocolate and truffle butter; reduce until glossy.", "Plate the chops over a potato purée; spoon the truffle-chocolate jus and shave fresh truffle over."]),

    ("chocolate","lamb","vanilla",
     "Chocolate and vanilla share vanillin and furfural — lactonic-sweet and caramel compounds — while vanilla's vanillin sweetness contrasts lamb's gamey 4-methyloctanoic acid through the same sweet-fat modulation as caramel with lamb. Chocolate's bitterness bridges vanilla's sweetness and lamb's gameyness through the bitter-gamey suppression mechanism seen in mole.",
     "Vanilla Dark Chocolate Moroccan Lamb",
     ["Brown lamb with onion and sweet Moroccan spices; add a split vanilla bean, dark chocolate, and stock.", "Braise at 300°F for 2 hours; the vanilla and chocolate create a complex sweet-bitter sauce.", "Serve over couscous with dried fruit, toasted almonds, and fresh herb garnish."]),

    ("chocolate","lavender","lemon",
     "Chocolate's fermented-bitter complexity and lavender's linalool floral warmth create a dark-floral combination — the same principle as chocolate with floral tea — while lemon's citric acid and limonene provide the brightness that cuts through both chocolate's richness and lavender's heaviness, lifting the combination into a lighter, more vertical register. The trio drives refined Provençal chocolate desserts.",
     "Lavender Lemon Dark Chocolate Tart",
     ["Make a dark chocolate lavender ganache: melt chocolate with lavender-infused cream and lemon zest.", "Pour into a blind-baked tart shell and refrigerate until set and glossy.", "Serve with lemon curd, a sprig of fresh lavender, and candied lemon peel."]),

    ("chocolate","lavender","mint",
     "Chocolate and mint is a celebrated pairing — menthol cooling amplifying chocolate's bitterness through thermal contrast — while lavender's linalool reinforces mint's herbal-floral register and adds Provençal depth that prevents the combination from tasting like mint candy. The trio creates a sophisticated herb-floral chocolate confection.",
     "Lavender Mint Dark Chocolate Bark",
     ["Melt dark chocolate; spread thinly on parchment and immediately scatter dried lavender and fresh mint.", "Add fleur de sel; allow to set completely at room temperature.", "Break into irregular pieces; store at room temperature and serve within a few days."]),

    ("chocolate","lavender","oyster",
     "Chocolate and oyster share dimethyl sulfide — sulfurous compounds in both — while lavender's linalool provides a floral aromatic bridge that softens the unusual chocolate-marine combination through fragrant displacement. The trio creates an avant-garde oyster preparation where dark bitter and floral soft bracket the marine briny oyster.",
     "Lavender Dark Chocolate Oyster Mignonette",
     ["Dissolve a tiny amount of dark chocolate into warm sherry vinegar; add a pinch of dried lavender.", "Add finely minced shallot and cracked pepper; cool and allow lavender to steep 10 minutes.", "Strain and spoon very sparingly over freshly shucked raw oysters on ice."]),

    ("chocolate","lavender","parmesan",
     "Chocolate and Parmesan share phenylacetaldehyde — rosy-fermented compounds in both cacao and aged dairy — while lavender's linalool provides a Provençal floral bridge that lifts the fermented-funky chocolate-cheese combination into a more aromatic, elegant register. The trio creates a sophisticated savory chocolate cheese preparation.",
     "Lavender Dark Chocolate Parmesan Shortbread",
     ["Blend Parmesan, butter, flour, dried lavender, and a tablespoon of dark cocoa into a dough.", "Refrigerate 30 minutes; roll, cut into rounds, and bake at 350°F until just golden.", "Cool; serve with dark chocolate shavings and a drizzle of lavender honey."]),

    ("chocolate","lavender","rose",
     "Chocolate and rose share phenylacetaldehyde — the rosy-fermented compound in cacao and rose petals — while lavender and rose share linalool and 2-phenylethanol, creating a chain where chocolate's fermented depth connects to rose's floral register through lavender as the aromatic bridge. The trio creates the most refined floral chocolate confection possible.",
     "Rose Lavender Dark Chocolate Truffles",
     ["Melt dark chocolate; whisk in hot cream infused with dried lavender and rose water.", "Cool until firm enough to roll; shape into balls with cool hands.", "Roll half in cocoa powder and half in dried rose petal powder mixed with powdered sugar."]),

    ("chocolate","lavender","salmon",
     "Chocolate and salmon share dimethyl sulfide — sulfurous compounds in both — while lavender's linalool and linalyl acetate provide floral-herbal softening that suppresses salmon's trimethylamine and bridges chocolate's bitter-dark register to salmon's delicate fatty aromatics. The trio appears in avant-garde salmon preparations with mole influences.",
     "Lavender Dark Chocolate Mole Salmon",
     ["Make a thin chocolate-lavender mole: dark chocolate, dried chilies, lavender, and fish stock.", "Brush the mole over salmon fillets and bake at 400°F for 12 minutes.", "Serve over jasmine rice with fresh lavender flowers and a squeeze of lemon."]),

    ("chocolate","lavender","strawberry",
     "Chocolate and strawberry share furaneol — sweet-caramel compound in both — while lavender and strawberry share linalool, creating a dual compound connection where chocolate deepens strawberry's sweet register and lavender elevates its floral dimension simultaneously. The trio creates a summer chocolate-floral dessert of unusual aromatic completeness.",
     "Lavender Strawberry Dark Chocolate Tart",
     ["Make a dark chocolate ganache with lavender-infused cream; pour into a baked tart shell.", "Arrange halved fresh strawberries over the set ganache in a concentric pattern.", "Glaze with a lavender-strawberry jelly and decorate with dried lavender flowers."]),

    ("chocolate","lavender","tomato",
     "Chocolate and tomato share phenylacetaldehyde and pyrazines — rosy-fermented and Maillard-roasted compounds — while lavender's linalool provides a Provençal floral note that bridges the dark-roasted chocolate and Mediterranean tomato savory registers. The trio appears in sophisticated Provençal chocolate tomato sauce preparations.",
     "Lavender Dark Chocolate Tomato Sauce",
     ["Cook tomatoes with garlic until deeply reduced; add a small square of dark chocolate and dried lavender.", "Simmer 5 minutes until glossy; the chocolate and lavender create unusual depth.", "Serve over pasta or roasted meat; the lavender lifts and the chocolate deepens the tomato simultaneously."]),

    ("chocolate","lavender","truffle",
     "Chocolate and truffle share dimethyl sulfide and phenylacetaldehyde — sulfurous-rosy compounds spanning cacao and earthy fungal fermentation — while lavender's linalool and anisaldehyde bridge chocolate's bitter-earthy register to truffle's anise-adjacent character. The trio creates an opulent luxury confection where earthy and floral balance dark bitterness.",
     "Truffle Lavender Dark Chocolate Pralines",
     ["Melt dark chocolate with truffle oil; whisk in lavender-infused cream and a pinch of fleur de sel.", "Pour into praline molds and allow to set; unmold carefully.", "Dust with cocoa powder and dried lavender; serve as petit fours with espresso."]),

    ("chocolate","lavender","vanilla",
     "Chocolate and vanilla share vanillin and furfural — the lactonic-sweet compounds spanning cured vanilla and cacao fermentation — while lavender and vanilla share linalool, creating a dual compound connection where vanilla's sweetness bridges chocolate's bitterness and lavender's floral warmth elevates the combination into a Provençal confectionery register.",
     "Lavender Vanilla Dark Chocolate Pots de Crème",
     ["Heat cream with lavender and split vanilla bean; steep 20 minutes and strain onto dark chocolate.", "Whisk until glossy; add eggs and strain into ramekins; bake at 325°F in a water bath until set.", "Chill; serve with a sprig of lavender and a drizzle of lavender honey on top."]),
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
print(f"Batch 032 done: inserted {len(TRIPLETS)} triplets.")
