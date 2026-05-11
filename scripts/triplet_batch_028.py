#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("caramel","lemon","strawberry",
     "Caramel and strawberry share furaneol as their dominant sweet-caramel compound, while lemon's citric acid and limonene brighten the combination through acid contrast — lemon's acidity intensifying strawberry's apparent freshness by cutting through furaneol's warmth. The trio creates a refined summer dessert where sweet-caramel and tart-citrus balance precisely around strawberry.",
     "Caramel Lemon Strawberry Pavlova",
     ["Whip meringue to stiff peaks; bake at 250°F for 90 minutes until crisp outside and marshmallow inside.", "Macerate sliced strawberries with lemon juice, zest, and a drizzle of caramel sauce for 30 minutes.", "Top meringue with whipped cream; pile strawberry mixture over and drizzle caramel generously."]),

    ("caramel","lemon","tomato",
     "Caramel and tomato share furaneol — the sweet-caramel compound at the heart of both — while lemon's citric acid provides the brightness that cuts through caramel's richness and intensifies tomato's acidity into a balanced sweet-sour-savory register. The trio is the foundation of caramelized tomato jam and sophisticated tomato confiture preparations.",
     "Caramel Lemon Tomato Jam",
     ["Simmer chopped ripe tomatoes with sugar until thick; add lemon juice, zest, and a spoonful of dark caramel.", "Cook until jammy and glossy; season with flaky salt and a pinch of chili if desired.", "Cool and jar; serve with cheese, charcuterie, or spread on sourdough toast."]),

    ("caramel","lemon","truffle",
     "Caramel's Maillard sweetness and truffle's dimethyl sulfide earthiness represent opposite ends of the aromatic spectrum — sweet versus funky-earthy — while lemon's citric acid and limonene provide the brightness that cuts through both richness vectors, lifting the combination into a lighter, more vertical register. The trio creates a sophisticated luxury pasta or egg preparation.",
     "Truffle Caramel Lemon Tagliolini",
     ["Cook fresh tagliolini al dente; melt truffle butter in the pan, add a drizzle of caramel, and lemon zest.", "Toss pasta with the sauce and a splash of pasta water until glossy and coating each strand.", "Plate immediately; shave fresh truffle over generously and finish with a squeeze of lemon juice."]),

    ("caramel","lemon","vanilla",
     "Caramel and vanilla share furaneol and vanillin — sweet-caramel and lactonic compounds — while lemon's citric acid provides the brightness that prevents the double-sweet combination from becoming cloying, sharpening vanilla's floral character and caramel's Maillard warmth into a balanced acid-sweet register. The trio defines sophisticated lemon tart preparations.",
     "Vanilla Caramel Lemon Tart",
     ["Make a lemon curd with eggs, lemon juice, and zest; off heat whisk in caramel sauce and vanilla bean seeds.", "Pour into a blind-baked tart shell; refrigerate until fully set and glossy.", "Serve with a tuile, lemon zest curls, and a drizzle of warm caramel at the table."]),

    ("caramel","mint","oyster",
     "Caramel's sweetness creates a bold marine-sweet contrast against oyster's briny trimethylamine — the sweet-salt principle — while mint's menthol provides a palate-cleansing cooling effect that cuts through both caramel's richness and oyster's brine, creating a three-stage aromatic sequence of sweet, marine, and cool. The trio is an avant-garde raw bar concept.",
     "Caramel Mint Oyster Shooter",
     ["Mix a small amount of caramel with apple cider vinegar and minced shallot into a mignonette.", "Stir in very finely chopped fresh mint; adjust sweet-tart balance with vinegar.", "Spoon a small amount over freshly shucked oysters; serve immediately over ice with lemon."]),

    ("caramel","mint","parmesan",
     "Caramel and Parmesan share furaneol and butyric acid — sweet-caramel and fatty-dairy compounds — while mint's menthol provides cooling contrast that cuts Parmesan's fatty richness and caramel's Maillard warmth through olfactory cooling. The unusual trio achieves a sophisticated savory-sweet-cool balance in compound butter or tasting-menu preparations.",
     "Caramel Mint Parmesan Crostini",
     ["Shave Parmesan into large curls; toast crostini until crisp and drizzle with dark caramel while warm.", "Top with Parmesan curls and a tiny amount of very finely chopped fresh mint.", "Add cracked pepper and flaky salt; serve as an aperitivo with a dry sparkling wine."]),

    ("caramel","mint","rose",
     "Caramel's warm Maillard sweetness contrasts with mint's menthol cooling — sweet-cool opposition — while rose's 2-phenylethanol provides the floral bridge that connects caramel's warmth to mint's freshness through shared aromatic register. The trio creates a refined confection where warming, cooling, and floral play in sequence on the palate.",
     "Rose Mint Caramel Bonbons",
     ["Make a dark caramel, whisk in rose-infused cream, butter, and a drop of peppermint extract.", "Add flaky salt and rose water; pour into small molds and allow to set until firm.", "Unmold; dust with dried rose petal powder and a tiny mint leaf on each before serving."]),

    ("caramel","mint","salmon",
     "Caramel's sweet Maillard compounds suppress salmon's trimethylamine marine notes — the teriyaki mechanism — while mint's menthol adds its own olfactory masking of marine amines through palate-cooling aromatic competition. The combination creates a double trimethylamine-suppression that produces the cleanest-tasting salmon possible, with a refreshing finish.",
     "Caramel Mint Glazed Salmon",
     ["Make a caramel-mint glaze: caramel sauce, rice vinegar, soy, and a handful of muddled fresh mint.", "Strain out mint; brush salmon fillets and bake at 425°F for 10 minutes, glazing halfway through.", "Garnish with fresh mint leaves and sesame seeds; serve over cucumber noodles or jasmine rice."]),

    ("caramel","mint","strawberry",
     "Caramel and strawberry share furaneol — sweet-caramel at the heart of both — while mint's menthol adds a cooling effect that makes strawberry taste sharper and more vibrant through olfactory contrast, the same phenomenon in mint chocolate chip ice cream applied to fruit. The trio creates a refreshing summer dessert.",
     "Caramel Mint Strawberry Parfait",
     ["Layer sliced macerated strawberries with caramel sauce and Greek yogurt in tall glasses.", "Add a layer of crushed caramelized biscuits for crunch between each strawberry layer.", "Top with a drizzle of caramel, fresh mint leaves, and a final whole strawberry to serve."]),

    ("caramel","mint","tomato",
     "Caramel and tomato share furaneol — their dominant sweet-caramel compound — while mint's menthol provides cooling herbal contrast that cuts through the sweet-savory richness and adds a fresh Mediterranean dimension. The combination creates a sophisticated chilled tomato soup or sauce with layered aromatic complexity.",
     "Caramel Mint Tomato Gazpacho",
     ["Blend ripe tomatoes with olive oil, garlic, and a splash of sherry vinegar until very smooth; strain.", "Stir in a drizzle of dark caramel and a large handful of fresh mint; blend briefly and strain again.", "Serve very cold in chilled bowls with mint oil, a swirl of caramel, and a mint leaf garnish."]),

    ("caramel","mint","truffle",
     "Caramel and truffle share Maillard-derived aromatics — both developing complex compounds through heat-driven and fermentation-driven biochemical processes respectively — while mint's menthol provides a cooling palate-cleansing contrast that prevents the sweet-earthy richness from becoming heavy. Menthol's olfactory competition gives truffle a cleaner, more distinct presence.",
     "Truffle Caramel Mint Compound Butter",
     ["Beat softened butter with truffle paste, a small drizzle of caramel, and very finely chopped fresh mint.", "Add flaky salt; refrigerate in a log until firm, then slice into rounds.", "Melt over scrambled eggs, grilled beef, or warm pasta just before serving for an unusual layered finish."]),

    ("caramel","mint","vanilla",
     "Caramel and vanilla share furaneol and vanillin — sweet-caramel and lactonic compounds — while mint's menthol provides the classic cool-sweet opposition that makes mint-vanilla ice cream such a universal combination. Menthol's cooling amplifies vanilla's perceived sweetness through olfactory contrast, and caramel deepens the Maillard dimension.",
     "Vanilla Caramel Mint Crème Brûlée",
     ["Infuse cream with split vanilla bean and a handful of fresh mint; steep 20 minutes and strain.", "Whisk into egg yolks with caramel sauce; pour into ramekins and bake at 325°F in a water bath.", "Chill; top with sugar and brûlée; garnish with a fresh mint tip and a drizzle of caramel."]),

    ("caramel","oyster","parmesan",
     "Caramel and Parmesan share furaneol and butyric acid — sweet-caramel and fatty-dairy compounds — while oyster's marine umami (glutamates and IMP) compounds with Parmesan's free glutamates into a double-umami stack that caramel's sweetness balances through sweet-savory contrast. The trio creates the richest possible savory gratin preparation.",
     "Caramel Parmesan Oyster Gratin",
     ["Make a caramel-cream sauce: dark caramel whisked into warm cream with a grating of Parmesan.", "Shuck oysters into half-shells; spoon a small amount of caramel-Parmesan sauce over each.", "Top with more grated Parmesan and breadcrumbs; broil until golden and oyster edges just curl."]),

    ("caramel","oyster","rose",
     "Oyster and rose share phenylacetaldehyde — the rosy-fermented compound that both marine bivalves and rose petals produce through unrelated pathways — while caramel's sweetness provides the contrast that makes the rose-oyster combination readable rather than strange, softening brine through sweet-salt opposition. The trio creates a delicate perfumed oyster preparation.",
     "Rose Caramel Oyster on the Half Shell",
     ["Dissolve a tiny amount of caramel into rose water and white wine vinegar; add minced shallot.", "Allow to cool completely; the caramel rounds the vinegar's sharpness while preserving acidity.", "Spoon very sparingly over freshly shucked oysters; garnish with a single rose petal."]),

    ("caramel","oyster","salmon",
     "Caramel's sweetness suppresses marine amines — trimethylamine in oyster and salmon both reduced by sweet Maillard compounds through the same mechanism as teriyaki glaze — while oyster and salmon share dimethyl sulfide and the broader marine aromatic compound family. The trio is a natural sweet-glazed seafood combination.",
     "Caramel Glazed Seafood Platter",
     ["Make a caramel-miso glaze: amber caramel, white miso, mirin, and rice vinegar whisked smooth.", "Brush salmon fillets; bake at 425°F for 10 minutes; separately, broil oysters in the shell 3 minutes.", "Serve salmon and oysters side by side, each brushed with the caramel-miso glaze; garnish with scallion."]),

    ("caramel","oyster","strawberry",
     "Caramel and strawberry share furaneol as their dominant sweet-caramel compound — both producing intense caramel-sweet aroma at high concentrations — while oyster's marine brine creates a sweet-salt contrast with both through opposing polarities. The trio is an advanced raw bar concept where strawberry and caramel act as complementary sweet-tart foils to brine.",
     "Caramel Strawberry Oyster Mignonette",
     ["Blend muddled fresh strawberry with a touch of caramel and white wine vinegar into a smooth mignonette.", "Strain; adjust sweet-tart-acid balance and add finely minced shallot and cracked pepper.", "Spoon over freshly shucked oysters on ice; the caramel-strawberry softens the brine beautifully."]),

    ("caramel","oyster","tomato",
     "Caramel and tomato share furaneol — the sweet-caramel compound in both — while oyster's marine glutamates combine with tomato's free glutamates into a double-umami base that caramel's Maillard sweetness elevates into a rich, complex chowder register. The trio creates a sophisticated seafood stew where sweet, marine, and vegetal layers build.",
     "Caramel Tomato Oyster Stew",
     ["Sauté shallots and garlic; add crushed tomatoes and a spoonful of dark caramel; simmer 15 minutes.", "Add shucked oysters with their liquor; poach gently 2 minutes until just barely cooked.", "Season with salt and fresh herbs; serve in warm bowls with crusty bread to soak the broth."]),

    ("caramel","oyster","truffle",
     "Caramel and truffle share Maillard-derived aromatic compounds — dimethyl sulfide present in both roasted sugars and black truffle fermentation — while oyster's marine dimethyl sulfide provides a third marine expression of the same sulfurous compound, creating a complete sweet-earthy-marine aromatic stack. The trio is haute cuisine at its most opulent.",
     "Truffle Caramel Oyster Tartare",
     ["Shuck and finely chop oysters; mix with a drizzle of truffle oil and caramel reduction.", "Season with fleur de sel and white pepper; mound into oyster shells over crushed ice.", "Shave fresh truffle over each portion generously; serve with cold champagne immediately."]),

    ("caramel","oyster","vanilla",
     "Caramel and vanilla share furaneol and vanillin — sweet-caramel and lactonic compounds — while oyster's marine brine creates the sweet-salt contrast that makes this unusual seafood preparation work, applying the salted caramel principle directly to oyster cookery. Vanilla's floral depth bridges caramel's warmth to oyster's minor floral phenylacetaldehyde.",
     "Vanilla Caramel Broiled Oysters",
     ["Make a vanilla-caramel butter: dark caramel, vanilla bean seeds, cold butter, and fleur de sel.", "Shuck oysters into half-shells; top each with a small sliver of vanilla caramel butter.", "Broil 3-4 minutes until the butter is melted and oyster edges just begin to curl; serve immediately."]),

    ("caramel","parmesan","rose",
     "Caramel and Parmesan share furaneol and butyric acid — sweet-caramel and fatty-dairy compounds that create a naturally sweet-savory dairy base — while rose's 2-phenylethanol bridges the combination through its connection to Parmesan's fermentation esters and caramel's warm Maillard register. The trio creates a refined sweet-floral-savory risotto or pasta.",
     "Rose Caramel Parmesan Risotto",
     ["Cook arborio risotto with white wine and stock until creamy and al dente; remove from heat.", "Stir in cold butter, finely grated Parmesan, a drizzle of dark caramel, and a splash of rose water.", "Plate; garnish with crystallized rose petals and a final grating of Parmesan."]),
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
print(f"Batch 028 done: inserted {len(TRIPLETS)} triplets.")
