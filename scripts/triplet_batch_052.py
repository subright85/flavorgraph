#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("lemon","mint","oyster",
     "Lemon and mint both suppress oyster's trimethylamine through complementary mechanisms — citric acid reduces amine volatility while menthol's cooling displaces marine aromatics — while their shared linalool creates a coherent herbal-citrus register over the briny shellfish. The double-suppression creates the cleanest possible raw oyster preparation.",
     "Lemon Mint Oyster Shooter",
     ["Juice cucumber with lemon, fresh mint, and a pinch of salt; strain until crystal clear.", "Season with a touch of white pepper; keep very cold until service.", "Pour a small amount over each freshly shucked oyster; serve immediately over ice."]),

    ("lemon","mint","parmesan",
     "Lemon and Parmesan share acidity — citric acid cutting through Parmesan's butyric acid fat — while mint's menthol and 1,8-cineole provide the cooling herbal contrast that prevents the bright lemon-cheese combination from becoming sharp. The trio refines the classic Italian lemon-Parmesan pasta brightening technique.",
     "Lemon Mint Parmesan Pasta",
     ["Cook pasta al dente; reserve pasta water before draining well.", "Toss off heat with lemon juice, lemon zest, cold Parmesan, and finely chopped fresh mint.", "Loosen with pasta water to a glossy consistency; finish with more Parmesan and mint leaves."]),

    ("lemon","mint","rose",
     "Lemon and rose share geraniol — the citrus-floral terpene present in both lemon peel and rose petals — while mint's linalool and 2-phenylethanol reinforce rose's floral register and menthol's cooling provides contrast to the warm-sweet rose aromatic. Together the trio creates a Persian-inspired cold drink or dessert.",
     "Rose Lemon Mint Granita",
     ["Make a syrup from rose water, fresh mint, and lemon juice; chill well.", "Pour into a shallow freezer dish and freeze, scraping with a fork every 30 minutes.", "Serve in chilled glasses with a fresh mint sprig and a twist of lemon peel."]),

    ("lemon","mint","salmon",
     "Lemon and mint both suppress salmon's trimethylamine — citric acid through pH-driven amine reduction, menthol through olfactory displacement — while their shared linalool creates a coherent herbal-citrus register over the fatty fish. The double-suppression creates an exceptionally clean and fresh salmon preparation.",
     "Lemon Mint Salmon Ceviche",
     ["Dice sushi-grade salmon; cure in fresh lemon juice with salt for 5 minutes.", "Drain, toss with finely chopped fresh mint, cucumber, red onion, and a drizzle of olive oil.", "Season with flaky salt; serve immediately chilled with mint-lemon oil drizzled over."]),

    ("lemon","mint","strawberry",
     "Lemon and strawberry share furaneol and geraniol — sweet-caramel and citrus-floral compounds — while mint's menthol and linalool amplify the perceived brightness of both strawberry and lemon through palate-cleansing cooling. Menthol makes strawberry taste more intense and acidic register more vibrant. The trio is summer dessert at its sharpest.",
     "Lemon Mint Strawberry Pavlova",
     ["Bake a large meringue until crisp outside and marshmallow inside; cool completely.", "Whip cream with a touch of lemon zest and vanilla; pile onto the meringue.", "Top with sliced strawberries macerated in lemon juice and fresh mint leaves."]),

    ("lemon","mint","tomato",
     "Lemon and tomato share citric acid and furaneol — tart and sweet-caramel compounds — while mint's menthol and linalool provide the cooling herbal contrast that lifts the tomato's Mediterranean sweetness into a brighter, more vertical register. The trio is the flavor of Middle Eastern tabbouleh where all three ingredients are essential.",
     "Lemon Mint Tomato Tabbouleh",
     ["Soak bulgur in hot water; drain and cool completely before using.", "Fold in masses of chopped fresh mint, diced tomatoes, cucumber, and parsley.", "Dress with generous lemon juice, olive oil, salt, and cracked pepper; rest 15 minutes."]),

    ("lemon","mint","truffle",
     "Truffle's phenylacetaldehyde and dense earthiness meet lemon's citric brightness and mint's menthol in a luxury-aromatic contrast — the lightest acid and the coolest herb against the heaviest mushroom — while their shared linalool provides the fragile terpene connection. The trio creates a light, perfumed truffle pasta.",
     "Lemon Mint Truffle Tagliolini",
     ["Cook fresh tagliolini al dente; toss with truffle butter, lemon zest, and pasta water.", "Add finely chopped fresh mint off heat; toss quickly to just wilt the herb.", "Plate immediately; shave generous fresh truffle over and finish with a lemon curl."]),

    ("lemon","mint","vanilla",
     "Lemon and vanilla represent the cleanest sweet-sour contrast — citric acid against vanillin sweetness — while mint's menthol provides the coolest possible aromatic bridge between lemon's sharp brightness and vanilla's warm-sweet register. The trio is lemon-mint-vanilla ice cream, sorbet, and summer tart territory.",
     "Lemon Mint Vanilla Sorbet",
     ["Make a lemon syrup with sugar, water, and lemon zest; cool completely.", "Add lemon juice, vanilla bean seeds, and finely chopped fresh mint; churn in an ice cream maker.", "Freeze until firm; serve scooped with a fresh mint leaf and a small lemon curl."]),

    ("lemon","oyster","parmesan",
     "Lemon and oyster are the classic pairing — citric acid suppresses trimethylamine — while Parmesan's glutamate and phenylacetaldehyde add savory-rosy depth that amplifies oyster's own marine umami, and lemon's geraniol bridges citrus and dairy through their shared floral register. The trio creates a refined baked oyster preparation.",
     "Lemon Parmesan Baked Oysters",
     ["Mix breadcrumbs with finely grated Parmesan, lemon zest, garlic, and butter.", "Top shucked oysters in their half-shells with the breadcrumb mixture.", "Broil 4 minutes until golden; squeeze lemon over immediately before serving."]),

    ("lemon","oyster","rose",
     "Lemon and rose share geraniol — the citrus-floral terpene present in both — while oyster's marine phenylacetaldehyde provides the natural rosy-floral connection to rose's dominant compound. Lemon's citric acid cuts oyster's marine fat while rose's geraniol amplifies the shared floral register. The trio creates a delicate floral oyster preparation.",
     "Rose Lemon Oyster on the Half Shell",
     ["Mix white wine vinegar with rose water, lemon juice, minced shallot, and cracked white pepper.", "Add lemon zest and a touch of rose petal jam; rest 10 minutes.", "Spoon over freshly shucked raw oysters; garnish with rose petals and lemon zest curls."]),

    ("lemon","oyster","salmon",
     "Lemon suppresses trimethylamine in both oyster and salmon — through pH-driven amine volatility reduction — making it the universal double-seafood acid brightener, while geraniol provides the floral-citrus aromatic that connects both marine proteins through their minor floral compound families. The trio creates a classic raw seafood platter.",
     "Lemon Oyster and Salmon Tartare Duo",
     ["Dice sushi-grade salmon finely; season with lemon juice, lemon zest, and flaky salt.", "Shuck oysters and arrange alongside the salmon tartare on a chilled platter.", "Serve with lemon wedges, crème fraîche, and toasted blini; the lemon bridges both seafoods."]),

    ("lemon","oyster","strawberry",
     "Lemon and strawberry share furaneol and geraniol — sweet-caramel and citrus-floral compounds — while oyster's marine brine creates a dramatic sweet-salty contrast with strawberry's fruity register, and lemon's citric acid provides the acid bridge that connects fruit and shellfish. The trio is a bold avant-garde raw bar concept.",
     "Strawberry Lemon Oyster Mignonette",
     ["Blend muddled strawberry with white wine vinegar, lemon juice, and minced shallot.", "Season with cracked white pepper and lemon zest; strain through a fine sieve.", "Spoon over freshly shucked oysters; serve on crushed ice with lemon wedges."]),

    ("lemon","oyster","tomato",
     "Lemon and tomato share citric acid and furaneol while tomato and oyster share acetic acid and dimethyl sulfide — two separate compound bridges — making tomato the natural connector between lemon's bright citrus and oyster's briny marine register. The trio drives Italian seafood preparations like oysters alla pizzaiola.",
     "Lemon Tomato Oyster Stew",
     ["Sauté garlic in olive oil; add cherry tomatoes and lemon zest; cook 10 minutes until jammy.", "Add shucked oysters with their liquor; poach gently 2 minutes until edges just curl.", "Finish with a squeeze of fresh lemon and serve immediately with crusty bread."]),

    ("lemon","oyster","truffle",
     "Lemon's citric brightness and geraniol provide the lightest possible aromatic contrast to the luxury double-umami of oyster and truffle — which share phenylacetaldehyde and dimethyl sulfide — creating a trio where lemon lifts rather than competes with the intense savory register. The preparation is haute cuisine brevity.",
     "Lemon Truffle Oyster Tartare",
     ["Finely chop oysters; mix with truffle oil, lemon juice, lemon zest, and fleur de sel.", "Arrange in chilled oyster shells; shave fresh truffle over generously.", "Serve immediately with champagne; lemon's brightness elevates the truffle-oyster combination."]),

    ("lemon","oyster","vanilla",
     "Lemon and vanilla form the sour-sweet axis that vanilla-lemon curd exploits — citric against vanillin — while oyster's marine brine adds the saltiest possible contrast to both, and vanilla's furaneol provides a sweet-caramel accent that echoes salted caramel logic applied to raw shellfish. The trio is unconventional but precise.",
     "Vanilla Lemon Oyster Beurre Blanc",
     ["Reduce white wine with shallots and lemon juice; whisk cold butter piece by piece until emulsified.", "Add vanilla bean seeds and a touch of lemon zest; strain and season.", "Spoon over warm broiled oysters; the vanilla-lemon beurre blanc is deeply elegant."]),

    ("lemon","parmesan","rose",
     "Lemon and rose share geraniol — the citrus-floral terpene in both lemon peel and rose petals — while Parmesan's 2-phenylethanol from fermentation connects to rose's dominant compound, and lemon's citric brightness cuts Parmesan's butyric fat. The trio creates a refined floral-citrus-cheese combination for aperitivo boards.",
     "Rose Lemon Parmesan Honey Board",
     ["Shave aged Parmesan into irregular pieces; arrange on a board with rose petals.", "Mix lemon zest into floral honey; drizzle over the Parmesan.", "Serve with crackers and thin lemon slices; the rose and lemon lift the Parmesan's umami."]),

    ("lemon","parmesan","salmon",
     "Lemon and Parmesan work together on salmon through complementary mechanisms — citric acid suppresses trimethylamine while Parmesan's butyric fat amplifies salmon's fatty acids through dairy-protein binding — while geraniol bridges the citrus-marine-cheese registers through shared floral aromatic compounds. The trio is Italian salmon pasta territory.",
     "Lemon Parmesan Salmon Pasta",
     ["Cook salmon until just done; flake into large pieces over pasta.", "Toss pasta with lemon juice, lemon zest, cold Parmesan, and pasta water until glossy.", "Fold salmon in gently; finish with more Parmesan, lemon zest, and cracked pepper."]),

    ("lemon","parmesan","strawberry",
     "Lemon and strawberry share furaneol and geraniol — sweet-caramel and citrus-floral compounds — while Parmesan's furaneol from aging and butyric acid create a savory-sweet anchor, and lemon's citric brightness amplifies strawberry's fruit register. The Italian tradition of strawberries with aged cheese and the citrus-fruit connection combine.",
     "Lemon Strawberry Parmesan Salad",
     ["Slice ripe strawberries; toss with lemon juice and a pinch of sugar; macerate 10 minutes.", "Arrange over arugula; shave Parmesan generously with a vegetable peeler.", "Dress with lemon vinaigrette and cracked pepper; serve immediately."]),

    ("lemon","parmesan","tomato",
     "Lemon and tomato share citric acid and furaneol while Parmesan and tomato share furaneol and acetic acid — double compound bridges through tomato — making tomato the natural connector in this Italian flavor trio. The combination is the foundation of every bright Italian pasta preparation with lemon and cheese.",
     "Lemon Parmesan Tomato Soup",
     ["Roast tomatoes with garlic and olive oil; blend smooth with stock and simmer 10 minutes.", "Finish with lemon juice, lemon zest, and a shower of freshly grated Parmesan.", "Serve with more Parmesan, a drizzle of good olive oil, and torn basil."]),

    ("lemon","parmesan","truffle",
     "Lemon's citric brightness provides the cleanest possible aromatic lift for the dense luxury double-umami of Parmesan and truffle — which share phenylacetaldehyde and dimethyl sulfide — while geraniol bridges citrus and fermented dairy through their shared floral register. The trio is the flavor of high-end Italian truffle pasta with lemon finish.",
     "Lemon Truffle Parmesan Risotto",
     ["Cook arborio risotto until creamy; off heat stir in cold Parmesan and truffle butter.", "Add lemon juice and zest to lift; loosen with pasta water for a glossy flow.", "Plate; shave fresh truffle over generously and finish with a curl of lemon peel."]),
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
print(f"Batch 052 done: inserted {len(TRIPLETS)} triplets.")
