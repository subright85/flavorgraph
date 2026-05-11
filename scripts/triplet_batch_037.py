#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("coffee","lamb","vanilla",
     "Coffee and vanilla share furfural and vanillin — caramel and lactonic compounds from roasting and curing — while vanilla's vanillin sweetness contrasts lamb's gamey 4-methyloctanoic acid through sweet-fat modulation, and coffee's bitter pyrazines moderate gaminess through a second mechanism. Double gamey-note suppression with a warm sweet-bitter aromatic result defines this Moroccan-spice territory.",
     "Vanilla Espresso Moroccan Lamb",
     ["Brown lamb with sweet Moroccan spices; add a split vanilla bean, brewed espresso, and stock.", "Braise at 300°F for 2 hours; the espresso deepens the braise while vanilla rounds gaminess.", "Serve over couscous with dried apricots and toasted almonds; remove vanilla bean before serving."]),

    ("coffee","lavender","lemon",
     "Coffee's bitter pyrazines and lavender's linalool create a Provençal café register — dark and floral — while lemon's citric acid and limonene provide the brightness that cuts through both coffee's bitterness and lavender's heaviness, lifting the combination into a clean, aromatic summer beverage. The trio drives sophisticated Provençal cold brew preparations.",
     "Lavender Lemon Cold Brew",
     ["Steep cold brew coffee overnight with dried lavender; strain clean.", "Add fresh lemon juice, lemon zest, and simple syrup to balance.", "Serve over ice with a lavender sprig and lemon wheel — light, aromatic, and refreshing."]),

    ("coffee","lavender","mint",
     "Coffee's bitter pyrazines and lavender's linalool create a dark-floral combination while mint's menthol adds cooling contrast that lifts both — cool against dark, floral against bitter. All three ingredients have distinct aromatic registers that play in sequence on the palate, creating a layered herb-floral-bitter cold beverage.",
     "Lavender Mint Cold Brew Coffee",
     ["Steep cold brew overnight with dried lavender and fresh mint; strain through a fine sieve.", "Sweeten lightly with lavender simple syrup; add a squeeze of lime.", "Serve over ice with fresh mint and lavender sprigs; the three aromatics bloom in sequence."]),

    ("coffee","lavender","oyster",
     "Coffee and oyster share dimethyl sulfide — sulfurous compounds in roasted coffee and marine bivalves — while lavender's linalool provides floral aromatic bridging between the dark-roasted and marine registers. The trio creates an avant-garde oyster preparation where coffee's bitter earthiness and lavender's Provençal floral bracket the oceanic brine.",
     "Lavender Espresso Oyster Mignonette",
     ["Reduce brewed espresso with sherry vinegar until syrupy; add a pinch of dried lavender.", "Add finely minced shallot and cracked pepper; cool completely.", "Spoon very sparingly over raw oysters on ice; the espresso adds earthiness against lavender floral."]),

    ("coffee","lavender","parmesan",
     "Coffee and Parmesan share dimethyl sulfide — the sulfurous compound in both — while lavender's linalool provides floral bridging between coffee's bitter roasted register and Parmesan's fermented-dairy depth. The trio creates a sophisticated savory coffee-cheese shortbread or crostini with Provençal aromatics.",
     "Lavender Espresso Parmesan Biscotti",
     ["Make biscotti dough with espresso powder, finely grated Parmesan, flour, eggs, and dried lavender.", "Bake at 350°F until set; slice and return to oven 15 minutes until dried and crisp.", "Cool; serve with espresso or wine — the lavender bridges the bitter and savory registers beautifully."]),

    ("coffee","lavender","rose",
     "Coffee's bitter pyrazines provide dark depth while lavender and rose share linalool and 2-phenylethanol — the overlapping floral terpene compounds connecting both flowers — creating a dark-floral combination where coffee anchors the double-floral register. The trio is the flavor of sophisticated Provençal café au lait and Middle Eastern qahwa.",
     "Rose Lavender Espresso",
     ["Brew double espresso; add rose water and lavender simple syrup.", "Froth milk; pour espresso first, then add frothed milk.", "Garnish with a rose petal and a tiny pinch of dried lavender; serve immediately."]),

    ("coffee","lavender","salmon",
     "Coffee and salmon share dimethyl sulfide — sulfurous compounds in both — while coffee's bitter Maillard compounds suppress salmon's trimethylamine through the same mechanism as a coffee rub on fish, and lavender's linalool provides floral aromatic bridging that softens the dark-roasted and marine combination. The trio creates a bold Provençal coffee-herb salmon.",
     "Lavender Espresso Salmon",
     ["Make a glaze: brewed espresso, dried lavender, honey, and a splash of sherry vinegar.", "Brush salmon fillets; bake at 400°F for 12 minutes, glazing halfway through.", "Serve with lavender-herb rice and lemon; the espresso-lavender creates an unexpected aromatic crust."]),

    ("coffee","lavender","strawberry",
     "Coffee's furfural shares a Maillard lineage with strawberry's furaneol — both caramel-adjacent compounds — while lavender and strawberry share linalool, creating a dual compound connection where coffee deepens strawberry's sweet register and lavender elevates its floral dimension. The trio creates a refined café-style summer dessert.",
     "Lavender Strawberry Espresso Cake",
     ["Make a lavender-espresso sponge cake flavored with dried lavender and espresso powder.", "Frost with lavender mascarpone cream; top with macerated fresh strawberries.", "Drizzle cold brew espresso over the finished cake and garnish with a lavender sprig."]),

    ("coffee","lavender","tomato",
     "Coffee and tomato share pyrazines and phenylacetaldehyde — Maillard-roasted and rosy-fermented compounds that both develop through heat treatment — while lavender's linalool provides Provençal floral bridging between the roasted-bitter coffee and savory-acid tomato registers. The trio appears in Provence-inspired slow-roasted tomato preparations.",
     "Lavender Espresso Roasted Tomatoes",
     ["Halve cherry tomatoes; toss with olive oil, dried lavender, a drizzle of espresso, and salt.", "Roast at 300°F for 2 hours until deeply concentrated and caramelized.", "Serve over ricotta toast or pasta; the espresso and lavender add aromatic depth to the tomatoes."]),

    ("coffee","lavender","truffle",
     "Coffee and truffle share dimethyl sulfide — sulfurous compounds in roasted coffee and earthy fungal fermentation — while lavender's anisaldehyde bridges coffee's bitter-dark register to truffle's anise-adjacent character. The three-way aromatic combination creates an opulent savory preparation where floral Provençal notes lift the heavy earthy-bitter combination.",
     "Truffle Lavender Espresso Butter",
     ["Beat softened butter with truffle paste, espresso powder, dried lavender, and flaky salt.", "Refrigerate in a log until firm; slice into rounds.", "Melt over warm risotto or grilled steak — the lavender lifts the truffle-espresso earthiness beautifully."]),

    ("coffee","lavender","vanilla",
     "Coffee and vanilla share furfural and vanillin — caramel and lactonic compounds — while lavender and vanilla share linalool, creating a dual compound connection where vanilla's sweetness bridges coffee's bitterness and lavender's floral warmth elevates the combination into a Provençal confectionery register. The trio creates a sophisticated café dessert.",
     "Lavender Vanilla Espresso Crème Brûlée",
     ["Infuse cream with dried lavender and split vanilla bean; steep 20 minutes and strain.", "Add brewed espresso and whisk with egg yolks; pour into ramekins and bake in a water bath.", "Chill; top with sugar mixed with lavender; brûlée until amber — a Provençal café in a ramekin."]),

    ("coffee","lemon","mint",
     "Coffee's bitter pyrazines are moderated by lemon's citric acid through pH-driven bitterness reduction — the same mechanism as adding lemon to espresso — while mint's menthol provides cooling contrast that extends the citrus-bright feeling through olfactory cooling. The trio creates the most refreshing possible cold coffee preparation.",
     "Lemon Mint Cold Brew Coffee",
     ["Brew strong cold brew overnight; add fresh mint and lemon slices; steep 1 hour.", "Strain; sweeten lightly and serve over ice with a generous squeeze of lemon.", "Garnish with fresh mint and a lemon wheel; serve immediately over crushed ice."]),

    ("coffee","lemon","oyster",
     "Coffee and oyster share dimethyl sulfide — sulfurous compounds in both — while lemon's citric acid performs its classic marine-note suppression by neutralizing trimethylamine and simultaneously cutting coffee's bitterness. The trio creates a sophisticated seafood preparation where coffee's depth is tempered by lemon's brightness.",
     "Espresso Lemon Oyster Mignonette",
     ["Reduce brewed espresso with white wine vinegar and lemon juice until concentrated.", "Add lemon zest, finely minced shallot, and cracked pepper; cool completely.", "Spoon sparingly over raw oysters on ice; the espresso adds unexpected depth to the bright citrus mignonette."]),

    ("coffee","lemon","parmesan",
     "Coffee and Parmesan share dimethyl sulfide while lemon's citric acid cuts Parmesan's fat and coffee's bitterness simultaneously — acid as universal brightener for both rich, complex flavors. The combination creates a sophisticated savory coffee-cheese preparation where lemon's acid lifts rather than fights the bitter-umami register.",
     "Espresso Lemon Parmesan Risotto",
     ["Cook arborio risotto with white wine and stock; off heat stir in lemon zest and juice.", "Add cold butter, finely grated Parmesan, and a splash of cold brew espresso; beat until glossy.", "Plate; finish with more Parmesan, lemon zest, and a very light dusting of ground espresso."]),

    ("coffee","lemon","rose",
     "Coffee's roasted pyrazines and rose's 2-phenylethanol create a bold dark-floral contrast while lemon's geraniol directly overlaps with rose's geraniol — sharing a terpene compound — creating a citrus-floral bridge that grounds the rose's sweetness and brightens coffee's darkness. The trio drives sophisticated rose-citrus coffee preparations.",
     "Rose Lemon Espresso",
     ["Brew double espresso; add rose water and fresh lemon juice while still hot.", "Froth oat milk until silky; pour over the rose-lemon espresso.", "Garnish with a dried rose petal and lemon zest curl; serve immediately."]),

    ("coffee","lemon","salmon",
     "Coffee and salmon share dimethyl sulfide while coffee's bitter compounds suppress salmon's trimethylamine — the coffee rub mechanism — and lemon's citric acid simultaneously suppresses trimethylamine through a second, acid-driven mechanism. The double-suppression of marine notes produces the cleanest-tasting coffee-salmon preparation.",
     "Lemon Espresso Rubbed Salmon",
     ["Make a rub: ground espresso, lemon zest, garlic powder, brown sugar, and salt.", "Press onto salmon fillets; rest 20 minutes before cooking.", "Sear or bake at 400°F; serve with lemon wedges and a cold brew espresso-lemon drizzle."]),

    ("coffee","lemon","strawberry",
     "Coffee's furfural is a Maillard cousin of strawberry's furaneol — both caramel-adjacent compounds — while lemon's citric acid brightens strawberry's sweetness and simultaneously cuts coffee's bitterness. The trio creates a vibrant summer dessert where the caramel-adjacent compounds provide aromatic coherence beneath the sweet-sour-bitter interplay.",
     "Strawberry Lemon Espresso Sorbet",
     ["Blend ripe strawberries with cold brew espresso, lemon juice, and simple syrup until smooth.", "Churn in an ice cream maker until firm; transfer to a container and freeze.", "Serve scooped in chilled glasses with a curl of lemon zest and a drizzle of espresso."]),

    ("coffee","lemon","tomato",
     "Coffee and tomato share pyrazines and phenylacetaldehyde — Maillard-roasted and rosy-fermented compounds — while lemon's citric acid provides the brightness that cuts through both coffee's bitterness and tomato's acidity into a cleaner, more vertical register. The trio creates a bright, acid-forward tomato sauce where espresso adds depth.",
     "Espresso Lemon Tomato Sauce",
     ["Cook crushed tomatoes with garlic until reduced; add a shot of espresso and lemon zest.", "Simmer 5 minutes; finish with lemon juice and olive oil off heat.", "Season and serve over pasta with Parmesan; the espresso adds roasted depth beneath the brightness."]),

    ("coffee","lemon","truffle",
     "Coffee and truffle share dimethyl sulfide — sulfurous compounds in both — while lemon's citric acid and limonene provide the brightness that lifts the intensely dark, earthy coffee-truffle combination into a lighter, more elegant register. The acid contrast turns an otherwise heavy luxury preparation into something surprisingly fresh.",
     "Truffle Lemon Espresso Pasta",
     ["Melt truffle butter with a shot of espresso and lemon zest in a wide pan.", "Toss al dente pasta with the truffle-espresso sauce and pasta water until glossy.", "Squeeze lemon juice over; shave generous truffle and finish with lemon zest."]),

    ("coffee","lemon","vanilla",
     "Coffee and vanilla share furfural and vanillin — caramel and lactonic compounds — while lemon's citric acid prevents the sweet-rich coffee-vanilla combination from being cloying, sharpening vanilla's floral register and coffee's Maillard depth into a balanced acid-sweet-bitter arc. The trio defines the most elegant cold brew dessert preparation.",
     "Vanilla Lemon Cold Brew Affogato",
     ["Brew very strong cold brew; add lemon zest and steep 30 minutes for subtle citrus note.", "Place a scoop of vanilla ice cream in a chilled glass.", "Pour cold brew over immediately; the lemon-vanilla-coffee combination is unexpectedly bright and clean."]),
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
print(f"Batch 037 done: inserted {len(TRIPLETS)} triplets.")
