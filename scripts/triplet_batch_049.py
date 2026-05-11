#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("lamb","rose","salmon",
     "Lamb and salmon share dimethyl sulfide and trimethylamine — the sulfurous-marine compound family linking gamey meat and fatty fish — while rose's geraniol and 2-phenylethanol provide floral aromatic displacement that suppresses both lamb's 4-methyloctanoic acid and salmon's trimethylamine through the same olfactory masking mechanism. The trio works in Persian surf-turf preparations.",
     "Rose Persian Lamb and Salmon Platter",
     ["Marinate both lamb and salmon separately in rose water, saffron, lemon, and herbs.", "Grill lamb to medium-rare and salmon until just opaque; rest each before plating.", "Arrange together on a platter with rose petals, fresh herbs, and a rose-yogurt sauce."]),

    ("lamb","rose","strawberry",
     "Lamb and rose share 2-phenylethanol and geraniol — floral-citrus compounds that rose produces and that suppress lamb's gamey acids — while strawberry's furaneol sweetness and linalool reinforce rose's floral register and add fruit-sweet contrast to the meat. The trio creates an aromatic Middle Eastern lamb preparation with fruit accent.",
     "Rose Strawberry Lamb Salad",
     ["Grill lamb loin to medium-rare; rest and slice thin against the grain.", "Arrange over arugula with sliced fresh strawberries, rose petals, and crumbled feta.", "Dress with a rose water-strawberry vinaigrette; finish with rose petals and mint."]),

    ("lamb","rose","tomato",
     "Lamb and tomato share furaneol and acetic acid — the sweet-caramel and tart compounds driving rich meat braises — while rose's 2-phenylethanol and geraniol provide floral displacement that softens both lamb's gaminess and tomato's raw acidity into a perfumed, gentle register. The trio drives Iranian lamb-tomato stews and Turkish güveç preparations.",
     "Rose Tomato Braised Lamb",
     ["Brown lamb with onion; add crushed tomatoes, rose water, saffron, cinnamon, and stock.", "Braise at 300°F for 2 hours until tender; reduce sauce until concentrated and glossy.", "Serve over saffron rice garnished with dried rose petals and fresh herb."]),

    ("lamb","rose","truffle",
     "Lamb and truffle share dimethyl sulfide and phenylacetaldehyde — the sulfurous-rosy compound pair linking gamey meat and earthy fungus — while rose's 2-phenylethanol reinforces truffle's own rosy-fermented compound and amplifies the floral register that suppresses lamb's 4-methyloctanoic acid. The trio reaches the pinnacle of luxury savory flavor.",
     "Rose Truffle Lamb Saddle",
     ["Stuff lamb saddle with a rose-truffle compound butter and truffle paste; tie and roast.", "Roast at 400°F to medium-rare; rest 10 minutes before slicing to reveal the stuffing.", "Serve over truffle-potato purée with a rose-truffle jus and fresh rose petal garnish."]),

    ("lamb","rose","vanilla",
     "Lamb and vanilla form the boldest sweet-savory contrast in this set — vanilla's vanillin and furaneol suppressing lamb's 4-methyloctanoic acid through sweet-lactonic displacement — while rose's geraniol and 2-phenylethanol provide the floral bridge between vanilla's perfumed sweetness and the gamey meat. The trio is Moroccan and Persian in character.",
     "Rose Vanilla Moroccan Lamb",
     ["Brown lamb with ras el hanout, onion, rose water, and a split vanilla bean in a tagine.", "Add dried apricots, almonds, honey, and stock; braise covered at 300°F for 2 hours.", "Finish with dried rose petals and fresh coriander; serve over couscous with rose-yogurt."]),

    ("lamb","salmon","strawberry",
     "Lamb and salmon share dimethyl sulfide and trimethylamine — the sulfurous-marine animal compound family — while strawberry's furaneol sweetness and linalool provide the dual sweet-floral aromatic bridge that suppresses both lamb's gaminess and salmon's marine notes simultaneously. The unusual trio works in elaborate surf-turf presentations with fruit sauce.",
     "Strawberry Lamb and Salmon Duo",
     ["Make a strawberry-balsamic reduction as the unifying sauce for both proteins.", "Grill lamb to medium-rare and pan-sear salmon; rest each before plating.", "Plate side by side, drizzle the strawberry reduction over both, garnish with fresh strawberries."]),

    ("lamb","salmon","tomato",
     "Lamb and salmon share dimethyl sulfide while both share furaneol and acetic acid with tomato — the sweet-caramel and tart compounds creating a three-way aromatic bridge — making tomato the natural connector between gamey meat and fatty fish. The trio appears in Mediterranean seafood-meat one-pot preparations like Sicilian fish braises with lamb.",
     "Tomato Braised Lamb and Salmon",
     ["Brown lamb pieces; add crushed tomatoes, white wine, garlic, and herbs; braise 1 hour.", "Add salmon pieces in the final 8 minutes; they cook gently in the tomato-lamb broth.", "Serve with crusty bread; the tomato braise has unified the meat and fish seamlessly."]),

    ("lamb","salmon","truffle",
     "Lamb, salmon, and truffle form a triple-dimethyl sulfide combination — all three share the sulfurous aromatic compound that creates their distinct earthy-marine-animal character — making this the most sulfurous-rich combination in the triplet set. The trio requires careful acid and herb balance to manage the intensity.",
     "Truffle Lamb and Salmon Surf-Turf",
     ["Sear both lamb loin and salmon with truffle butter in separate pans until each is perfect.", "Rest lamb to medium-rare; finish salmon just barely opaque at the center.", "Plate together over truffle-potato purée with shaved fresh truffle over both proteins."]),

    ("lamb","salmon","vanilla",
     "Lamb and salmon share trimethylamine and dimethyl sulfide — the animal-marine compound family — while vanilla's vanillin and furaneol provide the sweetest possible aromatic counterpoint that suppresses both proteins' pungent volatiles through sweet-lactonic displacement. The unusual trio works in Scandinavian sweet-spiced preparations.",
     "Vanilla Poached Salmon and Lamb Duo",
     ["Poach salmon gently in a vanilla bean court bouillon until just cooked; keep warm.", "Serve alongside pan-seared lamb loin with a vanilla-lamb jus and roasted root vegetables.", "Vanilla bridges both proteins; the sweet-lactonic compounds suppress marine and gamey notes equally."]),

    ("lamb","strawberry","tomato",
     "Lamb and tomato share furaneol and acetic acid — sweet-caramel and tart compounds driving braises — while strawberry amplifies tomato's own furaneol content and adds fruit-sweet contrast to the meat, creating a triple-furaneol sweet-savory preparation. The trio appears in Moroccan lamb tagines with tomato-fruit bases.",
     "Strawberry Tomato Lamb Tagine",
     ["Brown lamb with onion, ras el hanout, and cinnamon in a tagine.", "Add crushed tomatoes, strawberry jam, preserved lemon, and stock; braise 2 hours at 300°F.", "Finish with fresh strawberries and mint; the furaneol in all three ingredients unifies the dish."]),

    ("lamb","strawberry","truffle",
     "Lamb and truffle share dimethyl sulfide and phenylacetaldehyde — the sulfurous-rosy compound pair — while strawberry's furaneol sweetness and phenylacetaldehyde provide the sweet-rosy contrast that suppresses lamb's gaminess and complements truffle's own rosy fermentation compound. The trio creates an indulgent luxury spring lamb preparation.",
     "Truffle Strawberry Lamb Tartare",
     ["Finely chop raw lamb loin; season with truffle oil, shallot, and flaky salt.", "Gently fold in diced fresh strawberry and a drizzle of truffle honey.", "Plate on chilled plates, shave fresh truffle over the top, and garnish with strawberry coulis."]),

    ("lamb","strawberry","vanilla",
     "Vanilla and strawberry share furaneol, linalool, and 2-phenylethanol — the most complete overlap between any spice and fruit — while lamb's gamey 4-methyloctanoic acid is suppressed by both vanilla's sweetness and strawberry's fruity-floral contrast simultaneously. The trio creates the most fragrant possible sweet-savory lamb preparation.",
     "Strawberry Vanilla Braised Lamb Shank",
     ["Brown lamb shanks; braise with strawberry purée, vanilla bean, wine, and stock at 325°F for 3 hours.", "Remove shanks; reduce braising liquid with fresh strawberries until a glossy sauce forms.", "Plate shanks on polenta with the strawberry-vanilla sauce and a fresh strawberry garnish."]),

    ("lamb","tomato","truffle",
     "Lamb and tomato share furaneol while lamb and truffle share dimethyl sulfide and phenylacetaldehyde — two separate aromatic bridges linking the three ingredients — creating a rich layered umami base where truffle's earthiness elevates the long-cooked lamb-tomato into a luxury register. The trio is the flavor of high-end Italian lamb ragù with truffle.",
     "Truffle Tomato Lamb Ragù",
     ["Brown ground lamb; add crushed San Marzano tomatoes, red wine, and herbs; simmer 1 hour.", "Off heat, stir in truffle butter until glossy and deeply aromatic; season precisely.", "Toss with pappardelle, shave generous truffle over, and finish with Parmesan at the table."]),

    ("lamb","tomato","vanilla",
     "Lamb and tomato share furaneol and acetic acid — the sweet-caramel and tart compound pair — while vanilla's own furaneol and vanillin sweetness amplifies tomato's natural furaneol and softens lamb's gamey acids simultaneously. The trio creates an unusual but chemically sound sweet-savory lamb braise echoing Moroccan preparations.",
     "Vanilla Tomato Braised Lamb",
     ["Brown lamb with onion and ras el hanout; add crushed tomatoes, a split vanilla bean, and stock.", "Braise at 300°F for 2 hours until tender; remove vanilla pod and reduce sauce.", "Serve over couscous; the vanilla lifts the tomato and softens the gamey lamb aromatics."]),

    ("lamb","truffle","vanilla",
     "Lamb and truffle share dimethyl sulfide and phenylacetaldehyde — the sulfurous-rosy compound pair — while vanilla's vanillin provides the sweetest possible aromatic contrast that softens lamb's 4-methyloctanoic acid and truffle's intense earthiness simultaneously. The trio creates the most luxurious sweet-savory-earthy lamb preparation.",
     "Truffle Vanilla Braised Lamb with Potato Purée",
     ["Braise lamb shoulder with truffle paste, vanilla bean, wine, and veal stock for 3 hours at 325°F.", "Shred lamb; reduce braising liquid with more truffle butter to a glossy sauce.", "Serve over butter-rich potato purée; shave fresh truffle over and finish with vanilla jus."]),

    ("lavender","lemon","mint",
     "Lavender, lemon, and mint share linalool — the dominant terpene compound that all three produce — creating the most concentrated linalool combination in the culinary plant set, while lemon's citric brightness and mint's menthol provide contrasting foreground aromatics above the shared terpene base. The trio is Provençal lemonade and Mediterranean herb water.",
     "Lavender Lemon Mint Spritzer",
     ["Make lavender-mint syrup by steeping both in hot sugar water 20 minutes; strain.", "Combine syrup with fresh lemon juice and sparkling water in a chilled pitcher.", "Serve over ice with a fresh mint sprig, a wedge of lemon, and a pinch of dried lavender."]),

    ("lavender","lemon","oyster",
     "Lavender's linalool and linalyl acetate provide a floral-herbal counterpoint to oyster's marine dimethyl sulfide — an unexpected floral-brine encounter — while lemon's citric acid provides the acid bridge that cuts through oyster's marine fat and softens lavender's floral intensity into a Provençal refined oyster preparation.",
     "Lavender Lemon Oyster Mignonette",
     ["Combine white wine vinegar, finely minced shallots, dried lavender, and cracked pepper.", "Add fresh lemon juice and zest; rest 15 minutes for the lavender to infuse.", "Spoon over freshly shucked raw oysters on crushed ice; serve immediately with extra lemon."]),

    ("lavender","lemon","parmesan",
     "Lavender and Parmesan create a floral-umami encounter — lavender's linalool and linalyl acetate contrasting with Parmesan's butyric acid and glutamate — while lemon's citric acid brightens both the cheese and the floral herb, cutting through Parmesan's fat and grounding lavender's perfumed sweetness. The trio creates Provençal-Italian savory shortbreads.",
     "Lavender Lemon Parmesan Shortbread",
     ["Blend grated Parmesan with cold butter, flour, lemon zest, and dried lavender until crumbly.", "Knead gently, roll, and cut into rounds; refrigerate 20 minutes before baking.", "Bake at 350°F until just golden; cool and finish with a drop of lemon juice each."]),

    ("lavender","lemon","rose",
     "Lavender, lemon, and rose share geraniol and linalool — the citrus-floral terpene pair produced in all three — creating the most concentrated floral-citrus terpene combination in the culinary set, while each contributes a distinct foreground aroma above the shared terpene base. The trio defines Provençal and Persian cold drink and dessert preparations.",
     "Rose Lavender Lemon Panna Cotta",
     ["Warm cream with rose water, dried lavender, and lemon zest; steep 20 minutes, strain.", "Dissolve gelatin, sweeten lightly, pour into molds, and refrigerate 4 hours until set.", "Unmold, drizzle with rose-lemon syrup, and garnish with rose petals and a tiny lavender sprig."]),

    ("lavender","lemon","salmon",
     "Lavender's linalool and lemon's geraniol both suppress salmon's trimethylamine through terpene displacement — lavender from the floral direction and lemon from the citrus direction — creating a double-aromatic suppression of salmon's marine notes while their shared linalool builds a coherent herbal-floral-citrus register around the fish.",
     "Lavender Lemon Baked Salmon",
     ["Mix dried lavender with lemon zest, olive oil, and a touch of honey; rub over salmon.", "Bake at 400°F for 12 minutes until just opaque; rest 3 minutes before serving.", "Plate with a lavender-lemon beurre blanc and a thin slice of lemon over each fillet."]),
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
print(f"Batch 049 done: inserted {len(TRIPLETS)} triplets.")
