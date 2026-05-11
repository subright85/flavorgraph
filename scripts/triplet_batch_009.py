#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("basil","rose","vanilla",
     "Rose and vanilla share 2-phenylethanol and vanillin — rosy-floral and sweet-lactonic compounds — while basil's eugenol adds a spiced warmth that echoes vanilla's anise-adjacent character and grounds rose's delicate perfume into a richer register. Together they create the most complete sweet-floral-herbal dessert base possible from three ingredients.",
     "Rose Vanilla Basil Madeleine",
     ["Melt butter until lightly browned; cool slightly then whisk with eggs, sugar, rose water, and vanilla.","Fold in flour with finely chopped fresh basil; rest batter 1 hour in the refrigerator.","Bake in madeleine molds at 400°F for 11 minutes until domed; dust with powdered rose-sugar."]),

    ("basil","salmon","strawberry",
     "Salmon and strawberry share furaneol — the sweet-caramel compound present in both ripe strawberry and the skin of high-quality salmon — while basil's linalool and 2-phenylethanol amplify strawberry's floral esters and bridge the fruit-fish gap through herbal-terpene compounds. The unusual pairing works as a sweet-acid glaze or ceviche.",
     "Strawberry Basil Salmon Ceviche",
     ["Dice sushi-grade salmon; cure in a blend of strawberry juice, lime, and salt for 5 minutes.","Drain, fold in diced fresh strawberry, chopped basil, cucumber, and shallot.","Season with flaky salt, serve immediately chilled with basil oil and strawberry coulis."]),

    ("basil","salmon","tomato",
     "Salmon and tomato share furaneol and acetic acid — sweet-caramel and tart compounds linking fatty fish and ripe fruit — while basil's linalool and eugenol complete the Mediterranean aromatic triad that defines Italian brodetto di pesce and French salmon provençal. Tomato's acidity brightens salmon while basil bridges both ingredients.",
     "Provençal Salmon Tomato Braise",
     ["Sear salmon skin-side down in olive oil; remove and sauté garlic and cherry tomatoes.","Return salmon on top, add white wine and basil; cover and cook 8 minutes until just done.","Plate salmon over the tomato-basil pan sauce with crusty bread and extra fresh basil."]),

    ("basil","salmon","truffle",
     "Salmon and truffle share dimethyl sulfide — the sulfurous compound linking fatty fish and earthy fungus — while basil's linalool and 2-phenylethanol bridge the marine-earthy contrast through herbal-floral terpenes that suppress salmon's trimethylamine and lift truffle's earthiness into a cleaner register. The trio is a signature of haute cuisine seafood.",
     "Truffle Basil Salmon en Croûte",
     ["Spread truffle-basil compound butter over salmon fillets; wrap in puff pastry and seal.","Brush with egg wash; bake at 400°F for 20 minutes until pastry is deeply golden.","Rest 5 minutes before slicing; serve with a truffle-cream sauce and fresh basil garnish."]),

    ("basil","salmon","vanilla",
     "Salmon and vanilla share furaneol and trace vanillin — caramel-lactonic compounds — while basil's eugenol adds herbal spiced warmth that bridges vanilla's sweet-anise character to salmon's delicate fatty-fish aromatics. Vanilla-poached salmon is a classic French technique where sweetness suppresses trimethylamine marine notes.",
     "Vanilla Basil Poached Salmon",
     ["Make a court bouillon with white wine, split vanilla bean, fresh basil, and aromatics.","Poach salmon at barely a simmer for 10 minutes; remove carefully with a slotted spoon.","Serve with a vanilla-basil beurre blanc and a scattering of fresh basil leaves."]),

    ("basil","strawberry","tomato",
     "Strawberry and tomato share furaneol — the caramel-sweet compound that is the single most important aroma molecule in both ripe strawberry and ripe tomato — creating an unusually coherent fruit-vegetable pairing, while basil's linalool and eugenol complete the Italian summer flavor trinity where garden-sweetness and herbal warmth balance precisely.",
     "Strawberry Tomato Basil Gazpacho",
     ["Blend ripe tomatoes with fresh strawberries, a handful of basil, garlic, and olive oil until smooth.","Season with sherry vinegar, salt, and white pepper; strain for a silky texture.","Serve very cold in chilled bowls with diced strawberry, torn basil, and a basil oil drizzle."]),

    ("basil","strawberry","truffle",
     "Strawberry and truffle share phenylacetaldehyde — the rosy compound in truffle fermentation and strawberry fermentation esters — while basil's linalool and 2-phenylethanol bridge the floral-sweet and earthy-luxury registers through their shared terpene presence with both ingredients. The trio creates a bold luxury dessert-savory pairing.",
     "Truffle Strawberry Basil Risotto",
     ["Cook arborio risotto until creamy; off heat stir in mascarpone, Parmesan, and lemon zest.","Fold in diced fresh strawberry and torn basil immediately before plating.","Shave generous fresh truffle over the top; finish with a drizzle of truffle honey."]),

    ("basil","strawberry","vanilla",
     "Strawberry and vanilla share furaneol, linalool, and 2-phenylethanol — the most complete aromatic overlap between a fruit and a spice in the culinary world — while basil amplifies both ingredients' shared floral compounds with its own 2-phenylethanol and adds eugenol spiced warmth that prevents the sweet-floral from becoming cloying. The trio is summer dessert perfected.",
     "Strawberry Vanilla Basil Panna Cotta",
     ["Warm cream with vanilla bean and fresh basil; steep 20 minutes, strain, dissolve gelatin.","Pour into molds and set in refrigerator 4 hours; macerate sliced strawberries with vanilla and basil.","Unmold, spoon macerated strawberries around the base, and garnish with a basil tip."]),

    ("basil","tomato","truffle",
     "Tomato and truffle share dimethyl sulfide and phenylacetaldehyde — sulfurous and rosy compounds that roasted tomato and earthy fungus both produce through separate biochemical pathways — while basil's linalool and eugenol bridge the Mediterranean-herbal register to truffle's luxury earthiness. The trio appears in high-end Italian truffle pasta preparations with pomodoro.",
     "Truffle Pomodoro with Basil",
     ["Simmer crushed San Marzano tomatoes with garlic until reduced and sweet, about 25 minutes.","Toss al dente pasta with the sauce, truffle butter, and a splash of pasta water off heat.","Fold in torn fresh basil, plate, and finish with shaved truffle and a truffle oil drizzle."]),

    ("basil","tomato","vanilla",
     "Tomato and vanilla share furaneol at high concentrations — the sweet-caramel compound in both ripe tomato and cured vanilla beans — while basil's eugenol adds herbal spiced warmth that bridges the sweet-savory gap. The unusual but chemically precise pairing drives sophisticated tomato-vanilla chutney, jam, and slow-roasted tomato preparations.",
     "Vanilla Tomato Basil Confit",
     ["Halve cherry tomatoes, arrange in a baking dish with a split vanilla bean and fresh basil.","Cover with olive oil, roast at 250°F for 2 hours until concentrated and jammy.","Use as a sauce over pasta or cheese; the vanilla amplifies the tomato's natural furaneol sweetness."]),

    ("basil","truffle","vanilla",
     "Truffle and vanilla share vanillin — the compound that vanilla produces as its dominant molecule also appears as a minor aromatic in some black truffle cultivars — while basil's eugenol and linalool bridge the earthy-luxury and sweet-lactonic registers with herbal spiced warmth. The trio creates the most sophisticated savory-sweet compound butter possible.",
     "Truffle Vanilla Basil Compound Butter",
     ["Beat softened butter with truffle paste, vanilla bean seeds, and finely chopped fresh basil.","Add flaky salt and mix until completely smooth; taste and adjust seasoning carefully.","Shape into a log, refrigerate until firm, and slice over risotto, scrambled eggs, or warm brioche."]),

    ("blue cheese","butter","caramel",
     "Blue cheese and butter share butyric acid and diacetyl — the fatty-dairy and butterscotch compounds connecting two dairy products — while caramel's furaneol and Maillard sweetness contrasts the blue cheese funk in a sweet-funky balance that drives sophisticated salted-caramel cheese preparations. The trio creates an indulgent savory-sweet dairy register.",
     "Blue Cheese Caramel Butter Sauce",
     ["Make a dark caramel, whisk in warm cream and cold salted butter until glossy and smooth.","Stir in crumbled blue cheese off heat until just melted and creamy; don't overheat.","Serve immediately drizzled over sliced steak or roasted vegetables as a finishing sauce."]),

    ("blue cheese","butter","chocolate",
     "Blue cheese and chocolate share phenylacetaldehyde and dimethyl sulfide — rosy-fermented and sulfurous compounds that fermented cacao and aged dairy both produce — while butter's fat carries and amplifies both ingredients' volatile aromatics and rounds blue cheese's harsh ammonia notes. The combination works in sophisticated sweet-savory cheese-chocolate truffles.",
     "Blue Cheese Dark Chocolate Butter Truffles",
     ["Melt dark chocolate; off heat whisk in softened butter and crumbled blue cheese until smooth.","Refrigerate until firm enough to roll; shape into balls with cool hands.","Roll in cocoa powder and store refrigerated; serve at room temperature for full flavor."]),

    ("blue cheese","butter","coffee",
     "Blue cheese and coffee share dimethyl sulfide, acetic acid, and phenylacetaldehyde — the roasted-fermented pungent compound set — while butter's fat carries these volatile aromatics more effectively to the palate and softens blue cheese's harsh ammonia edge. The trio creates an intense savory-bitter compound butter for steak applications.",
     "Blue Cheese Coffee Compound Butter",
     ["Beat softened butter with crumbled blue cheese, finely ground espresso, and cracked pepper.","Mix until smooth; roll in plastic wrap into a log and refrigerate until firm.","Slice and place over hot grilled steak or mushrooms just before serving at the table."]),

    ("blue cheese","butter","cucumber",
     "Blue cheese and cucumber share trace (E)-2-nonenal — the clean watery compound that cucumber produces and that appears as a minor fresh note in some aged blues — while butter's fat rounds the blue cheese funk and amplifies cucumber's delicate volatile aldehydes, creating a cool-rich-funky compound that works as an elegant canapé spread.",
     "Blue Cheese Butter Cucumber Canapés",
     ["Beat softened butter with crumbled blue cheese, lemon zest, and cracked pepper until smooth.","Spread generously on thick cucumber rounds or thin crackers.","Top with a small herb leaf and a drizzle of wildflower honey; serve immediately chilled."]),

    ("blue cheese","butter","garlic",
     "Blue cheese and garlic share dimethyl sulfide and acetic acid — sulfurous and tart compounds creating a pungent double-allium-dairy intensity — while butter's fat converts harsh allicin into sweet cooked-garlic notes and rounds the blue cheese ammonia into a richer, more approachable register. The trio is the flavor of blue cheese garlic bread.",
     "Blue Cheese Garlic Butter Bread",
     ["Beat softened butter with crumbled blue cheese, roasted garlic paste, and fresh thyme until smooth.","Spread generously on sliced sourdough; bake at 400°F until bubbling and golden at edges.","Broil 2 minutes to crisp the top; serve immediately while blue cheese is still molten."]),

    ("blue cheese","butter","lamb",
     "Blue cheese, butter, and lamb share butyric acid and dimethyl sulfide — the fatty-acid and sulfurous compound family spanning fermented dairy, fat, and animal meat — while blue cheese's phenylacetaldehyde provides rosy depth that rounds lamb's gamey 4-methyloctanoic acid rather than suppressing it. The trio creates the richest possible savory dairy-meat combination.",
     "Blue Cheese Butter Lamb Chops",
     ["Make compound butter from softened butter, crumbled blue cheese, garlic, and herbs.","Sear lamb chops hard on both sides in a very hot cast-iron pan until crusted.","Top each chop with a slice of blue cheese butter; broil 1 minute until just melting."]),

    ("blue cheese","butter","lavender",
     "Blue cheese and lavender create an unusual pairing where lavender's linalool and linalyl acetate soften blue cheese's harsh ammonia through floral aromatic displacement — the same mechanism as honey with cheese — while butter's fat carries and extends both ingredients' volatile aromatics much longer on the palate. The trio achieves Provençal sophistication.",
     "Lavender Blue Cheese Compound Butter",
     ["Beat softened butter with crumbled blue cheese, dried lavender, and a drizzle of lavender honey.","Mix until smooth and roll in plastic wrap; refrigerate until firm.","Serve sliced on warm crusty bread or melted over roasted beets and walnuts."]),

    ("blue cheese","butter","lemon",
     "Blue cheese and lemon share acetic acid and trace citric compounds — both producing tartness that combines into a bright, sharp dairy-citrus contrast — while butter's fat rounds blue cheese's ammonia and amplifies lemon's volatile limonene and geraniol over a longer palate duration. The trio creates the classic sharp-bright blue cheese dressing base.",
     "Blue Cheese Lemon Butter Sauce",
     ["Melt butter with lemon juice and zest over medium heat until foamy and fragrant.","Stir in crumbled blue cheese off heat; swirl until just barely melted and creamy.","Spoon over grilled chicken or pasta, finish with more lemon zest and cracked pepper."]),

    ("blue cheese","butter","mint",
     "Blue cheese's butyric acid funk and mint's menthol create a cooling-pungent contrast — menthol directly suppresses the perception of ammonia-adjacent compounds through olfactory competition — while butter's fat bridges both extremes, carrying volatile mint aromatics and rounding blue cheese's sharpness simultaneously. The trio creates a refined compound butter for lamb.",
     "Blue Cheese Mint Butter",
     ["Beat softened butter with crumbled blue cheese and a generous amount of finely chopped fresh mint.","Add a squeeze of lemon juice and mix until smooth; roll in plastic wrap to a log.","Refrigerate until firm; slice and serve melting over grilled lamb chops or roasted new potatoes."]),
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
print(f"Batch 009 done: inserted {len(TRIPLETS)} triplets.")
