#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("coffee","mint","oyster",
     "Coffee and oyster share dimethyl sulfide — sulfurous compounds in roasted coffee and marine bivalves — while mint's menthol provides cooling palate-cleansing contrast that cuts both coffee's bitterness and oyster's marine brine. The three-stage aromatic sequence of bitter-dark, briny-marine, and cool-fresh creates a unique avant-garde raw bar experience.",
     "Espresso Mint Oyster Shooter",
     ["Brew strong espresso; dissolve a pinch of sugar and add fresh mint; cool completely.", "Add a splash of rice vinegar and minced shallot; strain out mint.", "Spoon a small amount over raw oysters on ice; the mint-espresso mignonette is polarizing but precise."]),

    ("coffee","mint","parmesan",
     "Coffee and Parmesan share dimethyl sulfide while mint's menthol provides cooling contrast that cuts Parmesan's fat and coffee's bitterness through olfactory competition. The unusual combination creates a savory shortbread or cheese crisp where bitter, umami, and cool read in sequence rather than simultaneously.",
     "Espresso Mint Parmesan Crisps",
     ["Grate Parmesan; mix with espresso powder and very finely chopped fresh mint.", "Arrange in small mounds on a silpat; bake at 375°F until spread and golden.", "Cool until crisp; serve as an aperitivo with espresso or white wine."]),

    ("coffee","mint","rose",
     "Coffee's bitter pyrazines provide dark depth while mint's menthol cools and rose's 2-phenylethanol warms — three distinct aromatic registers in succession. Rose and coffee share no direct compound but the floral-bitter contrast is the same opposition that drives Turkish coffee with rose water, and mint provides the palate-cleansing reset between bites.",
     "Rose Mint Espresso Martini",
     ["Shake cold brew espresso with rose water, mint simple syrup, and ice vigorously until frothy.", "Double strain into a chilled coupe glass.", "Garnish with three coffee beans floated on the foam and a dried rose petal."]),

    ("coffee","mint","salmon",
     "Coffee and salmon share dimethyl sulfide while mint's menthol suppresses salmon's trimethylamine marine notes through olfactory masking — double trimethylamine suppression from both bitter-compound coffee and cooling menthol. The combination creates the most effective aromatic suppression of marine notes possible with a coffee-herb rub.",
     "Espresso Mint Rubbed Salmon",
     ["Make a rub: ground espresso, finely chopped fresh mint, lemon zest, and garlic powder.", "Press onto salmon fillets; rest 15 minutes at room temperature.", "Sear in a very hot pan skin-side down; finish in a 400°F oven 8 minutes; serve with cucumber."]),

    ("coffee","mint","strawberry",
     "Coffee's furfural is a Maillard cousin of strawberry's furaneol — caramel-adjacent compounds — while mint's menthol amplifies strawberry's perceived brightness through cooling contrast, making the fruit taste sharper and more vibrant. The trio creates a refreshing summer coffee dessert where all three work in different sensory registers.",
     "Mint Strawberry Cold Brew Popsicles",
     ["Blend fresh strawberries with cold brew, mint simple syrup, and lemon juice until smooth.", "Pour into popsicle molds and freeze 6 hours until firm.", "Unmold and serve immediately; mint, espresso, and strawberry bloom in sequence on each bite."]),

    ("coffee","mint","tomato",
     "Coffee and tomato share pyrazines and phenylacetaldehyde — Maillard-roasted and rosy-fermented compounds — while mint's menthol provides cooling herbal freshness that cuts through the rich roasted-savory tomato-coffee combination. The trio creates a refreshing espresso-tomato-herb sauce or gazpacho with unexpected depth.",
     "Espresso Mint Bloody Mary",
     ["Blend tomato juice with cold brew espresso, fresh mint, lemon juice, and horseradish.", "Season with hot sauce, Worcestershire, and celery salt; stir over ice.", "Serve in a chilled glass with a celery stalk and mint sprig; the espresso adds unexpected depth."]),

    ("coffee","mint","truffle",
     "Coffee and truffle share dimethyl sulfide — sulfurous compounds in roasted coffee and earthy fungal fermentation — while mint's menthol provides cooling contrast that lifts the intensely dark, earthy coffee-truffle combination. Menthol's olfactory competition gives truffle's heavy earthiness a surprisingly clean, refreshing finish.",
     "Truffle Espresso Mint Chocolate",
     ["Make a truffle ganache: melt dark chocolate with truffle-infused cream and a shot of espresso.", "Add a drop of peppermint extract; cool until firm and roll into balls.", "Coat in tempered chocolate; garnish with a fresh mint leaf and a dusting of ground espresso."]),

    ("coffee","mint","vanilla",
     "Coffee and vanilla share furfural and vanillin — the classic mocha-vanilla register — while mint's menthol provides cooling contrast that makes the sweet-bitter coffee-vanilla combination taste brighter and more refreshing. The trio is mint chip mocha in its most aromatic form, where all three aromatics play distinctly on the palate.",
     "Mint Vanilla Cold Brew Coffee Ice Cream",
     ["Churn a vanilla custard ice cream base with cold brew espresso folded in.", "Add a generous amount of finely chopped fresh mint and freeze until firm.", "Serve scooped with warm espresso poured over as an affogato variation."]),

    ("coffee","oyster","parmesan",
     "Coffee, oyster, and Parmesan all share dimethyl sulfide — the sulfurous compound spanning roasted coffee, marine bivalves, and aged dairy — creating a three-way sulfurous alignment that also includes triple umami (coffee's bitter umami amplifiers, oyster's glutamates, Parmesan's free glutamates). The combination creates an intensely savory preparation.",
     "Espresso Parmesan Oyster Gratin",
     ["Make an espresso-Parmesan cream sauce: brew espresso into a béchamel, add grated Parmesan.", "Shuck oysters into shells; spoon espresso-Parmesan sauce over each.", "Top with breadcrumbs; broil until golden and sauce is bubbling."]),

    ("coffee","oyster","rose",
     "Coffee's bitter pyrazines and rose's 2-phenylethanol create a bold dark-floral contrast while oyster's phenylacetaldehyde connects to both rose's rosy-fermented character and coffee's fermentation byproducts. The trio creates a delicate but daring Levantine oyster preparation where perfume and brine meet coffee's roasted anchor.",
     "Rose Espresso Oyster Mignonette",
     ["Reduce brewed espresso with white wine vinegar to a syrupy consistency; cool completely.", "Add rose water, finely minced shallot, and cracked white pepper; stir gently.", "Spoon sparingly over raw oysters on ice; the rose-espresso creates an unexpectedly refined mignonette."]),

    ("coffee","oyster","salmon",
     "Coffee, oyster, and salmon all share dimethyl sulfide — the sulfurous compound spanning roasted coffee, marine bivalves, and fatty fish — creating a three-way sulfurous alignment across very different food categories. Coffee's bitter umami amplifiers deepen both oyster's briny umami and salmon's fatty richness through the same sensory mechanism.",
     "Espresso Miso Seafood Platter",
     ["Make an espresso-miso glaze: brewed espresso, white miso, mirin, and rice vinegar whisked together.", "Brush salmon fillets and bake at 425°F; broil oysters in the shell 3 minutes with a little glaze.", "Plate side by side; the espresso-miso bridges both seafoods into a unified aromatic register."]),

    ("coffee","oyster","strawberry",
     "Coffee's furfural is a caramel-adjacent compound to strawberry's furaneol while coffee and oyster share dimethyl sulfide — creating a triangle where coffee bridges the sweet-fruit and marine registers simultaneously. Strawberry's sweetness applies the sweet-salt contrast principle against oyster brine while coffee's depth anchors both.",
     "Strawberry Espresso Oyster Shooter",
     ["Blend muddled strawberry with brewed espresso and white wine vinegar into a smooth mignonette.", "Strain and cool; add minced shallot and cracked pepper.", "Spoon over raw oysters on ice; the strawberry-espresso is polarizing and precise."]),

    ("coffee","oyster","tomato",
     "Coffee and tomato share pyrazines and phenylacetaldehyde — Maillard and fermented compounds — while coffee and oyster share dimethyl sulfide, creating a chain where tomato's savory acidity bridges coffee's roasted bitterness to oyster's marine umami. The trio is the flavor logic of a coffee-depth Bloody Mary or tomato-oyster chowder with espresso.",
     "Espresso Tomato Oyster Chowder",
     ["Sauté shallots and garlic; add crushed tomatoes and a shot of espresso; simmer 15 minutes.", "Add shucked oysters with their liquor; cook gently 2 minutes until just done.", "Season with salt and herbs; the espresso deepens the tomato-brine combination dramatically."]),

    ("coffee","oyster","truffle",
     "Coffee and truffle share dimethyl sulfide while coffee and oyster share dimethyl sulfide — creating a double overlap where all three connect through the same sulfurous compound across roasted, marine, and fungal chemistry. The three-way sulfurous alignment at different aromatic intensities creates one of the boldest possible tasting-menu preparations.",
     "Truffle Espresso Oyster Tartare",
     ["Shuck and finely chop oysters; mix with a drizzle of truffle oil and a tiny amount of espresso reduction.", "Season with fleur de sel and white pepper; mound in oyster shells over crushed ice.", "Shave fresh truffle over each; serve with cold champagne and espresso on the side."]),

    ("coffee","oyster","vanilla",
     "Coffee and vanilla share furfural and vanillin while coffee and oyster share dimethyl sulfide — creating a triangle where vanilla's sweetness applies the sweet-salt principle to the coffee-oyster combination. Vanilla's lactonic warmth bridges coffee's bitterness and oyster's marine brine through sweet-compound aromatic displacement.",
     "Vanilla Espresso Broiled Oysters",
     ["Make a vanilla-espresso butter: vanilla bean seeds, a tiny espresso reduction, butter, and fleur de sel.", "Shuck oysters into half shells; top each with a small amount of vanilla-espresso butter.", "Broil 3 minutes until butter melts and oyster edges just curl; serve immediately."]),

    ("coffee","parmesan","rose",
     "Coffee and Parmesan share dimethyl sulfide while coffee's pyrazines and rose's 2-phenylethanol create a dark-floral contrast — bitter and perfumed. Rose's 2-phenylethanol also connects to Parmesan's fermentation esters, creating a chain where Parmesan's umami bridges the bold floral-bitter coffee-rose combination into a sophisticated savory-aromatic territory.",
     "Rose Espresso Parmesan Risotto",
     ["Cook arborio risotto with white wine and stock until creamy; off heat stir in butter and Parmesan.", "Add a splash of rose water and a tiny shot of espresso to the finished risotto; season.", "Plate; garnish with crystallized rose petals and a very fine drizzle of espresso oil."]),

    ("coffee","parmesan","salmon",
     "Coffee, Parmesan, and salmon all share dimethyl sulfide — the sulfurous compound spanning roasted coffee, aged dairy, and marine fish — while coffee's bitter compounds suppress salmon's trimethylamine and Parmesan's umami amplifies the overall savory register. The trio creates a bold crust preparation with unexpected depth.",
     "Espresso Parmesan Crusted Salmon",
     ["Mix finely grated Parmesan with espresso powder, breadcrumbs, herbs, and olive oil.", "Press firmly onto salmon fillets; bake at 400°F for 12 minutes until crust is golden.", "Serve with lemon and a cold brew espresso drizzle; the crust is bitter, salty, and umami-rich."]),

    ("coffee","parmesan","strawberry",
     "Coffee's furfural is caramel-adjacent to strawberry's furaneol while Parmesan and strawberry share furaneol — creating a double furaneol connection that strawberry bridges. Coffee deepens the sweet-caramel register while Parmesan's umami-salt contrasts strawberry's sweetness in the same way aged cheese and fresh fruit work on a dessert plate.",
     "Strawberry Espresso Parmesan Tart",
     ["Make an espresso custard tart: whisk espresso into egg custard; bake in pastry shell until set.", "Cool completely; arrange sliced fresh strawberries over the espresso custard.", "Shave aged Parmesan over the top; serve immediately — a bold sweet-bitter-umami combination."]),

    ("coffee","parmesan","tomato",
     "Coffee and tomato share pyrazines and phenylacetaldehyde — Maillard compounds shared through roasting and fermentation — while Parmesan and tomato share furaneol and acetic acid, creating two separate pair-connections with tomato at the center. The triple umami (coffee, Parmesan, tomato glutamates) creates a deeply savory pasta sauce.",
     "Espresso Parmesan Tomato Sauce",
     ["Cook garlic in olive oil; add crushed tomatoes and a small shot of espresso; simmer 20 minutes.", "Off heat stir in grated Parmesan to bind the sauce; season well.", "Toss with pasta; finish with more Parmesan — the espresso adds roasted depth beneath the tomato."]),

    ("coffee","parmesan","truffle",
     "Coffee, Parmesan, and truffle all share dimethyl sulfide — the sulfurous compound spanning roasted coffee, aged dairy, and earthy fungal fermentation — while Parmesan and truffle additionally share phenylacetaldehyde. The double compound overlap makes this a powerfully coherent umami-earthy-bitter combination for luxury risotto.",
     "Truffle Espresso Parmesan Risotto",
     ["Cook arborio risotto with stock; off heat beat in truffle butter, cold Parmesan, and a shot of espresso.", "Add pasta water if needed to achieve a loose, glossy texture.", "Plate; shave fresh truffle generously, finish with more Parmesan and an espresso oil drizzle."]),
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
print(f"Batch 038 done: inserted {len(TRIPLETS)} triplets.")
