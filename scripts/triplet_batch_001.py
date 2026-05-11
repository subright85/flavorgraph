#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("basil","blue cheese","butter",
     "Basil's linalool and 2-phenylethanol bridge blue cheese's butyric acid funk to butter's diacetyl richness, while all three share dimethyl sulfide as a sulfurous backbone. The result is deeply savory dairy richness lifted by herbal brightness into something refined and complex.",
     "Blue Cheese Basil Compound Butter",
     ["Blend softened butter with crumbled blue cheese and finely chopped fresh basil until smooth.","Roll into a log in plastic wrap and refrigerate until firm, at least 2 hours.","Slice and melt over grilled steak or roasted vegetables just before serving."]),

    ("basil","blue cheese","caramel",
     "Basil's eugenol and linalool bridge blue cheese's fermented acetic acid tartness to caramel's diacetyl Maillard sweetness, creating a herbal connector between pungent funk and warm sugar depth. The combination balances salt, sweet, and herb in an unexpectedly harmonious register.",
     "Caramel Blue Cheese Basil Tart",
     ["Fill a blind-baked tart shell with warm salted caramel and let set slightly.","Crumble blue cheese across the caramel and scatter torn fresh basil leaves over top.","Bake at 350°F for 12 minutes until cheese softens; serve warm with honey."]),

    ("basil","blue cheese","chocolate",
     "Chocolate and blue cheese share phenylacetaldehyde and dimethyl sulfide — rosy-fermented compounds — while basil's 2-phenylethanol amplifies these floral notes into a complex herbal-savory-roasted depth. Together they form a bold trio where herb, ferment, and dark roast each occupy distinct yet connected aromatic registers.",
     "Dark Chocolate Blue Cheese Basil Bites",
     ["Melt dark chocolate and pour into small molds, top each with a crumble of blue cheese.","Press a small fresh basil leaf onto each piece before chocolate sets fully.","Refrigerate until firm; serve at room temperature for full aromatic expression."]),

    ("basil","blue cheese","coffee",
     "Blue cheese and coffee share dimethyl sulfide, acetic acid, and phenylacetaldehyde — the roasted-fermented pungent compound set — while basil's linalool and eugenol provide a clean herbal bridge between the two intensities. The trio creates a savory-bitter-herbal layering where each element deepens the others' complexity.",
     "Coffee Blue Cheese Basil Bruschetta",
     ["Toast thick sourdough, rub with garlic, and brush lightly with espresso reduction.","Spread room-temperature blue cheese generously across each slice while still warm.","Top with torn fresh basil and a drizzle of good olive oil; serve immediately."]),

    ("basil","blue cheese","cucumber",
     "Basil and cucumber share linalool and benzaldehyde — fresh-floral and almond-adjacent compounds — creating a cool herbal counterpoint to blue cheese's dense butyric acid funk. Cucumber's hexanal and (E)-2-nonenal provide a palate-cleansing aldehyde freshness that resets between each bite of the pungent cheese.",
     "Blue Cheese Basil Cucumber Cups",
     ["Slice cucumber into thick rounds and scoop a small well from the center of each.","Pipe or spoon room-temperature blue cheese into each cup generously.","Top with a small basil leaf and a drizzle of honey; serve immediately chilled."]),

    ("basil","blue cheese","garlic",
     "Garlic and blue cheese share dimethyl sulfide and acetic acid — sulfurous and tart compounds forming a pungent savory base — while basil's linalool and eugenol add the herbal lift that bridges allium pungency and fermented dairy. This is the classic Mediterranean flavor triangle of herb, allium, and aged dairy.",
     "Blue Cheese Basil Garlic Flatbread",
     ["Spread roasted garlic oil across flatbread dough and bake at 450°F until crisp.","Remove from oven and immediately top with crumbled blue cheese to slightly melt.","Scatter torn fresh basil and cracked pepper; slice and serve while hot."]),

    ("basil","blue cheese","lamb",
     "Blue cheese and lamb share butyric acid, dimethyl sulfide, and trimethylamine — the animal-fermented sulfurous compound family — while basil's linalool and eugenol provide the herbal brightness needed to cut through both ingredients' rich fatty depth. The trio amplifies deep savory umami while basil prevents any single pungent note from overwhelming.",
     "Lamb Blue Cheese Basil Burgers",
     ["Mix ground lamb with minced garlic, form into patties, and grill to medium-rare.","Top each patty immediately with crumbled blue cheese to melt from the residual heat.","Serve in toasted buns with thick slices of tomato and a generous handful of fresh basil."]),

    ("basil","blue cheese","lavender",
     "Basil and lavender share the highest linalool and 2-phenylethanol concentrations among culinary herbs, creating a layered floral-herbal compound that softens blue cheese's ammonia edge into something elegantly perfumed. The combination reads as Provençal sophistication — herbal, floral, and funky in measured proportion.",
     "Lavender Blue Cheese Basil Honey Toast",
     ["Toast thick-cut bread and spread with room-temperature blue cheese while still warm.","Drizzle with lavender-infused honey and scatter fresh basil leaves across the top.","Add cracked black pepper and a pinch of flaky salt before serving immediately."]),

    ("basil","blue cheese","lemon",
     "Basil and lemon share linalool and trace geraniol — citrus-herbal terpenes that cut through blue cheese's dense butyric acid fat — while lemon's citric acidity mirrors the fermentation-derived tartness already present in blue cheese. The trio achieves self-balancing flavors: herbal-citrus freshness against rich dairy funk.",
     "Lemon Basil Blue Cheese Dip",
     ["Blend room-temperature blue cheese with lemon juice, lemon zest, and a little cream until smooth.","Fold in finely chopped fresh basil and season with cracked black pepper.","Serve chilled with crudités, pita chips, and a final drizzle of good olive oil."]),

    ("basil","blue cheese","mint",
     "Basil and mint share linalool and 1,8-cineole — complementary terpenes creating a layered cool-warm herbal character — and their combined freshness directly counteracts blue cheese's ammonia-forward fermented funk. Menthol's cooling sensation provides a palate-cleansing finish that resets cleanly between each bite of the pungent cheese.",
     "Mint Basil Blue Cheese Flatbread",
     ["Roll out flatbread dough thin, brush with olive oil, and par-bake at 450°F 5 minutes.","Scatter crumbled blue cheese evenly and return to oven until bubbly and golden.","Remove, immediately top with torn mint and basil, drizzle with honey, slice to serve."]),

    ("basil","blue cheese","oyster",
     "Blue cheese and oyster share phenylacetaldehyde, dimethyl sulfide, and trimethylamine — the pungent fermented-marine compound set — while basil's benzaldehyde and linalool provide the herbal aromatic lift that bridges dairy funk and oceanic brine. Together the trio forms a bold umami combination where basil acts as the critical aromatic connector.",
     "Oyster Blue Cheese Basil Gratin",
     ["Place shucked oysters in their half-shells on a baking sheet over rock salt.","Top each with a small amount of blue cheese and a tiny fresh basil leaf.","Broil 3–4 minutes until cheese bubbles and oyster edges just begin to curl."]),

    ("basil","blue cheese","parmesan",
     "Blue cheese and Parmesan share butyric acid, acetic acid, phenylacetaldehyde, and dimethyl sulfide — nearly identical aged dairy compound sets at different intensities — while basil's linalool and 2-phenylethanol provide a herbal-floral lift that prevents double-cheese richness from becoming overwhelming. This creates a three-tier umami escalation with clean herbal brightness on top.",
     "Three Cheese Basil Gnocchi",
     ["Boil potato gnocchi until they float, transfer to a buttered baking dish.","Make a sauce by melting blue cheese and Parmesan into cream, pour over gnocchi.","Bake at 400°F until bubbling and golden, finish with torn fresh basil to serve."]),

    ("basil","blue cheese","rose",
     "Basil and rose share 2-phenylethanol, linalool, and benzaldehyde — a trifecta of floral-herbal aromatic compounds — that together create a perfumed brightness softening blue cheese's harsh fermented pungency into something elegant. The combination reads as a refined aperitivo board where the floral notes round the funk into sophistication.",
     "Rose Basil Blue Cheese Crostini",
     ["Toast baguette rounds until golden and let cool slightly before topping.","Spread room-temperature blue cheese generously and add a fresh basil leaf.","Scatter crystallized rose petals and drizzle with floral honey to finish."]),

    ("basil","blue cheese","salmon",
     "Blue cheese and salmon share dimethyl sulfide, trimethylamine, and acetic acid — the marine-sulfurous compound family — while basil's linalool bridges fatty fish and fermented dairy through its shared terpene presence in both. The trio creates a Scandinavian-Mediterranean crossover where each element amplifies the others' savory depth.",
     "Salmon Blue Cheese Basil Tart",
     ["Blind-bake a pastry shell, spread with whipped blue cheese as the base layer.","Arrange thin slices of smoked salmon over the cheese and top with fresh basil.","Serve at room temperature with lemon wedges and cracked black pepper."]),

    ("basil","blue cheese","strawberry",
     "Strawberry and basil share furaneol, linalool, and 2-phenylethanol — sweet-caramel and floral-rosy compounds — creating a fruit-herb aromatic layer that contrasts with blue cheese's fermented butyric acid sharpness. Strawberry's sweetness amplifies the salt in blue cheese while basil provides the herbal bridge between fruit and funk.",
     "Strawberry Blue Cheese Basil Flatbread",
     ["Bake flatbread until crisp and golden, remove from oven immediately.","Scatter crumbled blue cheese and halved fresh strawberries across the hot flatbread.","Top with torn basil, a balsamic reduction drizzle, and cracked pepper to serve."]),

    ("basil","blue cheese","tomato",
     "Basil and tomato share linalool and furaneol — the defining volatile pair of the garden — while blue cheese's phenylacetaldehyde and butyric acid provide a fermented depth that elevates the classic Caprese into something more complex and umami-forward. Together the trio reads as a sophisticated Italian profile pushed into aged-dairy territory.",
     "Blue Cheese Caprese Bruschetta",
     ["Dice ripe tomatoes, toss with olive oil, salt, and torn basil; rest 10 minutes.","Toast thick sourdough slices and spread each with a generous layer of blue cheese.","Spoon the tomato-basil mixture over the cheese and serve immediately."]),

    ("basil","blue cheese","truffle",
     "Blue cheese and truffle share phenylacetaldehyde, dimethyl sulfide, and anisaldehyde — the most powerful fermented-earthy aromatic compound set in savory cooking — while basil's linalool and 2-phenylethanol provide herbal lift to prevent the funk from becoming overwhelming. This luxury trio requires restraint: small amounts of each produce maximum complexity.",
     "Truffle Blue Cheese Basil Pizza",
     ["Stretch pizza dough thin, brush with truffle oil, and bake at 500°F until crisp.","Immediately top with crumbled blue cheese and let the residual heat melt it.","Add fresh basil, shaved black truffle, and a final drizzle of truffle oil to serve."]),

    ("basil","blue cheese","vanilla",
     "Basil and vanilla share 2-phenylethanol and linalool — rose-floral and terpene compounds — bridging vanilla's sweet vanillin warmth to blue cheese's sharp fermented funk in a surprising sweet-savory register. Vanilla suppresses blue cheese's harshest ammonia notes while basil provides the herbal bridge between the sweet and funky extremes.",
     "Vanilla Blue Cheese Basil Cheesecake",
     ["Make a crust from gingersnaps, press into a springform pan, and pre-bake 10 minutes.","Beat blue cheese with cream cheese, eggs, vanilla bean seeds, and a touch of honey.","Bake in a water bath at 325°F until just set; chill overnight before serving with basil."]),

    ("basil","butter","caramel",
     "Butter and caramel share furaneol, diacetyl, and acetic acid — the sweet-buttery-tart compound trio — while basil's eugenol and linalool add spiced herbal brightness that prevents the butter-caramel from reading as cloying. The combination achieves sophisticated sweetness with a savory herbal edge that makes it suitable for both sweet and savory applications.",
     "Basil Caramel Butter Sauce",
     ["Make a dry caramel until deep amber, whisk in warm cream carefully off heat.","Beat in cold salted butter in pieces until the sauce is glossy and smooth.","Stir in finely chopped fresh basil at the last moment and serve immediately warm."]),

    ("basil","butter","chocolate",
     "Butter and chocolate share dimethyl sulfide and furaneol — fat-soluble aromatic compounds that butter amplifies in chocolate's roasted profile — while basil contributes linalool and 2-phenylethanol that echo chocolate's floral fermentation esters. The trio creates a herbal-chocolate-butter depth used in contemporary European patisserie.",
     "Basil Chocolate Butter Cake",
     ["Brown butter until deeply nutty, cool slightly, then whisk into dark chocolate ganache.","Fold in beaten eggs, sugar, and flour with a generous handful of finely chopped fresh basil.","Bake in a buttered pan at 350°F until just set at center; serve warm with cream."]),
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
print(f"Batch 001 done: inserted {len(TRIPLETS)} triplets.")
