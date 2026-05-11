#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("lamb","mint","parmesan",
     "Mint and Parmesan share trace 1,8-cineole and butyric acid — the cooling terpene and fatty-acid compound that appear in both herb and aged dairy — while lamb's 4-methyloctanoic acid gaminess is suppressed by menthol's olfactory masking and rounded by Parmesan's glutamate umami. The trio creates a refined Mediterranean herb-cheese-meat combination.",
     "Mint Parmesan Lamb Meatball Broth",
     ["Roll ground lamb with chopped mint, grated Parmesan, garlic, and breadcrumbs into balls.", "Simmer gently in lamb broth until cooked through, about 12 minutes.", "Serve in the broth with shaved Parmesan, fresh mint leaves, and cracked pepper."]),

    ("lamb","mint","rose",
     "Mint and rose share 2-phenylethanol and linalool — floral-herbal terpenes that both the herb and the flower produce — while lamb's gamey 4-methyloctanoic acid is suppressed by menthol's masking effect and softened by rose's geraniol. The trio creates an aromatic Persian lamb preparation where floral-cool herbal register dominates.",
     "Rose Mint Persian Lamb Chops",
     ["Marinate lamb chops with rose water, fresh mint, saffron, garlic, and olive oil overnight.", "Grill or pan-sear over high heat until charred; rest 5 minutes before serving.", "Plate with a rose-mint yogurt sauce, dried rose petals, and a fresh mint garnish."]),

    ("lamb","mint","salmon",
     "Lamb and salmon share dimethyl sulfide and trimethylamine — the sulfurous-marine compound family spanning animal fat and fatty fish — while mint's menthol provides the strongest palate-cleansing volatile that suppresses both lamb's gaminess and salmon's marine notes simultaneously. The unusual surf-and-turf trio works with mint as the essential bridge.",
     "Mint-Crusted Lamb and Salmon Duo",
     ["Make a mint-herb crust from chopped mint, breadcrumbs, and olive oil; press onto both proteins.", "Roast lamb at 425°F to medium-rare and salmon at 400°F until just opaque; rest each.", "Plate together with a mint yogurt sauce and cucumber-mint salsa bridging the two proteins."]),

    ("lamb","mint","strawberry",
     "Strawberry's furaneol sweetness directly counters lamb's 4-methyloctanoic acid gaminess through sweet-savory contrast — the same logic as mint jelly with lamb — while mint's menthol bridges the fruit-meat gap with its palate-cleansing volatiles and amplifies strawberry's linalool floral compounds. The trio refines the classic lamb-mint combination.",
     "Strawberry Mint Lamb Salad",
     ["Grill lamb loin to medium-rare; rest and slice thin against the grain.", "Toss arugula with sliced fresh strawberries, torn mint, and a balsamic-strawberry dressing.", "Arrange lamb over the salad with crumbled feta and a mint-strawberry vinaigrette drizzle."]),

    ("lamb","mint","tomato",
     "Tomato and lamb share furaneol and acetic acid — sweet-caramel and tart compounds that bridge meat and vegetable through acid-fat balance — while mint's menthol provides the cooling aromatic counterpoint that prevents the rich lamb-tomato combination from becoming heavy. The trio is the flavor of classic Turkish kofta in tomato sauce with mint.",
     "Mint Lamb Kofta Tomato Sauce",
     ["Mix ground lamb with chopped fresh mint, onion, cumin, coriander, and salt; shape into kofta.", "Grill or pan-fry until crusted; meanwhile simmer a simple tomato sauce with garlic.", "Serve kofta over the tomato sauce with fresh mint, yogurt, and warm flatbread."]),

    ("lamb","mint","truffle",
     "Lamb and truffle share dimethyl sulfide and phenylacetaldehyde — the sulfurous-rosy compound family linking gamey meat and earthy fungus — while mint's menthol provides the high-volatile aromatic that lifts truffle's dense earthiness and suppresses lamb's 4-methyloctanoic acid through olfactory displacement. The trio is haute cuisine territory.",
     "Truffle Mint Rack of Lamb",
     ["Rub rack of lamb with truffle paste and press a mint-breadcrumb crust firmly onto the fat cap.", "Roast at 425°F for 18 minutes to medium-rare; rest 8 minutes before carving into chops.", "Serve over truffle-potato purée with a fresh mint-truffle jus and extra mint garnish."]),

    ("lamb","mint","vanilla",
     "Vanilla's vanillin sweetness contrasts with lamb's gamey 4-methyloctanoic acid while mint's menthol provides the coolest aromatic contrast against vanilla's warm-sweet register — cool and sweet simultaneously suppressing animal pungency from two directions. The trio is the logic of Moroccan lamb with sweet spices pushed to its most fragrant extreme.",
     "Vanilla Mint Moroccan Lamb Tagine",
     ["Brown lamb with onion, cinnamon, a split vanilla bean, and ras el hanout in a tagine.", "Add honey, preserved lemon, stock, and a bundle of fresh mint; braise at 300°F for 2 hours.", "Stir in fresh mint just before serving; discard vanilla pod and serve over couscous."]),

    ("lamb","oyster","parmesan",
     "Lamb, oyster, and Parmesan form a powerful triple-umami combination — lamb's glutamate from slow-cooked meat, oyster's succinate and glycine marine umami, and Parmesan's inosinate and glutamate from aging — while shared dimethyl sulfide links all three through the same sulfurous aromatic family. The trio creates an intensely savory pasta preparation.",
     "Oyster Parmesan Braised Lamb Pasta",
     ["Braise lamb shoulder until falling apart; shred and reduce braising liquid to a glossy sauce.", "Toss pasta with the braised lamb sauce and a handful of shucked oysters added off heat.", "Finish with generous Parmesan, cracked pepper, and parsley; the residual heat just cooks the oysters."]),

    ("lamb","oyster","rose",
     "Lamb and oyster share trimethylamine and dimethyl sulfide — the gamey-marine compound family linking animal meat and bivalve — while rose's geraniol and 2-phenylethanol provide the strongest floral aromatic displacement that suppresses both lamb's gaminess and oyster's marine notes into a refined, perfumed register. The trio is bold but precise.",
     "Rose-Poached Oysters with Lamb Tartare",
     ["Gently poach oysters in a rose water and white wine court bouillon until barely set.", "Finely chop lamb loin, season with rose water, shallot, and flaky salt; plate raw.", "Arrange poached oysters alongside lamb tartare; garnish with rose petals and microgreens."]),

    ("lamb","oyster","salmon",
     "Lamb, oyster, and salmon form the fullest possible triple-marine-animal flavor — all three share trimethylamine and dimethyl sulfide at significant concentrations — creating a dramatic surf-turf-reef combination where each ingredient's sulfurous-marine aromatic reinforces the others. The combination requires careful acid or herb bridging to succeed.",
     "Lamb Oyster Salmon Hot Pot",
     ["Simmer a dashi-lamb broth with ginger, lemongrass, and a splash of sake.", "Add thin-sliced lamb, salmon pieces, and shucked oysters to the simmering broth.", "Cook each briefly and eat immediately with dipping sauces; the broth becomes richer with each addition."]),

    ("lamb","oyster","strawberry",
     "Strawberry's furaneol sweetness provides the strongest sweet-savory contrast to lamb's gamey fat acids — while oyster's marine dimethyl sulfide meets strawberry's floral esters in an unusual brine-fruit encounter — and the three-way combination achieves its coherence through strawberry's role as an acid-sweet bridge between animal and marine registers.",
     "Strawberry Oyster Lamb Mignonette Platter",
     ["Prepare a strawberry mignonette: blend muddled strawberry, shallot, vinegar, and cracked pepper.", "Arrange freshly shucked oysters alongside thin-sliced rare lamb loin on a serving platter.", "Serve with strawberry mignonette for both oysters and lamb; the same sauce bridges both proteins."]),

    ("lamb","oyster","tomato",
     "Lamb and tomato share furaneol and acetic acid — the sweet-caramel and tart compounds that drive rich meat braises — while oyster's marine dimethyl sulfide and succinate umami add a briny depth that amplifies the tomato-lamb base in the same way as fish sauce. The trio creates a deeply savory slow-cooked stew.",
     "Oyster Tomato Braised Lamb Stew",
     ["Brown lamb shoulder; cook with crushed tomatoes, garlic, red wine, and herbs for 2 hours.", "Add shucked oysters with their liquor in the final 5 minutes of braising.", "Serve the stew with crusty bread; oyster's brine has enriched the lamb-tomato sauce deeply."]),

    ("lamb","oyster","truffle",
     "Lamb, oyster, and truffle form an extraordinary triple-sulfurous combination — all three share dimethyl sulfide and phenylacetaldehyde — creating the richest possible animal-marine-fungal umami register. The three together represent the luxury extremes of meat, sea, and earth brought into a single preparation through their shared aroma chemistry.",
     "Truffle Oyster Braised Lamb Consommé",
     ["Make a clear lamb consommé from roasted bones; clarify with egg white raft.", "Warm shucked oysters gently in the consommé until barely opaque.", "Serve with shaved fresh truffle floating on top — three luxury umami sources in one bowl."]),

    ("lamb","oyster","vanilla",
     "Lamb and oyster share trimethylamine — the marine-animal amine that connects gamey meat and briny shellfish — while vanilla's vanillin and furaneol sweetness provides the strongest aromatic counterpoint, suppressing animal pungency through sweet-lactonic contrast. The trio appears in refined chawanmushi and custard-based savory applications.",
     "Vanilla Oyster Lamb Chawanmushi",
     ["Beat eggs with dashi, a touch of vanilla bean, and soy; steam gently until barely set.", "Nestle pieces of braised lamb and one shucked oyster into each cup before steaming.", "Serve warm with a dot of ponzu; vanilla lifts the gamey-marine combination into delicacy."]),

    ("lamb","parmesan","rose",
     "Lamb and Parmesan share butyric acid and dimethyl sulfide — the fatty-acid and sulfurous compound families connecting animal fat and aged dairy — while rose's 2-phenylethanol and geraniol suppress lamb's gaminess and Parmesan's sharpest butyric notes through floral aromatic displacement. The trio creates a refined Persian-Italian fusion preparation.",
     "Rose Parmesan Lamb Stuffed Peppers",
     ["Brown ground lamb with rose water, garlic, herbs, and raisins; mix with Parmesan and rice.", "Stuff roasted peppers, top with more Parmesan, and bake at 375°F until golden.", "Garnish with dried rose petals, a drizzle of rose-infused oil, and shaved Parmesan."]),

    ("lamb","parmesan","salmon",
     "Lamb and salmon share dimethyl sulfide — the sulfurous compound family linking animal fat and fatty fish — while Parmesan's butyric acid fat and umami round both proteins through the same dairy-binding mechanism. The unusual meat-fish-cheese combination works in Mediterranean preparations where Parmesan breadcrumb crusts bridge both proteins.",
     "Parmesan-Crusted Lamb and Salmon Surf-Turf",
     ["Make a Parmesan-herb crust from grated Parmesan, breadcrumbs, garlic, and herbs.", "Press crust onto both lamb rack and salmon fillet; roast together at 400°F until each is done.", "Plate side by side with a lemon-caper butter sauce and fresh herb garnish."]),

    ("lamb","parmesan","strawberry",
     "Lamb and Parmesan share butyric acid — the fatty-acid compound in both animal fat and aged dairy — while strawberry's furaneol sweetness directly softens Parmesan's sharpness and lamb's gaminess through sweet-savory contrast. The trio creates a sophisticated salad that echoes the Italian tradition of aged cheese with fruit.",
     "Strawberry Parmesan Lamb Salad",
     ["Slice grilled lamb loin thinly; toss arugula with halved strawberries and aged balsamic.", "Arrange lamb over the salad; use a vegetable peeler to add large Parmesan shards.", "Finish with cracked pepper, flaky salt, and a drizzle of strawberry-balsamic reduction."]),

    ("lamb","parmesan","tomato",
     "Lamb and tomato share furaneol and acetic acid — the sweet-caramel and tart compounds essential to Mediterranean meat braises — while Parmesan's glutamate umami amplifies the tomato-meat base through the same mechanism as long-cooked Italian ragù. The trio is the foundation of Italian lamb pasta sauce and Greek moussaka topping.",
     "Lamb Tomato Parmesan Ragù",
     ["Brown ground lamb until caramelized; add garlic, crushed tomatoes, and red wine; simmer 45 minutes.", "Toss with rigatoni, loosen with pasta water to achieve a glossy, coating consistency.", "Finish with a generous amount of freshly grated Parmesan and torn basil before serving."]),

    ("lamb","parmesan","truffle",
     "Lamb and truffle share dimethyl sulfide and phenylacetaldehyde — the sulfurous-rosy compound pair — while Parmesan's phenylacetaldehyde from fermentation and glutamate umami combine with truffle's earthiness to create a three-way luxury umami stack above lamb's rich meat register. The trio appears in high-end Italian lamb pasta preparations.",
     "Truffle Parmesan Braised Lamb Tagliatelle",
     ["Braise lamb shoulder until falling apart; shred and reduce braising liquid until concentrated.", "Toss fresh tagliatelle with shredded lamb, truffle butter, and a splash of pasta water.", "Finish with shaved Parmesan, freshly shaved truffle, and cracked pepper at the table."]),

    ("lamb","parmesan","vanilla",
     "Lamb and Parmesan share butyric acid — the fatty-acid compound spanning animal fat and aged dairy — while vanilla's vanillin and furaneol sweetness bridges the gamey-dairy combination through sweet-lactonic compounds that soften both proteins' dominant flavor volatiles. The trio creates a sophisticated savory-sweet stuffed pasta preparation.",
     "Vanilla Parmesan Lamb Tortellini",
     ["Make a filling from braised lamb, Parmesan, a scrape of vanilla bean, and nutmeg.", "Stuff tortellini carefully; cook in salted water until they float and drain immediately.", "Toss with brown butter, sage, and a final grating of Parmesan; the vanilla echoes through the filling."]),
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
print(f"Batch 048 done: inserted {len(TRIPLETS)} triplets.")
