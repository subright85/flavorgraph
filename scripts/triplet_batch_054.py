#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("mint","oyster","tomato",
     "Mint and tomato share hexanal and furaneol — the green aldehyde and sweet-caramel compounds that give both their garden freshness — while oyster's marine dimethyl sulfide adds a briny depth that amplifies the tomato-mint combination in the same way fish sauce amplifies a tomato base. Menthol's cooling lifts the entire preparation.",
     "Mint Tomato Oyster Stew",
     ["Sauté garlic in olive oil; add cherry tomatoes and cook until jammy, about 10 minutes.", "Add shucked oysters with their liquor; poach 2 minutes until edges just curl.", "Stir in chopped fresh mint off heat; serve with crusty bread and a mint oil drizzle."]),

    ("mint","oyster","truffle",
     "Mint and truffle share anisaldehyde in trace amounts — the anise-adjacent aromatic that both herbs and earthy fungi produce — while oyster's marine phenylacetaldehyde connects to truffle's own phenylacetaldehyde, and menthol's cooling provides the highest-contrast aromatic against truffle's dense earthiness. The trio is bold luxury.",
     "Truffle Mint Oyster Custard",
     ["Make a savory custard with cream, eggs, truffle oil, and a small amount of fresh mint; strain.", "Nest one shucked oyster in each ramekin; pour custard over and steam gently until just set.", "Serve warm with shaved fresh truffle over each cup and a small mint leaf garnish."]),

    ("mint","oyster","vanilla",
     "Mint's menthol cooling and vanilla's warm-sweet vanillin create the greatest hot-cold aromatic contrast available — cool-herb versus warm-sweet — while oyster's marine brine adds the third dimension of salty contrast, and vanilla's furaneol suppresses oyster's marine trimethylamine. The trio creates a sophisticated avant-garde oyster preparation.",
     "Vanilla Mint Oyster Beurre Blanc",
     ["Reduce white wine and shallots; whisk cold butter piece by piece until emulsified.", "Add vanilla bean seeds and very finely chopped fresh mint; strain and season.", "Spoon over warm broiled oysters in their shells; cool-sweet-marine in one bite."]),

    ("mint","parmesan","rose",
     "Mint and rose share 2-phenylethanol and linalool — the rosy-floral and herbal terpene pair — while Parmesan's 2-phenylethanol from fermentation reinforces rose's dominant compound and creates a triple-2-phenylethanol concentration above the butyric acid savory base. The trio creates a refined aperitivo preparation.",
     "Rose Mint Parmesan Honey Crostini",
     ["Toast thin sourdough slices until crisp and golden.", "Spread a mixture of whipped Parmesan, rose water, and fresh mint over each piece.", "Top with a drizzle of floral honey and a rose petal; serve immediately."]),

    ("mint","parmesan","salmon",
     "Mint's menthol suppresses salmon's trimethylamine while Parmesan's butyric acid and umami amplify salmon's fatty protein register — the two ingredients working on opposite aspects of salmon simultaneously — while their shared 1,8-cineole creates a subtle cooling-dairy aromatic connection. The trio creates a refined salmon preparation.",
     "Mint Parmesan Crusted Salmon",
     ["Mix breadcrumbs with finely grated Parmesan, chopped fresh mint, and lemon zest.", "Press the crust firmly onto salmon fillets; bake at 400°F for 12 minutes until golden.", "Serve with a mint-lemon beurre blanc and a grating of fresh Parmesan over the top."]),

    ("mint","parmesan","strawberry",
     "Mint and strawberry share linalool and furaneol — the herbal terpene and sweet-caramel compound — while Parmesan's furaneol from aging creates the savory-sweet furaneol bridge to strawberry, and menthol amplifies strawberry's perceived sweetness and brightness. The trio echoes Italian strawberries with aged cheese and fresh herbs.",
     "Mint Strawberry Parmesan Salad",
     ["Slice ripe strawberries; toss with torn fresh mint, aged balsamic, and a pinch of sugar.", "Arrange on a plate; shave Parmesan generously over with a vegetable peeler.", "Finish with cracked pepper, flaky salt, and a drizzle of mint oil."]),

    ("mint","parmesan","tomato",
     "Mint and tomato share hexanal and furaneol — the green aldehyde and sweet-caramel compounds that define garden freshness — while Parmesan's glutamate amplifies tomato's natural umami, and menthol's cooling provides the herbal counterpoint. The trio defines the flavor of a refined Italian caprese variation with fresh herbs.",
     "Mint Parmesan Tomato Bruschetta",
     ["Dice ripe tomatoes; toss with chopped fresh mint, olive oil, salt, and a splash of balsamic.", "Toast thick sourdough; top with a spread of whipped Parmesan.", "Spoon the mint-tomato mixture over, finish with Parmesan shavings and fresh mint."]),

    ("mint","parmesan","truffle",
     "Mint and truffle share trace anisaldehyde while Parmesan and truffle share phenylacetaldehyde and dimethyl sulfide — the fermented-rosy and sulfurous compound pair — while menthol's cooling provides the most volatile aromatic contrast to the dense truffle-cheese umami. The trio creates an aromatic luxury pasta.",
     "Mint Truffle Parmesan Pasta",
     ["Cook fresh pasta al dente; toss with truffle butter and cold Parmesan off heat.", "Add pasta water for a glossy sauce; fold in finely chopped fresh mint at the very last second.", "Plate immediately, shave truffle generously over, and serve before the mint wilts."]),

    ("mint","parmesan","vanilla",
     "Mint's menthol and vanilla's vanillin create the cool-warm aromatic axis — the same contrast as mint-chocolate — while Parmesan's vanillin from aging provides a savory-sweet bridge between the two extremes. The trio creates a sophisticated savory-sweet gelato or frozen dessert with cheese.",
     "Mint Vanilla Parmesan Semifreddo",
     ["Make a vanilla custard with a pinch of dried Parmesan stirred in for savory depth; cool.", "Fold in whipped cream and chopped fresh mint; pour into a loaf mold.", "Freeze 4 hours; unmold and serve sliced with a mint oil drizzle and Parmesan shavings."]),

    ("mint","rose","salmon",
     "Mint and rose share 2-phenylethanol and linalool — the rosy-floral and herbal terpene pair — while both simultaneously suppress salmon's trimethylamine through floral and cool aromatic displacement. The triple-mechanism suppression (rose's geraniol + mint's menthol + shared linalool) creates the cleanest possible aromatic salmon.",
     "Rose Mint Salmon Carpaccio",
     ["Slice sushi-grade salmon paper-thin; arrange on a chilled plate.", "Dress with rose water, a few drops of mint oil, and lemon juice; scatter fleur de sel.", "Garnish with rose petals, fresh mint leaves, and a drizzle of rose-mint vinaigrette."]),

    ("mint","rose","strawberry",
     "Mint, rose, and strawberry share 2-phenylethanol, linalool, and furaneol — a three-way compound overlap — with menthol's cooling amplifying strawberry's perceived sweetness and brightness while rose's geraniol amplifies the floral register. Together the trio creates the most aromatic summer fruit-herb combination possible.",
     "Rose Mint Strawberry Sorbet",
     ["Blend fresh strawberries with rose water, mint, and lemon juice; strain well.", "Make a simple syrup; combine with the strained strawberry mixture and churn in an ice cream maker.", "Serve scooped with a fresh mint leaf, rose petals, and a drizzle of rose water."]),

    ("mint","rose","tomato",
     "Mint and tomato share hexanal and furaneol while rose and tomato share furaneol and geraniol — two compound bridges through tomato — making tomato the natural connector between mint's cool herbal register and rose's warm floral. Together the trio creates a unique Middle Eastern-inspired tomato salad.",
     "Rose Mint Tomato Salad",
     ["Slice ripe tomatoes and arrange on a serving plate; scatter fresh rose petals and mint leaves.", "Dress with a rose water-mint vinaigrette of white wine vinegar, rose water, and olive oil.", "Season with flaky salt and white pepper; let rest 5 minutes before serving."]),

    ("mint","rose","truffle",
     "Mint and rose share 2-phenylethanol and linalool while rose and truffle share phenylacetaldehyde — the rosy-fermented compound — and mint's menthol provides the most volatile aromatic contrast to truffle's dense earthiness. The trio creates a perfumed yet grounded luxury preparation.",
     "Rose Mint Truffle Butter",
     ["Beat softened butter with rose water, truffle paste, finely chopped fresh mint, and flaky salt.", "Mix until completely smooth; taste and adjust seasoning carefully.", "Roll into a log, refrigerate until firm, and slice over seared scallops or warm brioche."]),

    ("mint","rose","vanilla",
     "Mint, rose, and vanilla share linalool and 2-phenylethanol — the herbal-floral and rosy terpene pair present in all three — while menthol's cooling contrasts vanilla's warm-sweet register and rose's geraniol amplifies the floral register above vanilla's lactonic sweetness. The trio creates an aromatic floral-cool dessert register.",
     "Rose Mint Vanilla Ice Cream",
     ["Infuse cream with fresh mint, rose water, and split vanilla bean; steep 20 minutes, strain.", "Churn into a rich custard ice cream; freeze until firm.", "Serve scooped with rose petals, a fresh mint leaf, and a drizzle of rose water."]),

    ("mint","salmon","strawberry",
     "Mint's menthol suppresses salmon's trimethylamine while strawberry's furaneol and linalool provide sweet-floral aromatic contrast to the fatty fish — the two working from opposite aromatic directions to clean and brighten the salmon register — while their shared linalool creates a coherent herbal-sweet bridge. The trio creates a summer salmon salad.",
     "Mint Strawberry Salmon Salad",
     ["Pan-sear salmon; cool slightly and flake into large pieces over mixed greens.", "Toss with halved strawberries, fresh mint, and a strawberry-mint vinaigrette.", "Arrange salmon over the salad with a mint oil drizzle and crumbled feta cheese."]),

    ("mint","salmon","tomato",
     "Mint and tomato share hexanal and furaneol while tomato and salmon share dimethyl sulfide and furaneol — two compound bridges through tomato — making tomato the natural connector between mint's cool herbal register and salmon's marine profile. The trio drives Mediterranean herb-fish preparations.",
     "Mint Tomato Salmon Salsa",
     ["Make a salsa from diced tomatoes, chopped fresh mint, garlic, lemon, and olive oil.", "Grill salmon fillets over high heat until charred and just cooked through.", "Serve immediately topped with the mint-tomato salsa and extra mint leaves."]),

    ("mint","salmon","truffle",
     "Mint's menthol provides the highest-contrast aromatic against both salmon's marine dimethyl sulfide and truffle's earthy dimethyl sulfide — all sharing the same sulfurous compound family — while their shared linalool creates the fragile terpene bridge between cooling herb and earthy fungus over fatty fish.",
     "Truffle Mint Salmon",
     ["Sear salmon in truffle butter; finish with a generous drizzle of truffle oil.", "Make a mint-truffle gremolata from chopped mint, truffle, lemon zest, and garlic.", "Plate salmon with the gremolata scattered over and shaved truffle at the table."]),

    ("mint","salmon","vanilla",
     "Mint's menthol and vanilla's vanillin create the cool-warm aromatic axis that together suppress salmon's trimethylamine from both temperature directions — menthol through cooling displacement and vanillin through sweet-lactonic displacement. The double-suppression creates a beautifully clean, fragrant salmon preparation.",
     "Vanilla Mint Poached Salmon",
     ["Make a court bouillon with vanilla bean, fresh mint bundles, white wine, and aromatics.", "Poach salmon at barely a simmer for 10 minutes until just opaque.", "Serve with a vanilla-mint beurre blanc; the cool-sweet aromatic combination is subtle and precise."]),

    ("mint","strawberry","tomato",
     "Mint, strawberry, and tomato share furaneol and hexanal — the sweet-caramel and green aldehyde compounds creating the garden-freshness register — while menthol's cooling amplifies the perceived brightness of both strawberry and tomato. Together the trio creates a summer salad of unusual freshness and aromatic completeness.",
     "Mint Strawberry Tomato Summer Salad",
     ["Slice ripe tomatoes and strawberries; arrange together on a wide plate.", "Scatter large amounts of fresh mint over; dress with a mint-balsamic vinaigrette.", "Season with flaky salt and white pepper; rest 5 minutes before serving."]),

    ("mint","strawberry","truffle",
     "Mint and strawberry share linalool and furaneol while strawberry and truffle share phenylacetaldehyde — the rosy-fermented compound — while menthol's cooling provides the most volatile aromatic contrast to truffle's dense earthiness, and strawberry's sweetness bridges the cool herb and the earthy fungus. The unusual trio works as a luxury dessert.",
     "Truffle Strawberry Mint Dessert",
     ["Macerate sliced strawberries with a drizzle of truffle honey and torn fresh mint leaves.", "Arrange over a mint-scented cream or vanilla ice cream in chilled bowls.", "Shave a very small amount of fresh truffle over the top; the rosy compound bridges all three."]),
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
print(f"Batch 054 done: inserted {len(TRIPLETS)} triplets.")
