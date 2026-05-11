#!/usr/bin/env python3
"""Seed pair descriptions batch 1: basil through caramel pairs (pairs 1-70)"""
import sqlite3, json, os

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db")

PAIRS = [
    # ── basil (19 pairs) ──
    ("basil","blue cheese",
     "Basil and blue cheese share linalool and phenolic aromatic compounds that bridge fresh herbaceousness with pungent fermented funk. Eugenol in basil softens the ammonia edge of blue mold, producing a surprisingly balanced savory-floral bite.",
     "Blue Cheese Basil Crostini",
     ["Toast baguette slices until crisp and golden brown.","Spread room-temperature blue cheese generously, top with torn fresh basil.","Drizzle with honey and cracked black pepper to finish."]),

    ("basil","butter",
     "Basil and butter share 2-phenylethanol and trace linalool, which together amplify the buttery roundness while adding a bright herbal lift. The fat in butter carries basil's volatile eugenol compounds longer on the palate.",
     "Basil Compound Butter",
     ["Blend softened butter with finely chopped fresh basil and lemon zest.","Roll into a log using plastic wrap and chill until firm.","Slice and melt over grilled fish or pasta immediately before serving."]),

    ("basil","caramel",
     "Basil and caramel share furaneol, a compound responsible for sweet strawberry-like and caramel-adjacent warmth in both. The contrast between basil's sharp phenolic bite and caramel's deep Maillard sweetness creates addictive complexity.",
     "Caramel Basil Panna Cotta",
     ["Warm cream with sugar until dissolved, bloom gelatin, stir in fresh basil.","Strain into molds and refrigerate until set, at least 4 hours.","Unmold and drizzle with warm salted caramel sauce to serve."]),

    ("basil","chocolate",
     "Both basil and chocolate contain phenylacetaldehyde and 2-phenylethanol, floral-rosy compounds that create an unexpected aromatic kinship. Basil's eugenol adds a spice-adjacent warmth that mirrors the darker roasted notes in fine dark chocolate.",
     "Dark Chocolate Basil Bark",
     ["Melt dark chocolate and temper to a glossy shine on parchment.","Scatter finely julienned fresh basil leaves evenly across the surface.","Sprinkle with flaky salt, cool completely, then break into shards."]),

    ("basil","coffee",
     "Basil and coffee share phenylacetaldehyde and acetic acid, compounds that together create a bridge between herbal brightness and roasted depth. Basil's volatile linalool cuts through coffee bitterness, adding a floral dimension rarely expected.",
     "Basil Cold Brew Lemonade",
     ["Steep coarse-ground coffee in cold water 18 hours, strain clean.","Muddle fresh basil with simple syrup and lemon juice in a glass.","Pour cold brew over ice, top with basil-lemon mixture, stir gently."]),

    ("basil","cucumber",
     "Basil and cucumber share linalool and benzaldehyde, which together produce a clean, garden-fresh aromatic profile with faint almond undertones. The aldehyde compounds in both create a brightness that reads as cooling even at room temperature.",
     "Basil Cucumber Agua Fresca",
     ["Blend cucumber with water, lemon juice, and a handful of basil leaves.","Strain through a fine mesh sieve, pressing pulp to extract liquid.","Serve over ice with a basil sprig and thin cucumber rounds."]),

    ("basil","garlic",
     "Basil and garlic form the aromatic backbone of Mediterranean cuisine through complementary sulfur and phenolic compound sets — garlic's diallyl disulfide deepens basil's eugenol into something intensely savory and round. This pairing is why pesto works.",
     "Classic Pesto",
     ["Blend basil, garlic, pine nuts, and Parmesan in a food processor.","Stream in olive oil until smooth and emulsified, season with salt.","Toss immediately with warm pasta, adding pasta water to loosen."]),

    ("basil","lamb",
     "Lamb's characteristic 4-methyloctanoic acid gives it a grassy, sheep-like quality that basil's eugenol and linalool directly counterbalance with herbal freshness. This is a classic Middle Eastern pairing precisely because the herbs suppress gaminess.",
     "Herb-Crusted Rack of Lamb",
     ["Mix minced garlic, basil, and breadcrumbs into a coarse paste with olive oil.","Press herb crust firmly onto the rack of lamb and let rest 20 minutes.","Roast at 425°F (220°C) until internal temp hits 130°F for medium-rare."]),

    ("basil","lavender",
     "Basil and lavender share the highest concentration of linalool of any culinary herbs — this shared terpene creates a seamless floral-herbal bridge that reads as elegant rather than overwhelming. Their 2-phenylethanol content adds a rosy, slightly sweet frame.",
     "Lavender Basil Olive Oil Cake",
     ["Infuse warm olive oil with dried lavender for 20 minutes then strain.","Mix into a standard cake batter with chopped fresh basil and lemon zest.","Bake at 350°F, cool, and dust with powdered sugar before slicing."]),

    ("basil","lemon",
     "Basil and lemon share linalool and trace geraniol — terpene compounds that together produce the signature aroma of a summer garden. Lemon's citral brightens basil's slightly anise-adjacent sweetness into something vivid and clean.",
     "Lemon Basil Risotto",
     ["Toast arborio rice in butter, add white wine and let absorb fully.","Ladle warm stock gradually, stirring constantly until creamy and al dente.","Finish off heat with lemon zest, juice, Parmesan, and torn fresh basil."]),

    ("basil","mint",
     "Basil and mint both carry linalool alongside their distinct signature compounds — eugenol in basil, menthol in mint — creating a layered herbal chord that is simultaneously warming and cooling. Used together they amplify each other's brightness.",
     "Basil Mint Chimichurri",
     ["Blend equal parts basil and mint with garlic, red wine vinegar, and oil.","Season with red pepper flakes, salt, and a pinch of sugar to balance.","Spoon generously over grilled steak or roasted vegetables immediately."]),

    ("basil","oyster",
     "Basil and oyster share phenylacetaldehyde and benzaldehyde — compounds that connect basil's floral-herbal character to the subtle sweetness hidden beneath brine. Basil's eugenol bridges the oceanic minerality into something aromatic and savory.",
     "Oysters with Basil Mignonette",
     ["Mince shallots finely, combine with white wine vinegar and chopped basil.","Season with cracked black pepper and a pinch of sugar, chill 30 minutes.","Spoon a small amount onto freshly shucked oysters and serve immediately."]),

    ("basil","parmesan",
     "Basil and Parmesan share phenylacetaldehyde and 2-phenylethanol, which create a floral-savory bridge that explains their near-universal co-appearance in Italian cooking. Parmesan's butyric acid richness rounds basil's volatile sharpness into something lingering.",
     "Parmesan Basil Soufflé",
     ["Make a roux, whisk in warm milk and finely grated Parmesan until thick.","Fold in beaten egg whites and chopped basil very gently to keep volume.","Bake in buttered ramekins at 375°F until puffed and golden, serve at once."]),

    ("basil","rose",
     "Basil and rose share 2-phenylethanol, geraniol, and linalool — a trifecta of floral terpene compounds that make them natural perfume allies. Both contain benzaldehyde at trace levels, adding an almond-adjacent depth beneath the flower-forward character.",
     "Rose Basil Sorbet",
     ["Heat water with sugar to make a syrup, steep rose petals until fragrant.","Blend cooled syrup with lemon juice and a generous handful of fresh basil.","Strain, churn in ice cream maker, freeze firm before scooping."]),

    ("basil","salmon",
     "Basil and salmon share linalool, connecting basil's herbal brightness directly to the subtle floral notes found in quality fatty salmon. Basil's 2-phenylethanol helps mask trimethylamine (fishy compounds) while amplifying salmon's natural sweetness.",
     "Basil-Crusted Salmon",
     ["Pulse basil, breadcrumbs, lemon zest, and olive oil to a coarse paste.","Press crust firmly onto salmon fillets and rest 10 minutes at room temp.","Bake at 400°F until crust is golden and fish flakes easily, about 12 minutes."]),

    ("basil","strawberry",
     "Basil and strawberry share furaneol, linalool, and 2-phenylethanol — a trio of sweet-floral compounds that make the combination taste like a single coherent flavor rather than two separate ones. This is textbook food pairing: high shared volatile overlap.",
     "Strawberry Basil Salad",
     ["Slice strawberries, toss with a little sugar and balsamic vinegar, rest 10 minutes.","Tear fresh basil directly over the strawberries just before serving.","Add fresh mozzarella and a crack of black pepper to complete."]),

    ("basil","tomato",
     "Basil and tomato share furaneol, linalool, and hexanal — the exact volatile set that defines 'garden ripe.' Basil's eugenol amplifies tomato's beta-ionone (its subtle violet note), transforming a raw tomato's aggressive acidity into something harmonious.",
     "Caprese with Torn Basil",
     ["Slice ripe tomatoes and best-quality mozzarella into equal rounds.","Arrange alternating, tuck torn fresh basil between each slice.","Drizzle with best olive oil, flaky salt, and cracked pepper — nothing else."]),

    ("basil","truffle",
     "Basil and truffle share phenylacetaldehyde and anisaldehyde — compounds that bridge basil's herbal brightness to truffle's deep earthy-sulfurous character. Basil's 2-phenylethanol lifts truffle's sometimes muddy earthiness into something more aromatic and vertical.",
     "Truffle Basil Pasta",
     ["Cook fresh tagliatelle until just al dente in well-salted boiling water.","Toss hot pasta with truffle oil, grated Parmesan, and finely torn basil.","Shave fresh black truffle generously over the top and serve immediately."]),

    ("basil","vanilla",
     "Basil and vanilla share vanillin, linalool, and 2-phenylethanol — a floral-sweet aromatic triad that makes this pairing surprisingly coherent. Basil's eugenol adds a spice-like warmth that mirrors vanilla's natural anise-adjacent sweetness in Madagascar beans.",
     "Vanilla Basil Crème Brûlée",
     ["Steep cream with a split vanilla bean and a few basil leaves over low heat.","Whisk into egg yolks and sugar, strain into ramekins, bake in water bath.","Refrigerate until set, then torch sugar topping until deeply caramelized."]),

    # ── blue cheese (18 pairs) ──
    ("blue cheese","butter",
     "Blue cheese and butter share butyric acid, acetic acid, and dimethyl sulfide — the same compound family responsible for the rich, slightly sharp quality in both. Fat acts as a carrier for blue cheese's volatile pungent esters, extending the flavor finish dramatically.",
     "Blue Cheese Butter Steak Sauce",
     ["Melt butter in a skillet over high heat until just beginning to brown.","Add crumbled blue cheese and swirl until melted into a glossy sauce.","Pour immediately over a rested steak and garnish with fresh thyme."]),

    ("blue cheese","caramel",
     "Blue cheese and caramel share acetic acid and diacetyl, which together create a sweet-tart-rich foundation. Caramel's Maillard compounds suppress blue cheese's ammonia edge while amplifying its nutty, aged depth — the combination is powerfully umami-adjacent.",
     "Blue Cheese Caramel Walnut Tart",
     ["Make a brown butter caramel, add toasted walnuts and a pinch of salt.","Pour into a blind-baked shell, crumble blue cheese across the top generously.","Bake at 350°F for 15 minutes until cheese softens and edges bubble."]),

    ("blue cheese","chocolate",
     "Blue cheese and chocolate share phenylacetaldehyde and dimethyl sulfide — compounds produced both by Maillard roasting and microbial fermentation. Dark chocolate's bitterness and blue cheese's funk share a chemical kinship that makes them taste like two expressions of the same depth.",
     "Dark Chocolate Blue Cheese Truffles",
     ["Melt dark chocolate with cream to make ganache, cool to spreadable consistency.","Mix in a small amount of crumbled blue cheese, roll into 1-inch balls.","Coat in cocoa powder, chill until firm, and serve at room temperature."]),

    ("blue cheese","coffee",
     "Blue cheese and coffee share dimethyl sulfide, acetic acid, and phenylacetaldehyde — roasted, fermented, and pungent compound threads connecting two very different foods. Coffee's bitterness and blue cheese's saltiness create a contrast that makes both flavors read as sharper and more distinct.",
     "Coffee-Glazed Blue Cheese Burger",
     ["Season a beef patty with salt, cook to medium, rest 3 minutes.","Whisk strong espresso with honey, brush onto bun and toast lightly.","Top burger with crumbled blue cheese and a coffee-glazed caramelized onion."]),

    ("blue cheese","cucumber",
     "Blue cheese and cucumber share hexanal and linalool at trace levels, which creates a refreshing counterpoint — cucumber's clean green aldehydes cut through blue cheese's heavy lactic fat and pungent ammonia compounds. The contrast reads as bright and palate-cleansing.",
     "Blue Cheese Cucumber Bites",
     ["Slice cucumber into thick rounds and hollow out a small well in each.","Pipe or spoon room-temperature blue cheese into each cucumber cup.","Top with a walnut half and a drizzle of honey, serve immediately."]),

    ("blue cheese","garlic",
     "Blue cheese and garlic share dimethyl sulfide and acetic acid — sulfurous, pungent compounds that in combination become surprisingly savory rather than harsh. Garlic's allicin transforms as it cooks, softening into sweet compounds that counterbalance blue cheese's ammonia sharpness.",
     "Blue Cheese Garlic Bread",
     ["Mix softened butter with roasted (not raw) garlic and crumbled blue cheese.","Spread generously on halved baguette and broil until bubbly and golden.","Garnish with chives and serve while hot."]),

    ("blue cheese","lamb",
     "Lamb and blue cheese share butyric acid, trimethylamine, and dimethyl sulfide — the same class of aliphatic and sulfurous compounds that give both their characteristic animal depth. Far from clashing, they reinforce each other's savory richness in a way that reads as deeply umami.",
     "Lamb Chops with Blue Cheese Crust",
     ["Mix blue cheese, breadcrumbs, and rosemary into a coarse crust mixture.","Press firmly onto seared lamb chops and transfer to a 400°F oven.","Roast 8–10 minutes until crust is golden and lamb is medium-rare."]),

    ("blue cheese","lavender",
     "Blue cheese and lavender share linalool, the primary terpene compound in lavender, which occurs in trace amounts within blue cheese's complex fermentation profile. Lavender's linalool acetate rounds the sharp ammonia notes of blue cheese into something almost floral and refined.",
     "Lavender Blue Cheese Honey Toast",
     ["Toast thick-cut bread, spread with room-temperature blue cheese while warm.","Warm honey with dried lavender buds until fragrant, strain out the buds.","Drizzle lavender honey over cheese and add a crack of black pepper."]),

    ("blue cheese","lemon",
     "Blue cheese and lemon share acetic acid, which connects the tartness of both — lemon's citric acidity acts as a natural contrast agent, cutting through blue cheese's heavy fat and amplifying its salt. The citral in lemon lifts and brightens the fermented depth dramatically.",
     "Lemon Blue Cheese Dressing",
     ["Whisk crumbled blue cheese with lemon juice, lemon zest, and a little cream.","Add a minced shallot, season with black pepper, and thin with buttermilk.","Drizzle over iceberg wedge with cherry tomatoes and candied walnuts."]),

    ("blue cheese","mint",
     "Blue cheese and mint share linalool, connecting the fermented dairy's subtle floral undertones to mint's bright, cooling terpene signature. Mint's menthol creates a refreshing contrast to blue cheese's dense, heavy fat — like a palate cleanser built into the pairing itself.",
     "Mint Blue Cheese Lamb Burger",
     ["Combine ground lamb with minced garlic, form into patties, grill to medium.","Make a sauce of crumbled blue cheese, fresh mint, and a spoon of yogurt.","Assemble in a pita with sliced cucumber and the blue cheese-mint sauce."]),

    ("blue cheese","oyster",
     "Blue cheese and oyster share dimethyl sulfide, trimethylamine, and phenylacetaldehyde — the pungent, briny compound set that connects fermented dairy and oceanic shellfish. Both have complex microbial backstories; together the brine of the oyster sharpens blue cheese's depth into something intensely saline and mineral.",
     "Oysters with Blue Cheese Foam",
     ["Blend room-temperature blue cheese with buttermilk until smooth, season lightly.","Use a hand blender or whisk vigorously to create a light foam.","Spoon a small amount of foam onto freshly shucked oysters on the half-shell."]),

    ("blue cheese","parmesan",
     "Blue cheese and Parmesan share butyric acid, acetic acid, dimethyl sulfide, and phenylacetaldehyde — they are essentially expressions of the same aged dairy compound family at different intensities. Parmesan's crystalline glutamate provides umami scaffolding that makes blue cheese's pungency feel structured rather than sharp.",
     "Three-Cheese Gnocchi Gratin",
     ["Boil potato gnocchi until they float, transfer to a buttered baking dish.","Make a béchamel, melt in both blue cheese and Parmesan until smooth.","Pour over gnocchi, top with breadcrumbs, bake at 400°F until golden."]),

    ("blue cheese","rose",
     "Blue cheese and rose share 2-phenylethanol and beta-ionone — floral compounds more unexpected in blue cheese but present from the metabolic byproducts of Penicillium roqueforti fermentation. Rose's geraniol contrasts the pungent ammonia sharpness with something delicate and perfumed.",
     "Rose Petal Blue Cheese Board",
     ["Bring blue cheese to room temperature and arrange on a wooden board.","Scatter fresh or crystallized rose petals around the cheese generously.","Add wildflower honey, marcona almonds, and sliced pear to complete the board."]),

    ("blue cheese","salmon",
     "Blue cheese and salmon share dimethyl sulfide and trimethylamine — marine sulfurous compounds that connect fatty fish and fermented dairy in unexpected chemical kinship. Salmon's omega-rich fat provides a smooth carrier for blue cheese's volatile pungent esters, mellowing both into a unified savory depth.",
     "Smoked Salmon Blue Cheese Bagel",
     ["Spread softened blue cheese on a toasted bagel as the base layer.","Layer with smoked salmon, thin red onion rounds, and capers generously.","Finish with a squeeze of lemon and fresh dill fronds."]),

    ("blue cheese","strawberry",
     "Blue cheese and strawberry share furaneol — a sweet, caramel-adjacent compound responsible for strawberry's distinctive scent that also appears in trace amounts in aged blue cheese. The contrast between blue cheese's pungent saltiness and strawberry's bright fruity sweetness is a classic of modern cheese boards.",
     "Blue Cheese Strawberry Flatbread",
     ["Stretch flatbread dough thin, brush with olive oil, bake at 450°F until crisp.","Scatter crumbled blue cheese and halved strawberries across the hot flatbread.","Drizzle with balsamic reduction and torn fresh basil before serving."]),

    ("blue cheese","tomato",
     "Blue cheese and tomato share furaneol, acetic acid, and hexanal — a surprisingly aligned volatile set connecting roasted depth and fermented funk. Tomato's acidity mirrors the tartness of the fermentation acids in blue cheese, while its beta-ionone adds violet-like floral depth.",
     "Heirloom Tomato Blue Cheese Tart",
     ["Blind-bake a pastry shell, spread with whipped blue cheese as the base.","Arrange sliced heirloom tomatoes in overlapping concentric circles on top.","Bake at 375°F until edges are golden, finish with fresh thyme and honey."]),

    ("blue cheese","truffle",
     "Blue cheese and truffle share phenylacetaldehyde, dimethyl sulfide, and anisaldehyde — three of the most powerful aromatic compounds in the savory world. Both are products of complex microbial activity; together their earthy-fungal-fermented aromatic sets amplify each other into something intensely luxurious.",
     "Truffle Blue Cheese Risotto",
     ["Sauté shallots in butter, toast arborio rice, deglaze with white wine.","Add warm stock ladle by ladle, stirring until creamy and al dente.","Finish off heat with blue cheese, truffle oil, and shaved fresh truffle."]),

    ("blue cheese","vanilla",
     "Blue cheese and vanilla share vanillin and 2-phenylethanol — sweet, floral compounds that soften blue cheese's aggression into something unexpectedly refined. Vanilla's anisaldehyde rounds the sharp butyric edge of blue cheese, making the combination taste like the complexity of a very aged cheese.",
     "Vanilla Blue Cheese Cheesecake",
     ["Make a gingersnap crust, press into a springform pan and bake 10 minutes.","Beat blue cheese with cream cheese, eggs, vanilla, and a touch of honey.","Bake in a water bath at 325°F until just set, chill overnight before serving."]),

    # ── butter (17 pairs) ──
    ("butter","caramel",
     "Butter and caramel share diacetyl, furaneol, and delta-decalactone — the exact trio of compounds responsible for the richest tasting notes in both. Butter's fat acts as a solvent that extends caramel's volatile aroma compounds, producing a finish that is rounder and longer than either alone.",
     "Salted Butter Caramel Sauce",
     ["Cook sugar dry in a heavy pan until deep amber, swirl gently to even color.","Remove from heat, whisk in warm heavy cream carefully (it will bubble).","Beat in cold salted butter in pieces until glossy, pour into a jar."]),

    ("butter","chocolate",
     "Butter and chocolate share dimethyl sulfide and furaneol — fat-soluble aromatic compounds that make butter the ideal medium for carrying and amplifying chocolate's roasted flavor. The dairy fat in butter softens chocolate's bitter polyphenols while extending the mouthfeel dramatically.",
     "Brown Butter Chocolate Chip Cookies",
     ["Brown butter until nutty and fragrant, cool to room temperature before mixing.","Cream with sugar, add eggs and vanilla, fold in flour and chocolate chunks.","Bake at 375°F, pull from oven while centers look underdone — they firm up."]),

    ("butter","coffee",
     "Butter and coffee share dimethyl sulfide and acetic acid — compounds that form the bridge between dairy richness and roasted bitterness. The fat in butter coats bitter coffee receptors on the tongue, making the same coffee taste less harsh and more complex simultaneously.",
     "Butter Coffee (Bulletproof Style)",
     ["Brew strong espresso or very concentrated French press coffee.","Add a tablespoon of high-quality unsalted butter to the hot coffee.","Blend at high speed until frothy and emulsified, drink immediately."]),

    ("butter","cucumber",
     "Butter and cucumber share hexanal and linalool at low levels — fresh green aldehyde notes that provide a clean, bright counterpoint to butter's fat richness. The (E)-2-nonenal in cucumber creates a melon-like freshness that makes butter feel lighter and more elegant.",
     "Cucumber Tea Sandwiches with Herb Butter",
     ["Blend softened butter with chives, dill, and a pinch of lemon zest.","Spread generously on thin white bread, layer with paper-thin cucumber slices.","Trim crusts, cut diagonally, and serve chilled on a platter."]),

    ("butter","garlic",
     "Butter and garlic share dimethyl sulfide and acetic acid, but the real magic is physical: butter's fat acts as the perfect carrier and moderator for garlic's harsh allicin, converting raw pungency into sweet, round savoriness through heat. Together they define an entire culinary flavor category.",
     "Garlic Brown Butter Sauce",
     ["Melt butter in a light-colored pan over medium heat, swirl frequently.","Add minced garlic when butter turns golden, cook 60 seconds until fragrant.","Pour immediately over pasta, roasted vegetables, or grilled fish."]),

    ("butter","lamb",
     "Butter and lamb share butyric acid and dimethyl sulfide — compounds that connect dairy fat and animal fat into a deeply savory whole. Butter's diacetyl (the primary buttery aroma compound) bridges lamb's characteristic grassy fatty acids into something more refined and less gamey.",
     "Butter-Basted Lamb Chops",
     ["Season lamb chops with salt and pepper, sear hot in a dry cast-iron pan.","Add butter, garlic, and rosemary, tilt pan and baste constantly for 3 minutes.","Rest 5 minutes before serving — the butter infuses the crust as it cools."]),

    ("butter","lavender",
     "Butter and lavender share linalool and trace 2-phenylethanol — floral terpenes that butter's fat captures and amplifies. Lavender's linalyl acetate dissolves readily into dairy fat, making infused butter a more efficient flavor vehicle than water-based infusions.",
     "Lavender Shortbread",
     ["Cream softened butter with powdered sugar until pale and fluffy.","Mix in flour, dried culinary lavender buds, and a pinch of salt until cohesive.","Slice into rounds, bake at 325°F until just golden at the edges, not brown."]),

    ("butter","lemon",
     "Butter and lemon share acetic acid and trace linalool, but the pairing is primarily textural-chemical: lemon's citric acid reacts with butter's fat to create emulsion stability while its volatile citral compounds cut through richness with vivid brightness. This is why beurre blanc works.",
     "Classic Lemon Beurre Blanc",
     ["Reduce white wine, shallots, and lemon juice in a small saucepan until syrupy.","Remove from heat, whisk in cold butter a few pieces at a time rapidly.","Strain, adjust seasoning, and spoon over poached fish or steamed vegetables."]),

    ("butter","mint",
     "Butter and mint share linalool and trace acetic acid, but the pairing works primarily through contrast: butter's dense fat provides a rich backdrop that allows menthol and menthone to read as cooling and refreshing rather than medicinal. The fat modulates mint's intensity.",
     "Mint Pea Butter Pasta",
     ["Blend fresh peas with mint and a splash of pasta water until smooth.","Toss cooked pasta with the pea-mint purée and cold diced butter off heat.","Finish with lemon zest, Pecorino, and a few whole mint leaves."]),

    ("butter","oyster",
     "Butter and oyster share dimethyl sulfide and acetic acid — compounds connecting dairy fat to oceanic brine. Butter's fat captures and carries oyster's delicate volatile esters, amplifying the brine and mineral character without overwhelming the oyster's subtle sweetness.",
     "Pan-Fried Oysters in Brown Butter",
     ["Dredge shucked oysters in seasoned flour, shake off excess.","Fry in a mix of butter and neutral oil until golden and just cooked through.","Brown extra butter separately and spoon over oysters with lemon and herbs."]),

    ("butter","parmesan",
     "Butter and Parmesan share butyric acid, acetic acid, furaneol, and dimethyl sulfide — overlapping dairy compound families that together produce a richer, more complex fat-umami flavor than either alone. Parmesan's glutamate works synergistically with butter's fat to create the silk-and-savory quality of great risotto.",
     "Parmesan Risotto Mantecatura",
     ["Cook risotto until al dente, remove from heat completely before finishing.","Add cold diced butter and finely grated Parmesan in stages, stirring vigorously.","Rest covered 2 minutes, then stir again — the emulsification creates the silk."]),

    ("butter","rose",
     "Butter and rose share 2-phenylethanol and trace geraniol — floral compounds that butter's fat captures more efficiently than water. Rose's citronellol dissolves into dairy fat and releases slowly on the palate, creating a perfumed, lingering butter that is more complex than it appears.",
     "Rose Butter on Warm Brioche",
     ["Blend softened unsalted butter with a few drops of rose water and rose petals.","Add a pinch of flaky salt and shape into a log, refrigerate until firm.","Serve in thick slices with warm, toasted brioche and wildflower honey."]),

    ("butter","salmon",
     "Butter and salmon share dimethyl sulfide, linalool, and acetic acid — fat-soluble aroma compounds that connect dairy richness and fatty fish. Butter's fat mutes trimethylamine (fishy off-notes) while carrying salmon's delicate floral volatiles more effectively to the nose.",
     "Butter-Poached Salmon",
     ["Heat butter with water in a wide pan until emulsified and just barely simmering.","Submerge salmon portions fully in the butter emulsion, cook gently 8–10 minutes.","Serve immediately with capers, dill, and a squeeze of lemon."]),

    ("butter","strawberry",
     "Butter and strawberry share furaneol — the single compound most responsible for strawberry's distinctive sweet-caramel scent — which also appears in browned butter. When strawberries are cooked in butter, furaneol from both sources combines into something that tastes more intensely 'strawberry' than either raw.",
     "Brown Butter Strawberry Skillet Cake",
     ["Brown butter until nutty, mix into a simple batter with sugar, eggs, and flour.","Pour into a cast-iron skillet, press halved strawberries deep into the batter.","Bake at 375°F until golden and set, serve warm directly from the pan."]),

    ("butter","tomato",
     "Butter and tomato share furaneol and trace hexanal — compounds that together create a sweet-savory richness. Butter's fat rounds tomato's sharp acidity into something deep and silky; this is the principle behind Marcella Hazan's famous tomato sauce, where butter replaces all the need for added sugar.",
     "Marcella Hazan Tomato Sauce",
     ["Simmer whole canned tomatoes with an onion halved and a large knob of butter.","Cook uncovered for 45 minutes, pressing tomatoes occasionally to break them.","Discard onion, season with salt, toss directly with pasta and more butter."]),

    ("butter","truffle",
     "Butter and truffle share dimethyl sulfide and phenylacetaldehyde — the sulfurous-roasted compound thread connecting two of the most expensive flavors in the world. Butter's fat is the ideal solvent for truffle's volatile 2,4-dithiapentane, making truffle butter more aromatic than truffle in oil.",
     "Truffle Butter Scrambled Eggs",
     ["Beat eggs with a splash of cream and season gently with salt.","Cook very slowly in a pan with truffle butter over lowest heat, stirring constantly.","Remove from heat while still slightly loose, top with shaved fresh truffle."]),

    ("butter","vanilla",
     "Butter and vanilla share vanillin, furaneol, delta-decalactone, and 2-phenylethanol — a near-complete overlap of sweet, lactonic, and floral aroma compounds. This is why vanilla butter frosting tastes 'more vanilla' than vanilla extract alone: the fat extends and amplifies the volatile esters.",
     "Vanilla Brown Butter Financiers",
     ["Brown butter to deep hazelnut color, cool slightly, whisk in egg whites.","Mix in powdered sugar, almond flour, flour, and scraped vanilla seeds.","Pour into financier molds and bake at 400°F for 12 minutes until golden."]),

    # ── caramel (16 pairs) ──
    ("caramel","chocolate",
     "Caramel and chocolate share furaneol, vanillin, furfural, and acetic acid — four major Maillard and caramelization reaction products that make both taste like 'cooked sugar' at different intensities. Together they create a unified deep-roasted sweet profile far more complex than either ingredient alone.",
     "Salted Caramel Chocolate Tart",
     ["Make dark chocolate ganache with cream, pour into a baked tart shell.","Layer with a thick salted caramel before the chocolate sets completely.","Chill until firm, top with flaky sea salt just before slicing and serving."]),

    ("caramel","coffee",
     "Caramel and coffee share furfural, acetic acid, and vanillin — three of the primary volatile compounds produced by the Maillard reaction and caramelization. Both are 'roasted' foods in chemical terms; together their bittersweet, brown-sugar aromatic profiles reinforce each other into something deeply complex.",
     "Coffee Caramel Affogato",
     ["Scoop good vanilla ice cream into a warmed espresso cup or small bowl.","Pour a single hot shot of espresso directly over the ice cream.","Drizzle with a spoonful of salted caramel sauce and serve immediately."]),

    ("caramel","cucumber",
     "Caramel and cucumber share very few direct volatile compounds, making this a contrast pairing: caramel's intensely sweet Maillard products are cut by cucumber's (E)-2-nonenal and hexanal, which act like a palate-reset between bites. The contrast creates a refreshing balance.",
     "Caramel Cucumber Granita Float",
     ["Blend cucumber with lime juice and simple syrup, freeze in a shallow pan.","Scrape regularly with a fork every 30 minutes until granita texture is achieved.","Serve in a glass with a drizzle of warm salted caramel poured over top."]),

    ("caramel","garlic",
     "Caramel and garlic share acetic acid and trace dimethyl sulfide — but this pairing works primarily through contrast and the surprising sweetness of caramelized garlic itself. When garlic is slowly browned in sugar or caramelized, its harsh allicin converts into sweet vinyl compounds that mirror caramel's Maillard products.",
     "Caramelized Garlic Tarte Tatin",
     ["Slowly caramelize whole garlic cloves with butter and a touch of sugar until sweet.","Arrange in a skillet, pour over a caramel made in the same pan.","Top with puff pastry, bake at 400°F until golden, invert carefully to serve."]),

    ("caramel","lamb",
     "Caramel and lamb share acetic acid and trace dimethyl sulfide, but the pairing works through flavor contrast — caramel's intense sweetness provides a foil for lamb's gamey fat acids. Caramelized sugars in glazes suppress the sharp 4-methyloctanoic acid that defines lamb's characteristic smell.",
     "Caramel-Glazed Lamb Ribs",
     ["Slow-cook lamb ribs at 300°F for 3 hours until tender and falling apart.","Make a caramel with sugar, soy sauce, garlic, and ginger until syrupy.","Brush ribs with glaze, broil 5 minutes each side until charred and lacquered."]),

    ("caramel","lavender",
     "Caramel and lavender share diacetyl and trace linalool — buttery and floral compounds that connect caramel's warm sweetness to lavender's cool terpene character. Caramel's Maillard depth provides the grounding that prevents lavender from reading as soapy or overly perfumed.",
     "Lavender Caramel Macarons",
     ["Infuse hot cream with dried lavender, strain and use to make caramel filling.","Pipe French macaron shells using standard egg white and almond flour method.","Fill cooled shells with lavender caramel, rest overnight before serving."]),

    ("caramel","lemon",
     "Caramel and lemon share acetic acid — the tartness thread connecting Maillard sweetness and citrus brightness. Lemon's citral and limonene cut through caramel's heavy, cloying sweetness and reset the palate, which is exactly why a squeeze of lemon over a caramel dessert always tastes right.",
     "Lemon Caramel Tart",
     ["Make a curd with lemon juice, zest, eggs, and butter until thickened.","Pour into a fully baked tart shell and refrigerate until set, about 3 hours.","Drizzle with warm caramel and top with candied lemon zest before serving."]),

    ("caramel","mint",
     "Caramel and mint share diacetyl at trace levels — buttery compounds that connect mint's subtle richness to caramel's sweet warmth. Menthol's cooling sensation creates a dramatic thermal contrast with hot caramel, making the combination feel like dessert and palate-cleanser simultaneously.",
     "Mint Caramel Hot Chocolate",
     ["Make a caramel, whisk in hot whole milk until smooth and combined.","Add good-quality dark chocolate in pieces, whisk until fully melted.","Serve in warmed mugs, top with a mint sprig and a few drops of mint oil."]),

    ("caramel","oyster",
     "Caramel and oyster is a bold contrast pairing — caramel's Maillard sweetness creates a foil for oyster's oceanic brine, with acetic acid shared between them as a tension-building thread. The sweetness of caramel amplifies the perceived salinity of the oyster dramatically.",
     "Caramel Miso-Glazed Oysters",
     ["Whisk white miso with caramel sauce, sake, and a drop of sesame oil.","Spoon a small amount of miso-caramel onto each shucked oyster in the shell.","Broil 3–4 minutes until edges curl and glaze is bubbling and golden."]),

    ("caramel","parmesan",
     "Caramel and Parmesan share furaneol, acetic acid, and diacetyl — the same sweet-tart-buttery compound set that appears in aged dairy and Maillard-driven cooked sugars. Parmesan's intense glutamate makes caramel's sweetness read as savory rather than cloying — the basis of candied Parmesan crisps.",
     "Parmesan Caramel Crisps",
     ["Arrange small mounds of finely grated Parmesan on a parchment-lined baking sheet.","Bake at 375°F until lacy and golden, remove from oven and drizzle with caramel.","Cool flat until crisp, then serve as a snack or salad garnish."]),

    ("caramel","rose",
     "Caramel and rose share 2-phenylethanol and beta-ionone — floral compounds that Maillard reactions in caramel produce in trace amounts and rose contains in abundance. Rose's geraniol lifts caramel's sometimes heavy sweetness into something more aromatic and delicate.",
     "Rose Caramel Semifreddo",
     ["Make a caramel, stir in rose water and cream until smooth and cooled.","Fold into whipped cream and beaten egg whites until light and airy.","Freeze in a loaf mold, slice and serve with fresh rose petals scattered over."]),

    ("caramel","salmon",
     "Caramel and salmon share acetic acid and dimethyl sulfide — a sulfurous-acidic thread that makes sweet glazes and fatty fish a surprisingly natural pairing. Caramel's sweetness suppresses the trimethylamine (fishy) compounds in salmon while its Maillard crust adds textural contrast.",
     "Caramel Miso Salmon",
     ["Whisk caramel with white miso, soy sauce, and grated ginger for the glaze.","Marinate salmon fillets 30 minutes, then place on a foil-lined baking sheet.","Broil 8–10 minutes until caramelized on top and just cooked through inside."]),

    ("caramel","strawberry",
     "Caramel and strawberry share furaneol — in fact, furaneol is one of strawberry's most important aroma compounds and also a key product of caramelization. When strawberries are cooked into caramel, furaneol from both sources concentrates into a single note of extraordinary sweet intensity.",
     "Strawberry Caramel Jam",
     ["Cook strawberries with sugar until they release their juice and begin to soften.","Continue cooking until a candy thermometer reads 220°F (jam set point).","Stir in a touch of butter and salt at the end, jar immediately while hot."]),

    ("caramel","tomato",
     "Caramel and tomato share furaneol and acetic acid — the sweet-savory molecular bridge that explains why slow-roasting tomatoes with sugar is such an effective technique. Heat converts tomato's acidity into sweet Maillard compounds; caramel reinforces this transformation.",
     "Caramelized Tomato Galette",
     ["Slow-roast tomatoes with sugar and olive oil at 325°F until jammy and deep.","Spread onto a rough puff pastry circle, fold edges and bake until golden.","Drizzle with caramel and fresh thyme just before serving warm."]),

    ("caramel","truffle",
     "Caramel and truffle share phenylacetaldehyde and acetic acid — a rosy, honey-like compound and a sharp acidic note that together create unexpected aromatic resonance. Truffle's sulfurous earthiness is cut and elevated by caramel's Maillard sweetness into something intensely luxurious.",
     "Truffle Honey Caramel Cheese Plate",
     ["Make a dry caramel, stir in truffle oil and flaky salt off the heat.","Pour thin onto parchment, cool completely until brittle and snappable.","Break into shards and serve alongside aged cheeses and honeycomb."]),

    ("caramel","vanilla",
     "Caramel and vanilla share vanillin, furaneol, diacetyl, and 2-acetyl furan — a nearly perfect overlap of sweet Maillard and aldehyde aroma compounds. Vanilla's pure vanillin rounds caramel's sometimes harsh burned-sugar edge into something rounder, creamier, and more complex.",
     "Vanilla Caramel Pot de Crème",
     ["Heat cream with a split vanilla bean until just simmering, steep 20 minutes.","Whisk into egg yolks with caramel, strain into small ramekins.","Bake in a water bath at 325°F until just set with a slight jiggle in center."]),
]

conn = sqlite3.connect(os.path.normpath(DB))
c = conn.cursor()
inserted = 0
for (a, b, desc, title, steps) in PAIRS:
    a, b = sorted([a, b])
    c.execute(
        "INSERT OR REPLACE INTO pair_info (ing_a, ing_b, description, recipe_title, recipe_steps) VALUES (?, ?, ?, ?, ?)",
        (a, b, desc, title, json.dumps(steps))
    )
    inserted += 1
conn.commit()
conn.close()
print(f"Batch 1 done: inserted {inserted} pairs.")
