#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("coffee","parmesan","vanilla",
     "Coffee, Parmesan, and vanilla share vanillin — the lactonic-sweet compound in cured vanilla bean, aged Parmesan fermentation, and roasted coffee — creating a three-way vanillin alignment. Coffee and vanilla additionally share furfural and diacetyl, making this one of the most compound-connected trios in the coffee family, driving a sophisticated savory-sweet risotto.",
     "Vanilla Espresso Parmesan Panna Cotta",
     ["Warm cream with split vanilla bean; stir in a shot of cold brew espresso and dissolve gelatin.", "Add finely grated Parmesan; stir until melted; season lightly and pour into molds.", "Set in refrigerator 4 hours; unmold and serve drizzled with an espresso reduction and Parmesan shavings."]),

    ("coffee","rose","salmon",
     "Coffee and salmon share dimethyl sulfide while coffee's bitter pyrazines suppress salmon's trimethylamine — the coffee rub mechanism — and rose's 2-phenylethanol provides floral displacement as a second independent trimethylamine suppressor. The double suppression with floral aromatic depth creates a unique Persian-café influenced salmon glaze.",
     "Rose Espresso Glazed Salmon",
     ["Make a rose-espresso glaze: brewed espresso, rose water, honey, and rice vinegar reduced together.", "Brush salmon fillets; bake at 425°F for 10 minutes, glazing halfway through.", "Garnish with dried rose petals and serve over jasmine rice with a lemon wedge."]),

    ("coffee","rose","strawberry",
     "Coffee's furfural is caramel-adjacent to strawberry's furaneol while coffee and rose share the dark-floral contrast that Middle Eastern café culture has long explored. Rose and strawberry share 2-phenylethanol and linalool, creating a chain where coffee anchors the floral-sweet combination with roasted depth and strawberry bridges rose to coffee through furaneol.",
     "Rose Strawberry Espresso Cake",
     ["Make an espresso sponge; soak with rose water simple syrup.", "Frost with rose-strawberry mascarpone cream; decorate with sliced strawberries and rose petals.", "Drizzle cold brew espresso over the finished cake for a café-floral-fruit aromatic combination."]),

    ("coffee","rose","tomato",
     "Coffee and tomato share pyrazines and phenylacetaldehyde — Maillard-roasted and rosy-fermented compounds — while rose's 2-phenylethanol provides floral depth that softens tomato's acidity through aromatic displacement. The trio creates a sophisticated Turkish rose-tomato preparation deepened by espresso.",
     "Rose Espresso Tomato Jam",
     ["Cook ripe tomatoes with sugar, a shot of espresso, and a splash of rose water until jammy.", "The espresso deepens the tomato's savory register while rose softens the acidity.", "Jar and cool; serve with cheese, cured meat, or spread on toast."]),

    ("coffee","rose","truffle",
     "Coffee and truffle share dimethyl sulfide while coffee's pyrazines and rose's 2-phenylethanol create a dark-floral contrast — bitter and perfumed. Rose and truffle share phenylacetaldehyde through their separate fermentation chemistries, creating a compound chain where truffle's earthiness and rose's floral character share rosy-fermented common ground.",
     "Rose Truffle Espresso Compound Butter",
     ["Beat softened butter with truffle paste, rose water, a pinch of ground espresso, and flaky salt.", "Refrigerate in a log until firm; slice into rounds.", "Melt over warm risotto or grilled steak — the rose-espresso lifts truffle's earthiness into a floral register."]),

    ("coffee","rose","vanilla",
     "Coffee and vanilla share furfural and vanillin while rose and vanilla share 2-phenylethanol and linalool — every ingredient connects to at least one other through multiple shared compounds. The trio creates the most aromatic and compound-rich sweet-dark-floral combination in the coffee family, appearing in rose-vanilla espresso beverages.",
     "Rose Vanilla Espresso",
     ["Brew double espresso; immediately add vanilla syrup and a splash of rose water.", "Froth oat milk with a pinch of vanilla; pour the espresso base, then froth gently.", "Garnish with a rose petal; the three aromatics create a sweet-floral-bitter aromatic arc."]),

    ("coffee","salmon","strawberry",
     "Coffee and salmon share dimethyl sulfide — the sulfurous compound suppression mechanism — while coffee's furfural is caramel-adjacent to strawberry's furaneol, and strawberry's sweetness provides a second trimethylamine suppressor alongside coffee's bitter compounds. The double-mechanism TMA suppression produces a clean, sweet-bitter glazed salmon.",
     "Strawberry Cold Brew Glazed Salmon",
     ["Blend fresh strawberries with cold brew, soy sauce, and rice vinegar into a smooth glaze; reduce.", "Brush salmon fillets; bake at 425°F for 10 minutes, glazing halfway through.", "Serve over arugula with sliced strawberry; the strawberry-coffee bridges sweet and marine registers."]),

    ("coffee","salmon","tomato",
     "Coffee and salmon share dimethyl sulfide while coffee and tomato share pyrazines and phenylacetaldehyde — Maillard-roasted compounds that both coffee and roasted tomato develop. Tomato's savory acidity bridges coffee's bitterness to salmon's fatty richness through the shared compound chain, creating a bold Mediterranean-café salmon preparation.",
     "Espresso Tomato Braised Salmon",
     ["Simmer tomatoes with garlic and a shot of espresso until deeply reduced and concentrated.", "Nestle salmon fillets into the sauce; cover and cook gently 8 minutes until just opaque.", "Serve over pasta or polenta with fresh basil and a drizzle of olive oil."]),

    ("coffee","salmon","truffle",
     "Coffee, salmon, and truffle all share dimethyl sulfide — the sulfurous compound spanning roasted coffee, marine fish, and earthy fungal fermentation — creating a three-way alignment. Coffee's bitter Maillard compounds suppress salmon's TMA while truffle's dimethyl sulfide deepens the marine-earthy register into a singular luxury preparation.",
     "Truffle Espresso Salmon",
     ["Make a truffle-espresso glaze: truffle oil, brewed espresso, soy sauce, and honey reduced together.", "Brush salmon fillets; roast at 425°F for 10 minutes, glazing halfway through.", "Plate; shave fresh truffle over and finish with a drizzle of truffle-espresso glaze."]),

    ("coffee","salmon","vanilla",
     "Coffee and vanilla share furfural and vanillin while coffee and salmon share dimethyl sulfide — vanilla's sweet lactonic compounds suppress salmon's trimethylamine through sweet-compound masking and coffee's bitter compounds do the same through a different mechanism. The dual-suppression with a warm sweet-bitter aromatic creates an elegant café-style salmon.",
     "Vanilla Cold Brew Salmon",
     ["Make a vanilla-espresso court bouillon: cold brew, split vanilla bean, white wine, and aromatics.", "Poach salmon at barely a simmer for 10 minutes; remove carefully.", "Serve with a vanilla-espresso beurre blanc made by reducing the court bouillon with cold butter."]),

    ("coffee","strawberry","tomato",
     "Coffee's furfural is caramel-adjacent to both strawberry's furaneol and tomato's furaneol — all three sharing the sweet-caramel compound family through Maillard and natural fruit chemistry. Coffee deepens the shared furaneol register with roasted complexity while tomato's savory acidity contrasts strawberry's sweetness in a sophisticated sauce.",
     "Strawberry Espresso Tomato Salsa",
     ["Dice ripe tomatoes and strawberries; toss with cold brew espresso, lime juice, and chili.", "Add red onion, cilantro, and salt; rest 10 minutes for flavors to develop.", "Serve alongside mole chicken or as a bold dip with tortilla chips."]),

    ("coffee","strawberry","truffle",
     "Coffee's furfural is caramel-adjacent to strawberry's furaneol while coffee and truffle share dimethyl sulfide — creating a triangle where coffee bridges the sweet-fruit and earthy-fungal registers. Truffle and strawberry share phenylacetaldehyde through their separate fermentation chemistries, completing the compound web.",
     "Truffle Strawberry Espresso Dessert",
     ["Make a coffee panna cotta; cool until just set with a gentle wobble.", "Top with sliced fresh strawberries and a drizzle of truffle honey.", "Finish with a drizzle of cold brew espresso — the truffle honey bridges strawberry's sweetness to coffee's depth."]),

    ("coffee","strawberry","vanilla",
     "Coffee and vanilla share furfural and vanillin while coffee's furfural is caramel-adjacent to strawberry's furaneol, and strawberry and vanilla share linalool and 2-phenylethanol. Every ingredient connects to the others through shared compounds, creating a deeply cohesive sweet-dark-floral trio for classic café desserts.",
     "Vanilla Strawberry Espresso Tiramisu",
     ["Soak ladyfingers in espresso; layer with vanilla mascarpone cream and sliced fresh strawberries.", "Repeat layers; top with a final cream layer and refrigerate overnight.", "Dust with cocoa; garnish with strawberry and a drizzle of espresso before serving."]),

    ("coffee","tomato","truffle",
     "Coffee and tomato share pyrazines and phenylacetaldehyde — Maillard-roasted and rosy-fermented compounds — while coffee and truffle share dimethyl sulfide, and tomato and truffle share both compounds through their separate roasted and fermented chemistry. The triple compound overlap creates the most complex savory pasta sauce possible.",
     "Truffle Espresso Tomato Pasta",
     ["Cook tomato sauce with garlic; add a shot of espresso and truffle butter off heat.", "Toss with al dente pasta and pasta water; shave truffle generously over the top.", "The espresso and truffle amplify tomato's savory register into an intensely complex sauce."]),

    ("coffee","tomato","vanilla",
     "Coffee and tomato share pyrazines and phenylacetaldehyde while coffee and vanilla share furfural and vanillin, and tomato and vanilla share furaneol — creating a chain of compound connections through all three ingredients. The trio produces a sophisticated sweet-savory sauce where vanilla bridges tomato's savory acidity to coffee's roasted bitterness.",
     "Vanilla Espresso Tomato Jam",
     ["Cook ripe tomatoes with sugar, a split vanilla bean, and a shot of espresso until thick.", "The vanilla rounds tomato's acidity and espresso deepens the savory register.", "Remove vanilla bean; jar and cool; serve with cheese or as an elegant pizza base."]),

    ("coffee","truffle","vanilla",
     "Coffee and vanilla share furfural and vanillin while coffee and truffle share dimethyl sulfide, and truffle and vanilla share vanillin — the lactonic compound that black truffle produces through enzymatic fermentation. The three-way vanillin connection creates an unusual earthy-sweet-roasted compound alignment for a luxury sauce.",
     "Truffle Vanilla Espresso Pasta",
     ["Melt truffle butter with a tiny shot of espresso and vanilla bean seeds in a wide pan.", "Toss al dente pasta with the glossy sauce and a splash of pasta water.", "Plate; shave fresh truffle and a vanilla bean pod curl as garnish; serve immediately."]),

    ("cucumber","garlic","lamb",
     "Cucumber and garlic share no direct compound but work through aromatic contrast — cucumber's (E)-2-nonenal cool freshness against garlic's allicin pungency — while both independently modulate lamb's gamey 4-methyloctanoic acid: garlic through allicin-acid interaction and cucumber through watery dilution of the animal-fat register. The trio defines Greek tzatziki with lamb.",
     "Garlic Cucumber Tzatziki with Lamb Kofta",
     ["Make kofta: mix ground lamb with garlic, cumin, and herbs; shape onto skewers and grill.", "Make tzatziki: grated cucumber squeezed dry, yogurt, garlic, lemon, olive oil, and dill.", "Serve kofta over warm flatbread with a generous spoonful of tzatziki and lemon wedges."]),

    ("cucumber","garlic","lavender",
     "Cucumber's (E)-2-nonenal cool freshness contrasts with garlic's allicin pungency through a sharp-clean opposition, while lavender's linalool provides floral softening that mediates between the two extremes — bridging the cool-watery and pungent-allium registers into a coherent Provençal preparation. The trio drives sophisticated herb-garlic dip preparations.",
     "Lavender Garlic Cucumber Dip",
     ["Blend grated and squeezed cucumber with garlic, dried lavender, yogurt, and lemon juice.", "Add olive oil; blend until smooth and season with salt and white pepper.", "Serve chilled with warm flatbread and crudités; the lavender lifts the garlic-cucumber combination."]),

    ("cucumber","garlic","lemon",
     "Cucumber and lemon share geraniol — a floral-citrus terpene present in both cucumber's minor aromatics and lemon peel oil — while garlic's allicin converts to sweet cooked-garlic notes that lemon's citric acid moderates through pH adjustment. The trio is the chemical basis of classic Greek salad dressing and tzatziki.",
     "Lemon Garlic Cucumber Greek Salad",
     ["Dice cucumber, tomatoes, and red onion; add Kalamata olives and crumbled feta.", "Dress with lemon juice, lemon zest, minced garlic, and good olive oil.", "Season with dried oregano and flaky salt; rest 10 minutes before serving."]),

    ("cucumber","garlic","mint",
     "Cucumber and mint share (E)-2-nonenal and linalool — the cool-watery and herbal-terpene compounds that amplify the fresh, green register of both — while garlic's dimethyl sulfide provides savory grounding that prevents the double-cool herb-vegetable combination from being flat. The trio defines Persian mast-o-khiar and South Asian cucumber raita.",
     "Mint Garlic Cucumber Raita",
     ["Grate cucumber; squeeze out excess water in a clean towel.", "Mix with yogurt, minced garlic, fresh mint, cumin, and lemon juice.", "Season with salt; serve chilled as a cooling accompaniment to spiced meats or biryani."]),
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
print(f"Batch 039 done: inserted {len(TRIPLETS)} triplets.")
