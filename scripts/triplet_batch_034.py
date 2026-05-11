#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("chocolate","oyster","strawberry",
     "Chocolate and oyster share dimethyl sulfide — the sulfurous compound spanning cacao and marine bivalves — while chocolate and strawberry share furaneol, creating a triangle where sweet-caramel and marine-brine bracket the dark bitter register. Strawberry's furaneol sweetness provides the contrast that makes the chocolate-oyster combination accessible in an adventurous dessert-raw bar crossover.",
     "Strawberry Dark Chocolate Oyster Shooter",
     ["Blend muddled strawberry with a tiny amount of dissolved dark chocolate and sherry vinegar.", "Strain; add minced shallot and cracked pepper; cool completely.", "Spoon over freshly shucked raw oysters on ice; the strawberry-chocolate creates an unusual sweet-brine balance."]),

    ("chocolate","oyster","tomato",
     "Chocolate and tomato share phenylacetaldehyde and pyrazines — rosy-fermented and Maillard-roasted compounds — while chocolate and oyster share dimethyl sulfide, creating a chain where tomato's savory acidity bridges the chocolate's bitterness to oyster's marine umami. The trio is the flavor logic of dark Bloody Mary preparations with chocolate depth.",
     "Dark Chocolate Tomato Oyster Stew",
     ["Sauté garlic and shallots; add crushed tomatoes and a small square of dark chocolate; simmer 15 minutes.", "Add shucked oysters with their liquor; poach 2 minutes until just cooked.", "Season with sherry, salt, and fresh herbs; serve with crusty bread to soak the complex broth."]),

    ("chocolate","oyster","truffle",
     "Chocolate, oyster, and truffle all share dimethyl sulfide — the sulfurous compound spanning cacao fermentation, marine bivalve metabolism, and earthy fungal chemistry — creating the deepest three-way sulfurous alignment possible. The trio also shares phenylacetaldehyde across chocolate and truffle, making this the most aromatically complex savory luxury combination.",
     "Truffle Dark Chocolate Oyster Tartare",
     ["Shuck and finely chop oysters; mix with a drizzle of truffle oil and dissolved dark chocolate.", "Season with fleur de sel and white pepper; mound carefully in oyster shells over crushed ice.", "Shave fresh truffle over generously; serve immediately with cold champagne."]),

    ("chocolate","oyster","vanilla",
     "Chocolate and vanilla share vanillin — the lactonic-sweet compound in both — while chocolate and oyster share dimethyl sulfide, creating a triangle where vanilla's sweet warmth brackets the marine-dark combination. Vanilla's sweetness applies the salted caramel principle directly to the chocolate-oyster combination, making the sulfurous link palatable.",
     "Vanilla Dark Chocolate Broiled Oysters",
     ["Make a vanilla-chocolate butter: dark chocolate, vanilla bean seeds, cold butter, and fleur de sel.", "Shuck oysters into half shells; top each with a sliver of vanilla-chocolate butter.", "Broil 3-4 minutes until butter is melted and oyster edges just curl; serve immediately."]),

    ("chocolate","parmesan","rose",
     "Chocolate, Parmesan, and rose all share phenylacetaldehyde — the rosy-fermented compound produced through cacao fermentation, aged dairy fermentation, and rose petal biosynthesis. This three-way shared compound creates an unusual but precise aromatic alignment where each ingredient's fermented-rosy character reinforces the others in a complex savory-floral-bitter combination.",
     "Rose Dark Chocolate Parmesan Shortbread",
     ["Blend Parmesan, cold butter, flour, rose water, and dark cocoa into a firm dough.", "Refrigerate 30 minutes; roll, cut, and bake at 350°F until just set and fragrant.", "Cool; top each with a crystallized rose petal and a shaving of dark chocolate."]),

    ("chocolate","parmesan","salmon",
     "Chocolate, Parmesan, and salmon all share dimethyl sulfide — the sulfurous compound spanning cacao, aged dairy, and marine fish — creating a three-way sulfurous alignment that is unusual but chemically precise. Chocolate's bitterness amplifies Parmesan's umami register while suppressing salmon's trimethylamine in a bold savory crust preparation.",
     "Dark Chocolate Parmesan Salmon Crust",
     ["Mix finely grated Parmesan with dark cocoa, breadcrumbs, herbs, and olive oil into a paste.", "Press firmly onto salmon fillets; bake at 400°F for 12 minutes until crust is deeply golden.", "Serve with lemon and an aged balsamic drizzle; the chocolate-Parmesan crust is surprisingly elegant."]),

    ("chocolate","parmesan","strawberry",
     "Chocolate, Parmesan, and strawberry all share furaneol — the sweet-caramel compound spanning Maillard cacao chemistry, aged dairy fermentation, and ripe fruit. This triple furaneol alignment creates an unusual but aromatic coherence, appearing in Italian-influenced dessert boards where aged cheese, chocolate, and fresh fruit share a single dominant flavor compound.",
     "Dark Chocolate Parmesan Strawberry Board",
     ["Melt dark chocolate and dip ripe strawberries; allow to set on parchment.", "Shave aged Parmesan Reggiano into large irregular curls.", "Arrange chocolate strawberries and Parmesan on a board with honeycomb and cracked pepper — the furaneol in all three creates surprising unity."]),

    ("chocolate","parmesan","tomato",
     "Chocolate and tomato share phenylacetaldehyde and pyrazines — rosy-fermented and Maillard compounds — while Parmesan and tomato share furaneol and acetic acid, creating a chain where Parmesan's umami anchors the tomato-chocolate combination into a savory-bitter depth that defines complex mole-style pasta sauces. The trio is sophisticated Italian-Mexican crossover.",
     "Dark Chocolate Parmesan Tomato Pasta",
     ["Cook tomato sauce with garlic until reduced; add a square of dark chocolate and stir until melted.", "Toss with al dente pasta and pasta water; finish with a generous grating of Parmesan off heat.", "Plate; grate more Parmesan and add a very fine dusting of dark cocoa powder to finish."]),

    ("chocolate","parmesan","truffle",
     "Chocolate and truffle share dimethyl sulfide and phenylacetaldehyde — sulfurous and rosy-fermented compounds — while Parmesan and truffle share the same compound pair, creating a double-overlap where all three ingredients connect through the identical compound family. The trio creates the most complete umami-dark-earthy aromatic stack possible from three ingredients.",
     "Truffle Dark Chocolate Parmesan Fondue",
     ["Melt aged Parmesan and Gruyère with white wine; stir in truffle butter and a square of dark chocolate.", "Keep warm; the chocolate rounds the cheese sharpness while truffle adds earthy depth.", "Serve with crusty bread, apple slices, and cured meats for dipping."]),

    ("chocolate","parmesan","vanilla",
     "Chocolate and vanilla share vanillin and furfural — lactonic-sweet and caramel compounds — while Parmesan and vanilla share vanillin and furaneol, creating a chain where vanilla's sweetness bridges chocolate's bitterness and Parmesan's fermented umami. The trio creates a sophisticated sweet-savory preparation where all three share at least one key aromatic compound.",
     "Vanilla Dark Chocolate Parmesan Pots de Crème",
     ["Infuse cream with split vanilla bean; add dark chocolate and melt; whisk with eggs and a pinch of salt.", "Stir in finely grated Parmesan; pour into ramekins and bake at 325°F in a water bath.", "Chill; serve with a shaving of Parmesan and a drizzle of dark chocolate."]),

    ("chocolate","rose","salmon",
     "Chocolate and salmon share dimethyl sulfide — the sulfurous compound in both — while chocolate and rose share phenylacetaldehyde, creating a chain where rose's 2-phenylethanol and geraniol suppress salmon's trimethylamine through floral displacement and chocolate's bitterness amplifies the marine-earthy register. The trio creates a Persian-influenced salmon preparation.",
     "Rose Dark Chocolate Glazed Salmon",
     ["Make a rose-chocolate glaze: dark chocolate, rose water, mirin, and soy sauce reduced together.", "Brush salmon fillets; bake at 425°F for 10 minutes, glazing halfway through.", "Garnish with dried rose petals and serve over saffron rice with a lemon wedge."]),

    ("chocolate","rose","strawberry",
     "Chocolate and strawberry share furaneol — sweet-caramel in both — while chocolate and rose share phenylacetaldehyde, and rose and strawberry share 2-phenylethanol and linalool, creating a three-way chain of compound connections. Every ingredient connects to at least two others through shared aromatic compounds, making this one of the most cohesive chocolate-fruit-floral trios.",
     "Rose Strawberry Dark Chocolate Pavlova",
     ["Fold rose water into meringue; bake at 250°F for 90 minutes until crisp outside, soft inside.", "Macerate sliced strawberries with rose water and a drizzle of melted dark chocolate.", "Top meringue with rose-dark chocolate cream; pile strawberries over and scatter rose petals."]),

    ("chocolate","rose","tomato",
     "Chocolate, rose, and tomato all share phenylacetaldehyde — the rosy-fermented compound produced through cacao fermentation, rose petal biosynthesis, and roasted tomato chemistry — creating an unusual three-way shared compound that makes this trio more coherent than it appears. The combination works in sophisticated rose-infused tomato chocolate sauce.",
     "Rose Dark Chocolate Tomato Sauce",
     ["Cook tomatoes until deeply reduced; add a square of dark chocolate and a splash of rose water.", "Simmer 5 minutes; the rose softens the tomato's acidity while chocolate deepens the sauce.", "Serve over pasta or use as a braising liquid for lamb — unexpected but chemically precise."]),

    ("chocolate","rose","truffle",
     "Chocolate, rose, and truffle all share phenylacetaldehyde — the rosy-fermented compound spanning cacao, rose petals, and earthy truffle fermentation — while chocolate and truffle additionally share dimethyl sulfide, creating a double compound overlap. The trio achieves a perfumed earthy-dark luxury that is rare in confectionery.",
     "Rose Truffle Dark Chocolate Pralines",
     ["Melt dark chocolate; whisk in truffle-infused cream and a splash of rose water.", "Cool until firm; shape into balls and coat in tempered dark chocolate.", "Dust with cocoa mixed with dried rose petal powder; serve as petit fours."]),

    ("chocolate","rose","vanilla",
     "Chocolate and vanilla share vanillin — lactonic-sweet compounds in both — while rose and vanilla share 2-phenylethanol and linalool, and chocolate and rose share phenylacetaldehyde, creating a chain of compound connections through all three ingredients. The trio creates a complete sweet-floral-bitter aromatic arc that is the foundation of high-end rose chocolates.",
     "Rose Vanilla Dark Chocolate Truffles",
     ["Melt dark chocolate; whisk in vanilla-infused cream and rose water into a smooth ganache.", "Cool until firm enough to roll; shape into balls and chill briefly.", "Roll in cocoa powder mixed with dried rose petal dust; serve at room temperature."]),

    ("chocolate","salmon","strawberry",
     "Chocolate and salmon share dimethyl sulfide — sulfurous compounds in cacao and marine fish — while chocolate and strawberry share furaneol, creating a triangle where sweet-caramel and sulfurous-marine bracket the dark bitter register. Strawberry's sweetness provides the same trimethylamine-suppressing function as any sweet compound, doubly supported by chocolate.",
     "Strawberry Chocolate Glazed Salmon",
     ["Blend fresh strawberry with dark chocolate, rice vinegar, and soy sauce into a smooth glaze.", "Brush salmon fillets; bake at 425°F for 10 minutes, glazing halfway through.", "Serve over arugula with sliced fresh strawberry and a dark chocolate drizzle."]),

    ("chocolate","salmon","tomato",
     "Chocolate and salmon share dimethyl sulfide — the sulfurous compound in cacao and marine fish — while chocolate and tomato share phenylacetaldehyde and pyrazines, creating a chain where tomato's savory acidity bridges chocolate's bitterness to salmon's fatty richness. The trio is the flavor logic of a bold Peruvian-influenced mole applied to seafood.",
     "Dark Chocolate Tomato Braised Salmon",
     ["Simmer crushed tomatoes with garlic, dark chocolate, and dried chili until thick and glossy.", "Nestle salmon fillets into the sauce; cover and cook gently 8 minutes until just opaque.", "Serve over rice with fresh cilantro and a final grating of dark chocolate."]),

    ("chocolate","salmon","truffle",
     "Chocolate, salmon, and truffle all share dimethyl sulfide — the sulfurous compound spanning cacao fermentation, fatty fish metabolism, and earthy fungal fermentation — creating one of the most unexpected three-way sulfurous alignments in food. The trio creates an intensely savory luxury preparation where all three ingredients amplify each other's dark, earthy register.",
     "Truffle Dark Chocolate Glazed Salmon",
     ["Make a truffle-chocolate glaze: dark chocolate, truffle oil, mirin, and soy sauce reduced together.", "Brush salmon fillets; bake at 425°F for 10 minutes, glazing halfway through.", "Plate; shave truffle over generously and finish with a drizzle of truffle oil and a dark chocolate curl."]),

    ("chocolate","salmon","vanilla",
     "Chocolate and vanilla share vanillin and furfural — lactonic-sweet compounds in both — while chocolate and salmon share dimethyl sulfide, creating a triangle where vanilla's sweetness suppresses salmon's trimethylamine through the same sweet-compound mechanism as teriyaki. Chocolate's bitterness deepens vanilla's sweetness into a complex savory-sweet fish glaze.",
     "Vanilla Dark Chocolate Salmon",
     ["Make a vanilla-chocolate court bouillon: split vanilla bean, dark chocolate, white wine, and aromatics.", "Poach salmon in the vanilla-chocolate broth at barely a simmer for 10 minutes.", "Serve with a vanilla-chocolate beurre blanc and a curl of dark chocolate grated over."]),

    ("chocolate","strawberry","tomato",
     "Chocolate, strawberry, and tomato all share furaneol — the sweet-caramel compound at the heart of all three, spanning Maillard cacao chemistry, ripe berry, and ripe tomato. This triple furaneol alignment is one of the most unusual in food chemistry, appearing in avant-garde mole negro served with strawberry-tomato salsa where the shared compound creates hidden coherence.",
     "Dark Chocolate Strawberry Tomato Salsa",
     ["Dice ripe tomatoes and strawberries; toss with a drizzle of melted dark chocolate, lime juice, and chili.", "Add fresh cilantro, red onion, and a pinch of salt; mix gently and rest 10 minutes.", "Serve alongside mole-braised chicken or as an unusual dip with plantain chips."]),
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
print(f"Batch 034 done: inserted {len(TRIPLETS)} triplets.")
