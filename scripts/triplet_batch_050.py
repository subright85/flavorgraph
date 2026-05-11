#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("lavender","lemon","strawberry",
     "Lavender and strawberry share linalool and furaneol — floral terpene and sweet-caramel compounds — while lemon's citric brightness and geraniol amplify strawberry's acidic fruit register and sharpen lavender's floral softness into a clean three-way aromatic. The trio defines Provençal summer dessert flavor.",
     "Lavender Lemon Strawberry Tart",
     ["Make a lemon-lavender pastry cream by infusing cream with lavender and lemon zest; strain and cook.", "Fill a blind-baked tart shell; arrange fresh strawberries in a geometric pattern over the cream.", "Glaze with a lavender-strawberry gel and serve chilled with a few dried lavender flowers."]),

    ("lavender","lemon","tomato",
     "Lavender and tomato create a Provençal pairing where lavender's linalool contrasts with tomato's furaneol sweetness — the principle of Niçoise cooking — while lemon's citric brightness and geraniol provide the acid bridge that sharpens both the tomato and the lavender into a clean, aromatic Mediterranean preparation.",
     "Lavender Lemon Roasted Tomatoes",
     ["Halve cherry tomatoes, arrange cut-side up with lavender sprigs and lemon zest.", "Drizzle with olive oil, season with salt, and roast at 300°F for 90 minutes until jammy.", "Serve warm or at room temperature over ricotta toast with extra lemon zest and lavender."]),

    ("lavender","lemon","truffle",
     "Lavender and truffle share anisaldehyde — the anise-adjacent aromatic compound — while lemon's citric brightness and geraniol provide the lightest possible aromatic contrast to truffle's intense earthiness, and lavender's linalool bridges the floral-earthy gap. The trio creates an unusual light-luxury preparation.",
     "Lavender Lemon Truffle Risotto",
     ["Cook arborio risotto until creamy; off heat stir in truffle butter and lemon zest.", "Add a pinch of dried lavender, stir quickly, and loosen with pasta water for a glossy finish.", "Plate, shave fresh truffle over, and finish with a thin curl of lemon peel and lavender flowers."]),

    ("lavender","lemon","vanilla",
     "Lavender and vanilla share linalool and linalyl acetate — floral terpene compounds that both produce dominantly — while lemon's citric brightness and geraniol provide the acid contrast that sharpens the sweet-floral combination. The trio creates an elegant floral-citrus dessert register that is more sophisticated than any two-ingredient pairing alone.",
     "Lavender Lemon Vanilla Crème Brûlée",
     ["Infuse cream with split vanilla bean, dried lavender, and lemon zest; steep 30 minutes, strain.", "Whisk into egg yolks with sugar, strain again, pour into ramekins, and bake in a water bath.", "Refrigerate until set; caramelize sugar topping just before serving with a lavender sprig."]),

    ("lavender","mint","oyster",
     "Lavender and mint share linalool and 1,8-cineole — floral and cooling terpene compounds that both produce — while their combined volatile intensity provides the strongest possible aromatic counterpoint to oyster's marine dimethyl sulfide. The unusual floral-cool-brine combination creates a highly perfumed Provençal oyster preparation.",
     "Lavender Mint Oyster Granita",
     ["Make a granita from lavender-mint syrup with lemon juice and sea salt; freeze and scrape.", "Shuck oysters and arrange on crushed ice in their half-shells.", "Top each oyster with a small spoonful of lavender-mint granita; serve immediately."]),

    ("lavender","mint","parmesan",
     "Lavender and mint share linalool and 1,8-cineole — the herbal terpene compounds both produce — while Parmesan's butyric acid and glutamate umami provide the rich savory anchor that grounds the floral-cool aromatic combination into something edible rather than perfumed. The trio creates an unusual herb-cheese shortbread or savory cracker.",
     "Lavender Mint Parmesan Crackers",
     ["Blend cold butter with grated Parmesan, flour, dried lavender, and finely chopped fresh mint.", "Roll thin, cut into shapes, and refrigerate 20 minutes before baking.", "Bake at 350°F until just golden; serve with honey and a glass of sparkling wine."]),

    ("lavender","mint","rose",
     "Lavender, mint, and rose share 2-phenylethanol and linalool — the rosy-floral and herbal terpenes that all three produce — creating the most concentrated floral-herbal terpene combination in the culinary set, while menthol's cooling adds a refreshing counterpoint to the warm-sweet rose-lavender register. The trio defines Middle Eastern and Persian herb drinks.",
     "Rose Lavender Mint Sherbet",
     ["Make a triple-herb syrup from rose water, lavender, and fresh mint steeped in hot sugar water.", "Strain and combine with cold water, lemon juice, and a pinch of salt for balance.", "Serve over crushed ice with fresh mint, rose petals, and a sprig of dried lavender."]),

    ("lavender","mint","salmon",
     "Lavender and mint both suppress salmon's trimethylamine through terpene displacement — lavender via linalool and linalyl acetate, mint via menthol — creating a double-aromatic suppression of marine notes while their shared linalool builds a coherent floral-cool herbal register over the fatty fish. The strongest possible aromatic salmon preparation.",
     "Lavender Mint Salmon en Papillote",
     ["Place salmon on parchment with lavender sprigs, fresh mint, lemon, and olive oil.", "Fold into a sealed parcel; bake at 400°F for 14 minutes until salmon is just cooked.", "Open at the table; the aromatic steam of lavender and mint perfumes the entire plate."]),

    ("lavender","mint","strawberry",
     "Lavender and strawberry share linalool and furaneol while mint and strawberry share linalool and the cool-sweet contrast — three-way linalool concentration plus menthol's amplification of perceived strawberry sweetness — creating a trifecta where strawberry tastes simultaneously richer, cooler, and more floral than any solo preparation.",
     "Lavender Mint Strawberry Sorbet",
     ["Blend fresh strawberries with lavender-mint syrup and lemon juice until smooth; strain.", "Churn in an ice cream maker; finish with finely chopped fresh mint folded in.", "Freeze until firm; serve scooped with fresh mint, rose petals, and a dried lavender sprig."]),

    ("lavender","mint","tomato",
     "Lavender and tomato form a Provençal pairing — lavender's linalool against tomato's furaneol sweetness — while mint's menthol and linalool amplify lavender's cooling-herbal register and provide a refreshing contrast to tomato's warm-sweet umami. The trio defines Niçoise summer cooking at its most aromatic.",
     "Lavender Mint Tomato Bruschetta",
     ["Dice ripe tomatoes; toss with a pinch of dried lavender, chopped fresh mint, and olive oil.", "Let rest 15 minutes; meanwhile toast thick sourdough slices until crisp and golden.", "Spoon tomato mixture over toast with flaky salt and a few whole mint leaves on top."]),

    ("lavender","mint","truffle",
     "Lavender and truffle share anisaldehyde — the anise-adjacent compound — while mint's menthol provides the most volatile aromatic contrast to truffle's dense earthiness, and lavender's linalool bridges the floral-earthy gap. The trio creates an unusual high-aromatic luxury preparation where truffle's richness is lifted rather than buried.",
     "Lavender Mint Truffle Pasta",
     ["Cook fresh pasta al dente; toss with truffle butter and a splash of pasta water.", "Add a pinch of dried lavender and finely chopped fresh mint off heat; toss quickly.", "Plate immediately, shave truffle generously over, and finish with a mint leaf and lavender flower."]),

    ("lavender","mint","vanilla",
     "Lavender and vanilla share linalool and linalyl acetate — the dominant floral terpenes in both — while mint's menthol provides the coolest possible contrast to vanilla's warm-sweet register, and their shared linalool creates a coherent floral-cool-sweet trio. The combination is sophisticated ice cream and cold dessert territory.",
     "Lavender Mint Vanilla Ice Cream",
     ["Infuse cream with split vanilla bean, dried lavender, and a large bunch of fresh mint; strain.", "Churn into a rich custard ice cream base; freeze until firm.", "Serve scooped with a fresh mint leaf, a dried lavender flower, and a drizzle of honey."]),

    ("lavender","oyster","parmesan",
     "Lavender's linalool and linalyl acetate provide a floral counterpoint to the double-umami combination of oyster's marine succinate and Parmesan's glutamate-inosinate — floral against rich savory — creating an unusual but precise flavor encounter where lavender's perfume lifts the intense umami base into a more aromatic register.",
     "Lavender Parmesan Baked Oysters",
     ["Mix breadcrumbs with grated Parmesan, a pinch of dried lavender, garlic, and butter.", "Top shucked oysters in their half-shells with the lavender-Parmesan mixture.", "Broil 4 minutes until golden and bubbling; serve with lemon and dried lavender."]),

    ("lavender","oyster","rose",
     "Lavender and rose share 2-phenylethanol, linalool, and geraniol — the full floral terpene overlap between two flowers — while oyster's marine phenylacetaldehyde provides the natural floral connection to the flower-flower aromatic pair. The trio creates the most perfumed oyster preparation possible.",
     "Rose Lavender Oyster on the Half Shell",
     ["Mix rose water with white wine vinegar, dried lavender, finely minced shallot, and cracked pepper.", "Rest 15 minutes for the lavender to infuse fully into the mignonette.", "Spoon over freshly shucked oysters on crushed ice; garnish with a rose petal and lavender flower."]),

    ("lavender","oyster","salmon",
     "Lavender's linalool and lemon's geraniol suppress both oyster's and salmon's trimethylamine — floral aromatic displacement working simultaneously on two marine proteins — while their shared linalool creates a coherent aromatic base above the marine register. The trio creates a Provençal double-seafood preparation.",
     "Lavender Salmon and Oyster Tartare",
     ["Finely dice sushi-grade salmon; season with lavender oil, shallot, lemon, and sea salt.", "Arrange on chilled plates with two fresh oysters on the half shell alongside.", "Garnish with lavender flowers and microgreens; the lavender bridges salmon and oyster."]),

    ("lavender","oyster","strawberry",
     "Lavender and strawberry share linalool and furaneol — floral terpene and sweet-caramel compounds — while oyster's marine dimethyl sulfide creates a sharp brine-sweet-floral contrast that the linalool connection between lavender and strawberry helps bridge. The trio creates a provocative and precise avant-garde oyster preparation.",
     "Strawberry Lavender Oyster Granita",
     ["Blend fresh strawberries with lavender syrup and lemon juice; freeze into a granita, scraping hourly.", "Shuck oysters and arrange in their shells on crushed ice.", "Top each oyster with strawberry-lavender granita; serve immediately for maximum aromatic contrast."]),

    ("lavender","oyster","tomato",
     "Lavender and tomato form the Provençal pairing where floral linalool contrasts with tomato's furaneol sweetness — the principle of Niçoise cooking — while oyster's marine dimethyl sulfide adds a briny depth that amplifies the tomato-lavender combination in the same way fish sauce amplifies tomato-based preparations.",
     "Lavender Tomato Oyster Stew",
     ["Sauté garlic in olive oil; add crushed tomatoes, dried lavender, and white wine; simmer 15 minutes.", "Add shucked oysters with their liquor; cook gently 2 minutes until edges just curl.", "Serve in warm bowls with crusty bread; the lavender perfumes the whole tomato-oyster stew."]),

    ("lavender","oyster","truffle",
     "Lavender and truffle share anisaldehyde — the anise-adjacent aromatic compound — while oyster's marine phenylacetaldehyde provides the rosy-fermented complement to truffle's own phenylacetaldehyde. The trio creates a triple-anisaldehyde-phenylacetaldehyde luxury preparation of extraordinary aromatic complexity.",
     "Truffle Lavender Oyster Custard",
     ["Make a savory custard base with cream, eggs, truffle oil, and a pinch of dried lavender; strain.", "Fill small ramekins with a shucked oyster each; pour custard over and steam gently.", "Serve warm topped with a shaving of fresh truffle and a dried lavender flower."]),

    ("lavender","oyster","vanilla",
     "Lavender and vanilla share linalool and linalyl acetate — the dominant floral terpenes in both — while oyster's marine brine and vanilla's sweet-lactonic vanillin create a bold sweet-salt contrast that the shared linalool bridges into a floral connecting register. The trio creates a sophisticated Provençal oyster preparation.",
     "Vanilla Lavender Oyster Beurre Blanc",
     ["Reduce white wine and shallots; whisk cold butter piece by piece until a rich beurre blanc forms.", "Add vanilla bean seeds and a pinch of dried lavender; strain through a fine sieve.", "Spoon the vanilla-lavender beurre blanc over warm broiled oysters still in their half-shells."]),

    ("lavender","parmesan","rose",
     "Lavender, Parmesan, and rose form a trifecta where rose and lavender share 2-phenylethanol and linalool — the full floral-herbal terpene overlap — while Parmesan's glutamate umami and butyric acid provide the savory anchor that prevents the double-floral from becoming perfumed. The trio creates a refined savory-floral preparation.",
     "Rose Lavender Parmesan Honey Board",
     ["Shave aged Parmesan in large irregular pieces; scatter dried lavender and crystallized rose petals.", "Arrange on a board with honeycomb, walnuts, and thin crackers.", "The rose and lavender floral volatiles lift Parmesan's umami into a perfumed register."]),
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
print(f"Batch 050 done: inserted {len(TRIPLETS)} triplets.")
