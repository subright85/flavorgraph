#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("lavender","parmesan","salmon",
     "Lavender's linalool and linalyl acetate suppress salmon's trimethylamine through floral aromatic displacement — the same mechanism as dill — while Parmesan's butyric acid and glutamate umami provide a savory anchor that prevents the lavender-fish pairing from reading as perfumed. The trio creates a Provençal baked salmon preparation.",
     "Lavender Parmesan Crusted Salmon",
     ["Mix breadcrumbs with grated Parmesan, dried lavender, lemon zest, and olive oil.", "Press firmly onto salmon fillets; bake at 400°F for 12 minutes until the crust is golden.", "Serve with a lavender-lemon butter sauce and a sprinkle of dried lavender over the crust."]),

    ("lavender","parmesan","strawberry",
     "Lavender and strawberry share linalool and furaneol — floral terpene and sweet-caramel compounds — while Parmesan's butyric acid and furaneol provide the savory-sweet anchor that grounds the perfumed floral-fruit combination. The Italian tradition of aged cheese with fruit and the Provençal use of lavender meet in this unusual trio.",
     "Lavender Strawberry Parmesan Salad",
     ["Arrange halved strawberries on a plate with shaved Parmesan and a drizzle of lavender honey.", "Scatter a pinch of dried lavender flowers and cracked black pepper over the top.", "Finish with a squeeze of lemon and good olive oil; serve immediately."]),

    ("lavender","parmesan","tomato",
     "Lavender and tomato form the Provençal pairing where lavender's linalool contrasts with tomato's furaneol sweetness — the Niçoise principle — while Parmesan's glutamate and furaneol amplify tomato's natural umami-sweet register into a richer, more complex savory base. The trio creates a refined tarte fine preparation.",
     "Lavender Tomato Parmesan Tarte Fine",
     ["Roll puff pastry very thin; scatter grated Parmesan over, then overlap sliced tomatoes.", "Sprinkle a pinch of dried lavender and olive oil over; bake at 400°F for 20 minutes.", "Serve warm with a last drizzle of lavender oil and extra Parmesan at the table."]),

    ("lavender","parmesan","truffle",
     "Lavender and truffle share anisaldehyde — the anise-adjacent aromatic — while Parmesan and truffle share phenylacetaldehyde and dimethyl sulfide — the fermented-rosy and sulfurous compound pair — creating a double-bridge where lavender connects to truffle through anise and Parmesan connects through fermentation chemistry. The trio is extraordinary.",
     "Lavender Truffle Parmesan Risotto",
     ["Cook arborio risotto until creamy; off heat stir in truffle butter and cold Parmesan.", "Add a tiny pinch of dried lavender and a splash of pasta water; stir until glossy.", "Plate, shave generous truffle over, and finish with a single lavender flower on each bowl."]),

    ("lavender","parmesan","vanilla",
     "Lavender and vanilla share linalool and linalyl acetate — the dominant floral terpenes in both — while Parmesan's vanillin from aging and butyric acid provide the savory-sweet bridge that grounds the perfumed floral-sweet combination. The trio creates a sophisticated savory-sweet compound that works in refined cheese pastry applications.",
     "Lavender Vanilla Parmesan Shortbread",
     ["Blend cold butter with Parmesan, flour, vanilla bean seeds, and dried lavender until crumbly.", "Press into a tart pan or cut into rounds; refrigerate 20 minutes before baking.", "Bake at 325°F until just golden; serve with lavender honey for dipping."]),

    ("lavender","rose","salmon",
     "Lavender and rose share 2-phenylethanol, linalool, and geraniol — the complete floral terpene overlap — and together provide the strongest possible floral aromatic displacement of salmon's trimethylamine, while their shared linalool creates a unified floral register over the fatty fish. The double-floral salmon preparation is Provençal-Persian in character.",
     "Rose Lavender Persian Salmon",
     ["Marinate salmon in rose water, dried lavender, saffron, lemon, and olive oil for 30 minutes.", "Bake at 400°F for 12 minutes; make a rose-lavender butter with rose water and lavender.", "Serve topped with the compound butter, rose petals, and dried lavender flowers."]),

    ("lavender","rose","strawberry",
     "Lavender, rose, and strawberry share 2-phenylethanol, linalool, and furaneol — the most complete three-way floral-sweet compound overlap in the culinary set — with each ingredient reinforcing the others' dominant aromatic compounds. The trio creates the most concentrated floral-sweet dessert register possible.",
     "Rose Lavender Strawberry Layer Cake",
     ["Bake a rose water-scented sponge; brush each layer with lavender-lemon syrup.", "Fill with a rose-mascarpone cream; frost with lavender buttercream.", "Decorate with fresh strawberries, rose petals, and dried lavender flowers over the top."]),

    ("lavender","rose","tomato",
     "Lavender, rose, and tomato combine the Provençal and Turkish aromatic principles — both cuisines use rose and lavender with tomato — where lavender's linalool contrasts tomato's furaneol and rose's geraniol softens tomato's acidity through floral displacement. The trio creates a refined slow-roasted tomato or cold soup preparation.",
     "Rose Lavender Tomato Gazpacho",
     ["Blend ripe tomatoes with cucumber, garlic, rose water, and a pinch of dried lavender until smooth.", "Strain through a fine sieve; season with sherry vinegar, olive oil, salt, and white pepper.", "Serve chilled in bowls with rose petals, lavender flowers, and a drizzle of rose-olive oil."]),

    ("lavender","rose","truffle",
     "Lavender, rose, and truffle form a triple-anisaldehyde-phenylacetaldehyde combination — all three produce these rosy-anise aromatic compounds — making this the most rosy-anise-intense preparation in the entire culinary set. The trio requires restraint but creates extraordinary aromatic depth when balanced correctly.",
     "Rose Lavender Truffle Compound Butter",
     ["Beat softened butter with rose water, truffle paste, dried lavender, and flaky salt.", "Mix until completely smooth; roll into a log in plastic wrap and refrigerate until firm.", "Slice and serve melting over warm brioche, scrambled eggs, or a seared scallop."]),

    ("lavender","rose","vanilla",
     "Lavender, rose, and vanilla share linalool, 2-phenylethanol, and linalyl acetate — the complete floral-sweet terpene overlap across all three — creating the most intensely perfumed sweet preparation in the culinary set. The trio requires balancing with acid to prevent the floral-sweet from becoming overwhelming.",
     "Lavender Rose Vanilla Panna Cotta",
     ["Infuse cream with split vanilla bean, dried lavender, and rose water; steep 30 minutes, strain.", "Dissolve gelatin, sweeten very lightly, pour into molds, and refrigerate 4 hours.", "Unmold; serve with rose-berry coulis, rose petals, and a sprig of dried lavender."]),

    ("lavender","salmon","strawberry",
     "Lavender's linalool suppresses salmon's trimethylamine while strawberry's furaneol and linalool provide sweet-floral contrast to the fatty fish — a two-pronged aromatic approach to making salmon more aromatic — while their shared linalool creates a coherent floral-sweet register above the marine base. The trio creates a summer salmon salad.",
     "Lavender Strawberry Salmon Salad",
     ["Pan-sear salmon fillets with a drizzle of lavender honey until just cooked; cool slightly.", "Arrange over mixed greens with sliced strawberries and a lavender-strawberry vinaigrette.", "Finish with dried lavender flowers, crumbled feta, and cracked pepper."]),

    ("lavender","salmon","tomato",
     "Lavender's linalool contrasts with both salmon's marine dimethyl sulfide and tomato's furaneol sweetness — Provençal aromatic displacement working on two ingredients simultaneously — while tomato's acidity bridges salmon and lavender through the Mediterranean acid-herb principle. The trio creates a Provençal baked salmon preparation.",
     "Lavender Tomato Baked Salmon",
     ["Arrange salmon fillets in a baking dish over a bed of sliced tomatoes with lavender sprigs.", "Drizzle with olive oil, season, and bake at 375°F for 15 minutes until salmon is just done.", "Serve with the roasted lavender-tomatoes spooned over and fresh herbs."]),

    ("lavender","salmon","truffle",
     "Lavender and truffle share anisaldehyde while lavender and salmon share linalool terpene displacement — lavender working as a floral aromatic bridge between truffle's earthiness and salmon's marine register — while truffle's dimethyl sulfide creates a sulfurous connection to salmon's marine aromatic family. The trio is luxurious and precisely balanced.",
     "Lavender Truffle Salmon",
     ["Sear salmon skin-side down in truffle oil until skin is crisp; flip and finish briefly.", "Meanwhile make a lavender-truffle beurre blanc by infusing butter with lavender and truffle.", "Serve salmon with the sauce; shave fresh truffle over and finish with a lavender flower."]),

    ("lavender","salmon","vanilla",
     "Lavender and vanilla share linalool and linalyl acetate — the dominant floral terpenes in both — while vanilla's vanillin sweetness suppresses salmon's trimethylamine through sweet-lactonic displacement and lavender's linalool provides the secondary floral aromatic suppression. The double-suppression creates a perfectly clean, fragrant salmon.",
     "Lavender Vanilla Poached Salmon",
     ["Make a court bouillon with white wine, vanilla bean, dried lavender, and aromatics.", "Poach salmon at barely a simmer for 10 minutes until just opaque; lift out carefully.", "Serve with a vanilla-lavender beurre blanc and a dried lavender flower garnish."]),

    ("lavender","strawberry","tomato",
     "Lavender and strawberry share linalool and furaneol while strawberry and tomato share furaneol — the sweet-caramel compound critical to both ripe fruit and ripe vegetable — creating a triple-furaneol sweet-floral combination with lavender's floral contrast above the shared sweet register. The trio makes an unusual summer soup or salad.",
     "Lavender Strawberry Tomato Salad",
     ["Slice ripe tomatoes and fresh strawberries; toss gently with a pinch of dried lavender.", "Dress with lavender honey, white balsamic, and a drizzle of good olive oil.", "Serve at room temperature with torn mint, flaky salt, and a few lavender flowers."]),

    ("lavender","strawberry","truffle",
     "Lavender and truffle share anisaldehyde while strawberry and truffle share phenylacetaldehyde — two separate bridges linking lavender and strawberry each to truffle — while lavender and strawberry share linalool and furaneol on their own. The trio achieves maximum compound connectivity across the entire set.",
     "Truffle Strawberry Lavender Dessert",
     ["Make a lavender panna cotta; top with diced fresh strawberries macerated in truffle honey.", "Shave a very small amount of fresh truffle over the strawberries; the contrast is the point.", "Finish with a dried lavender flower; serve cold with a drizzle of strawberry-lavender coulis."]),

    ("lavender","strawberry","vanilla",
     "Lavender, strawberry, and vanilla share linalool, furaneol, and 2-phenylethanol — a near-complete three-way compound overlap — creating the most aromatic floral-sweet dessert base possible. The trio requires only the lightest acid touch to prevent it from becoming cloying.",
     "Lavender Strawberry Vanilla Tart",
     ["Make a vanilla custard flavored with lavender; pour into a blind-baked tart shell.", "Arrange sliced fresh strawberries in overlapping circles over the set custard.", "Glaze with lavender-strawberry gel; finish with rose petals and a dried lavender sprig."]),

    ("lavender","tomato","truffle",
     "Lavender and truffle share anisaldehyde — the anise-adjacent aromatic compound — while tomato and truffle share dimethyl sulfide and phenylacetaldehyde through different biochemical pathways. The triple-anisaldehyde-phenylacetaldehyde-dimethyl sulfide connection creates an earthy-floral-sweet umami preparation of unusual depth.",
     "Lavender Truffle Roasted Tomatoes",
     ["Halve cherry tomatoes, arrange with truffle oil, dried lavender, and garlic; roast at 275°F for 2 hours.", "Transfer to a serving dish; drizzle with more truffle oil and scatter lavender flowers.", "Serve over creamy polenta or ricotta toast with shaved truffle at the table."]),

    ("lavender","tomato","vanilla",
     "Lavender and tomato form the Provençal pairing while tomato and vanilla share furaneol — the sweet-caramel compound critical to both ripe tomato and cured vanilla beans — with lavender's linalool providing the floral aromatic bridge that lifts the unusual tomato-vanilla combination. The trio creates a sophisticated savory-sweet preserve or sauce.",
     "Lavender Vanilla Tomato Confit",
     ["Halve cherry tomatoes, place in a baking dish with a split vanilla bean and lavender sprigs.", "Cover with olive oil; roast at 250°F for 2 hours until concentrated and jammy.", "Serve over burrata or fresh cheese; the vanilla-lavender amplifies the tomato's natural sweetness."]),

    ("lavender","truffle","vanilla",
     "Lavender and vanilla share linalool and linalyl acetate — the dominant floral terpenes in both — while lavender and truffle share anisaldehyde, creating a dual aromatic bridge where lavender connects to both vanilla through terpenes and to truffle through anise chemistry. The extraordinary trio is the most complex compound butter in this set.",
     "Lavender Truffle Vanilla Compound Butter",
     ["Beat softened butter with truffle paste, vanilla bean seeds, dried lavender, and flaky salt.", "Mix until completely smooth; taste carefully and adjust seasoning with salt only.", "Roll into a log, refrigerate until firm, slice over warm risotto or seared scallops."]),
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
print(f"Batch 051 done: inserted {len(TRIPLETS)} triplets.")
