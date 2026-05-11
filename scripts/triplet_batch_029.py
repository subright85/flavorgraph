#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("caramel","parmesan","salmon",
     "Caramel and Parmesan share furaneol and butyric acid — sweet-caramel and fatty-dairy compounds — while caramel's Maillard sweetness simultaneously suppresses salmon's trimethylamine marine notes and amplifies Parmesan's fermented-sweet register. The trio creates a rich savory-sweet crust preparation where dairy umami and caramel sweetness work in tandem against fatty fish.",
     "Caramel Parmesan Crusted Salmon",
     ["Mix grated Parmesan with a drizzle of dark caramel, breadcrumbs, garlic, and herbs into a paste.", "Press firmly onto salmon fillets; bake at 400°F for 12 minutes until the crust is golden and salmon just cooked.", "Serve with lemon and a caramel-parmesan pan sauce made from the drippings."]),

    ("caramel","parmesan","strawberry",
     "Caramel, Parmesan, and strawberry all share furaneol — the sweet-caramel compound that spans Maillard chemistry, aged dairy fermentation, and ripe fruit — making this one of the few triplets with the same key compound in all three ingredients. The combination creates an Italian-inspired sweet-savory dessert where furaneol's presence in every component creates unusual aromatic unity.",
     "Strawberry Caramel Parmesan Salad",
     ["Slice ripe strawberries; toss with a drizzle of dark caramel, aged balsamic, and torn fresh basil.", "Arrange on a plate; shave aged Parmesan Reggiano generously with a vegetable peeler.", "Finish with cracked pepper, flaky salt, and good olive oil; serve immediately before the caramel sets."]),

    ("caramel","parmesan","tomato",
     "Caramel, Parmesan, and tomato all share furaneol — the sweet-caramel compound at the heart of Maillard sweetness, aged dairy, and ripe tomato alike — creating a triple furaneol alignment that produces maximum sweet-umami-savory depth. The trio is the flavor foundation of caramelized onion-tomato-Parmesan preparations and sophisticated pizza bianca.",
     "Caramel Tomato Parmesan Tart",
     ["Caramelize a large quantity of onions until deeply golden; stir in crushed tomatoes and a drizzle of caramel.", "Spread into a blind-baked tart shell; top with thick slices of ripe tomato and grated Parmesan.", "Bake at 375°F until the cheese is bubbling and tomatoes are slightly caramelized; serve warm."]),

    ("caramel","parmesan","truffle",
     "Caramel and Parmesan share furaneol and butyric acid — sweet-caramel and fatty-dairy compounds — while Parmesan and truffle share phenylacetaldehyde and dimethyl sulfide, creating a chain-compound connection where caramel sweetens Parmesan's dairy-umami and truffle deepens it with earthy fungal aromatics. The trio creates the richest possible umami preparation.",
     "Truffle Caramel Parmesan Fondue",
     ["Melt aged Gruyère and Parmesan with white wine; stir in truffle butter and a drizzle of dark caramel.", "Keep warm in a fondue pot; the caramel rounds the cheese's sharpness while truffle adds earthy depth.", "Serve with crusty bread, apple slices, and vegetables for dipping at the table."]),

    ("caramel","parmesan","vanilla",
     "Caramel, Parmesan, and vanilla all share furaneol and vanillin — the sweet-caramel and lactonic compounds spanning Maillard chemistry, aged dairy, and cured vanilla bean. This triple shared-compound alignment creates a complete sweet-lactonic-savory register that appears in sophisticated Italian savory-dessert crossover preparations.",
     "Vanilla Caramel Parmesan Panna Cotta",
     ["Warm cream with split vanilla bean and a drizzle of caramel; steep 20 minutes and strain.", "Dissolve gelatin; stir in finely grated Parmesan and pour into molds to set 4 hours in the refrigerator.", "Unmold; serve drizzled with warm dark caramel sauce and shaved Parmesan."]),

    ("caramel","rose","salmon",
     "Caramel's sweetness suppresses salmon's trimethylamine marine notes through the sweet-compound masking mechanism — the teriyaki principle — while rose's 2-phenylethanol provides a floral aromatic that displaces trimethylamine through a second, different mechanism, giving a double trimethylamine reduction. The trio produces an aromatic, clean-tasting glazed salmon.",
     "Rose Caramel Glazed Salmon",
     ["Make a rose-caramel glaze: amber caramel, rose water, rice vinegar, and a touch of soy sauce.", "Brush salmon fillets generously; bake at 425°F for 10 minutes, glazing once halfway through.", "Garnish with rose petals and serve over jasmine rice with a rose water and caramel drizzle."]),

    ("caramel","rose","strawberry",
     "Caramel and strawberry share furaneol as their dominant sweet-caramel compound, while rose shares 2-phenylethanol and linalool with strawberry's dominant floral esters — creating a dual compound connection where caramel deepens strawberry's sweet register and rose elevates its floral dimension simultaneously. The trio is romantic dessert flavor at its most precise.",
     "Rose Caramel Strawberry Pavlova",
     ["Fold rose water into meringue; bake at 250°F for 90 minutes until crisp outside, soft inside.", "Make rose-caramel: cook sugar to amber, add rose-water cream, and cool to a drizzleable consistency.", "Top meringue with whipped cream, macerated strawberries, and drizzle rose caramel generously."]),

    ("caramel","rose","tomato",
     "Caramel and tomato share furaneol — sweet-caramel at the core of both — while rose's 2-phenylethanol provides a floral softening that rounds tomato's acidity through aromatic displacement, the same principle behind Turkish rose-tomato jam. Caramel's Maillard depth amplifies tomato's own caramel notes while rose lifts the combination into a perfumed register.",
     "Rose Caramel Tomato Jam",
     ["Cook ripe tomatoes with sugar until thick and jammy; add a drizzle of dark caramel and a splash of rose water.", "Simmer until glossy and concentrated; season with a pinch of salt and flaky sea salt to finish.", "Cool and jar; serve with cheese, on toast, or as a glaze for roasted meats."]),

    ("caramel","rose","truffle",
     "Rose and truffle share phenylacetaldehyde — the rosy-fermented compound that both produce through unrelated biochemical pathways — while caramel's warm Maillard sweetness bridges the floral-luxury and earthy-luxury registers by softening truffle's dense earthiness into a more approachable sweet-floral-earthy combination. The trio is haute cuisine at maximum aromatic contrast.",
     "Rose Truffle Caramel Butter",
     ["Beat softened butter with truffle paste, rose water, a drizzle of caramel, and flaky salt.", "Refrigerate in a log until firm; slice into rounds.", "Melt over risotto, scrambled eggs, or warm brioche — the rose and caramel lift truffle into an ethereal register."]),

    ("caramel","rose","vanilla",
     "Caramel and vanilla share furaneol and vanillin — sweet-caramel and lactonic compounds — while rose shares 2-phenylethanol and linalool with vanilla's floral profile, creating a chain of compound connections from caramel's Maillard warmth through vanilla's lactonic sweetness to rose's floral register. The trio is the most complete sweet-floral-lactonic combination possible.",
     "Rose Vanilla Caramel Crème Caramel",
     ["Make a dark caramel; pour into ramekins to coat the base.", "Infuse warm cream with vanilla bean and rose water; whisk into eggs and strain over the caramel.", "Bake in a water bath at 325°F until set; chill overnight and unmold with crystallized rose petals."]),

    ("caramel","salmon","strawberry",
     "Caramel and strawberry share furaneol — the sweet-caramel compound that dominates both — while caramel's Maillard sweetness independently suppresses salmon's trimethylamine, and strawberry's furaneol echoes and extends caramel's dominant compound over the palate. The trio creates an unusually cohesive sweet-fish preparation with summer fruit brightness.",
     "Caramel Strawberry Glazed Salmon",
     ["Blend fresh strawberries with caramel sauce and rice vinegar into a smooth glaze; reduce until syrupy.", "Brush salmon fillets; bake at 425°F for 10 minutes, brushing once more halfway through.", "Garnish with sliced fresh strawberry and serve over arugula dressed with the caramel-strawberry reduction."]),

    ("caramel","salmon","tomato",
     "Caramel and tomato share furaneol — the compound at the heart of both — while caramel's sweetness suppresses salmon's trimethylamine marine notes, and tomato's acidity brightens the combination through acid-sweet contrast. The trio creates a sophisticated teriyaki-meets-Italian glazed salmon preparation.",
     "Caramel Tomato Braised Salmon",
     ["Make a caramel-tomato sauce: amber caramel deglazed with crushed San Marzano tomatoes; simmer 15 minutes.", "Nestle salmon fillets into the sauce; cover and cook at a gentle simmer for 8 minutes.", "Serve salmon over pasta or polenta with the caramel-tomato sauce and fresh basil."]),

    ("caramel","salmon","truffle",
     "Caramel and truffle share Maillard-derived aromatic complexity — dimethyl sulfide appearing in both — while caramel's sweetness suppresses salmon's trimethylamine through sweet-compound masking, and truffle's dimethyl sulfide adds earthiness that converts the marine note into a deeper savory register. The trio is classic French haute cuisine glazed salmon territory.",
     "Truffle Caramel Glazed Salmon",
     ["Make a truffle-caramel glaze: dark caramel, truffle oil, soy sauce, and mirin reduced to syrupy.", "Brush salmon fillets generously; bake at 425°F for 10 minutes, brushing once more halfway.", "Shave truffle over the finished salmon; serve over potato purée with a truffle caramel drizzle."]),

    ("caramel","salmon","vanilla",
     "Caramel and vanilla share furaneol and vanillin — sweet-caramel and lactonic compounds — and both suppress salmon's trimethylamine through sweet-compound masking, giving a double trimethylamine reduction with a warm lactonic register. Vanilla-caramel poached or glazed salmon is a French technique where the sweet-spice combination transforms fatty fish aromatics completely.",
     "Vanilla Caramel Poached Salmon",
     ["Make a court bouillon with white wine, split vanilla bean, caramelized shallots, and aromatics.", "Poach salmon at barely a simmer for 10 minutes until just cooked through; remove carefully.", "Serve with a vanilla-caramel beurre blanc made from the court bouillon reduced and finished with butter."]),

    ("caramel","strawberry","tomato",
     "Caramel, strawberry, and tomato all share furaneol — the sweet-caramel compound at the heart of all three — making this a triple-furaneol combination of unusual aromatic unity. Tomato's acidity and strawberry's fruit freshness balance caramel's Maillard richness, creating a summer sauce or gazpacho base where the three furaneol sources create extraordinary depth.",
     "Caramel Strawberry Tomato Gazpacho",
     ["Blend ripe tomatoes with fresh strawberries, a drizzle of caramel, garlic, and olive oil until smooth.", "Season with sherry vinegar, salt, and white pepper; strain for a silky texture.", "Serve very cold with diced strawberry, a swirl of caramel, and a drizzle of good olive oil."]),

    ("caramel","strawberry","truffle",
     "Caramel and strawberry share furaneol — their dominant sweet-caramel compound — while truffle and strawberry share phenylacetaldehyde, the rosy-fermented compound that both earthy fungus and ripe berry produce independently. Caramel's warm sweetness bridges these two unusual aromatic dimensions into an opulent dessert-savory luxury preparation.",
     "Truffle Strawberry Caramel Risotto",
     ["Cook arborio risotto until creamy; off heat stir in mascarpone, a drizzle of caramel, and lemon zest.", "Fold in diced fresh strawberry and a drizzle of truffle oil; season precisely.", "Shave generous fresh truffle over the top; finish with a caramel drizzle and whole strawberries."]),

    ("caramel","strawberry","vanilla",
     "Caramel, strawberry, and vanilla share furaneol and linalool — the most complete three-way aromatic overlap in the sweet-dessert flavor family — while vanilla also contributes vanillin and caramel adds Maillard depth not present in the other two, creating a complete sweet-floral-warm-caramel dessert foundation. This trio is summer dessert's most precise flavor logic.",
     "Caramel Strawberry Vanilla Shortcakes",
     ["Macerate sliced strawberries with vanilla extract, caramel sauce, and lemon juice for 30 minutes.", "Bake fluffy buttermilk biscuits; split while warm and layer with vanilla caramel whipped cream.", "Spoon the macerated strawberry mixture generously over and drizzle warm caramel over the top."]),

    ("caramel","tomato","truffle",
     "Caramel and tomato share furaneol — their dominant sweet-caramel compound — while tomato and truffle share dimethyl sulfide and phenylacetaldehyde, creating a chain where caramel sweetens tomato's savory depth and truffle deepens tomato's earthy-umami register. The trio creates a sophisticated luxury tomato sauce preparation found in high-end Italian truffle pasta.",
     "Truffle Caramel Tomato Sauce",
     ["Simmer crushed San Marzano tomatoes with garlic until reduced; stir in a drizzle of dark caramel.", "Off heat, add truffle butter and toss with al dente pasta until glossy and coating each strand.", "Plate, shave fresh truffle generously, and finish with a drizzle of truffle oil."]),

    ("caramel","tomato","vanilla",
     "Caramel, tomato, and vanilla all share furaneol — the sweet-caramel compound spanning Maillard chemistry, ripe tomato, and cured vanilla bean — while vanilla also contributes vanillin which rounds and deepens tomato's caramelized sweetness. The three-way furaneol alignment creates a sophisticated tomato confiture or chutney where sweetness has unusual depth.",
     "Vanilla Caramel Tomato Confit",
     ["Halve cherry tomatoes, place in a baking dish with a split vanilla bean, garlic, and olive oil.", "Add a drizzle of dark caramel; roast at 250°F for 2 hours until concentrated and jammy.", "Use warm over pasta, cheese, or toast; the vanilla amplifies the tomato's own furaneol sweetness."]),

    ("caramel","truffle","vanilla",
     "Caramel and vanilla share furaneol and vanillin — the most direct sweet-caramel compound overlap — while truffle and vanilla share vanillin as a key aromatic component, black truffle producing trace vanillin through its enzymatic fermentation process. The three-way vanillin connection creates an unusual earthy-sweet-lactonic combination for luxury compound butter or sauce.",
     "Truffle Vanilla Caramel Compound Butter",
     ["Beat softened butter with truffle paste, vanilla bean seeds, a drizzle of dark caramel, and flaky salt.", "Refrigerate in a log shape until firm; slice into rounds.", "Serve melting over warm brioche, risotto, or a seared scallop — earthy, sweet, and lactonic simultaneously."]),
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
print(f"Batch 029 done: inserted {len(TRIPLETS)} triplets.")
