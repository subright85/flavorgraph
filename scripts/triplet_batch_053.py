#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("lemon","parmesan","vanilla",
     "Lemon and vanilla create the sour-sweet axis while Parmesan's vanillin from aging bridges them through shared lactonic-sweet compounds — Parmesan contains trace vanillin from fermentation — while lemon's citric brightness cuts Parmesan's butyric fat and lifts vanilla's dense sweetness. The trio creates sophisticated savory-sweet pastry applications.",
     "Lemon Vanilla Parmesan Tart",
     ["Make a Parmesan pastry crust with cold butter, flour, and grated Parmesan; blind bake.", "Fill with a lemon-vanilla custard made from cream, eggs, lemon zest, and vanilla bean.", "Bake until just set; cool and serve with a drizzle of lemon curd and Parmesan shavings."]),

    ("lemon","rose","salmon",
     "Lemon and rose share geraniol — the dominant citrus-floral terpene in both — while rose's 2-phenylethanol and lemon's citric acid both suppress salmon's trimethylamine through different mechanisms. The shared geraniol creates a coherent citrus-floral aromatic register over the fatty fish that is more complete than either ingredient alone.",
     "Rose Lemon Salmon Carpaccio",
     ["Slice sushi-grade salmon paper-thin; arrange on a chilled plate in overlapping circles.", "Dress with rose water, lemon juice, and good olive oil; scatter fleur de sel.", "Garnish with rose petals, lemon zest curls, and a drizzle of rose-lemon vinaigrette."]),

    ("lemon","rose","strawberry",
     "Lemon, rose, and strawberry share geraniol, linalool, and furaneol — a three-way compound overlap covering citrus-floral, herbal-floral, and sweet-caramel registers — creating the most aromatic floral-citrus-sweet summer dessert combination. Each ingredient reinforces the others' dominant aromatic compounds.",
     "Rose Lemon Strawberry Tart",
     ["Make a lemon curd with rose water stirred in; cool completely before using.", "Fill a blind-baked tart shell with the rose-lemon curd; arrange sliced strawberries over.", "Glaze with rose-strawberry gel and finish with rose petals and a curl of lemon zest."]),

    ("lemon","rose","tomato",
     "Lemon and rose share geraniol while tomato and lemon share citric acid and furaneol — two aromatic bridges through lemon — while rose's 2-phenylethanol softens tomato's acidity through floral displacement. The trio creates a Turkish-inspired rose-tomato salad preparation that echoes the flavor of fine gazpacho.",
     "Rose Lemon Tomato Salad",
     ["Slice ripe heirloom tomatoes; arrange on a plate with a drizzle of rose water and olive oil.", "Add lemon juice, lemon zest, and flaky salt; scatter fresh rose petals generously.", "Rest 5 minutes; serve with crusty bread and a final drizzle of floral olive oil."]),

    ("lemon","rose","truffle",
     "Lemon's citric brightness and geraniol provide the lightest possible aromatic lift for the rose-truffle luxury combination — which shares phenylacetaldehyde — while rose's geraniol connects to lemon's geraniol through the shared citrus-floral terpene. The trio creates an aromatic truffle preparation with maximum vertical uplift.",
     "Rose Lemon Truffle Tagliolini",
     ["Cook fresh tagliolini; toss with truffle butter, a splash of rose water, and lemon zest.", "Loosen with pasta water until the sauce is glossy and coats each strand.", "Plate immediately; shave fresh truffle over and finish with a rose petal and lemon curl."]),

    ("lemon","rose","vanilla",
     "Lemon, rose, and vanilla share geraniol and 2-phenylethanol — the citrus-floral and rosy compounds connecting all three — while lemon's citric brightness provides the acid contrast that prevents the rose-vanilla sweet-floral combination from becoming cloying. The trio is Turkish delight and Persian candy in flavor register.",
     "Rose Lemon Vanilla Posset",
     ["Heat cream with sugar, vanilla bean, and rose water until simmering; remove from heat.", "Add lemon juice and zest; stir until just combined and pour into glasses.", "Refrigerate 4 hours until set; serve with rose petals, a vanilla sprig, and lemon zest."]),

    ("lemon","salmon","strawberry",
     "Lemon and strawberry both suppress salmon's trimethylamine — citric acid through pH reduction and furaneol-linalool sweetness through aromatic displacement — while geraniol connects lemon and strawberry through the shared citrus-floral terpene. The trio creates a summer salmon salad where fruit and citrus work as a unified brightener.",
     "Lemon Strawberry Salmon Salad",
     ["Pan-sear salmon until just done; cool to room temperature and flake into pieces.", "Toss arugula with sliced strawberries, lemon juice, and a touch of lemon zest.", "Arrange salmon over the salad, dress with lemon vinaigrette, and garnish with strawberries."]),

    ("lemon","salmon","tomato",
     "Lemon and tomato share citric acid and furaneol while tomato and salmon share dimethyl sulfide and furaneol — double compound bridges through tomato — making tomato the natural connector between lemon's bright citrus and salmon's marine register. The trio drives Mediterranean fish with tomato and lemon preparations.",
     "Lemon Tomato Poached Salmon",
     ["Simmer a shallow broth of crushed tomatoes, lemon juice, garlic, and white wine.", "Poach salmon gently in the tomato-lemon broth for 10 minutes until just opaque.", "Serve in the broth with crusty bread; finish with lemon zest and a drizzle of olive oil."]),

    ("lemon","salmon","truffle",
     "Lemon's citric brightness provides the cleanest possible lift for the salmon-truffle luxury combination — which share dimethyl sulfide — while geraniol bridges citrus and salmon's minor floral compounds. The trio creates a restrained high-end salmon preparation where lemon's acid prevents truffle from overwhelming the fish.",
     "Lemon Truffle Salmon Fillet",
     ["Sear salmon skin-side down in truffle oil until skin is perfectly crisp; flip briefly.", "Make a lemon-truffle beurre blanc by reducing lemon juice with shallots and finishing with truffle butter.", "Serve salmon with the sauce; shave fresh truffle over and finish with a lemon curl."]),

    ("lemon","salmon","vanilla",
     "Lemon and vanilla create the sour-sweet axis while both suppress salmon's trimethylamine — lemon through citric acid and vanilla through sweet-lactonic vanillin — creating a double-suppression with complementary aromatic registers. The trio defines sophisticated French-style poached salmon with sweet wine and citrus.",
     "Lemon Vanilla Salmon en Papillote",
     ["Place salmon on parchment with lemon slices, vanilla bean seeds, and a drizzle of butter.", "Seal the parcel tightly; bake at 400°F for 14 minutes until just cooked through.", "Serve in the parcel; the vanilla-lemon combination has perfumed the salmon delicately."]),

    ("lemon","strawberry","tomato",
     "Lemon, strawberry, and tomato share furaneol — the sweet-caramel compound critical to all three — and citric acid connects lemon and tomato through shared acidity. The triple-furaneol sweet-fruity-caramel register creates a gazpacho or salad where all three taste simultaneously brighter and sweeter together.",
     "Lemon Strawberry Tomato Gazpacho",
     ["Blend ripe tomatoes with fresh strawberries, lemon juice, cucumber, and garlic until smooth.", "Season with sherry vinegar, olive oil, salt, and white pepper; strain for a silky texture.", "Serve chilled in bowls with diced strawberry, lemon zest, and a drizzle of olive oil."]),

    ("lemon","strawberry","truffle",
     "Lemon and strawberry both share phenylacetaldehyde in trace amounts with truffle — rosy-fermented compound appearing in all three through separate biochemical pathways — while lemon's citric brightness provides the lightest possible aromatic uplift for the truffle-strawberry luxury combination. The trio creates a refined spring dessert.",
     "Lemon Strawberry Truffle Dessert",
     ["Macerate sliced strawberries with lemon juice, zest, and a drizzle of truffle honey.", "Arrange over a lemon posset or panna cotta in chilled glasses.", "Shave a tiny amount of fresh truffle over the top; the rosy compound bridges strawberry and truffle."]),

    ("lemon","strawberry","vanilla",
     "Lemon, strawberry, and vanilla share furaneol, geraniol, and linalool — a three-way compound overlap — while lemon's citric brightness provides the acid counterpoint that sharpens strawberry's sweet register and contrasts vanilla's warm-sweet lactonic character. The trio is the most complete lemon-strawberry-vanilla combination possible.",
     "Lemon Strawberry Vanilla Cheesecake",
     ["Make a cream cheese filling with vanilla bean, lemon zest, and lemon juice.", "Pour over a digestive biscuit crust; bake in a water bath until just set.", "Refrigerate overnight; top with fresh strawberries macerated in lemon juice and vanilla sugar."]),

    ("lemon","tomato","truffle",
     "Lemon and tomato share citric acid and furaneol while tomato and truffle share dimethyl sulfide and phenylacetaldehyde — double bridges through tomato — making tomato the natural connector between lemon's bright citrus and truffle's dense earthiness. The trio creates a refined Italian preparation where lemon lifts a heavy truffle-tomato base.",
     "Lemon Truffle Tomato Pasta",
     ["Simmer cherry tomatoes with garlic until bursting and jammy; add truffle butter off heat.", "Toss al dente pasta with the tomato-truffle sauce and pasta water until glossy.", "Finish with a squeeze of lemon, lemon zest, and shaved fresh truffle at the table."]),

    ("lemon","tomato","vanilla",
     "Lemon and tomato share citric acid and furaneol while tomato and vanilla share furaneol at high concentrations — the sweet-caramel compound critical to both ripe tomato and cured vanilla — while lemon's citric brightness amplifies tomato's natural acidity and sharpens the vanilla-furaneol sweetness. The trio creates a sophisticated slow-roasted preparation.",
     "Lemon Vanilla Tomato Confit",
     ["Halve cherry tomatoes; place with a vanilla bean, lemon zest strips, and herbs in a baking dish.", "Cover with olive oil; roast at 250°F for 90 minutes until concentrated and fragrant.", "Serve warm over ricotta with lemon zest; vanilla and lemon amplify the tomato's natural sweetness."]),

    ("lemon","truffle","vanilla",
     "Lemon's citric brightness and geraniol provide the cleanest possible aromatic contrast to the truffle-vanilla luxury combination — which share vanillin — while lemon's acid prevents the warm-sweet and earthy combination from becoming too dense. The trio creates a light, elegant truffle preparation.",
     "Lemon Vanilla Truffle Scrambled Eggs",
     ["Beat eggs with a scrape of vanilla bean, lemon zest, and a pinch of fleur de sel.", "Scramble slowly in truffle butter over very low heat, stirring constantly until creamy.", "Plate; shave fresh truffle generously over and finish with a final squeeze of lemon."]),

    ("mint","oyster","parmesan",
     "Mint and oyster share trace 1,8-cineole — the cooling terpene that appears as a minor compound in oyster's aromatic profile and dominates mint's essential oil — while Parmesan's glutamate and phenylacetaldehyde provide the savory-rosy depth that grounds the cooling-marine combination. The trio creates an unusual refreshing oyster gratin.",
     "Mint Parmesan Baked Oysters",
     ["Mix breadcrumbs with Parmesan, finely chopped fresh mint, garlic, and butter.", "Top shucked oysters in their half-shells with the mint-Parmesan mixture.", "Broil 4 minutes until golden; squeeze lemon over and serve immediately."]),

    ("mint","oyster","rose",
     "Mint and rose share 2-phenylethanol and linalool — the rosy-floral and herbal terpene pair — while oyster's marine phenylacetaldehyde provides the natural rosy-floral connection to rose's dominant compound, and menthol's cooling contrasts the warm-sweet rose register. The trio creates a unique floral-cool oyster preparation.",
     "Rose Mint Oyster Mignonette",
     ["Mix white wine vinegar with rose water, finely minced shallot, and cracked white pepper.", "Stir in finely chopped fresh mint and a pinch of fleur de sel; rest 10 minutes.", "Spoon over freshly shucked raw oysters on crushed ice; garnish with a rose petal and mint."]),

    ("mint","oyster","salmon",
     "Mint's menthol suppresses trimethylamine in both oyster and salmon simultaneously — palate-cleansing cooling displacing marine aromatics from both proteins — while their shared linalool and minor floral compounds create a coherent herbal register over the double-seafood combination. The double-marine-menthol combination works in elaborate seafood preparations.",
     "Mint Oyster Salmon Blinis",
     ["Make small yeast blinis; top each with sliced smoked salmon and one small raw oyster.", "Add a dollop of mint crème fraîche and a tiny mint leaf garnish.", "Serve immediately chilled; mint's menthol bridges and cleanses both seafood proteins."]),

    ("mint","oyster","strawberry",
     "Mint and strawberry share linalool and furaneol — the herbal-floral terpene and sweet-caramel compound — while menthol amplifies strawberry's perceived sweetness and brightness, and oyster's marine brine creates a dramatic salt-sweet-cool contrast that the linalool connection helps bridge. The avant-garde combination works as a mignonette.",
     "Strawberry Mint Oyster Granita",
     ["Blend fresh strawberries with mint syrup and lemon juice; freeze into a granita, scraping hourly.", "Shuck oysters into their half-shells and arrange on crushed ice.", "Top each oyster with a spoonful of strawberry-mint granita; serve immediately."]),
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
print(f"Batch 053 done: inserted {len(TRIPLETS)} triplets.")
