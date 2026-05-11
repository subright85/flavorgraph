#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("caramel","lamb","salmon",
     "Caramel's furaneol bridges two proteins that share no direct compound overlap — lamb's 4-methyloctanoic acid and salmon's trimethylamine both sit in the savory-animal register that caramelization's sweetness rounds through Maillard contrast. The trio works as a bold surf-and-turf glaze where caramel's sweetness simultaneously softens lamb's gamey intensity and salmon's marine richness.",
     "Caramel Glazed Lamb and Salmon Surf & Turf",
     ["Reduce a dark caramel with soy sauce, ginger, and rice vinegar into a glossy glaze.", "Sear lamb chops until crusted; brush with half the glaze; sear salmon skin-side down and brush with remaining glaze.", "Plate lamb and salmon side by side; drizzle with resting juices and serve with steamed jasmine rice."]),

    ("caramel","lamb","strawberry",
     "Lamb and strawberry share no direct aroma compound, but caramel's furaneol bridges both — matching strawberry's dominant sweet-caramel note while contrasting lamb's gamey 4-methyloctanoic acid with Maillard sweetness that suppresses animal-fat pungency. The trio creates a Scandinavian-inflected lamb preparation where fruit and caramel work as a dual softening agent.",
     "Caramel Strawberry Glazed Lamb Chops",
     ["Cook diced strawberries with sugar into a quick jam; add aged balsamic and reduce to a caramel-strawberry glaze.", "Sear lamb chops in a very hot pan until crusted on both sides; brush with glaze and finish in 375°F oven for 5 minutes.", "Rest 5 minutes, spoon warm glaze over, and garnish with fresh strawberry slices and mint."]),

    ("caramel","lamb","tomato",
     "Caramel and tomato share furaneol — the sweet-caramel compound at the heart of both dark caramel and ripe tomato — while lamb's long-braise chemistry interacts with tomato's malic acid to tenderize in a Mediterranean slow-cook register. Caramel adds deeper brown sweetness that balances lamb's gamey fat through Maillard contrast on the palate.",
     "Caramel Lamb Tomato Tagine",
     ["Brown lamb shoulder pieces in batches; add caramelized onions, crushed tomatoes, and ras el hanout.", "Cover and braise at 300°F for 2.5 hours; add a tablespoon of dark caramel near the end to deepen the sauce.", "Adjust seasoning; serve over couscous with fresh cilantro and a squeeze of preserved lemon."]),

    ("caramel","lamb","truffle",
     "Caramel and truffle share Maillard-derived aromatic compounds — dimethyl sulfide appears in both roasted sugars and black truffle fermentation — while lamb's dimethyl sulfide provides a third tier of the same sulfurous-earthy-sweet compound stack. The trio creates a deeply indulgent luxury preparation where caramel's sweetness softens truffle's earthiness and lamb's gamey richness simultaneously.",
     "Truffle Caramel Rack of Lamb",
     ["Make a dark caramel, deglaze with cognac, and whisk in truffle butter and cream for a glossy sauce.", "Rub a rack of lamb with truffle salt, garlic, and herbs; roast at 425°F for 22 minutes to medium-rare.", "Rest 8 minutes, carve into chops, and drizzle the truffle caramel sauce over generously; serve immediately."]),

    ("caramel","lamb","vanilla",
     "Caramel and vanilla share furaneol and vanillin — sweet-caramel and lactonic compounds present in both dark caramel and cured vanilla beans — while lamb's gamey 4-methyloctanoic acid is softened by this sweet compound duo through aromatic displacement. The trio defines Moroccan-style lamb with sweet spices where vanilla deepens caramel's Maillard complexity.",
     "Vanilla Caramel Lamb Tagine",
     ["Brown lamb with onion and sweet spices; add a split vanilla bean, honey, and a spoonful of dark caramel.", "Deglaze with stock and preserved lemon; braise at 300°F for 2 hours until meltingly tender.", "Stir in toasted almonds and dried apricots; remove vanilla bean and serve over saffron couscous."]),

    ("caramel","lavender","lemon",
     "Caramel and lavender are elevated by contrast — caramel's Maillard warmth intensifying lavender's linalool-forward floral register through sweet-floral opposition — while lemon's citric acid and limonene provide the brightness that cuts caramel's richness and lifts lavender's perfumed note into a clean, vertical aromatic finish. The trio defines Southern French caramel confectionery.",
     "Lavender Lemon Caramel Sauce",
     ["Cook sugar to a dark amber caramel; off heat whisk in warm cream infused with lavender and lemon zest.", "Add cold butter piece by piece stirring until glossy; season with flaky salt and lemon juice.", "Pour into jars or serve warm over vanilla ice cream; the lemon keeps the lavender caramel from turning cloying."]),

    ("caramel","lavender","mint",
     "Lavender and mint share linalool — the dominant terpene in both herbs — while caramel's furaneol sweetness provides the sweet contrast that elevates both herbal-terpene registers into a refined confectionery profile. Mint's menthol provides a clean cooling finish that follows caramel's warm Maillard sweetness and lavender's floral depth in sequence.",
     "Lavender Mint Caramel Bonbons",
     ["Make a dark caramel, off heat whisk in lavender-infused cream, butter, and a drop of peppermint extract.", "Add flaky salt; pour into small molds and allow to set at room temperature until firm enough to handle.", "Unmold onto parchment; dust with lavender sugar and a pinch of fleur de sel before serving."]),

    ("caramel","lavender","oyster",
     "Caramel's sweetness creates a bold marine-sweet contrast against oyster's briny dimethyl sulfide — the principle behind miso caramel with seafood — while lavender's linalool provides the aromatic bridge that softens the sweetness-brine juxtaposition through floral displacement. The trio is avant-garde but chemically supported by the linalool connection.",
     "Caramel Lavender Oyster Mignonette",
     ["Dissolve a small amount of light caramel into white wine vinegar; add minced shallots and a pinch of dried lavender.", "Cool completely and adjust sweet-sour balance with additional vinegar if needed.", "Spoon very sparingly over freshly shucked raw oysters on ice; serve immediately with lemon wedges."]),

    ("caramel","lavender","parmesan",
     "Caramel and Parmesan share furaneol and butyric acid — sweet-caramel and fatty-dairy compounds that both caramelized sugar and aged cheese produce — while lavender's linalool provides a Provençal floral note that bridges sweet-dairy-umami into an aromatic, sophisticated savory-sweet register. The trio works in refined savory cheese preparations.",
     "Caramel Lavender Parmesan Savory Tart",
     ["Make a lavender-caramel custard: whisk caramel with cream, eggs, and a pinch of dried lavender.", "Fold in finely grated Parmesan; pour into a blind-baked pastry shell and bake at 325°F until just set.", "Cool to room temperature and serve with lavender honey and shaved Parmesan."]),

    ("caramel","lavender","rose",
     "Caramel and lavender are amplified by contrast — caramel's warm sweetness intensifying lavender's linalool — while rose's 2-phenylethanol reinforces lavender's floral register and adds a deeper rosy character through the shared 2-phenylethanol and geraniol compounds both flower and lavender produce. The trio defines high-end French confiserie at its most refined.",
     "Rose Lavender Caramel",
     ["Cook sugar to amber caramel; off heat add warm cream steeped with dried lavender and rose petals.", "Whisk in cold butter until glossy; add a splash of rose water and flaky sea salt.", "Pour into jars or molds; serve warm over panna cotta or set into firm caramel candies dusted with rose."]),

    ("caramel","lavender","salmon",
     "Caramel's furaneol sweetness suppresses salmon's trimethylamine marine notes through the same mechanism as teriyaki glaze — sweet compounds reduce the perception of fishy amines — while lavender's linalool adds Provençal floral depth that bridges caramel's warm sweetness to salmon's delicate fatty aromatics. The trio creates an aromatic glazed salmon with unexpected sophistication.",
     "Lavender Caramel Glazed Salmon",
     ["Make a caramel-lavender glaze: cook sugar to amber, add cream, dried lavender, and a splash of soy sauce.", "Brush salmon fillets generously with glaze; bake at 400°F for 12 minutes, brushing once more halfway.", "Broil 1 minute for a glossy finish; serve with lavender-herb grain salad and lemon wedges."]),

    ("caramel","lavender","strawberry",
     "Caramel and strawberry share furaneol as their dominant sweet-caramel compound, while lavender's linalool connects to strawberry's minor floral esters — creating a triple alignment where each ingredient reinforces the others' aromatic profile without redundancy. The trio is among the most cohesive possible sweet-floral dessert flavor combinations.",
     "Lavender Strawberry Caramel Tart",
     ["Make a dark caramel, add lavender-infused cream, and cool to a pourable tart-filling consistency.", "Fill a baked tart shell with lavender caramel; arrange halved fresh strawberries over the top in concentric rings.", "Glaze with a light strawberry-lavender jelly; serve at room temperature with a dusting of lavender sugar."]),

    ("caramel","lavender","tomato",
     "Caramel and tomato share furaneol — the compound at the core of both roasted caramel and ripe tomato sweetness — while lavender's linalool adds a Provençal floral register that turns this sweet-vegetable combination into a sophisticated Southern French savory preparation. The trio is the flavor principle behind caramelized tomato tart with lavender.",
     "Caramel Tomato Lavender Tart Tatin",
     ["Make a caramel in an oven-safe pan; add halved cherry tomatoes and dried lavender and cook briefly until tomatoes soften at the edges.", "Top with puff pastry, tuck edges around the tomatoes, and bake at 400°F until pastry is deeply golden.", "Invert immediately onto a plate; scatter fresh lavender flowers and drizzle with lavender honey."]),

    ("caramel","lavender","truffle",
     "Caramel and truffle both develop dimethyl sulfide through Maillard and fermentation pathways respectively — the roasted-earthy compound axis connecting sweetness and fungal depth — while lavender's anisaldehyde bridges caramel's warm register to truffle's earthy anise-adjacent character. The trio creates an opulent savory-sweet luxury preparation that Provençal haute cuisine explores.",
     "Truffle Lavender Caramel Butter",
     ["Whisk together softened butter, truffle paste, caramel sauce, and a pinch of dried lavender until completely smooth.", "Add flaky salt; refrigerate in a log shape until firm, then slice into rounds.", "Melt over warm risotto, grilled mushrooms, or a seared scallop at the table for instant luxury."]),

    ("caramel","lavender","vanilla",
     "Caramel, lavender, and vanilla share linalool — the floral terpene compound present in all three — while caramel and vanilla also share furaneol and vanillin, creating perhaps the deepest shared-compound alignment among any three culinary flavors. Together they form the ultimate sweet-floral-lactonic dessert triad with a complete aromatic range from warm to floral.",
     "Lavender Vanilla Caramel Crème Brûlée",
     ["Infuse cream with split vanilla bean and dried lavender; strain and whisk with egg yolks and caramel sauce.", "Pour into ramekins; bake in a water bath at 325°F until just set with a gentle wobble in the center.", "Chill thoroughly; top with lavender sugar and brûlée until amber and crackled; serve immediately."]),

    ("caramel","lemon","mint",
     "Caramel's furaneol sweetness contrasts with lemon's citric acid brightness — sweet-sour contrast that elevates both registers — while mint's menthol provides a cooling clean finish that cuts caramel's richness and extends lemon's palate-cleansing acidity. The trio creates a refreshing yet indulgent dessert where each element plays a distinct and non-redundant aromatic role.",
     "Caramel Lemon Mint Semifreddo",
     ["Whisk egg yolks with sugar until pale; fold into whipped cream with lemon zest and finely chopped fresh mint.", "Pour into a loaf tin lined with plastic wrap and freeze at least 6 hours until firm throughout.", "Serve sliced, drizzled with warm dark caramel sauce and garnished with fresh mint and curled lemon zest."]),

    ("caramel","lemon","oyster",
     "Caramel's sweetness contrasts against oyster's marine brine in a sweet-salt interaction — the same logic as mignonette's acidity — while lemon's citric acid performs its classic trimethylamine-neutralizing function on the oyster and its limonene brightens caramel's Maillard depth. Lemon is the aromatic bridge that makes this unusual sweet-marine trio cohere.",
     "Caramel Lemon Broiled Oysters",
     ["Shuck oysters, reserving liquor; reduce oyster liquor with white wine and a touch of caramel to a light glaze.", "Add lemon zest, lemon juice, and cold butter off heat; swirl into a glossy sauce.", "Broil oysters in the half shell for 3 minutes; spoon the caramel-lemon butter over each and serve immediately."]),

    ("caramel","lemon","parmesan",
     "Caramel and Parmesan share furaneol and butyric acid — sweet-caramel and fatty-dairy compounds — while lemon's citric acid cuts through Parmesan's fat and provides the acid-brightness that transforms the sweet-savory combination into a balanced, refined sauce. The trio appears in sophisticated savory preparations where umami sweetness and citrus brightness must be carefully calibrated.",
     "Caramel Lemon Parmesan Risotto",
     ["Cook risotto with white wine and stock; off heat stir in a spoonful of caramelized shallot reduction.", "Add cold butter, lemon zest, lemon juice, and a generous grating of aged Parmesan; beat vigorously.", "Plate immediately; finish with more Parmesan shavings, a fine drizzle of olive oil, and lemon zest."]),

    ("caramel","lemon","rose",
     "Lemon provides the aromatic bridge between caramel and rose — lemon's geraniol overlaps with rose's geraniol and linalool while lemon's acidity cuts caramel's sweetness into a balanced sweet-floral register. The trio creates a refined Middle Eastern-influenced confection where the three flavors form a complete aromatic arc from warm-sweet to bright-citrus to floral.",
     "Rose Lemon Caramel Tart",
     ["Make a caramel-lemon curd: cook caramel, add lemon juice, zest, butter, and eggs; strain smooth.", "Stir in a splash of rose water; pour into a blind-baked tart shell and refrigerate until fully set.", "Serve with crystallized rose petals, lemon zest curls, and a very light dusting of edible gold."]),

    ("caramel","lemon","salmon",
     "Caramel's sweetness suppresses salmon's trimethylamine marine notes through the same mechanism as teriyaki and Asian glazes on fish — sweet Maillard compounds reduce the perception of fishy amines — while lemon's citric acid provides balancing brightness that cuts caramel's richness and adds its own trimethylamine-neutralizing acidity. Together the trio creates the most universally appealing salmon glaze.",
     "Caramel Lemon Glazed Salmon",
     ["Reduce dark caramel with soy sauce, lemon juice, and lemon zest into a glossy sweet-tart glaze.", "Brush salmon fillets; roast at 425°F for 10 minutes, brushing with glaze halfway through.", "Broil 1 minute for caramelization; serve over jasmine rice with lemon wedges and fresh herbs."]),
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
print(f"Batch 027 done: inserted {len(TRIPLETS)} triplets.")
