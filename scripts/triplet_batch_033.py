#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("chocolate","lemon","mint",
     "Chocolate and mint is a celebrated pairing — menthol's cooling amplifying chocolate's bitterness — while lemon's citric acid provides the acidity that brightens and sharpens both chocolate's Maillard depth and mint's herbal freshness, giving the trio a more vertical, clean aromatic profile than chocolate-mint alone. The trio appears in sophisticated citrus-herb chocolate confections.",
     "Lemon Mint Dark Chocolate Fondants",
     ["Melt dark chocolate and butter; whisk in eggs, sugar, lemon zest, and finely chopped fresh mint.", "Pour into buttered ramekins; bake at 400°F for 10 minutes until just set at the edges.", "Serve immediately with a scoop of mint-lemon sorbet and a dusting of cocoa powder."]),

    ("chocolate","lemon","oyster",
     "Chocolate and oyster share dimethyl sulfide — the sulfurous compound in both cacao fermentation and marine bivalve metabolism — while lemon's citric acid performs its classic trimethylamine-neutralizing function and its limonene adds brightness that cuts through chocolate's bitterness simultaneously. Lemon is the critical bridge that makes this unusual trio cohere.",
     "Dark Chocolate Lemon Oyster Pan Sauce",
     ["Shuck oysters, reserving liquor; reduce liquor with a small amount of dark chocolate and lemon zest.", "Whisk in cold butter and lemon juice off heat until glossy; season with salt.", "Broil oysters briefly in the shell; spoon chocolate-lemon butter over each and serve immediately."]),

    ("chocolate","lemon","parmesan",
     "Chocolate and Parmesan share phenylacetaldehyde — fermented-rosy compounds spanning cacao and aged dairy — while lemon's citric acid cuts through Parmesan's butyric fat and moderates chocolate's bitterness simultaneously through pH-driven aromatic adjustment. The trio appears in sophisticated savory chocolate preparations where acid balances rich umami and bitter.",
     "Dark Chocolate Lemon Parmesan Biscuits",
     ["Blend grated Parmesan, cold butter, flour, lemon zest, dark cocoa, and a pinch of cayenne.", "Roll dough, cut into rounds, and bake at 350°F until just golden and fragrant.", "Cool; serve as an aperitivo biscuit with wine — bitter, sharp, and savory simultaneously."]),

    ("chocolate","lemon","rose",
     "Chocolate and rose share phenylacetaldehyde — rosy-fermented compound in both cacao and rose petals — while lemon's geraniol directly overlaps with rose's geraniol, creating a citrus-floral bridge between lemon and rose that chocolate's depth anchors into a coherent dark-floral-citrus register. The trio creates a refined Turkish-influenced chocolate dessert.",
     "Rose Lemon Dark Chocolate Mousse",
     ["Melt dark chocolate; fold into whipped cream with rose water, lemon zest, and lemon juice.", "Chill in serving glasses until set and firm, at least 2 hours.", "Serve with candied rose petals, lemon zest curls, and a dusting of cocoa powder."]),

    ("chocolate","lemon","salmon",
     "Chocolate and salmon share dimethyl sulfide — sulfurous compounds in both — while lemon's citric acid suppresses salmon's trimethylamine marine notes and simultaneously cuts chocolate's bitterness. The double acid-mechanism lemon provides makes this the most effective single brightener for the chocolate-salmon combination in a bold glaze preparation.",
     "Dark Chocolate Lemon Glazed Salmon",
     ["Make a chocolate-lemon glaze: dark chocolate, lemon juice, soy sauce, and honey reduced together.", "Brush salmon fillets; bake at 425°F for 10 minutes, glazing halfway through.", "Serve over black rice with lemon wedges and a fine grating of dark chocolate."]),

    ("chocolate","lemon","strawberry",
     "Chocolate and strawberry share furaneol — sweet-caramel compounds in both dark chocolate and ripe strawberry — while lemon's citric acid brightens the sweet-rich chocolate-strawberry combination through acid contrast, and limonene adds floral brightness that amplifies strawberry's aroma. The trio drives the classic chocolate-dipped strawberry with citrus refinement.",
     "Lemon Dark Chocolate Strawberry Tart",
     ["Make a dark chocolate lemon ganache: melt chocolate with cream and lemon zest; pour into tart shell.", "Arrange halved fresh strawberries over the set ganache; glaze with lemon-strawberry jelly.", "Serve with lemon curd on the side and candied lemon peel garnish."]),

    ("chocolate","lemon","tomato",
     "Chocolate and tomato share phenylacetaldehyde and pyrazines — rosy-fermented and Maillard-roasted compounds — while lemon's citric acid brightens tomato's acidity and cuts chocolate's bitterness through pH-driven adjustment. The trio produces a bright, acid-forward version of mole-style tomato sauce where lemon gives the chocolate-tomato combination surprising freshness.",
     "Dark Chocolate Lemon Tomato Sauce",
     ["Cook crushed tomatoes until reduced; add dark chocolate and lemon zest; simmer 5 minutes.", "Finish with lemon juice off heat; the acid brightens both the chocolate depth and tomato sweetness.", "Serve over pasta with Parmesan, or use as a bold braising sauce for chicken or rabbit."]),

    ("chocolate","lemon","truffle",
     "Chocolate and truffle share dimethyl sulfide and phenylacetaldehyde — sulfurous and rosy-fermented compounds — while lemon's citric acid and limonene provide the brightness that lifts this intensely dark, earthy combination into a lighter, more vertical register. Lemon is the critical acid-brightness that makes truffle-chocolate preparations feel elegant rather than heavy.",
     "Truffle Lemon Dark Chocolate Pasta",
     ["Melt truffle butter with a small square of dark chocolate and lemon zest in a wide pan.", "Toss al dente pasta with the glossy truffle-chocolate sauce and a splash of pasta water.", "Plate; squeeze lemon juice over, shave truffle generously, and finish with lemon zest."]),

    ("chocolate","lemon","vanilla",
     "Chocolate and vanilla share vanillin and furfural — the lactonic-sweet compounds at the heart of both — while lemon's citric acid and limonene provide the brightness that prevents the sweet-rich chocolate-vanilla combination from becoming cloying, sharpening vanilla's floral register into a cleaner finish. The trio defines the most balanced form of chocolate-vanilla dessert.",
     "Vanilla Lemon Dark Chocolate Layer Cake",
     ["Make dark chocolate sponge layers flavored with espresso; cool completely.", "Make a vanilla-lemon buttercream: whip butter with vanilla bean seeds, lemon zest, and icing sugar.", "Layer and frost; finish with a drizzle of dark chocolate and candied lemon peel."]),

    ("chocolate","mint","oyster",
     "Chocolate and oyster share dimethyl sulfide — sulfurous compounds in cacao and marine bivalves — while mint's menthol provides cooling palate-cleansing contrast that cuts through both chocolate's richness and oyster's brine, creating a three-stage aromatic sequence of bitter-dark, briny-marine, and cool-fresh. The trio is extreme but chemically coherent.",
     "Mint Dark Chocolate Oyster Shooter",
     ["Dissolve a tiny square of dark chocolate in warm sherry vinegar; add muddled fresh mint.", "Strain and cool; add minced shallot and cracked pepper.", "Spoon very sparingly over raw oysters on ice; the mint cools while chocolate deepens the brine."]),

    ("chocolate","mint","parmesan",
     "Chocolate and Parmesan share phenylacetaldehyde — fermented-rosy compounds in both — while mint's menthol provides cooling contrast that cuts Parmesan's fat and chocolate's bitterness through olfactory competition. The unusual trio creates a sophisticated savory chocolate biscuit where all three flavors read in sequence rather than simultaneously.",
     "Mint Dark Chocolate Parmesan Crisps",
     ["Melt dark chocolate with a drizzle of olive oil and a pinch of fleur de sel; spread thin.", "Immediately sprinkle with finely grated Parmesan and very finely chopped fresh mint.", "Allow to set fully; break into irregular shards and serve as an aperitivo."]),

    ("chocolate","mint","rose",
     "Chocolate and rose share phenylacetaldehyde — the rosy-fermented compound in cacao and rose petals — while mint's menthol provides cooling contrast that prevents the floral-chocolate combination from being heavy, and rose's 2-phenylethanol adds a rosy dimension that connects to chocolate's own phenylacetaldehyde. The trio achieves a sophisticated perfumed chocolate confection.",
     "Rose Mint Dark Chocolate Bark",
     ["Melt dark chocolate; spread thinly on parchment and scatter dried rose petals and fresh mint leaves.", "Sprinkle with fleur de sel and allow to set completely at room temperature.", "Break into pieces; the rose and mint elevate the chocolate into a floral-cool register."]),

    ("chocolate","mint","salmon",
     "Chocolate and salmon share dimethyl sulfide — the sulfurous compound in cacao and marine fish — while mint's menthol independently suppresses salmon's trimethylamine through olfactory masking, giving a double-mechanism trimethylamine reduction. The combination creates a refreshing chocolate-glazed salmon where menthol's cool cleanses the marine-bitter richness.",
     "Mint Dark Chocolate Glazed Salmon",
     ["Make a mint-chocolate glaze: dark chocolate, fresh mint oil, soy sauce, and rice vinegar.", "Brush salmon fillets and bake at 425°F for 10 minutes, glazing halfway through.", "Garnish with fresh mint and serve over cucumber noodles for maximum cool-fresh contrast."]),

    ("chocolate","mint","strawberry",
     "Chocolate and strawberry share furaneol — sweet-caramel in both — while mint's menthol amplifies strawberry's perceived brightness through cooling contrast, the same mechanism that makes mint intensify fruit flavor in mojitos and summer desserts. The trio creates the freshest, most vibrant chocolate-strawberry experience possible.",
     "Mint Chocolate Covered Strawberries",
     ["Melt dark chocolate with a tiny drop of peppermint extract and a pinch of fleur de sel.", "Dip ripe whole strawberries and allow to set on parchment at room temperature.", "Scatter finely chopped fresh mint over before the chocolate sets for fragrant herb crust."]),

    ("chocolate","mint","tomato",
     "Chocolate and tomato share phenylacetaldehyde and pyrazines — rosy-fermented and Maillard-roasted compounds — while mint's menthol provides cooling herbal freshness that cuts through the rich chocolate-tomato combination and adds a Mediterranean herbal register reminiscent of Moroccan cuisine where mint bridges savory and sweet.",
     "Dark Chocolate Mint Tomato Mole",
     ["Cook crushed tomatoes with dark chocolate, dried chilies, garlic, and a large bunch of fresh mint.", "Simmer 20 minutes until thick; remove mint stems and blend until smooth.", "Serve over lamb or chicken; the mint provides unexpected freshness in the mole register."]),

    ("chocolate","mint","truffle",
     "Chocolate and truffle share dimethyl sulfide and phenylacetaldehyde — sulfurous-rosy compounds in cacao and earthy fungal fermentation — while mint's menthol provides cooling palate-cleansing contrast that lifts the intensely dark, earthy chocolate-truffle combination into a lighter register. Menthol gives truffle's heavy earthiness a surprising clean finish.",
     "Truffle Mint Dark Chocolate Bon Bons",
     ["Make a truffle ganache: melt dark chocolate with truffle-infused cream and a drop of peppermint extract.", "Cool until firm; roll into balls with cool hands.", "Coat in tempered dark chocolate; garnish each with a tiny fresh mint leaf while wet."]),

    ("chocolate","mint","vanilla",
     "Chocolate and vanilla share vanillin and furfural — lactonic-sweet compounds in both — while mint's menthol provides the classic cooling contrast that makes mint-chocolate ice cream universal. Vanilla's sweetness rounds menthol's sharpness into a more approachable register, and chocolate's bitterness gives the mint-vanilla combination savory depth. The trio is classic American ice cream perfected.",
     "Mint Chip Vanilla Dark Chocolate Ice Cream",
     ["Make a vanilla custard ice cream base; churn until thick.", "Fold in dark chocolate chips and finely chopped fresh mint in the last minute of churning.", "Freeze until firm; serve scooped with a warm dark chocolate fudge sauce on top."]),

    ("chocolate","oyster","parmesan",
     "Chocolate, oyster, and Parmesan all share dimethyl sulfide — the sulfurous compound spanning cacao fermentation, marine bivalve metabolism, and aged dairy — creating a three-way sulfurous alignment of unusual breadth. The combination's triple umami (chocolate theobromine, oyster glutamates, Parmesan free glutamates) makes for an intensely savory trio.",
     "Dark Chocolate Oyster Parmesan Gratin",
     ["Make a chocolate-Parmesan béchamel: melt a tiny square of chocolate into warm cream sauce with Parmesan.", "Shuck oysters into half shells; spoon chocolate-Parmesan sauce over each.", "Top with breadcrumbs and more Parmesan; broil until golden and just bubbling."]),

    ("chocolate","oyster","rose",
     "Chocolate, oyster, and rose all share phenylacetaldehyde — the rosy-fermented compound produced through cacao fermentation, bivalve marine chemistry, and rose petal biosynthesis through three entirely different biochemical pathways. This three-way shared compound creates an unusual but precise aromatic alignment in a delicate floral oyster preparation.",
     "Rose Dark Chocolate Oyster Mignonette",
     ["Dissolve a tiny amount of dark chocolate in warm sherry vinegar; add rose water and finely minced shallot.", "Add cracked pepper; cool completely and allow flavors to meld 10 minutes.", "Spoon very sparingly over freshly shucked raw oysters; serve on crushed ice immediately."]),

    ("chocolate","oyster","salmon",
     "Chocolate, oyster, and salmon all share dimethyl sulfide — the sulfurous compound spanning cacao fermentation, marine bivalve, and fatty fish — creating a three-way marine-earthy sulfurous alignment. In small amounts, chocolate's bitterness deepens the umami of both oyster and salmon while the sulfurous link creates an unexpectedly coherent flavor bridge.",
     "Dark Chocolate Miso Seafood Platter",
     ["Make a chocolate-miso glaze: dark chocolate, white miso, mirin, and rice vinegar whisked together.", "Brush salmon fillets; bake at 425°F for 10 minutes; separately glaze oysters and broil 3 minutes.", "Plate salmon and oysters side by side; both carry the chocolate-miso glaze with unexpected elegance."]),
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
print(f"Batch 033 done: inserted {len(TRIPLETS)} triplets.")
