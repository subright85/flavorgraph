#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("cucumber","garlic","oyster",
     "Cucumber and oyster share (E)-2-nonenal — the cool watery compound present in both cucumber flesh and as a minor fresh note in premium oysters — while garlic's dimethyl sulfide provides savory sulfurous grounding that bridges the cool-watery and marine registers. The trio creates a refreshing Asian-style raw oyster preparation.",
     "Cucumber Garlic Oyster Shooter",
     ["Make a dressing: cucumber juice, minced garlic, rice vinegar, and sesame oil whisked together.", "Add a pinch of chili and finely diced cucumber; season with salt.", "Spoon over freshly shucked raw oysters; serve over ice with a garnish of thinly sliced cucumber."]),

    ("cucumber","garlic","parmesan",
     "Cucumber's (E)-2-nonenal provides cool watery freshness that cuts through Parmesan's butyric acid richness — the same acid-fat balance as acid with cheese — while garlic's dimethyl sulfide provides savory allium depth that bridges the cool-vegetable and aged-dairy registers. The trio creates a refined summer crostini.",
     "Garlic Parmesan Cucumber Crostini",
     ["Rub crostini with raw garlic while still warm; top with shaved Parmesan curls.", "Add thin cucumber slices and a drizzle of lemon-infused olive oil.", "Season with flaky salt and cracked pepper; serve immediately as a summer aperitivo."]),

    ("cucumber","garlic","rose",
     "Cucumber's (E)-2-nonenal cool freshness contrasts with rose's 2-phenylethanol floral warmth — a water-fresh against perfumed opposition — while garlic's dimethyl sulfide provides savory grounding that prevents the floral-cool combination from being too delicate. The trio drives Persian-influenced cold preparations where floral and vegetable freshness meet savory.",
     "Rose Garlic Cucumber Salad",
     ["Thinly slice cucumber; toss with minced garlic, rose water, lemon juice, and good olive oil.", "Add torn fresh mint and a pinch of flaky salt; rest 5 minutes.", "Serve sprinkled with dried rose petals and a drizzle of rose-infused oil as a Persian salad."]),

    ("cucumber","garlic","salmon",
     "Cucumber's (E)-2-nonenal provides clean watery freshness that cuts salmon's fatty richness — the same principle as cucumber in sushi — while garlic's dimethyl sulfide bridges the cool-watery and marine-fatty registers through allium-fish affinity. Together the trio creates the purest expression of Nordic gravlax-style salmon with cucumber.",
     "Garlic Cucumber Gravlax",
     ["Cure salmon with salt, sugar, minced garlic, dill, and thin cucumber slices for 48 hours.", "Rinse and slice thin; serve with cucumber ribbons dressed in rice vinegar and sesame.", "Finish with a sesame-garlic dressing and a drizzle of cucumber oil."]),

    ("cucumber","garlic","strawberry",
     "Cucumber and strawberry share no direct compound but work through contrast — cucumber's cool watery freshness against strawberry's sweet furaneol — while garlic's dimethyl sulfide provides savory grounding that transforms the fresh-sweet combination into a sophisticated gazpacho or salsa territory with allium depth.",
     "Strawberry Garlic Cucumber Gazpacho",
     ["Blend cucumber with fresh strawberries, garlic, lime juice, and olive oil until smooth.", "Season with salt, white pepper, and a drizzle of good olive oil; strain for silky texture.", "Serve chilled with diced strawberry and cucumber, and a drizzle of garlic-infused oil."]),

    ("cucumber","garlic","tomato",
     "Cucumber, garlic, and tomato are the three founding ingredients of Mediterranean salad — all sharing or contrasting through crisp freshness (cucumber), pungent allium depth (garlic), and ripe savory acidity (tomato). Cucumber's (E)-2-nonenal provides freshness that amplifies tomato's aroma while garlic's acetic acid bridges both vegetable registers.",
     "Classic Mediterranean Salad",
     ["Dice cucumber, ripe tomatoes, and red onion into rough chunks.", "Dress with minced garlic, red wine vinegar, olive oil, dried oregano, and salt.", "Toss with Kalamata olives and crumbled feta; rest 10 minutes before serving."]),

    ("cucumber","garlic","truffle",
     "Cucumber's (E)-2-nonenal cool freshness contrasts with truffle's dimethyl sulfide earthiness — a clean-watery against earthy-funky opposition — while garlic's dimethyl sulfide bridges both through its own sulfurous character. The trio creates an elegant luxury salad where truffle's earthiness is refreshed by cucumber's clean contrast.",
     "Truffle Garlic Cucumber Tartine",
     ["Spread truffle cream cheese on toasted sourdough; rub the edge with raw garlic.", "Top with thinly sliced cucumber ribbons and a drizzle of truffle oil.", "Shave a little fresh truffle over; finish with fleur de sel and a lemon squeeze."]),

    ("cucumber","garlic","vanilla",
     "Cucumber's (E)-2-nonenal cool freshness contrasts with vanilla's vanillin sweetness through a watery-fresh against warm-sweet opposition, while garlic's allicin converts to sweet roasted-garlic notes that bridge the cool-vegetable and lactonic-sweet registers. The unusual trio appears in avant-garde cucumber-vanilla gazpacho preparations.",
     "Vanilla Cucumber Garlic Gazpacho",
     ["Blend cucumber with garlic, a scraping of vanilla bean seeds, lime juice, and yogurt.", "Season with salt and white pepper; strain through a fine sieve until smooth.", "Serve very cold with a cucumber ribbon, vanilla oil drizzle, and a tiny garlic crisp."]),

    ("cucumber","lamb","lavender",
     "Cucumber's (E)-2-nonenal cool freshness cuts through lamb's gamey 4-methyloctanoic acid through watery-dilution and olfactory cooling — the Greek tzatziki principle — while lavender's linalool provides floral displacement that suppresses lamb's gameyness through a second mechanism. The trio achieves Provençal lamb with maximum gamey-note suppression.",
     "Lavender Cucumber Lamb Kofta",
     ["Make kofta: ground lamb, garlic, dried lavender, and herbs; grill on skewers.", "Make cucumber-lavender tzatziki: grated cucumber, yogurt, lavender honey, and lemon.", "Serve kofta with tzatziki and warm flatbread; the cucumber and lavender both temper the lamb."]),

    ("cucumber","lamb","lemon",
     "Cucumber and lemon share geraniol — a floral-citrus terpene — while lemon's citric acid suppresses lamb's gamey 4-methyloctanoic acid through pH-driven acid-fat modulation, and cucumber's (E)-2-nonenal provides watery cooling that further dilutes the animal-fat register. The trio is the aromatic chemistry of classic Greek lamb with tzatziki.",
     "Lemon Cucumber Grilled Lamb",
     ["Marinate lamb chops in lemon juice, zest, garlic, and olive oil for 2 hours.", "Grill over high heat until charred; rest 5 minutes.", "Serve with thinly sliced cucumber dressed in lemon juice, olive oil, and flaky salt."]),

    ("cucumber","lamb","mint",
     "Cucumber and mint share (E)-2-nonenal and linalool — cool-watery and herbal compounds that amplify each other's fresh register — while both independently suppress lamb's gamey 4-methyloctanoic acid through olfactory masking and watery dilution. The trio creates a double-cooling gamey-note suppression that is the foundation of Greek raita and Middle Eastern lamb preparations.",
     "Mint Cucumber Lamb Meatballs",
     ["Mix ground lamb with chopped fresh mint, garlic, cumin, and breadcrumbs; roll into balls.", "Bake at 400°F for 15 minutes until cooked through.", "Serve over cucumber-mint tzatziki with warm pita and a squeeze of lemon."]),

    ("cucumber","lamb","oyster",
     "Cucumber's (E)-2-nonenal and oyster's marine (E)-2-nonenal share the same compound — the clean watery aldehyde present in both — while lamb's dimethyl sulfide bridges to oyster's marine chemistry through the shared sulfurous compound family. The trio creates an unusual surf-and-turf preparation where cucumber acts as the fresh connector between the two proteins.",
     "Lamb Oyster Tartare with Cucumber",
     ["Finely chop raw lamb loin and raw oysters separately; mix with minced shallot and lemon.", "Add very finely diced cucumber, olive oil, and flaky salt; mix gently.", "Serve in chilled oyster shells with a cucumber ribbon and lemon wedge garnish."]),

    ("cucumber","lamb","parmesan",
     "Cucumber's (E)-2-nonenal cool freshness cuts through Parmesan's butyric acid richness and lamb's gamey fat simultaneously — the clean-vegetable contrast principle — while Parmesan's umami amplifies lamb's savory register. The trio creates an Italian-Mediterranean lamb preparation where aged cheese adds depth and cucumber provides refreshing contrast.",
     "Parmesan Cucumber Lamb Salad",
     ["Grill lamb loin to medium-rare; rest and slice thin.", "Arrange over shaved fennel and cucumber ribbons; top with Parmesan shavings.", "Dress with lemon, olive oil, and flaky salt; the Parmesan and cucumber bracket the lamb's richness."]),

    ("cucumber","lamb","rose",
     "Cucumber's (E)-2-nonenal cool freshness and rose's 2-phenylethanol floral warmth both independently suppress lamb's gamey 4-methyloctanoic acid — cool-watery dilution and floral aromatic displacement respectively — creating a double gamey-note suppression in a fragrant Persian-style lamb preparation.",
     "Rose Cucumber Persian Lamb",
     ["Marinate lamb with rose water, garlic, saffron, and lemon; grill or roast to medium-rare.", "Make a cucumber-rose salad: thinly sliced cucumber with rose water, lemon, and mint.", "Serve lamb over the rose-cucumber salad with toasted pistachios and dried rose petals."]),

    ("cucumber","lamb","salmon",
     "Cucumber's (E)-2-nonenal appears in both fresh cucumber and as a minor note in premium salmon flesh — making it the rare compound that bridges a vegetable and a fish. Lamb and salmon share dimethyl sulfide through their respective animal-fat metabolisms, while cucumber's freshness cuts both proteins' rich registers simultaneously.",
     "Cucumber Lamb and Salmon Surf & Turf",
     ["Sear lamb chops and salmon fillets separately to proper doneness.", "Make a cucumber mignonette: diced cucumber, rice vinegar, shallot, and sesame oil.", "Plate side by side; spoon cucumber mignonette over both and serve with lemon."]),

    ("cucumber","lamb","strawberry",
     "Cucumber and strawberry contrast through fresh-cool against sweet-warm while both independently modulate lamb's gamey richness — cucumber through watery dilution and strawberry's furaneol through sweet-fat suppression. The unusual trio creates a Nordic-influenced lamb preparation with summer fruit and vegetable freshness.",
     "Strawberry Cucumber Lamb Salad",
     ["Grill lamb to medium-rare; rest and slice thin.", "Toss sliced strawberries and cucumber ribbons with lemon juice, olive oil, and fresh mint.", "Arrange lamb over the strawberry-cucumber salad; dress with a balsamic glaze."]),

    ("cucumber","lamb","tomato",
     "Cucumber, lamb, and tomato are the Mediterranean summer plate — cucumber's (E)-2-nonenal freshness cuts lamb's gamey fat while tomato's malic and citric acids tenderize and brighten, and the combination of fresh vegetable and acidic fruit around lamb defines the flavor of a Turkish et salata or Greek chopped salad with lamb.",
     "Turkish Lamb Cucumber Tomato Salad",
     ["Grill lamb chops until charred; rest and chop roughly.", "Toss with diced cucumber, ripe tomatoes, red onion, parsley, and sumac.", "Dress with lemon juice, olive oil, and flaky salt; serve with warm flatbread."]),

    ("cucumber","lamb","truffle",
     "Cucumber's (E)-2-nonenal cool freshness contrasts with truffle's dimethyl sulfide earthiness — clean-watery against earthy-funky — while lamb's dimethyl sulfide bridges to truffle through the shared sulfurous compound. The trio creates a luxury lamb preparation where cucumber's clean freshness prevents truffle's earthiness and lamb's richness from being too heavy.",
     "Truffle Lamb Chops with Cucumber",
     ["Rub lamb chops with truffle salt and herbs; sear in a very hot cast-iron pan until crusted.", "Rest; serve over thinly sliced cucumber dressed with rice vinegar and truffle oil.", "Shave fresh truffle over the warm lamb just before serving."]),

    ("cucumber","lamb","vanilla",
     "Cucumber's (E)-2-nonenal cool freshness contrasts with vanilla's vanillin sweetness — watery-cool against warm-sweet — while vanilla's sweet lactonic compounds suppress lamb's gamey 4-methyloctanoic acid through aromatic displacement. The unusual trio appears in Moroccan-inspired lamb preparations where sweet spices include vanilla.",
     "Vanilla Cucumber Lamb Tagine",
     ["Brown lamb with onion and sweet spices; add a split vanilla bean and enough stock to cover.", "Braise at 300°F for 2 hours until tender; remove vanilla bean before serving.", "Serve with a cucumber-yogurt side dressed with lemon; the cool cucumber contrasts the warm vanilla braise."]),

    ("cucumber","lavender","lemon",
     "Cucumber and lavender both produce linalool — the herbal-floral terpene connecting the green freshness of cucumber to lavender's perfumed warmth — while lemon's limonene and geraniol connect to lavender's terpene family and its citric acid provides brightness that lifts the floral-cool combination. The trio defines Provençal summer drinks and salads.",
     "Lavender Lemon Cucumber Agua Fresca",
     ["Blend cucumber with lavender simple syrup and lemon juice; strain until crystal clear.", "Adjust sweetness and acidity; add cold water to reach desired concentration.", "Serve over ice with a lavender sprig and lemon wheel; light, floral, and refreshing."]),
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
print(f"Batch 040 done: inserted {len(TRIPLETS)} triplets.")
