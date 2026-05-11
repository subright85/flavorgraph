#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("cucumber","rose","strawberry",
     "Cucumber, rose, and strawberry share 2-phenylethanol and linalool — the rosy-floral and herbal terpenes connecting all three through their respective green-vegetable, floral, and fruit aromatic profiles — while strawberry adds furaneol sweetness that bridges rose's perfume to cucumber's freshness. The trio is a complete cool-floral-sweet summer combination.",
     "Rose Strawberry Cucumber Salad",
     ["Slice ripe strawberries and cucumber; toss gently with rose water, lemon juice, and a pinch of sugar.", "Add torn fresh mint and a drizzle of rose-infused oil.", "Scatter dried rose petals and serve as a salad or dessert — the three-way linalool creates deep freshness."]),

    ("cucumber","rose","tomato",
     "Cucumber and tomato share hexanal — the green aldehyde defining garden freshness in both — while rose's 2-phenylethanol provides floral softening that rounds tomato's acidity. The trio creates a sophisticated Turkish-inspired tomato-rose salad where cucumber's cool freshness and rose's floral warmth bracket tomato's savory depth.",
     "Rose Cucumber Tomato Salad",
     ["Slice ripe tomatoes and cucumber; arrange on a platter.", "Dress with a splash of rose water, good olive oil, lemon juice, and flaky salt.", "Scatter dried rose petals and fresh herbs; the rose softens tomato's acidity beautifully."]),

    ("cucumber","rose","truffle",
     "Cucumber's (E)-2-nonenal cool freshness contrasts with truffle's dimethyl sulfide earthiness — the ultimate clean-watery against earthy opposition — while rose's 2-phenylethanol provides floral bridging between the two extremes, and rose and truffle share phenylacetaldehyde through their separate fermentation chemistries. The trio creates an opulent floral luxury preparation.",
     "Rose Truffle Cucumber Canapés",
     ["Make truffle cream: mascarpone, truffle paste, and rose water whipped together.", "Spread onto thick cucumber rounds; top with a sliver of fresh truffle.", "Finish with a dried rose petal and fleur de sel; the rose bridges truffle's earthiness and cucumber's freshness."]),

    ("cucumber","rose","vanilla",
     "Cucumber and rose share 2-phenylethanol and linalool while rose and vanilla share the same pair of compounds — creating a three-way linalool-2-phenylethanol alignment from cool-watery cucumber through floral-warm rose to sweet-lactonic vanilla. The trio creates an extraordinarily fragrant dessert where every ingredient connects to both others.",
     "Rose Vanilla Cucumber Panna Cotta",
     ["Infuse cream with vanilla bean and rose water; strain and dissolve gelatin.", "Add cucumber juice for subtle freshness; pour into molds and refrigerate 4 hours.", "Unmold; serve with cucumber ribbons dressed in rose water honey."]),

    ("cucumber","salmon","strawberry",
     "Cucumber and salmon share (E)-2-nonenal — the clean watery compound in both — while strawberry's furaneol sweetness suppresses salmon's trimethylamine through sweet-compound masking and cucumber's freshness adds a second olfactory cooling of marine notes. The double TMA suppression with sweet-fresh summer character defines this Nordic salad.",
     "Strawberry Cucumber Salmon Salad",
     ["Cure or smoke salmon; slice thin and arrange on a platter with cucumber ribbons and sliced strawberry.", "Dress with a strawberry-lemon vinaigrette: blended strawberry, lemon juice, and olive oil.", "Add fresh dill and flaky salt; the strawberry and cucumber together suppress marine notes beautifully."]),

    ("cucumber","salmon","tomato",
     "Cucumber, salmon, and tomato share hexanal and (E)-2-nonenal — the green aldehyde compounds of garden freshness — with cucumber and salmon sharing (E)-2-nonenal and cucumber and tomato sharing hexanal. The overlapping compound families create an unusually coherent summer seafood salad where vegetable freshness is native to the fish.",
     "Cucumber Tomato Salmon Salad",
     ["Mix flaked cooked salmon with diced cucumber, ripe tomato, and red onion.", "Dress with lemon juice, olive oil, capers, and fresh dill.", "Season with flaky salt; serve on sourdough toast or over crisp lettuce leaves."]),

    ("cucumber","salmon","truffle",
     "Cucumber and salmon share (E)-2-nonenal while truffle and salmon share dimethyl sulfide — creating a compound chain where cucumber's freshness ties to salmon's marine freshness and truffle's earthiness ties to salmon's sulfurous register simultaneously. Cucumber's cool watery contrast prevents the truffle-salmon luxury combination from being too heavy.",
     "Truffle Salmon with Cucumber",
     ["Sear salmon skin-side down until crisp; finish in a 400°F oven 8 minutes.", "Make a truffle cucumber salad: cucumber ribbons, truffle oil, lemon, and fleur de sel.", "Serve salmon over the truffle-cucumber salad; shave fresh truffle over generously."]),

    ("cucumber","salmon","vanilla",
     "Cucumber and salmon share (E)-2-nonenal while vanilla's vanillin sweetness suppresses salmon's trimethylamine through sweet-compound masking — the French vanilla-poached salmon technique. Cucumber's cool freshness provides a second TMA suppression through olfactory cooling, creating a delicate aromatic salmon preparation.",
     "Vanilla Cucumber Poached Salmon",
     ["Make a court bouillon with white wine, split vanilla bean, and sliced cucumber.", "Poach salmon at barely a simmer for 10 minutes; remove carefully.", "Serve over thin cucumber slices with a vanilla-cucumber beurre blanc."]),

    ("cucumber","strawberry","tomato",
     "Cucumber, strawberry, and tomato share hexanal — the green aldehyde compound defining garden freshness in all three — and strawberry and tomato additionally share furaneol, the sweet-caramel compound. The triple hexanal alignment with a furaneol subcombination creates the most fresh, garden-forward trio possible for summer salads.",
     "Strawberry Cucumber Tomato Gazpacho",
     ["Blend ripe tomatoes with fresh strawberries, cucumber, garlic, and olive oil until smooth.", "Season with sherry vinegar, salt, and white pepper; strain for silky texture.", "Serve very cold with diced strawberry, cucumber, and a drizzle of good olive oil."]),

    ("cucumber","strawberry","truffle",
     "Cucumber's (E)-2-nonenal and strawberry's furaneol contrast through cool-watery against sweet-caramel while truffle and strawberry share phenylacetaldehyde through their separate fermentation chemistries. Cucumber's freshness prevents the indulgent truffle-strawberry luxury combination from being too heavy.",
     "Truffle Strawberry Cucumber Salad",
     ["Slice ripe strawberries and cucumber; arrange on a chilled plate.", "Drizzle with truffle honey and a squeeze of lemon juice.", "Shave fresh truffle generously over the top; the cucumber freshness lifts the sweet-earthy combination."]),

    ("cucumber","strawberry","vanilla",
     "Cucumber, strawberry, and vanilla share linalool — the herbal-floral terpene connecting all three through their respective fresh-green, fruity, and sweet-lactonic aromatics — while strawberry and vanilla additionally share furaneol and 2-phenylethanol. The triple linalool with additional compound overlap creates a complete cool-sweet-floral summer dessert.",
     "Vanilla Strawberry Cucumber Sorbet",
     ["Blend fresh strawberries with cucumber juice, vanilla bean seeds, and lemon juice.", "Sweeten to taste; churn until smooth and freeze until firm.", "Serve scooped with a cucumber ribbon and strawberry fan — cool, sweet, and floral simultaneously."]),

    ("cucumber","tomato","truffle",
     "Cucumber and tomato share hexanal — the green aldehyde of garden freshness — while truffle and tomato share dimethyl sulfide and phenylacetaldehyde through roasted and fermented chemistry. Cucumber's cool freshness prevents the earthy truffle-tomato luxury combination from being too heavy, providing essential aromatic balance.",
     "Truffle Tomato Cucumber Bruschetta",
     ["Top toasted sourdough with ripe diced tomato dressed in olive oil, salt, and a drizzle of truffle oil.", "Add thin cucumber slices and shaved truffle.", "Finish with fleur de sel; the cucumber freshness lifts both tomato and truffle simultaneously."]),

    ("cucumber","tomato","vanilla",
     "Cucumber and tomato share hexanal — the green aldehyde of garden freshness — while tomato and vanilla share furaneol, the sweet-caramel compound at the heart of both ripe tomato and cured vanilla bean. Cucumber's cool watery freshness bridges the unusual sweet-savory tomato-vanilla combination through garden-fresh grounding.",
     "Vanilla Tomato Cucumber Salad",
     ["Slice ripe tomatoes; dress with a split vanilla bean scraped into olive oil, lemon, and salt.", "Add cucumber ribbons and fresh herbs.", "The vanilla amplifies tomato's natural furaneol sweetness while cucumber provides fresh contrast."]),

    ("cucumber","truffle","vanilla",
     "Cucumber's (E)-2-nonenal cool freshness contrasts with both truffle's dimethyl sulfide earthiness and vanilla's vanillin sweetness — the clean-watery element bracketing two rich, complex aromatics. Truffle and vanilla share vanillin, creating a direct compound connection, while cucumber provides the essential lightness that makes the luxury duo accessible.",
     "Truffle Vanilla Cucumber Canapés",
     ["Make truffle-vanilla cream: mascarpone, truffle paste, vanilla bean seeds, and a pinch of salt.", "Spread onto thick cucumber rounds and top with a tiny shaving of fresh truffle.", "Finish with fleur de sel; the cucumber's freshness lifts the rich truffle-vanilla combination."]),

    ("garlic","lamb","lavender",
     "Garlic and lamb share dimethyl sulfide — the sulfurous compound spanning allium and animal-fat metabolisms — while lavender's linalool softens lamb's gamey 4-methyloctanoic acid through floral displacement, and garlic's roasted sweetness grounds lavender's floral lightness into a coherent savory-Provençal register. The trio defines classic Provençal gigot d'agneau.",
     "Provençal Garlic Lavender Leg of Lamb",
     ["Stud a leg of lamb with garlic slivers; rub generously with dried lavender, olive oil, and herbes de Provence.", "Roast at 325°F for 3 hours, basting occasionally; the lavender and garlic form a fragrant crust.", "Rest 20 minutes; serve with lavender-garlic jus and roasted root vegetables."]),

    ("garlic","lamb","lemon",
     "Garlic and lamb share dimethyl sulfide — the sulfurous compound connecting allium and animal-fat chemistry — while lemon's citric acid suppresses lamb's gamey 4-methyloctanoic acid through pH-driven acid-fat modulation and converts garlic's allicin into less pungent breakdown products simultaneously. The trio defines Greek souvlaki and Italian agnello al limone.",
     "Lemon Garlic Grilled Lamb Chops",
     ["Marinate lamb chops in lemon juice, zest, minced garlic, olive oil, and oregano for 2 hours.", "Grill over high heat until charred and crisp at the edges.", "Serve with a squeeze of fresh lemon, garlic tzatziki, and warm pita."]),

    ("garlic","lamb","mint",
     "Garlic and lamb share dimethyl sulfide while mint's menthol provides olfactory cooling that suppresses lamb's gamey 4-methyloctanoic acid — the classic mint sauce mechanism — and garlic's cooked sweetness rounds mint's sharpness. The trio creates the definitive lamb-herb combination across British, Levantine, and Turkish culinary traditions.",
     "Mint Garlic Lamb Meatballs",
     ["Mix ground lamb with minced garlic, chopped fresh mint, cumin, allspice, and breadcrumbs.", "Roll into balls; brown in olive oil until crusted; finish in spiced tomato sauce 15 minutes.", "Serve with yogurt, fresh mint, and warm flatbread to scoop."]),

    ("garlic","lamb","oyster",
     "Garlic, lamb, and oyster share dimethyl sulfide — the sulfurous compound spanning allium, animal fat, and marine bivalve chemistry — creating a three-way sulfurous alignment across radically different food categories. The combination is the flavor of Cantonese oyster sauce braised lamb where garlic and marine umami deepen the long-cooked meat register.",
     "Oyster Sauce Garlic Braised Lamb",
     ["Brown lamb shoulder; add sliced garlic, oyster sauce, soy, star anise, and stock.", "Braise at 325°F for 2.5 hours until meltingly tender; reduce sauce until glossy.", "Serve over steamed rice with scallion oil; the garlic-oyster sauce amplifies lamb's savory depth."]),

    ("garlic","lamb","parmesan",
     "Garlic and lamb share dimethyl sulfide while Parmesan and lamb share butyric acid and dimethyl sulfide — the fatty-acid and sulfurous compound family spanning allium, animal fat, and aged dairy. The triple compound connection creates a coherent savory register for Italian lamb preparations where Parmesan adds umami and garlic adds allium depth.",
     "Parmesan Garlic Stuffed Lamb",
     ["Mix Parmesan, roasted garlic, herbs, and breadcrumbs into a stuffing.", "Butterfly a leg of lamb; spread stuffing over and roll tightly; tie with twine.", "Roast at 350°F until internal temperature reaches 130°F; rest 15 minutes before slicing."]),

    ("garlic","lamb","rose",
     "Garlic and lamb share dimethyl sulfide while rose's 2-phenylethanol and geraniol soften lamb's gamey 4-methyloctanoic acid through floral displacement — the Persian rose-water lamb mechanism — and garlic's roasted sweetness grounds rose's perfumed delicacy into a savory register. The trio defines Iranian khoresh recipes.",
     "Rose Garlic Persian Lamb",
     ["Brown lamb with caramelized onion and garlic; add rose water, saffron, and walnuts.", "Braise 1.5 hours until tender; stir in pomegranate molasses and dried rose petals.", "Serve over saffron rice; the rose and garlic create a fragrant-savory layered stew."]),
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
print(f"Batch 043 done: inserted {len(TRIPLETS)} triplets.")
