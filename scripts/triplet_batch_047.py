#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("lamb","lavender","lemon",
     "Lavender and lamb share linalool and butyric acid — floral terpene and fatty acid compounds that connect animal fat and herb — while lemon's citric acid suppresses lamb's gamey 4-methyloctanoic acid through pH-driven acid-fat modulation as a second gamey-note reducer alongside lavender's floral displacement. Triple gamey-note suppression defines Provençal citrus lamb.",
     "Lemon Lavender Lamb Chops",
     ["Make a rub: dried lavender, lemon zest, garlic, and olive oil; coat lamb chops.", "Grill over high heat until charred; rest 5 minutes.", "Serve with a lemon-lavender butter sauce and steamed spring vegetables."]),

    ("lamb","lavender","mint",
     "Lavender and mint share linalool — the dominant herbal terpene in both — while both independently suppress lamb's gamey 4-methyloctanoic acid: lavender through floral displacement and mint through menthol olfactory masking. The double-suppression via two distinct mechanisms with a shared linalool base creates the most effective gamey-note reduction possible.",
     "Lavender Mint Lamb Rack",
     ["Make a crust: dried lavender, fresh mint, breadcrumbs, and Dijon mustard.", "Coat a rack of lamb; roast at 425°F for 20 minutes to medium-rare.", "Rest 8 minutes; serve with lavender-mint jus and roasted spring vegetables."]),

    ("lamb","lavender","oyster",
     "Lamb and oyster share dimethyl sulfide and trimethylamine — the marine-animal sulfurous compound family — while lavender's linalool provides floral bridging between gamey animal fat and marine brine through aromatic displacement. The combination appears in surf-and-turf preparations where Provençal lavender serves as the aromatic connector.",
     "Lavender Lamb and Oyster Platter",
     ["Grill lamb chops with a lavender-herb crust until medium-rare; rest.", "Broil oysters in the shell with lavender-garlic butter.", "Plate lamb and oysters side by side; the lavender bridges both protein registers."]),

    ("lamb","lavender","parmesan",
     "Lamb and Parmesan share butyric acid and dimethyl sulfide — the fatty-acid and sulfurous compounds spanning animal fat and aged dairy — while lavender's linalool provides Provençal floral bridging between the meat and cheese registers. The trio creates a sophisticated lamb pasta preparation with aged cheese and Provençal herb aromatics.",
     "Lavender Parmesan Braised Lamb",
     ["Brown lamb pieces; add dried lavender, white wine, and stock; braise 2 hours.", "Reduce braising liquid; finish with grated Parmesan and a drizzle of olive oil.", "Serve over pappardelle; the lavender lifts the lamb-Parmesan into an aromatic Provençal register."]),

    ("lamb","lavender","rose",
     "Lavender and rose share linalool and 2-phenylethanol — the floral terpenes that both herbs produce at dominant levels — while both independently suppress lamb's gamey 4-methyloctanoic acid through floral aromatic displacement. The double-floral suppression with a shared compound base creates a Persian-Provençal lamb preparation of unusual refinement.",
     "Rose Lavender Persian Lamb",
     ["Brown lamb with onion; add rose water, dried lavender, saffron, and stock.", "Braise at 300°F for 1.5 hours until tender; the double-floral reduces gaminess completely.", "Serve over saffron rice with dried rose petals and toasted almonds."]),

    ("lamb","lavender","salmon",
     "Lamb and salmon share dimethyl sulfide and trimethylamine — the sulfurous-marine compound family — while lavender's linalool provides floral bridging between the gamey animal and marine registers, acting as an aromatic TMA suppressor for both proteins simultaneously. The trio creates a unique surf-and-turf with Provençal character.",
     "Lavender Glazed Lamb and Salmon",
     ["Make a lavender glaze: lavender honey, soy, and lemon reduced together.", "Sear lamb chops and salmon separately; brush both with lavender glaze in the last minute.", "Plate side by side; lavender bridges both proteins through its shared floral TMA-suppressing mechanism."]),

    ("lamb","lavender","strawberry",
     "Lamb and strawberry share no direct compound but lavender bridges both — lavender and strawberry share linalool and lavender softens lamb's gaminess through floral displacement. Strawberry's furaneol sweetness suppresses lamb's gamey 4-methyloctanoic acid through sweet-fat modulation while lavender's floral depth prevents the combination from being cloying.",
     "Strawberry Lavender Lamb Chops",
     ["Make a glaze: fresh strawberry reduced with lavender honey and a splash of balsamic.", "Sear lamb chops; brush with strawberry-lavender glaze and rest 5 minutes.", "Serve with fresh strawberry and lavender garnish; sweet-floral-gamey in layered sequence."]),

    ("lamb","lavender","tomato",
     "Lamb and tomato share furaneol and acetic acid — sweet-caramel and tart compounds that create the acid-meat bridge in long braises — while lavender's linalool provides Provençal floral bridging that lifts the Mediterranean lamb-tomato combination into an aromatic Southern French register. The trio drives Provençal daube d'agneau.",
     "Lavender Tomato Braised Lamb",
     ["Brown lamb; add crushed tomatoes, dried lavender, garlic, olives, and herbes de Provence.", "Braise at 325°F for 2 hours until tender; the lavender lifts tomato-lamb into Provençal territory.", "Serve over polenta or with crusty bread; garnish with fresh lavender and chopped parsley."]),

    ("lamb","lavender","truffle",
     "Lamb and truffle share dimethyl sulfide and phenylacetaldehyde — sulfurous and rosy-fermented compounds — while lavender's linalool and anisaldehyde bridge the earthy-gamey register into a clean floral-anise aromatic that lifts truffle's density. The trio creates a luxury Provençal lamb preparation where floral and earthy elements balance.",
     "Truffle Lavender Lamb Rack",
     ["Rub rack of lamb with truffle salt, dried lavender, and herbs; let rest 30 minutes.", "Roast at 425°F for 20 minutes to medium-rare; rest 8 minutes.", "Plate over truffle-lavender potato purée; shave truffle over and drizzle lavender-truffle jus."]),

    ("lamb","lavender","vanilla",
     "Lavender and vanilla share linalool and linalyl acetate — the floral terpene compounds in both herbs — while vanilla's vanillin sweetness contrasts lamb's gamey 4-methyloctanoic acid through sweet-fat modulation. The trio achieves double gamey-note suppression through both floral displacement (lavender) and sweet-compound masking (vanilla).",
     "Vanilla Lavender Braised Lamb",
     ["Brown lamb with onion; add a split vanilla bean, dried lavender, and sweet spices.", "Braise at 300°F for 2 hours until falling tender; remove vanilla bean.", "Serve over couscous with dried apricots; the vanilla-lavender creates a sweet-floral braise."]),

    ("lamb","lemon","mint",
     "Lamb, lemon, and mint form the classic Greek souvlaki trio — lemon's citric acid suppresses lamb's gamey 4-methyloctanoic acid through acid-fat modulation, mint's menthol independently suppresses it through olfactory masking, and the overlap of lemon's geraniol with mint's linalool creates an aromatic citrus-herb bridge. The triple gamey-note reduction is why this trio is universal.",
     "Greek Lemon Mint Lamb Souvlaki",
     ["Marinate lamb cubes in lemon juice, zest, fresh mint, garlic, and olive oil for 2 hours.", "Thread onto skewers and grill over high heat until charred at the edges.", "Serve with mint tzatziki, warm pita, and a lemon wedge."]),

    ("lamb","lemon","oyster",
     "Lamb and oyster share dimethyl sulfide and trimethylamine — the sulfurous-marine compound family — while lemon's citric acid suppresses both lamb's gamey acids and oyster's trimethylamine through pH-driven acid modulation. Lemon is the universal acid bridge that makes this unusual surf-and-turf combination accessible.",
     "Lemon Lamb and Oyster Stew",
     ["Brown lamb pieces; add white wine, lemon juice, and fish stock.", "Add shucked oysters in the last 3 minutes of cooking; season with preserved lemon and herbs.", "Serve with crusty bread; the lemon bridges the gamey-marine combination with citrus brightness."]),

    ("lamb","lemon","parmesan",
     "Lamb and Parmesan share butyric acid and dimethyl sulfide while lemon's citric acid cuts through Parmesan's fat and simultaneously moderates lamb's gamey acids through acid-fat pH adjustment. The trio creates an Italian-Greek crossover where Parmesan adds dairy umami and lemon provides the essential brightness.",
     "Lemon Parmesan Lamb Pasta",
     ["Brown ground lamb; add lemon zest, lemon juice, and white wine; reduce.", "Toss with al dente pasta and grated Parmesan; off heat beat until glossy.", "Plate; finish with more Parmesan, lemon zest, and fresh herbs."]),

    ("lamb","lemon","rose",
     "Lamb and rose share no direct compound but lemon's geraniol overlaps with rose's geraniol — sharing the citrus-floral terpene — while lemon's citric acid and rose's 2-phenylethanol both independently suppress lamb's gamey 4-methyloctanoic acid through acid-fat modulation and floral displacement respectively. The triple suppression creates a refined Persian preparation.",
     "Rose Lemon Persian Lamb Chops",
     ["Marinate lamb in lemon juice, rose water, saffron, and garlic overnight.", "Grill or pan-sear until crusted; rest 5 minutes.", "Serve with a rose-lemon yogurt sauce and saffron rice; both suppress lamb's gaminess through different mechanisms."]),

    ("lamb","lemon","salmon",
     "Lamb and salmon share dimethyl sulfide and trimethylamine while lemon's citric acid suppresses both lamb's gamey acids and salmon's marine TMA through acid-fat pH modulation simultaneously. Lemon is the critical acid-bridge that makes the unusual lamb-salmon surf-and-turf preparation taste clean and balanced.",
     "Lemon Lamb and Salmon Surf & Turf",
     ["Grill lamb chops and salmon fillets side by side over high heat.", "Make a lemon-herb sauce: lemon juice, zest, olive oil, and fresh herbs.", "Plate side by side with the shared lemon sauce; lemon bridges both proteins cleanly."]),

    ("lamb","lemon","strawberry",
     "Lamb and strawberry share no direct compound but lemon bridges both — lemon's geraniol connects to strawberry's floral esters while lemon's citric acid suppresses lamb's gamey acids. Strawberry's furaneol sweetness adds sweet-fat suppression as a second gamey-note reducer, creating a Nordic-influenced lamb preparation.",
     "Strawberry Lemon Glazed Lamb",
     ["Cook strawberries with lemon juice and zest into a bright, tart glaze.", "Brush lamb chops; grill or pan-sear with the strawberry-lemon glaze.", "Serve with fresh strawberry and lemon zest; the fruit-citrus combination tackles gaminess from two angles."]),

    ("lamb","lemon","tomato",
     "Lamb, lemon, and tomato together form the Mediterranean braising trio — tomato's malic and citric acids tenderizing lamb while lemon's citric acid provides additional gamey-note modulation, and both acidic components working together through the same pH-driven fat modulation mechanism. The trio drives Greek lamb stifado and Italian agnello all'agro.",
     "Lemon Tomato Braised Lamb",
     ["Brown lamb; add crushed tomatoes, lemon juice, lemon zest, and herbs.", "Braise at 325°F for 2 hours until tender; the double acid modulates gaminess effectively.", "Serve over orzo or rice; finish with fresh lemon juice and herbs."]),

    ("lamb","lemon","truffle",
     "Lamb and truffle share dimethyl sulfide while lemon's citric acid and limonene lift the earthy-gamey truffle-lamb combination through brightness — acid and citrus terpenes preventing the sulfurous-earthy-animal register from being too heavy. The trio creates an elegant light luxury lamb preparation where lemon gives truffle unexpected freshness.",
     "Truffle Lemon Lamb Chops",
     ["Sear lamb chops until crusted; make a truffle-lemon sauce: truffle butter, lemon juice, and pasta water.", "Rest lamb 5 minutes; plate over the truffle-lemon sauce.", "Shave fresh truffle over; finish with lemon zest — the lemon lifts truffle and lamb beautifully."]),

    ("lamb","lemon","vanilla",
     "Lamb and vanilla share no direct compound but lemon bridges both — lemon's acidity suppresses lamb's gamey acids while vanilla's vanillin sweetness adds a second sweet-fat suppression of gaminess. Lemon's brightness prevents vanilla's sweetness from being cloying against lamb's richness, creating a balanced Moroccan-inspired preparation.",
     "Vanilla Lemon Moroccan Lamb",
     ["Brown lamb with spices; add lemon juice, lemon zest, and a split vanilla bean.", "Braise at 300°F for 2 hours; remove vanilla and reduce sauce.", "Serve over couscous with preserved lemon and herbs; the vanilla-lemon creates a bright-sweet braise."]),

    ("lamb","mint","oyster",
     "Lamb, mint, and oyster share trimethylamine — the marine-animal amine compound present in all three, connecting gamey meat, cooling herb, and marine bivalve through the same compound that menthol helps suppress through olfactory masking. The unusual trio appears in surf-and-turf preparations where mint bridges the gamey-marine register.",
     "Mint Lamb and Oyster Stew",
     ["Brown lamb pieces; add fish stock and fresh mint; simmer 1 hour until lamb is tender.", "Add shucked oysters in the last 3 minutes; they just need to cook through.", "Season with lemon, salt, and fresh mint; serve with warm bread."]),
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
print(f"Batch 047 done: inserted {len(TRIPLETS)} triplets.")
