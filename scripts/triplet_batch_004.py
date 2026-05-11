#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("basil","chocolate","rose",
     "Dark chocolate and rose share 2-phenylethanol and phenylacetaldehyde — the rosy-floral compound set that fermented cacao and rose petals produce through entirely different biological pathways — while basil reinforces this overlap with its own 2-phenylethanol, creating a triple-floral register grounded by chocolate's bitter roast. The trio defines the flavor profile of Turkish-European luxury confection.",
     "Rose Basil Dark Chocolate Bark",
     ["Melt dark chocolate and spread onto a parchment-lined tray in an even thin layer.","Brush with a few drops of rose water and scatter very finely chopped fresh basil across the surface.","Press crystallized rose petals into the chocolate before it sets; cool completely, break into shards."]),

    ("basil","chocolate","salmon",
     "Dark chocolate and salmon share dimethyl sulfide and phenylacetaldehyde — sulfurous and rosy compounds spanning both marine and fermented registers — while basil's linalool bridges fatty fish to chocolate's herbal-floral fermentation esters. The pairing works best in savory mole-inspired preparations where chocolate is spice rather than sweetener.",
     "Chocolate Basil Mole Salmon",
     ["Blend toasted ancho chiles, garlic, tomato, and a square of dark chocolate with stock until smooth.","Simmer mole sauce until thick; season with salt and a handful of torn fresh basil.","Sear salmon to medium, spoon mole generously over the top, garnish with basil and sesame."]),

    ("basil","chocolate","strawberry",
     "Strawberry and dark chocolate share furaneol — the sweet-caramel compound critical to both strawberry's ripe aroma and chocolate's roasted character — while basil's linalool and 2-phenylethanol amplify strawberry's floral esters and connect them to chocolate's own fermentation-derived florals. The trio creates the most compound-coherent fruit-chocolate pairing possible.",
     "Strawberry Basil Dark Chocolate Pavé",
     ["Make a chocolate ganache with dark chocolate and cream infused with fresh basil; pour into a lined tray.","Refrigerate until set; press halved fresh strawberries in a grid pattern across the surface.","Brush with a strawberry reduction, scatter torn basil, and cut into clean squares to serve."]),

    ("basil","chocolate","tomato",
     "Tomato and chocolate share furaneol and trace phenylacetaldehyde — both produce these sweet-rosy compounds through different ripening and fermentation pathways — while basil's linalool and eugenol complete the Mediterranean aromatic set that makes tomato-chocolate mole an authentic Mexican culinary tradition. Together they create a savory depth where chocolate functions as umami amplifier.",
     "Tomato Basil Dark Chocolate Mole Verde",
     ["Roast tomatillos and garlic until charred, blend with toasted pumpkin seeds and a square of dark chocolate.","Simmer the green mole with fresh basil and stock until thick and intensely flavored.","Serve over pulled chicken with torn fresh basil, a squeeze of lime, and warm tortillas."]),

    ("basil","chocolate","truffle",
     "Dark chocolate and truffle share dimethyl sulfide, phenylacetaldehyde, and anisaldehyde — an extraordinary compound overlap of fermented-earthy aromatics — while basil's linalool and 2-phenylethanol provide herbal brightness that lifts both intense ingredients into a vertical, aromatic register. The trio represents the peak of European luxury savory-sweet ingredient pairing.",
     "Truffle Dark Chocolate Basil Risotto",
     ["Make a risotto base with Parmesan; off heat, stir in a square of grated dark chocolate and cold butter.","Fold in torn fresh basil immediately before plating to preserve volatile aromatics.","Plate in warm bowls and finish with shaved black truffle and a drizzle of good truffle oil."]),

    ("basil","chocolate","vanilla",
     "Chocolate and vanilla share vanillin, furaneol, and 2-phenylethanol — three overlapping sweet-rosy-floral compounds that together explain why chocolate-vanilla is the world's most popular dessert combination — while basil's eugenol adds a spiced herbal warmth that echoes vanilla's anise-adjacent character and lifts the sweet richness. The trio is refined chocolate-vanilla elevated by herb.",
     "Vanilla Basil Dark Chocolate Soufflé",
     ["Make a pastry cream base with vanilla bean and finely chopped fresh basil; stir in melted dark chocolate.","Fold in stiffly beaten egg whites in three additions to preserve volume; pour into buttered ramekins.","Bake at 375°F for 12 minutes until risen and set; serve immediately with vanilla crème anglaise."]),

    ("basil","coffee","cucumber",
     "Coffee's furfural and acetic acid meet cucumber's hexanal and (E)-2-nonenal in a bold bitter-green contrast pairing, while basil's linalool bridges the gap through its shared terpene presence with both cucumber's herbal freshness and coffee's trace floral compounds. The combination creates a sophisticated cold-brew cocktail or dessert flavor where bitterness and coolness balance precisely.",
     "Cold Brew Cucumber Basil Granita",
     ["Steep coarse coffee grounds in cold cucumber juice overnight; strain through a fine sieve.","Sweeten lightly, add torn fresh basil and a squeeze of lemon, pour into a shallow freezer pan.","Freeze, scraping every 30 minutes until icy granita; serve in chilled glasses with a basil sprig."]),

    ("basil","coffee","garlic",
     "Coffee and garlic share dimethyl sulfide and acetic acid — sulfurous and tart compounds that link roasted bitterness to allium pungency — while basil's eugenol and linalool provide the herbal bridge that channels this bold combination into savory rub and spice territory. The trio drives the flavor profile of South American coffee-garlic marinades for grilled meats.",
     "Coffee Garlic Basil Dry Rub",
     ["Combine finely ground espresso, roasted garlic powder, smoked paprika, salt, and torn dried basil.","Rub generously into steaks or pork shoulder and rest 30 minutes at room temperature before cooking.","Grill over high heat to develop a crust; finish with fresh basil oil just before slicing."]),

    ("basil","coffee","lamb",
     "Coffee and lamb share phenylacetaldehyde and dimethyl sulfide — Maillard-roasted and animal-fat sulfurous compounds that connect roasted bean to gamey meat — while basil's linalool and eugenol suppress lamb's 4-methyloctanoic acid and bridge the herbal-bitter-animal register. The trio is the flavor logic behind North African coffee-spice lamb preparations.",
     "Coffee Basil Braised Lamb Shoulder",
     ["Sear lamb shoulder all over; build a braise with espresso, crushed tomatoes, garlic, and cumin.","Cover and cook at 300°F for 3.5 hours until falling-apart tender; skim fat from braising liquid.","Reduce braising jus to a glaze, stir in torn fresh basil, and spoon over pulled lamb to serve."]),

    ("basil","coffee","lavender",
     "Coffee and lavender share trace linalool — lavender's dominant terpene appears as a minor compound in some high-quality arabicas — while basil amplifies this shared linalool connection into a triple-layered herbal-floral-bitter register. Together they create the aromatic logic of Provençal café culture: bitter espresso softened by floral herbs.",
     "Lavender Coffee Basil Affogato",
     ["Make lavender simple syrup by steeping dried lavender in sugar syrup; strain and cool.","Scoop basil-infused vanilla ice cream into chilled cups and drizzle with lavender syrup.","Pour a hot double shot of espresso over each immediately before serving; garnish with a basil tip."]),

    ("basil","coffee","lemon",
     "Coffee's acidity and lemon's citric acid reinforce each other — both contribute to perceived brightness and clarity in the cup — while basil's linalool and geraniol bridge the citrus-herbal register into coffee's own trace floral compounds. The trio drives the flavor of Ethiopian coffee preparations where lemon is a traditional accompaniment.",
     "Lemon Basil Coffee Cake",
     ["Make a sour cream coffee cake batter with lemon zest, espresso powder, and finely chopped fresh basil.","Layer with a brown sugar-cinnamon-coffee streusel in the middle and on top.","Bake at 350°F until golden; glaze with lemon icing while still warm and finish with basil sugar."]),

    ("basil","coffee","mint",
     "Coffee and mint share trace menthol-adjacent compounds that create a cooling-bitter interplay — the logic behind iced mint coffee drinks — while basil's linalool provides herbal warmth that bridges mint's cool and coffee's roasted bitterness into a more rounded, complex aromatic. Together the trio achieves a refreshing yet deeply flavored cold beverage register.",
     "Mint Basil Iced Coffee",
     ["Blend cold brew concentrate with fresh mint, basil, and a touch of honey until smooth; strain.","Pour over a tall glass of ice and top with a splash of cream or oat milk.","Garnish with a fresh mint sprig and a small basil leaf; serve immediately before ice dilutes."]),

    ("basil","coffee","oyster",
     "Coffee and oyster share dimethyl sulfide and acetic acid — sulfurous and tart compounds that span roasted bitterness and marine brine — while basil's benzaldehyde and linalool provide the herbal lift that bridges these two intensely savory registers. The trio works as an umami-stacked savory preparation where coffee functions as bitter-roasted seasoning rather than beverage.",
     "Coffee Roasted Oysters with Basil Butter",
     ["Mix softened butter with finely ground coffee, fresh basil, and lemon zest into a compound butter.","Place a small knob on each shucked oyster in its half-shell and arrange on a baking tray.","Broil 3 minutes until butter bubbles and edges curl; serve with strong espresso as aperitivo."]),

    ("basil","coffee","parmesan",
     "Coffee and Parmesan share phenylacetaldehyde and acetic acid — rosy-fermented and tart compounds that connect roasted arabica to aged dairy — while basil's linalool and 2-phenylethanol provide the herbal-floral bridge between these two umami powerhouses. The trio creates a sophisticated savory flavor used in coffee-crusted cheese preparations.",
     "Coffee Parmesan Basil Frittata",
     ["Whisk eggs with finely grated Parmesan, a teaspoon of espresso powder, and chopped fresh basil.","Cook in an oven-safe skillet over medium heat until edges set; transfer to a 375°F oven.","Bake until puffed and golden; finish with more Parmesan, torn basil, and cracked pepper."]),

    ("basil","coffee","rose",
     "Coffee and rose share 2-phenylethanol and phenylacetaldehyde — rosy-floral compounds that fine arabicas and roses both produce — while basil reinforces this shared compound set with its own 2-phenylethanol, creating a triple-floral-roasted register. The trio is the aromatic logic behind Middle Eastern rose coffee (qahwa) elevated with fresh herb.",
     "Rose Basil Coffee Pots de Crème",
     ["Steep fresh basil in hot cream 15 minutes; add espresso and a touch of rose water, strain.","Whisk into egg yolks with sugar; pour into ramekins and bake in water bath at 325°F until just set.","Chill 4 hours; serve topped with crystallized rose petals and a tiny fresh basil leaf."]),

    ("basil","coffee","salmon",
     "Coffee and salmon share dimethyl sulfide — the sulfurous compound linking roasted bitterness to marine aromatics — while basil's linalool and 2-phenylethanol bridge fatty fish to coffee's herbal-floral character. Coffee functions as a dry-rub spice here, creating a bitter crust that suppresses salmon's trimethylamine while adding deep roasted complexity.",
     "Coffee Crusted Salmon with Basil Oil",
     ["Mix finely ground espresso with brown sugar, smoked paprika, and salt to make a dry rub.","Press the rub firmly onto salmon fillets and sear crust-side down in a very hot dry pan 3 minutes.","Flip and finish in a 400°F oven 6 minutes; plate with basil oil and lemon segments."]),

    ("basil","coffee","strawberry",
     "Strawberry and coffee share furaneol — the sweet-caramel compound in ripe strawberries that also appears in roasted coffee — while basil's linalool and 2-phenylethanol amplify strawberry's floral esters and provide herbal brightness that lifts the sweet-bitter combination. The trio creates the flavor of a sophisticated café strawberry dessert.",
     "Strawberry Basil Espresso Tiramisu",
     ["Macerate sliced strawberries with espresso, sugar, and torn fresh basil for 20 minutes.","Layer espresso-soaked ladyfingers with mascarpone cream in a dish; add strawberry layer in the middle.","Top with final cream layer, dust with cocoa, and refrigerate overnight before serving."]),

    ("basil","coffee","tomato",
     "Coffee and tomato share furaneol and acetic acid — sweet-caramel and tart compounds that both roasted beans and ripe tomatoes produce through separate chemical pathways — while basil's linalool and eugenol complete the Mediterranean aromatic triad. Together they create the flavor logic behind Italian Sunday sauce where espresso is sometimes used as a secret ingredient.",
     "Coffee Tomato Basil Braised Pork",
     ["Brown pork shoulder all over, set aside; sauté garlic and onion, add espresso and crushed tomatoes.","Return pork to pot, braise at 300°F for 3 hours until fork-tender; reduce braising liquid.","Stir torn fresh basil into the sauce at the last moment; serve over polenta or pasta."]),

    ("basil","coffee","truffle",
     "Coffee and truffle share dimethyl sulfide, phenylacetaldehyde, and anisaldehyde — among the most extensive compound overlaps between two non-related ingredients — while basil's linalool and 2-phenylethanol provide herbal lift that prevents the dual-umami combination from collapsing into a single note. The trio defines the peak of savory luxury aromatic complexity.",
     "Truffle Coffee Basil Pasta",
     ["Cook fresh tagliatelle al dente; make a sauce by melting black truffle paste into coffee-infused cream.","Toss pasta in the truffle-coffee cream with Parmesan and cold butter; add a splash of pasta water.","Plate immediately, shave fresh black truffle over the top, and finish with torn fresh basil."]),

    ("basil","coffee","vanilla",
     "Coffee and vanilla share vanillin — the dominant sweet aroma compound in cured vanilla beans that also forms as a minor product of coffee's Maillard roasting — while basil's eugenol adds spiced warmth that mirrors vanilla's anise character and lifts the sweet-bitter combination. Together the trio creates the most refined version of vanilla coffee flavor.",
     "Vanilla Basil Coffee Panna Cotta",
     ["Warm cream with split vanilla bean, fresh basil, and a shot of espresso; steep 20 minutes and strain.","Dissolve gelatin in the warm cream, sweeten, pour into molds, and refrigerate until set.","Unmold onto plates, serve with an espresso reduction drizzle and a small fresh basil leaf."]),
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
print(f"Batch 004 done: inserted {len(TRIPLETS)} triplets.")
