#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("basil","mint","tomato",
     "Mint and tomato share furaneol and hexanal — sweet-caramel and green aldehyde compounds that give both ingredients their characteristic garden freshness — while basil's linalool and eugenol bridge the herbal-cool of mint to tomato's Mediterranean aromatic profile. The trio is the flavor of Levantine fattoush salads and Turkish çoban salatası.",
     "Mint Basil Tomato Fattoush",
     ["Tear toasted pita into rough pieces; dice ripe tomatoes and cucumber into chunky pieces.","Toss with large amounts of fresh mint and basil, sumac, lemon juice, and good olive oil.","Season with salt, let rest 5 minutes, then add the crispy pita just before serving."]),

    ("basil","mint","truffle",
     "Truffle's dimethyl sulfide and anisaldehyde meet mint's menthol and basil's linalool in a bold earthy-cool-herbal combination — truffle's richness tempered by mint's palate-cleansing volatiles — while basil bridges the two extremes through its terpene connection to both ingredients' herbal registers. The trio is unusual but achieves layered complexity.",
     "Truffle Mint Basil Potato Gnocchi",
     ["Make potato gnocchi; cook in salted water until they float and drain immediately.","Toss hot gnocchi with truffle butter and a chiffonade of fresh mint and basil until coated.","Plate, shave fresh truffle over generously, and finish with a drizzle of truffle oil."]),

    ("basil","mint","vanilla",
     "Mint's menthol and vanilla's vanillin create a classic ice cream pairing — cool-floral and warm-sweet — while basil's eugenol adds a spiced herbal warmth that rounds menthol's sharpness and connects it to vanilla's anise-adjacent character. The trio achieves a more sophisticated mint-vanilla than either pairing alone.",
     "Mint Basil Vanilla Ice Cream",
     ["Infuse cream with fresh mint, basil, and split vanilla bean over low heat 20 minutes; strain.","Whisk into egg yolk custard, churn in ice cream maker until thick and creamy.","Freeze until firm; serve with a fresh mint-basil sprig and a drizzle of honey."]),

    ("basil","oyster","parmesan",
     "Oyster and Parmesan share phenylacetaldehyde and dimethyl sulfide — rosy-fermented and sulfurous compounds that connect marine brine to aged dairy umami — while basil's linalool and benzaldehyde provide the herbal lift that bridges oceanic and dairy registers into an Italian-coastal flavor. The combination appears in baked oyster gratins with cheese.",
     "Oyster Parmesan Basil Gratin",
     ["Place shucked oysters in half-shells on a baking tray; top with a mix of Parmesan and breadcrumbs.","Drizzle with garlic butter and add a tiny fresh basil leaf pressed into each.","Broil 4 minutes until golden and the oyster edges just begin to curl; serve immediately."]),

    ("basil","oyster","rose",
     "Oyster and rose share phenylacetaldehyde — the rosy-floral compound that both marine bivalves and rose petals produce through unrelated biochemical pathways — while basil's 2-phenylethanol reinforces rose's dominant floral compound and bridges the ocean-flower contrast. The unlikely pairing creates a perfumed, delicate oyster preparation.",
     "Rose Basil Oyster on the Half Shell",
     ["Mix rose water with white wine vinegar, very finely minced shallot, and cracked white pepper.","Add finely chopped fresh basil and a tiny pinch of flaky salt; rest 5 minutes.","Spoon a small amount over freshly shucked raw oysters and serve on crushed ice immediately."]),

    ("basil","oyster","salmon",
     "Oyster and salmon share trimethylamine, dimethyl sulfide, and (E)-2-nonenal — the fullest marine-compound overlap between two seafoods — while basil's linalool and 2-phenylethanol bridge both proteins through shared terpene presence that suppresses marine off-notes and adds herbal brightness. The combination creates a sophisticated double-seafood preparation.",
     "Smoked Salmon Oyster Basil Blinis",
     ["Make small yeast blinis; top each with a thin slice of smoked salmon and a raw oyster.","Add a small dollop of crème fraîche and a tiny fresh basil leaf on top of each.","Finish with a drop of lemon juice and cracked pepper; serve immediately chilled."]),

    ("basil","oyster","strawberry",
     "Strawberry's furaneol sweetness and oyster's marine dimethyl sulfide create one of the bolder contrast pairings — sweet-fresh against briny-mineral — while basil's linalool and 2-phenylethanol bridge the fruit-marine gap through their shared terpene-floral connection to both strawberry's aroma and oyster's minor floral compounds. The trio is a New American raw bar concept.",
     "Strawberry Basil Oyster Mignonette",
     ["Blend muddled fresh strawberry with white wine vinegar, minced shallot, and cracked pepper.","Stir in very finely chopped fresh basil and a tiny pinch of salt; rest 10 minutes.","Spoon over freshly shucked raw oysters on ice; serve immediately with lemon wedges."]),

    ("basil","oyster","tomato",
     "Oyster and tomato share acetic acid and trace hexanal — tart and green aldehyde compounds — creating a natural brine-vegetable connection, while basil's linalool and eugenol complete the Mediterranean herb profile that makes tomato-oyster stew an Italian coastal tradition. The trio drives the flavor of Venetian seppie in umido and seafood cioppino.",
     "Tomato Basil Oyster Stew",
     ["Sauté garlic in olive oil; add crushed tomatoes and simmer 15 minutes until thickened.","Add shucked oysters with their liquor and poach gently 2 minutes until edges just curl.","Stir in torn fresh basil, adjust seasoning, and serve immediately with crusty bread."]),

    ("basil","oyster","truffle",
     "Oyster and truffle share dimethyl sulfide and phenylacetaldehyde — sulfurous-rosy compounds that both marine bivalves and earthy fungi produce — while basil's linalool and benzaldehyde provide the herbal lift that bridges the luxurious brine-earth register. The trio represents one of the most opulent savory flavor combinations in haute cuisine.",
     "Truffle Basil Oyster Tartare",
     ["Shuck and chop oysters finely; mix with a drizzle of truffle oil and very finely chopped basil.","Season with fleur de sel and white pepper; arrange in oyster shells over crushed ice.","Shave fresh truffle over each portion generously just before serving with champagne."]),

    ("basil","oyster","vanilla",
     "Oyster's marine brine and vanilla's vanillin sweetness create a bold sweet-salt contrast — the same logic as salted caramel applied to seafood — while basil's linalool bridges the herbal connection between vanilla's floral-lactonic character and oyster's minor floral phenylacetaldehyde. The trio appears in avant-garde oyster preparations with vanilla beurre blanc.",
     "Vanilla Basil Oyster Beurre Blanc",
     ["Reduce white wine and shallots; whisk in cold butter piece by piece until emulsified.","Add vanilla bean seeds and very finely chopped fresh basil; strain and season.","Spoon the vanilla-basil beurre blanc over warm broiled oysters still in the shell."]),

    ("basil","parmesan","rose",
     "Parmesan and rose share 2-phenylethanol and phenylacetaldehyde — fermented-rosy compounds spanning aged dairy and floral — while basil reinforces rose's dominant 2-phenylethanol and provides the herbal connection that bridges cheese funk and flower sweetness. The trio creates an unusual refined aperitivo flavor that works with honey-dressed cheese boards.",
     "Rose Basil Parmesan Honey Board",
     ["Shave aged Parmesan Reggiano into large irregular pieces on a slate board.","Scatter fresh basil leaves and crystallized rose petals over and around the cheese.","Drizzle with floral honey and serve with crackers — the rose and basil lift the Parmesan's umami."]),

    ("basil","parmesan","salmon",
     "Parmesan and salmon share dimethyl sulfide and butyric acid — sulfurous and fatty-acid compounds connecting aged dairy and fatty fish — while basil's linalool and 2-phenylethanol bridge both ingredients through herbal-floral terpenes that suppress salmon's trimethylamine and cheese's sharpest butyric notes. The Italian tradition of Parmesan with fish is contentious but chemically coherent.",
     "Parmesan Basil Crusted Salmon",
     ["Mix finely grated Parmesan with chopped fresh basil, garlic, lemon zest, and breadcrumbs.","Press the crust firmly onto salmon fillets; bake at 400°F for 12 minutes until golden.","Serve with a basil oil drizzle, lemon wedges, and a final grating of fresh Parmesan."]),

    ("basil","parmesan","strawberry",
     "Strawberry and Parmesan share furaneol — the sweet-caramel compound critical to both ripe strawberry aroma and aged cheese sweetness — while basil's linalool and 2-phenylethanol amplify strawberry's floral esters and provide the herbal connection to Parmesan's fermentation character. The Italian tradition of aged cheese with strawberries is ancient and chemically precise.",
     "Strawberry Parmesan Basil Salad",
     ["Slice ripe strawberries; toss gently with a splash of aged balsamic and torn fresh basil.","Arrange on a plate and shave Parmesan generously over the top with a vegetable peeler.","Finish with cracked pepper, flaky salt, and a drizzle of good olive oil; serve immediately."]),

    ("basil","parmesan","tomato",
     "Parmesan and tomato share furaneol and acetic acid — sweet-caramel and tart compounds that together create the richest possible umami-sweet tomato base — while basil completes the Italian flavor trinity that defines everything from bruschetta to pizza Margherita. These three ingredients together are arguably Italian cuisine's most important flavor combination.",
     "Tomato Parmesan Basil Soup",
     ["Roast tomatoes with garlic and olive oil at 400°F until caramelized and concentrated.","Blend roasted tomatoes with stock until smooth; simmer 10 minutes and season well.","Serve with a generous grating of Parmesan, torn fresh basil, and a drizzle of good olive oil."]),

    ("basil","parmesan","truffle",
     "Parmesan and truffle share phenylacetaldehyde and dimethyl sulfide — the fermented-rosy and sulfurous compound pair that makes aged cheese and earthy fungus such a powerful umami combination — while basil's linalool and 2-phenylethanol provide the herbal brightness that lifts the dense umami combination into a clean, vertical aromatic register.",
     "Truffle Parmesan Basil Risotto",
     ["Cook arborio risotto with stock until creamy; off heat stir in truffle butter and cold Parmesan.","Add a splash of pasta water to achieve a glossy, flowing texture; season precisely.","Plate, shave generous amounts of fresh truffle, and finish with torn fresh basil."]),

    ("basil","parmesan","vanilla",
     "Parmesan and vanilla share vanillin, furaneol, and butyric acid — an unusual overlap of sweet-lactonic and aged-dairy compounds — while basil's eugenol bridges the herbal-spiced connection to vanilla's anise character and Parmesan's fermentation register. The trio appears in refined Italian pasticceria savory-sweet crossover applications.",
     "Vanilla Parmesan Basil Panna Cotta",
     ["Warm cream with split vanilla bean and fresh basil; steep 20 minutes and strain well.","Dissolve gelatin, stir in finely grated Parmesan, sweeten lightly; pour into molds and set.","Unmold, serve with a basil oil drizzle and crumbled Parmesan for a savory-sweet finale."]),

    ("basil","rose","salmon",
     "Rose's 2-phenylethanol and geraniol provide floral-citrus brightness that suppresses salmon's trimethylamine through aromatic displacement — a more delicate version of the dill mechanism — while basil's 2-phenylethanol reinforces rose's dominant compound and adds herbal warmth. The trio produces an aromatic Persian-influenced salmon preparation.",
     "Rose Basil Persian Salmon",
     ["Marinate salmon in rose water, fresh basil, saffron, garlic, and lemon overnight.","Bake at 400°F for 12 minutes; meanwhile make a rose-basil butter with rose water and chopped basil.","Serve salmon topped with rose-basil butter, fresh rose petals, and a basil garnish."]),

    ("basil","rose","strawberry",
     "Rose and strawberry share 2-phenylethanol, linalool, and furaneol — the most complete floral-sweet compound overlap between a flower and a fruit — while basil reinforces rose's 2-phenylethanol and adds eugenol herbal warmth that prevents the floral-sweet combination from being one-dimensional. The trio defines romantic dessert flavor.",
     "Rose Strawberry Basil Panna Cotta",
     ["Warm cream with rose water and fresh basil; steep 15 minutes, strain, dissolve gelatin.","Pour into molds and set in refrigerator 4 hours; macerate sliced strawberries with rose water and basil.","Unmold onto plates, spoon rose-strawberry mixture around the base, and garnish with petals."]),

    ("basil","rose","tomato",
     "Rose's 2-phenylethanol and geraniol soften tomato's acidity through floral aromatic displacement — the principle behind Turkish rose-tomato jam preparations — while basil's linalool and eugenol complete the Mediterranean herbal triad connecting floral-sweet and savory-acid registers. The trio creates a nuanced summer sauce or reduction.",
     "Rose Tomato Basil Gazpacho",
     ["Blend ripe tomatoes with cucumber, garlic, a splash of rose water, and fresh basil until smooth.","Season with sherry vinegar, olive oil, salt, and white pepper; strain for a silky texture.","Serve chilled in bowls with rose petals, torn basil, and a drizzle of rose-infused olive oil."]),

    ("basil","rose","truffle",
     "Rose and truffle share phenylacetaldehyde and anisaldehyde — the rosy-anise compound pair produced independently by flower and fungus — while basil's linalool and 2-phenylethanol reinforce rose's floral register and bridge the perfumed-earthy contrast. The trio is a signature of haute cuisine where floral luxury meets earthy luxury.",
     "Rose Truffle Basil Butter",
     ["Blend softened butter with rose water, truffle oil, very finely chopped fresh basil, and flaky salt.","Roll into a log in plastic wrap and refrigerate until firm; slice into rounds.","Serve melting over warm brioche, risotto, or a seared scallop for maximum aromatic impact."]),
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
print(f"Batch 008 done: inserted {len(TRIPLETS)} triplets.")
