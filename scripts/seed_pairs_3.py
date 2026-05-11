#!/usr/bin/env python3
"""Seed pair descriptions batch 3: lamb through truffle+vanilla (66 pairs)"""
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

PAIRS = [
    # ── lamb (11 pairs) ──
    ("lamb","lavender",
     "Lamb and lavender share linalool and dimethyl sulfide — a floral-sulfurous compound thread that explains why lavender is a classic Provençal herb for roasted lamb. Lavender's linalyl acetate directly suppresses lamb's characteristic 4-methyloctanoic acid, the compound responsible for its gamey quality.",
     "Lavender-Crusted Rack of Lamb",
     ["Mix dried culinary lavender, fresh thyme, garlic, and olive oil into a paste.","Press firmly onto the rack of lamb and let rest at room temperature 30 minutes.","Roast at 425°F until internal temp hits 130°F; rest 8 minutes before carving."]),

    ("lamb","lemon",
     "Lamb and lemon share acetic acid and trace linalool — a tart-floral bridge that allows lemon to cut through lamb's rich, saturated fatty acids without suppressing its complexity. Lemon's citric acid acts on lamb's surface proteins, tenderizing while its volatile citral compounds brighten the fat.",
     "Lemon Lamb Souvlaki",
     ["Marinate lamb cubes in lemon juice, olive oil, garlic, and oregano overnight.","Thread onto skewers and grill over high heat, turning once, until charred outside.","Serve in warm pita with tzatziki, tomato, and shaved red onion."]),

    ("lamb","mint",
     "Lamb and mint share linalool and dimethyl sulfide — a pairing so classic it has defined British and Middle Eastern cuisine for centuries. Mint's menthol directly suppresses lamb's 4-methyloctanoic acid through competitive receptor interaction, while linalool bridges both into a clean, herbal finish.",
     "Mint Sauce for Roast Lamb",
     ["Finely chop a large bunch of fresh mint and combine with a pinch of sugar.","Pour over boiling water just to wilt, then add white wine vinegar to taste.","Let steep 30 minutes; serve at room temperature alongside sliced roast lamb."]),

    ("lamb","oyster",
     "Lamb and oyster share trimethylamine and dimethyl sulfide — both are defined by marine and animal-derived sulfurous compounds at different intensities. This surf-and-turf pairing creates a compound depth: oyster's mineral brine amplifies lamb's savory fat into something intensely umami-forward.",
     "Lamb and Oyster Pot Pie",
     ["Braise diced lamb shoulder in red wine and stock until very tender, about 2 hours.","Shuck oysters and fold into the warm lamb filling just before topping with pastry.","Brush pastry with egg wash, bake at 400°F until golden and filling is bubbling."]),

    ("lamb","parmesan",
     "Lamb and Parmesan share butyric acid, dimethyl sulfide, and phenylacetaldehyde — connecting animal fat and aged dairy through their shared fermentation-adjacent volatile compounds. Parmesan's crystalline glutamate amplifies lamb's own intrinsic umami, creating a deeply savory, rounded flavor.",
     "Lamb Ragù with Parmesan",
     ["Brown ground lamb in batches, deglaze with red wine until fully absorbed.","Add crushed tomatoes and simmer low and slow for 90 minutes uncovered.","Toss with pasta, finish with cold butter and a heavy snow of Parmesan."]),

    ("lamb","rose",
     "Lamb and rose share 2-phenylethanol and trace beta-ionone — floral compounds connecting lamb's complex aromatic fat profile to rose's primary aroma compounds. In Persian cuisine, rose water is traditionally paired with lamb precisely because its geraniol rounds the gamey fatty acids.",
     "Persian Rose Water Lamb Stew",
     ["Brown lamb pieces with onion, turmeric, and cinnamon until deeply colored.","Add saffron water, pomegranate molasses, and a teaspoon of rose water.","Simmer covered until very tender, serve over saffron rice with fresh herbs."]),

    ("lamb","salmon",
     "Lamb and salmon share dimethyl sulfide, trimethylamine, and linalool — sulfurous marine and floral compounds that create an unexpected savory kinship between fatty fish and red meat. Both contain omega-rich fats that carry aromatic compounds similarly on the palate.",
     "Surf and Turf Skewers",
     ["Cut lamb and salmon into equal-sized cubes, marinate separately in herb oil.","Alternate lamb and salmon on skewers with cherry tomatoes and lemon wedges.","Grill over high heat, turning once; both cook at similar times."]),

    ("lamb","strawberry",
     "Lamb and strawberry share furaneol and linalool — a sweet-floral bridge that sounds improbable but underlies several Moroccan and Middle Eastern tagine traditions. Furaneol from slow-cooked lamb caramelization combines with strawberry's fruity ethyl butanoate into a sweet-savory unity that reduces gaminess.",
     "Lamb Tagine with Strawberry Harissa",
     ["Simmer lamb shoulder with ras el hanout, onion, and preserved lemon 2 hours.","Blend fresh strawberries with harissa, add to the tagine in the last 20 minutes.","Serve over couscous with toasted almonds and fresh mint."]),

    ("lamb","tomato",
     "Lamb and tomato share hexanal, acetic acid, and furaneol — green aldehyde and sweet-tart compounds that connect lamb's savory fat to tomato's bright acidity. Tomato's lycopene-adjacent compounds directly cut through lamb's saturated fatty acids, making slow-cooked lamb-tomato preparations taste lighter than their fat content suggests.",
     "Slow-Braised Lamb with Tomatoes",
     ["Brown lamb pieces aggressively until a dark crust forms on all sides.","Add crushed tomatoes, garlic, and olives; braise at 325°F covered 2.5 hours.","Remove lid last 30 minutes to concentrate the sauce; serve with crusty bread."]),

    ("lamb","truffle",
     "Lamb and truffle share dimethyl sulfide, phenylacetaldehyde, and trimethylamine — pungent, earthy, and sulfurous compounds that both produce from their respective biological processes. Together their animal-meets-earth aromatic profiles amplify each other into something extraordinarily rich and complex.",
     "Truffle-Stuffed Lamb Loin",
     ["Butterfly a lamb loin, layer with black truffle shavings and fresh thyme.","Roll tightly, tie with butcher's twine, and sear all surfaces until deeply browned.","Roast at 375°F to medium-rare, rest 10 minutes, slice and serve immediately."]),

    ("lamb","vanilla",
     "Lamb and vanilla share 2-phenylethanol and trace dimethyl sulfide — a floral-sulfurous thread connecting fatty meat to sweet spice. Vanilla's vanillin is fat-soluble and dissolves into lamb's fat during slow cooking, creating a subtle sweet-savory depth used in Moroccan and Indian preparations.",
     "Vanilla-Spiced Lamb Shoulder",
     ["Blend vanilla bean seeds with Moroccan spices, garlic, and olive oil into a paste.","Rub the entire lamb shoulder and marinate refrigerated overnight.","Slow-roast at 300°F for 5 hours until falling-apart tender."]),

    # ── lavender (10 pairs) ──
    ("lavender","lemon",
     "Lavender and lemon share linalool and geraniol — terpene compounds that both plants produce in high concentrations, making this one of the highest compound-overlap pairings in the dataset. Lemon's citral prevents lavender from reading as soapy or medicinal, grounding the floral into vivid citrus brightness.",
     "Lavender Lemon Shortbread",
     ["Cream butter with powdered sugar, lemon zest, and dried lavender buds.","Mix in flour and a pinch of salt until a smooth dough forms; chill 30 minutes.","Slice into rounds and bake at 325°F until just set and barely golden."]),

    ("lavender","mint",
     "Lavender and mint share linalool and 1,8-cineole — terpene compounds that create a dual-cooling, herbal aromatic profile. Used together, lavender's floral sweetness and mint's menthol cooling reinforce each other; the combination is used in aromatherapy because both compounds act synergistically on the same receptors.",
     "Lavender Mint Herbal Tea",
     ["Combine dried lavender buds and fresh mint leaves in a warmed teapot.","Pour water heated to 90°C (not boiling) over herbs and steep 5 minutes.","Strain, sweeten lightly with honey if desired, and serve immediately."]),

    ("lavender","oyster",
     "Lavender and oyster share linalool and trace phenylacetaldehyde — floral and rosy compounds connecting herb and brine. Lavender's linalyl acetate provides an unexpected floral counterpoint to oyster's oceanic mineral character, lifting the saline intensity into something more aromatic and complex.",
     "Lavender Mignonette Oysters",
     ["Infuse red wine vinegar with dried lavender for 2 hours, then strain.","Add finely minced shallot, cracked pepper, and a pinch of sugar to taste.","Spoon a small amount onto each freshly shucked oyster and serve immediately."]),

    ("lavender","parmesan",
     "Lavender and Parmesan share linalool and 2-phenylethanol at trace levels — a floral-rosy thread that connects the herb to aged dairy. Parmesan's glutamate richness grounds lavender's sometimes overpowering terpene intensity into something more food-appropriate and savory-adjacent.",
     "Lavender Honey Parmesan Crisps",
     ["Arrange small mounds of grated Parmesan on parchment and bake at 375°F until lacy.","Remove from oven, immediately drizzle with lavender-infused honey.","Cool flat until crisp; serve as a snack or garnish for salads."]),

    ("lavender","rose",
     "Lavender and rose share linalool, 2-phenylethanol, geraniol, and beta-ionone — an almost complete overlap of floral terpene compounds that makes this the most aromatic pairing in the dataset. Together they create a perfume-like complexity that requires careful restraint to stay on the food side of the threshold.",
     "Rose and Lavender Crème Brûlée",
     ["Steep cream with rose petals and lavender buds until very fragrant, 30 minutes.","Strain, whisk into egg yolks with sugar, pour into ramekins.","Bake in a water bath at 325°F until just set; torch sugar topping to finish."]),

    ("lavender","salmon",
     "Lavender and salmon share linalool and acetic acid — a floral-tart compound thread that allows lavender's terpenes to complement rather than overwhelm delicate salmon. Lavender's linalyl acetate dissolves into salmon's fat during cooking, infusing the flesh with a subtle Provençal character.",
     "Lavender Honey Glazed Salmon",
     ["Make a glaze with lavender-infused honey, Dijon mustard, and a pinch of salt.","Brush generously onto salmon fillets on a parchment-lined baking sheet.","Bake at 400°F for 12 minutes until glaze caramelizes and fish is just cooked."]),

    ("lavender","strawberry",
     "Lavender and strawberry share linalool and 2-phenylethanol — two of strawberry's most important floral aroma compounds that lavender contains in dominant concentration. The lavender essentially amplifies strawberry's hidden floral dimension, making the strawberry taste more complex and less one-dimensionally sweet.",
     "Lavender Strawberry Jam",
     ["Cook strawberries with sugar and lemon juice until they release their juices.","Add a small bundle of dried lavender, continue cooking until jam consistency.","Remove lavender, jar the hot jam immediately, and seal for storage."]),

    ("lavender","tomato",
     "Lavender and tomato share linalool and beta-ionone — terpene and violet-like compounds that create an unexpected Provençal bridge. Tomato's linalool content is activated by heat in ways that mirror lavender; slow-roasting tomatoes with lavender amplifies both into something deeply aromatic and savory-sweet.",
     "Lavender Roasted Tomato Soup",
     ["Halve tomatoes, toss with olive oil, garlic, and a sprig of dried lavender.","Roast at 350°F for 90 minutes until very soft and slightly caramelized.","Blend smooth with stock, strain, season; serve with sourdough and crème fraîche."]),

    ("lavender","truffle",
     "Lavender and truffle share anisaldehyde and trace phenylacetaldehyde — aromatic aldehydes connecting floral herb and earthy fungus. Lavender's linalool provides a clean terpene brightness that lifts truffle's sometimes muddy earthiness into something more vertical and aromatic.",
     "Lavender Truffle Honey",
     ["Warm good honey gently with dried lavender buds until fragrant, 10 minutes.","Add a few drops of truffle oil off the heat and stir to combine.","Serve drizzled over aged Brie or Manchego on a cheese board."]),

    ("lavender","vanilla",
     "Lavender and vanilla share linalool, 2-phenylethanol, and trace vanillin — a floral-sweet compound triad that makes this one of the most harmonious dessert pairings in the dataset. Vanilla's fat-soluble vanillin absorbs lavender's volatile linalool, creating a compound aromatic that is greater than the sum of its parts.",
     "Lavender Vanilla Bean Ice Cream",
     ["Steep cream and milk with dried lavender and a split vanilla bean until fragrant.","Strain, whisk into egg yolks and sugar, cook until nappe consistency.","Chill overnight, churn in ice cream maker, freeze until firm before serving."]),

    # ── lemon (9 pairs) ──
    ("lemon","mint",
     "Lemon and mint share linalool and limonene — two of the most significant terpene compounds in both plants. Lemon's citral directly interacts with mint's menthol to create a compound cooling-brightening sensation that is used in drinks, desserts, and medicines worldwide for exactly this synergistic effect.",
     "Lemon Mint Granita",
     ["Make a lemon simple syrup with sugar, water, and lots of lemon zest.","Steep fresh mint in the warm syrup, then add fresh lemon juice.","Freeze in a shallow pan, scraping every 30 minutes until icy and slushy."]),

    ("lemon","oyster",
     "Lemon and oyster share acetic acid and trace linalool — a tart-floral bridge that explains why a squeeze of lemon is universally applied to raw oysters. Lemon's citric acid reacts with oyster proteins, firming the texture slightly while its volatile citral compounds cut through the oceanic trimethylamine (fishy) compounds.",
     "Classic Raw Oysters with Lemon",
     ["Shuck oysters carefully, keeping as much liquor as possible in the shell.","Arrange on crushed ice with lemon halves and a small pot of mignonette.","Squeeze lemon directly over each oyster and eat in one clean movement."]),

    ("lemon","parmesan",
     "Lemon and Parmesan share acetic acid and trace linalool — tart-floral compounds that create an amplifying relationship. Lemon's citric acid brightens Parmesan's umami, making the glutamate read as sharper and more vivid; Parmesan's fat carries lemon's volatile citral compounds longer on the palate.",
     "Lemon Parmesan Gremolata Pasta",
     ["Cook spaghetti al dente, reserve a cup of pasta water before draining.","Toss hot pasta with lemon zest, lemon juice, finely grated Parmesan, and olive oil.","Add pasta water as needed to emulsify into a silky, clinging sauce."]),

    ("lemon","rose",
     "Lemon and rose share geraniol, linalool, and nerol — terpene compounds that lemon's peel produces and rose petals contain in high concentration. Lemon's citral lifts rose's geraniol into something brighter and more citrus-adjacent, preventing the floral from becoming heavy or perfumed.",
     "Rose Lemonade",
     ["Make lemon simple syrup with equal parts sugar, water, and fresh lemon juice.","Add rose water to taste — start with a few drops, adjust up slowly.","Dilute with cold still or sparkling water, serve over ice with a rose petal."]),

    ("lemon","salmon",
     "Lemon and salmon share linalool and acetic acid — a floral-tart compound thread that defines one of the most classic pairings in European cooking. Lemon's citric acid partially denatures salmon's surface proteins (similar to ceviche) while its volatile compounds counteract trimethylamine, the primary fishy compound.",
     "Lemon Dill Cured Salmon",
     ["Mix salt, sugar, lemon zest, and chopped dill together for the cure.","Press firmly onto both sides of skin-on salmon, wrap tightly in plastic.","Cure refrigerated 24–48 hours; slice thin and serve on dark bread."]),

    ("lemon","strawberry",
     "Lemon and strawberry share linalool and acetic acid — terpene and tart compounds that together amplify strawberry's ethyl butanoate (its primary fruity ester) into something more vivid and complex. A squeeze of lemon on strawberries is the oldest flavor trick in the book: it works because these compounds are complementary.",
     "Strawberry Lemon Tart",
     ["Make a lemon curd and pour into a fully baked pastry shell, refrigerate until set.","Arrange sliced strawberries concentrically across the top of the curd.","Brush with a light apricot glaze for shine and serve chilled."]),

    ("lemon","tomato",
     "Lemon and tomato share acetic acid and linalool — the tart-floral backbone of countless Mediterranean dishes. Lemon's citral brightens tomato's beta-ionone (its subtle violet note) and suppresses the overly sharp edge of raw tomato acidity, creating a brighter, cleaner tomato flavor.",
     "Lemon Tomato Bruschetta",
     ["Dice ripe tomatoes, toss with lemon zest, olive oil, salt, and torn basil.","Let macerate 15 minutes so juices release and flavors meld together.","Pile onto thick toasted bread rubbed with garlic; serve immediately."]),

    ("lemon","truffle",
     "Lemon and truffle share anisaldehyde and trace phenylacetaldehyde — aromatic aldehyde compounds connecting citrus brightness to earthy depth. Lemon's citral provides a sharp contrast that lifts truffle's dense aromatic profile, making the earthiness more aromatic and less muddy.",
     "Truffle Lemon Tagliatelle",
     ["Cook fresh tagliatelle in well-salted water until just al dente.","Toss with truffle butter, lemon zest, and a splash of pasta water off heat.","Finish with shaved fresh truffle, Parmesan, and a final squeeze of lemon."]),

    ("lemon","vanilla",
     "Lemon and vanilla share linalool and trace geraniol — floral terpene compounds that create an elegant, citrus-sweet bridge. Lemon's citral amplifies vanilla's anisaldehyde into something brighter and more aromatic; vanilla's vanillin softens lemon's sharp citric edge into something rounder and more complex.",
     "Lemon Vanilla Posset",
     ["Heat heavy cream with sugar until just boiling, stirring to dissolve sugar fully.","Remove from heat, stir in lemon juice and lemon zest and vanilla extract.","Pour into ramekins, refrigerate at least 3 hours until set to a silky cream."]),

    # ── mint (8 pairs) ──
    ("mint","oyster",
     "Mint and oyster share linalool and trace benzaldehyde — floral and mild aromatic compounds connecting herb to brine. Mint's menthol creates a cooling sensation that amplifies the perception of oyster's mineral salinity; the combination reads as refreshing and oceanic simultaneously.",
     "Mint Cucumber Oyster Shooters",
     ["Blend cucumber and mint with a little lime juice and simple syrup.","Strain to a clean green liquid, chill until very cold.","Pour into shot glasses over freshly shucked small oysters to serve."]),

    ("mint","parmesan",
     "Mint and Parmesan share linalool and acetic acid — floral-tart compounds that bridge the herb's cool freshness to aged dairy's umami richness. Mint's menthol creates a perceived lightness that cuts through Parmesan's dense fat, making the combination taste more refreshing than Parmesan alone.",
     "Minted Pea Parmesan Crostini",
     ["Blanch fresh peas, blend with mint, olive oil, and a squeeze of lemon.","Spread pea-mint purée onto toasted baguette slices while still warm.","Top with Parmesan shavings and a few whole mint leaves to finish."]),

    ("mint","rose",
     "Mint and rose share 2-phenylethanol, linalool, and trace geraniol — floral and terpene compounds that connect the two most recognizable aromatic plants in the world. Mint's menthol-cooling and rose's geraniol-warmth create a thermal contrast that makes the combination feel more dimensional than either alone.",
     "Rose Mint Lassi",
     ["Blend whole-milk yogurt with rose water, fresh mint leaves, and honey.","Add cold water to thin to a pourable consistency and blend until smooth.","Serve chilled in tall glasses with a rose petal and a sprig of mint."]),

    ("mint","salmon",
     "Mint and salmon share linalool and acetic acid — a floral-tart compound bridge that allows mint to complement rather than overwhelm delicate salmon. Mint's menthol cuts through salmon's rich omega-3 fat in a similar way that lemon does, while its linalool bridges the fatty fish into something herbal and fresh.",
     "Mint Pesto Salmon",
     ["Blend fresh mint with pistachios, lemon zest, garlic, and olive oil into a pesto.","Spread generously across salmon fillets and rest 15 minutes before cooking.","Roast at 400°F for 12–14 minutes until pesto is fragrant and fish flakes."]),

    ("mint","strawberry",
     "Mint and strawberry share linalool and trace acetic acid — a floral-tart compound pair that amplifies strawberry's ethyl butanoate fruity ester into something more vivid and less cloying. Mint's menthol provides a cooling clean finish that prevents strawberry's sugar from becoming heavy.",
     "Strawberry Mint Sorbet",
     ["Blend fresh strawberries with a mint simple syrup and lemon juice.","Chill thoroughly, churn in an ice cream maker until smooth.","Freeze until firm, scoop into chilled glasses with fresh mint to serve."]),

    ("mint","tomato",
     "Mint and tomato share linalool and hexanal — floral and green aldehyde compounds that make mint a natural companion for tomato in Middle Eastern and Mediterranean salads. Mint's menthol provides a cooling finish that resets the acidity of raw tomato, creating a palate-cleansing effect between bites.",
     "Fattoush Salad",
     ["Combine diced tomatoes, cucumber, radish, and toasted pita chips.","Dress with lemon juice, olive oil, sumac, and salt, toss well.","Finish with a generous amount of fresh torn mint and flat-leaf parsley."]),

    ("mint","truffle",
     "Mint and truffle share anisaldehyde and trace linalool — aromatic aldehyde and floral compounds creating an unexpected herbal-earthy bridge. Mint's menthol cooling sensation creates a dramatic contrast with truffle's dense, warm earthiness, while their shared linalool provides aromatic continuity.",
     "Truffle Mint Chocolate Bark",
     ["Melt dark chocolate, stir in a few drops of truffle oil and peppermint extract.","Spread thin on parchment and sprinkle with crushed candy cane and truffle salt.","Refrigerate until firm, break into irregular shards and serve."]),

    ("mint","vanilla",
     "Mint and vanilla share linalool and trace 2-phenylethanol — floral terpene compounds that create a sweet-herbal bridge. Vanilla's fat-soluble vanillin absorbs mint's volatile menthol, moderating its intensity while its own sweetness softens the camphor-adjacent quality that mint can have at high concentrations.",
     "Mint Chip Ice Cream",
     ["Make a vanilla custard base with eggs, sugar, cream, and a split vanilla bean.","Steep fresh mint in warm cream before straining and chilling overnight.","Churn in an ice cream maker, fold in dark chocolate chips at the end."]),

    # ── oyster (7 pairs) ──
    ("oyster","parmesan",
     "Oyster and Parmesan share phenylacetaldehyde, dimethyl sulfide, and acetic acid — sulfurous-rosy-tart compounds connecting oceanic brine and aged dairy fermentation. Parmesan's intense glutamate amplifies oyster's intrinsic umami dramatically, while its fat moderates the sharp oceanic trimethylamine.",
     "Oysters Rockefeller",
     ["Make a filling of butter, Parmesan, spinach, and herbs — blend until smooth.","Top each oyster in its shell with a generous spoonful of the filling.","Broil until the topping is golden and the oyster edges just begin to curl."]),

    ("oyster","rose",
     "Oyster and rose share 2-phenylethanol and benzaldehyde — floral alcohol and almond-adjacent aromatic compounds bridging oceanic brine to delicate flower. Rose's geraniol lifts the briny, mineral intensity of raw oyster into something more aromatic; this is a celebrated pairing in French haute cuisine.",
     "Rose Mignonette Oysters",
     ["Combine minced shallots with champagne vinegar and a splash of dry rosé.","Add a few drops of rose water and cracked pepper; steep 30 minutes.","Spoon onto freshly shucked oysters and serve on crushed ice."]),

    ("oyster","salmon",
     "Oyster and salmon share dimethyl sulfide, trimethylamine, and hexanal — the marine sulfurous compound family that connects all seafood. Together they amplify oceanic minerality and fatty richness; the oyster's liquor acts as a natural brine that seasons salmon from within.",
     "Oyster-Stuffed Salmon",
     ["Butterfly a salmon fillet, layer shucked oysters across the center.","Roll tight, secure with toothpicks, and season the outside well with salt.","Bake at 400°F until salmon is just cooked and oysters are plump."]),

    ("oyster","strawberry",
     "Oyster and strawberry share trace furaneol and benzaldehyde — sweet and mildly aromatic compounds that create an unexpected contrast pairing. Strawberry's fruity ethyl butanoate and bright acidity create a dramatic polarity with oyster's oceanic brine that makes both flavors more vivid by contrast.",
     "Strawberry Mignonette on Oysters",
     ["Macerate finely diced strawberry with champagne vinegar, shallot, and pepper.","Let rest 20 minutes so strawberry releases its juice into the vinegar.","Spoon over freshly shucked oysters for a bright, fruit-forward garnish."]),

    ("oyster","tomato",
     "Oyster and tomato share hexanal, acetic acid, and furaneol — green aldehyde, tart, and sweet-caramel compounds creating a bridge between oceanic brine and garden acidity. Tomato's beta-ionone adds a violet-like floral note that softens oyster's sharp mineral intensity.",
     "Oyster Bloody Mary",
     ["Blend tomato juice with horseradish, Worcestershire, celery salt, and lemon.","Season aggressively with Tabasco and cracked pepper, chill until cold.","Serve over ice in a tall glass with a freshly shucked oyster submerged inside."]),

    ("oyster","truffle",
     "Oyster and truffle share dimethyl sulfide, phenylacetaldehyde, and bis(methylthio)methane — the most powerful sulfurous aromatic compounds in food. Both are defined by deep microbial transformation; together their marine-earthy-pungent profiles create an umami depth that is almost overwhelming in its complexity.",
     "Truffle Oyster Velouté",
     ["Shuck oysters, reserve liquor, and simmer in a rich fish stock 5 minutes.","Blend with cream and a splash of truffle oil until smooth and velvety.","Strain, adjust seasoning, serve in warm bowls with shaved fresh truffle."]),

    ("oyster","vanilla",
     "Oyster and vanilla share trace 2-phenylethanol and dimethyl sulfide — a floral-sulfurous thread bridging oceanic brine and sweet spice. This is a contrast pairing: vanilla's vanillin suppresses the harsh marine trimethylamine in oyster while amplifying its subtle sweetness, creating a confounding, elegant effect.",
     "Vanilla Butter Sauce for Oysters",
     ["Make a beurre blanc with shallots, white wine, and cream reduced down.","Whisk in cold butter in pieces off heat, add a tiny amount of vanilla extract.","Serve warm in a small cup alongside raw or lightly grilled oysters."]),

    # ── parmesan (6 pairs) ──
    ("parmesan","rose",
     "Parmesan and rose share 2-phenylethanol and phenylacetaldehyde — rosy-floral compounds that aged dairy fermentation and rose petals produce through very different biochemical pathways. Rose's geraniol provides a delicate floral lift that makes Parmesan's umami read as lighter and more aromatic.",
     "Rose Petal Parmesan Salad",
     ["Shave Parmesan into large thin curls using a vegetable peeler over arugula.","Scatter fresh or crystallized rose petals across the top of the salad.","Dress with a lemon and rose water vinaigrette, cracked pepper, and good oil."]),

    ("parmesan","salmon",
     "Parmesan and salmon share dimethyl sulfide, acetic acid, and linalool — sulfurous-tart-floral compounds connecting aged dairy to fatty fish. Parmesan's glutamate amplifies salmon's intrinsic umami dramatically; its fat provides an additional carrier for salmon's volatile aromatic esters.",
     "Parmesan-Crusted Salmon",
     ["Mix grated Parmesan with breadcrumbs, lemon zest, and chopped fresh dill.","Press the Parmesan crust firmly onto salmon fillets and drizzle with olive oil.","Bake at 400°F until crust is golden and fish is just cooked, about 14 minutes."]),

    ("parmesan","strawberry",
     "Parmesan and strawberry share furaneol and 2-phenylethanol — sweet-caramel and rosy-floral compounds that connect aged dairy and fruit. The classic Italian preparation of Parmigiano Reggiano with fresh strawberries is based on exactly this volatile overlap: furaneol in both creates a sweet, unified note.",
     "Strawberries with Aged Parmesan",
     ["Select very ripe strawberries and slice in half lengthwise.","Shave thin curls of well-aged Parmigiano Reggiano over the top.","Drizzle with aged balsamic vinegar and a thread of good olive oil to serve."]),

    ("parmesan","tomato",
     "Parmesan and tomato share furaneol, acetic acid, and hexanal — a sweet-tart-green compound triad that creates one of the strongest flavor marriages in Italian cooking. Parmesan's glutamate amplifies tomato's intrinsic glutamate content into an umami loop that explains why every pasta sauce improves with cheese.",
     "Tomato Parmesan Soup",
     ["Roast tomatoes with olive oil and garlic until caramelized and concentrated.","Blend with stock until smooth, heat through and season generously.","Ladle into bowls and shower with finely grated Parmesan just before serving."]),

    ("parmesan","truffle",
     "Parmesan and truffle share phenylacetaldehyde, dimethyl sulfide, and anisaldehyde — three of the most powerful aromatic compounds in savory cooking. Parmesan's glutamate provides the umami scaffolding that allows truffle's volatile sulfurous compounds to persist on the palate rather than disappearing quickly.",
     "Truffle Parmesan Arancini",
     ["Make a Parmesan risotto, cool completely, fold in finely diced black truffle.","Shape into balls around a cube of mozzarella, bread in egg and panko.","Deep-fry at 350°F until deep golden, serve immediately with more Parmesan."]),

    ("parmesan","vanilla",
     "Parmesan and vanilla share vanillin and 2-phenylethanol — sweet, floral compounds that aged dairy fermentation and vanilla beans produce by very different routes. Vanilla's vanillin is fat-soluble and dissolves into Parmesan's dairy fat, creating a subtle sweet-savory complexity in certain dessert applications.",
     "Parmesan Vanilla Shortbread",
     ["Cream butter with a small amount of powdered sugar and vanilla seeds.","Mix in finely grated Parmesan and flour until a cohesive dough forms.","Shape, chill, bake at 325°F until just golden; serve with a glass of aged wine."]),

    # ── rose (5 pairs) ──
    ("rose","salmon",
     "Rose and salmon share linalool, 2-phenylethanol, and acetic acid — floral-tart compounds that provide a delicate bridge between salmon's fatty marine character and rose's perfumed florality. Rose's geraniol cuts through salmon's omega-3 richness, lifting the fish into something more aromatic and elegant.",
     "Rose Water Poached Salmon",
     ["Combine water, white wine, a few drops of rose water, and pink peppercorns.","Bring to the barest simmer, submerge salmon portions, poach 8–10 minutes.","Serve with a yogurt sauce of rose water, cucumber, dill, and lemon."]),

    ("rose","strawberry",
     "Rose and strawberry share 2-phenylethanol, linalool, geraniol, and beta-ionone — four floral-terpene compounds that make this one of the highest-overlap pairs in the dataset. Rose's geraniol amplifies strawberry's linalool, making the strawberry flavor read as deeper and more complex rather than simply sweeter.",
     "Strawberry Rose Pavlova",
     ["Whip meringue to stiff peaks with a tablespoon of rose water added.","Bake at 250°F for 90 minutes; cool completely in the oven with the door ajar.","Top with whipped cream, sliced strawberries, and scattered rose petals."]),

    ("rose","tomato",
     "Rose and tomato share beta-ionone and linalool — a violet-like and floral compound pair that creates an unexpected aromatic bridge. Tomato's geranylacetone (rose-adjacent compound) directly connects to rose's geraniol; Persian cuisine exploits this with rose water in certain tomato-based preparations.",
     "Rose Tomato Jam",
     ["Cook halved cherry tomatoes with sugar, lemon juice, and a pinch of salt.","Stir frequently until thick and jammy, about 30 minutes over medium heat.","Stir in a small amount of rose water at the very end, jar while hot."]),

    ("rose","truffle",
     "Rose and truffle share phenylacetaldehyde and anisaldehyde — rosy-honeyed and anise-adjacent aromatic aldehydes connecting floral and earthy. Rose's 2-phenylethanol provides a warm floral base that softens truffle's pungent sulfurous compounds, making the earthiness more aromatic and less muddy.",
     "Rose Truffle Chocolate Ganache",
     ["Steep rose petals in hot cream 15 minutes, strain and use to make ganache.","Add a few drops of truffle oil to the warm chocolate-cream mixture.","Pour over a chocolate cake or serve as a warm sauce over vanilla ice cream."]),

    ("rose","vanilla",
     "Rose and vanilla share 2-phenylethanol, linalool, and vanillin — a complete aromatic triad connecting floral, terpene, and sweet aldehyde. Vanilla's vanillin is fat-soluble and reinforces rose's 2-phenylethanol (also present in vanilla beans) into a compound that reads as perfumed warmth rather than simply sweet.",
     "Rose Vanilla Panna Cotta",
     ["Bloom gelatin in cold water, dissolve in warm rose-and-vanilla infused cream.","Add sugar and a splash of rose water, pour into lightly oiled molds.","Refrigerate 4 hours until set, unmold onto plates and serve with rose petals."]),

    # ── salmon (4 pairs) ──
    ("salmon","strawberry",
     "Salmon and strawberry share linalool and trace 2-phenylethanol — a floral terpene bridge connecting fatty fish to sweet fruit. This is a Scandinavian and nouvelle cuisine pairing: strawberry's bright acidity (acetic acid, fruit esters) cuts through salmon's omega-3 richness while linalool connects both aromatically.",
     "Salmon Strawberry Ceviche",
     ["Slice sashimi-grade salmon thin, toss with lime juice and let cure 5 minutes.","Add diced strawberry, cucumber, red onion, and chopped cilantro.","Season with salt, serve immediately on tostadas or with crispy tortilla chips."]),

    ("salmon","tomato",
     "Salmon and tomato share hexanal, linalool, and acetic acid — green aldehyde, floral, and tart compounds that bridge fatty fish and acidic vegetable. Tomato's acidity acts on salmon's fat to create an emulsifying effect; its beta-ionone adds a violet-adjacent note that complements salmon's own floral esters.",
     "Salmon in Tomato Acqua Pazza",
     ["Sauté garlic and cherry tomatoes in olive oil until tomatoes begin to burst.","Add white wine and a cup of water, bring to a simmer over medium heat.","Nestle salmon portions into the liquid, cover and poach 8 minutes until just done."]),

    ("salmon","truffle",
     "Salmon and truffle share dimethyl sulfide, linalool, and phenylacetaldehyde — sulfurous, floral, and rosy compounds connecting fatty fish to earthy fungus. Truffle's volatile 2,4-dithiapentane dissolves readily into salmon's omega-3-rich fat, creating an intensely aromatic seafood preparation.",
     "Truffle Butter Salmon en Croûte",
     ["Spread truffle butter generously on a salmon fillet, season with salt.","Wrap tightly in puff pastry, seal edges with egg wash, chill 20 minutes.","Bake at 400°F until pastry is deep golden, about 25 minutes; rest before slicing."]),

    ("salmon","vanilla",
     "Salmon and vanilla share linalool, acetic acid, and trace 2-phenylethanol — floral and tart compounds that create a delicate sweet-savory bridge. Vanilla's fat-soluble vanillin dissolves into salmon's omega-3 fat during cooking, creating a subtle warm sweetness that complements rather than overwhelms.",
     "Vanilla Miso Salmon",
     ["Whisk white miso with a tiny amount of vanilla extract, mirin, and sake.","Marinate salmon fillets in the paste 2–4 hours in the refrigerator.","Broil or grill until lacquered and just cooked through, about 10 minutes."]),

    # ── strawberry (3 pairs) ──
    ("strawberry","tomato",
     "Strawberry and tomato share furaneol, linalool, and hexanal — nearly identical volatile profiles for two ingredients that evolved similar aroma chemistry to attract pollinators and seed dispersers. When combined, the compounds reinforce each other into an intensely sweet-tart-fresh aromatic that reads as both garden and fruit simultaneously.",
     "Strawberry Tomato Gazpacho",
     ["Blend ripe tomatoes with ripe strawberries, cucumber, bread, and olive oil.","Season with sherry vinegar, salt, and a pinch of smoked paprika.","Strain, chill overnight, serve very cold with diced strawberry and tomato on top."]),

    ("strawberry","truffle",
     "Strawberry and truffle share phenylacetaldehyde and trace anisaldehyde — rosy-honeyed and anise-adjacent aromatic compounds that create a surprising bridge between sweet fruit and earthy fungus. Truffle's dimethyl sulfide gives depth and complexity that prevents strawberry from reading as one-dimensionally sweet.",
     "Strawberry Truffle Tart",
     ["Make a pastry cream with vanilla, pour into a fully baked tart shell.","Arrange halved fresh strawberries tightly across the top of the cream.","Drizzle with truffle honey and a few drops of truffle oil just before serving."]),

    ("strawberry","vanilla",
     "Strawberry and vanilla share vanillin, furaneol, linalool, and 2-phenylethanol — four of the most significant aroma compounds in both ingredients, making this one of the highest-overlap pairs in the entire dataset. The combination is essentially two expressions of the same sweet-floral flavor family.",
     "Strawberry Vanilla Mille-Feuille",
     ["Bake puff pastry flat between two sheets until deeply golden and crisp.","Layer with vanilla pastry cream and sliced fresh strawberries three times.","Top with the final pastry layer, dust with powdered sugar, serve immediately."]),

    # ── tomato (2 pairs) ──
    ("tomato","truffle",
     "Tomato and truffle share phenylacetaldehyde, furaneol, and anisaldehyde — sweet-rosy, caramel-adjacent, and anise-like aromatic compounds connecting garden vegetable and earthy fungus. Both are defined by complex biochemical transformation (ripening/mycorrhiza); together their aromatic profiles create an intensely savory-sweet depth.",
     "Truffle Tomato Pasta",
     ["Sauté cherry tomatoes in butter until they burst and concentrate.","Add pasta cooking water, truffle oil, and toss with al dente spaghetti.","Finish with Parmesan, shaved truffle, and a drizzle of the best olive oil."]),

    ("tomato","vanilla",
     "Tomato and vanilla share furaneol, linalool, and trace beta-ionone — sweet-caramel, floral, and violet-like compounds that create an unexpected savory-sweet bridge. Vanilla's fat-soluble vanillin amplifies tomato's sweetness while suppressing its sharp acidity; this is a technique used in professional pastry kitchens for tomato desserts.",
     "Vanilla Tomato Jam",
     ["Cook halved cherry tomatoes low and slow with sugar, salt, and lemon juice.","Stir in seeds from a vanilla bean in the last 10 minutes of cooking.","Jar while hot; serve on cheese boards or spooned alongside fresh ricotta."]),

    # ── truffle + vanilla ──
    ("truffle","vanilla",
     "Truffle and vanilla share anisaldehyde, 2-phenylethanol, and trace vanillin — anise-adjacent, rosy-floral, and sweet aldehyde compounds connecting earthy fungus and tropical orchid. Vanilla's fat-soluble vanillin dissolves into truffle's aromatic matrix during infusion, creating a compound sweetness that makes truffle's earthiness more accessible and elegant.",
     "Truffle Vanilla Crème Anglaise",
     ["Infuse cream with a split vanilla bean and a slice of fresh black truffle overnight.","Strain and use to make a classic crème anglaise with egg yolks and sugar.","Serve warm over chocolate fondant or spooned around a slice of pear tart."]),
]

conn = sqlite3.connect(DB)
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
print(f"Batch 3 done: inserted {inserted} pairs.")
