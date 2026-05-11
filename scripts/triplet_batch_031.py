#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("chocolate","cucumber","parmesan",
     "Chocolate and Parmesan share phenylacetaldehyde and dimethyl sulfide — fermented-rosy and sulfurous compounds spanning cacao fermentation and aged dairy — while cucumber's (E)-2-nonenal provides clean watery freshness that cuts through the complex fermented-funky combination and acts as a palate-neutral spacer. The trio achieves a bold savory chocolate cheese board concept.",
     "Dark Chocolate Parmesan Cucumber Board",
     ["Shave aged Parmesan into large irregular pieces; arrange on a slate with dark chocolate shards.", "Fan thin slices of fresh cucumber around the cheese and chocolate as a palate cleanser.", "Drizzle with aged balsamic and a pinch of flaky salt; the cucumber refreshes between each bite."]),

    ("chocolate","cucumber","rose",
     "Chocolate and rose share phenylacetaldehyde — the rosy-fermented compound that cacao fermentation and rose petals produce through separate pathways — while cucumber's (E)-2-nonenal provides clean watery contrast that prevents the floral-fermented chocolate combination from being too heavy. The trio creates a delicate, perfumed summer chocolate dessert.",
     "Rose Chocolate Cucumber Sorbet",
     ["Make a dark chocolate sorbet: bloom cocoa in hot syrup, add rose water, and churn.", "Make a cucumber water by blending and straining fresh cucumber with a pinch of salt.", "Serve a scoop of rose-chocolate sorbet drizzled with cucumber water and rose petals."]),

    ("chocolate","cucumber","salmon",
     "Chocolate and salmon share dimethyl sulfide — the sulfurous compound spanning cacao fermentation and marine fish metabolism — while cucumber's (E)-2-nonenal provides clean contrast that mediates the unusual chocolate-fish combination through watery freshness. The trio appears in avant-garde sushi preparations where dark chocolate mole meets salmon.",
     "Dark Chocolate Mole Salmon with Cucumber",
     ["Make a very light dark chocolate-chili mole; thin with stock to a pourable sauce consistency.", "Sear salmon skin-side down until crisp; spoon a thin mole drizzle over the top.", "Serve with thinly sliced cucumber dressed in rice vinegar and sesame as a fresh contrast."]),

    ("chocolate","cucumber","strawberry",
     "Chocolate and strawberry share furaneol — the sweet-caramel compound dominant in both dark chocolate and ripe strawberry — while cucumber's (E)-2-nonenal provides cool watery freshness that amplifies strawberry's perceived brightness and cuts through chocolate's richness. The trio creates a refreshing summer chocolate-fruit dessert.",
     "Dark Chocolate Strawberry Cucumber Pavlova",
     ["Fold dark cocoa powder into meringue; bake at 250°F for 90 minutes until crisp outside.", "Macerate sliced strawberries with lemon juice and a drizzle of dark chocolate sauce.", "Top meringue with whipped cream, strawberry mixture, and thin cucumber ribbons for freshness."]),

    ("chocolate","cucumber","tomato",
     "Chocolate and tomato share phenylacetaldehyde and pyrazines — rosy-fermented and Maillard-roasted compounds that appear in both cacao fermentation and roasted tomato chemistry — while cucumber's (E)-2-nonenal provides clean contrast that brightens the roasted-savory tomato-chocolate combination. The trio is the flavor logic of Mexican mole with fresh garnish.",
     "Dark Chocolate Tomato Sauce with Cucumber Salsa",
     ["Simmer tomatoes with dark chocolate, chili, garlic, and spices into a rich mole-style sauce.", "Reduce until thick; season with salt and a touch of acidity from lime.", "Serve over roasted chicken with a fresh cucumber-tomato salsa and cilantro on top."]),

    ("chocolate","cucumber","truffle",
     "Chocolate and truffle share dimethyl sulfide and phenylacetaldehyde — the sulfurous-rosy compounds connecting cacao fermentation to earthy fungal fermentation — while cucumber's (E)-2-nonenal provides the clean watery counterpoint that prevents the dense chocolate-truffle combination from being overwhelming. The trio creates an opulent yet refreshing luxury preparation.",
     "Truffle Dark Chocolate Cucumber Terrine",
     ["Make a dark chocolate truffle terrine layered with truffle oil and set in a loaf tin.", "Slice thin when cold; serve on chilled plates with cucumber ribbons and fleur de sel.", "Drizzle with aged balsamic and shave a little fresh truffle over each serving."]),

    ("chocolate","cucumber","vanilla",
     "Chocolate and vanilla share vanillin and furfural — lactonic-sweet and caramel compounds spanning cured vanilla bean and cacao fermentation — while cucumber's (E)-2-nonenal provides cool watery freshness that lifts vanilla's sweetness and cuts through chocolate's richness. The trio creates a surprisingly light and refreshing chocolate-vanilla dessert.",
     "Dark Chocolate Vanilla Cucumber Popsicles",
     ["Make a dark chocolate-vanilla custard base: melt chocolate into hot vanilla cream and cool.", "Blend with diced fresh cucumber for a subtle cool freshness; pour into popsicle molds.", "Freeze 6 hours; unmold and serve with a drizzle of chocolate and thin cucumber ribbons."]),

    ("chocolate","garlic","lamb",
     "Chocolate, garlic, and lamb share dimethyl sulfide — the sulfurous compound spanning cacao fermentation, allium metabolism, and animal-fat chemistry — creating a three-way sulfurous alignment that is the flavor foundation of Mexican mole negro applied to lamb. Chocolate's bitterness rounds garlic's pungency and contrasts lamb's gamey 4-methyloctanoic acid simultaneously.",
     "Dark Chocolate Garlic Braised Lamb",
     ["Brown lamb shoulder pieces; add whole garlic cloves, dark chocolate, dried chilies, and stock.", "Braise at 325°F for 2.5 hours until falling-apart tender; reduce the sauce until glossy.", "Serve with warm tortillas, pickled onion, and a garnish of fresh cilantro."]),

    ("chocolate","garlic","lavender",
     "Chocolate's phenylacetaldehyde rosy-fermented depth and lavender's linalool floral warmth share an aromatic register — both in the floral-complex zone — while garlic's dimethyl sulfide provides the pungent savory grounding that prevents the floral-chocolate combination from becoming too confectionery. The trio creates a bold Provençal chocolate savory application.",
     "Lavender Dark Chocolate Garlic Lamb Rub",
     ["Blend dried lavender, roasted garlic paste, dark cocoa, olive oil, and spices into a thick paste.", "Rub generously onto a leg of lamb; marinate overnight in the refrigerator.", "Roast at 325°F for 3 hours until deeply crusted and tender; rest before carving."]),

    ("chocolate","garlic","lemon",
     "Chocolate's bitterness and garlic's pungency are both modulated by lemon's citric acid — acid reduces the perception of both bitterness and allium sharpness through pH-driven aromatic shift — while lemon's limonene provides a brightness that lifts the dense chocolate-allium combination into a more vertical, accessible register. The trio appears in bold chocolate-savory sauce preparations.",
     "Dark Chocolate Garlic Lemon Sauce",
     ["Sauté sliced garlic in olive oil; add dark chocolate and a splash of water to make a sauce.", "Add lemon juice and zest; whisk until glossy and season with salt and chili flakes.", "Drizzle over roasted vegetables, pasta, or use as a bold dipping sauce for crusty bread."]),

    ("chocolate","garlic","mint",
     "Chocolate and mint share the classic cooling-bitter opposition — menthol amplifies chocolate's perceived bitterness through thermal contrast — while garlic's dimethyl sulfide adds savory sulfurous depth that grounds the confectionery chocolate-mint register into a more complex, food-appropriate savory territory. The trio appears in bold savory chocolate applications.",
     "Dark Chocolate Mint Garlic Lamb Sauce",
     ["Make a dark chocolate mint sauce: melt chocolate with garlic-infused olive oil, fresh mint, and stock.", "Whisk until glossy; add a squeeze of lemon and season with salt.", "Serve spooned over grilled lamb chops with fresh mint leaves and a dusting of cocoa."]),

    ("chocolate","garlic","oyster",
     "Chocolate, garlic, and oyster share dimethyl sulfide — the sulfurous compound spanning cacao fermentation, allium metabolism, and marine bivalve chemistry — creating a three-way sulfurous alignment in an unusual marine-bitter-allium combination. The trio appears in Cantonese-influenced black bean and oyster preparations where chocolate provides depth.",
     "Dark Chocolate Garlic Oyster Sauce",
     ["Sauté minced garlic in oil; add dark chocolate, oyster sauce, soy, and a splash of stock.", "Simmer until glossy and thick; the chocolate amplifies the oyster sauce's umami depth.", "Toss with stir-fried greens or serve as a bold sauce over steamed fish."]),

    ("chocolate","garlic","parmesan",
     "Chocolate and Parmesan share phenylacetaldehyde and dimethyl sulfide — fermented-rosy and sulfurous compounds — while garlic's allicin adds sharp pungency that interacts with chocolate's bitterness through the same sweet-bitter-sharp balance seen in mole with garlic. The trio creates a bold savory chocolate application for pasta or cheese board.",
     "Dark Chocolate Garlic Parmesan Pasta",
     ["Cook pasta al dente; in the pan, sauté garlic in butter until golden.", "Add a small square of dark chocolate and a splash of pasta water; stir until melted and glossy.", "Toss pasta with the sauce; finish with grated Parmesan, cracked pepper, and fresh herbs."]),

    ("chocolate","garlic","rose",
     "Chocolate and rose share phenylacetaldehyde — the rosy-fermented compound in cacao and rose petals — while garlic's dimethyl sulfide provides savory pungent grounding that prevents the floral-chocolate combination from becoming too sweet. The unusual trio appears in Persian-influenced chocolate preparations where rose and savory coexist.",
     "Rose Dark Chocolate Garlic Lamb Tagine",
     ["Brown lamb with garlic and onion; add rose water, dark chocolate, saffron, and spices.", "Braise at 300°F for 2 hours; the chocolate and rose create a layered sweet-bitter-floral sauce.", "Serve over saffron rice with dried rose petals, pomegranate seeds, and toasted almonds."]),

    ("chocolate","garlic","salmon",
     "Chocolate and salmon share dimethyl sulfide — the sulfurous compound spanning cacao fermentation and marine fish metabolism — while garlic's allicin adds sharp pungency that transforms into sweet cooked-garlic notes with heat, bridging chocolate's bitterness to salmon's fatty richness. The trio drives bold Asian-influenced glazed salmon preparations.",
     "Dark Chocolate Miso Garlic Salmon",
     ["Make a glaze: dark chocolate, white miso, roasted garlic paste, and mirin whisked together.", "Brush salmon fillets; roast at 425°F for 10 minutes, glazing halfway through.", "Serve over sesame rice with pickled cucumber and the remaining glaze drizzled over."]),

    ("chocolate","garlic","strawberry",
     "Chocolate and strawberry share furaneol — sweet-caramel compound in both — while garlic's dimethyl sulfide provides the pungent savory bridge that transforms what would be a simple dessert pairing into a sophisticated sweet-savory gastrique territory. The trio appears in bold strawberry-garlic chocolate reductions and upscale compotes.",
     "Strawberry Chocolate Garlic Compote",
     ["Sauté thinly sliced garlic in olive oil until golden; add chopped strawberries and cook briefly.", "Stir in grated dark chocolate and a splash of balsamic; simmer until jammy.", "Cool slightly; serve over cheese, grilled duck breast, or spread on sourdough."]),

    ("chocolate","garlic","tomato",
     "Chocolate, garlic, and tomato share dimethyl sulfide and phenylacetaldehyde — sulfurous and rosy-fermented compounds spanning all three — creating the exact compound alignment of Mexican mole negro where garlic and tomato are the savory backbone that chocolate's bitterness deepens. This trio is the flavor chemistry proof of why mole works.",
     "Dark Chocolate Garlic Tomato Mole Sauce",
     ["Toast dried chilies; blend with roasted tomatoes, garlic, and a square of dark chocolate.", "Simmer with chicken stock until thick and glossy; season with salt and a touch of cider vinegar.", "Serve over poached chicken or enchiladas with sesame seeds and sour cream."]),

    ("chocolate","garlic","truffle",
     "Chocolate, garlic, and truffle all share dimethyl sulfide — the sulfurous compound connecting cacao fermentation, allium metabolism, and earthy fungal chemistry — creating the deepest possible earthy-savory-bitter compound alignment. The trio appears in Italian-influenced black truffle preparations where chocolate amplifies truffle's umami darkness.",
     "Truffle Dark Chocolate Garlic Pasta",
     ["Sauté garlic in truffle butter; add a small square of dark chocolate and pasta water.", "Toss al dente pasta in the glossy truffle-chocolate sauce; season with salt.", "Plate; shave fresh truffle generously and finish with a drizzle of truffle oil."]),

    ("chocolate","garlic","vanilla",
     "Chocolate and vanilla share vanillin and furfural — lactonic-sweet and caramel compounds — while garlic's allicin and dimethyl sulfide provide pungent savory contrast that transforms the sweet-lactonic chocolate-vanilla combination into a bold sweet-savory territory. The unexpected trio appears in chocolate mole preparations where vanilla's sweetness bridges garlic pungency.",
     "Vanilla Dark Chocolate Garlic Mole",
     ["Toast dried chilies; blend with roasted garlic, a split vanilla bean's seeds, and dark chocolate.", "Simmer with turkey or chicken stock until thick; the vanilla softens garlic's sharpness.", "Serve over roasted turkey with sesame seeds, plantain, and warm corn tortillas."]),

    ("chocolate","lamb","lavender",
     "Chocolate and lamb share dimethyl sulfide — sulfurous compound spanning cacao fermentation and animal-fat chemistry — while lavender's linalool and linalyl acetate soften lamb's gamey 4-methyloctanoic acid through floral aromatic displacement, and chocolate's bitterness rounds the lavender's sweetness into a more savory register. The trio is a sophisticated Provençal chocolate-lamb preparation.",
     "Lavender Dark Chocolate Braised Lamb",
     ["Brown lamb shanks; add dried lavender, dark chocolate, red wine, and stock.", "Braise at 325°F for 3 hours until tender; the lavender and chocolate create a complex sauce.", "Strain and reduce the sauce; serve over the lamb with lavender sprigs and chocolate shavings."]),
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
print(f"Batch 031 done: inserted {len(TRIPLETS)} triplets.")
