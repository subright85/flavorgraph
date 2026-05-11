#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("cucumber","mint","rose",
     "Cucumber, mint, and rose share 2-phenylethanol and linalool — the rosy-floral and herbal terpenes present in all three through different biosynthetic pathways — creating a triple compound alignment of unusual aromatic coherence. The trio achieves a cool, floral, and fresh combination that defines Persian rose-mint cucumber preparations.",
     "Rose Mint Cucumber Sherbet",
     ["Blend cucumber with rose water, fresh mint, and simple syrup; strain until crystal clear.", "Add lemon juice and cold water; chill thoroughly.", "Serve over crushed ice with rose petals and fresh mint — the three-way linalool creates deep freshness."]),

    ("cucumber","mint","salmon",
     "Cucumber and mint share (E)-2-nonenal and linalool — doubling the cool-watery and herbal-fresh aromatics — while both independently suppress salmon's trimethylamine: cucumber through watery freshness and mint through menthol's olfactory masking. The double-mechanism TMA suppression produces an unusually clean salmon preparation.",
     "Mint Cucumber Salmon Soba",
     ["Cook soba noodles; rinse cold and toss with sesame oil and soy sauce.", "Top with thin slices of cured or smoked salmon, cucumber ribbons, and fresh mint leaves.", "Dress with a sesame-cucumber-mint vinaigrette and serve chilled."]),

    ("cucumber","mint","strawberry",
     "Cucumber and mint share linalool — the herbal-floral terpene in both — while mint's menthol amplifies strawberry's perceived freshness through olfactory cooling (the same mechanism as mint in mojitos), and cucumber's (E)-2-nonenal provides additional watery freshness that further brightens the sweet-caramel strawberry register.",
     "Mint Cucumber Strawberry Granita",
     ["Blend strawberries with cucumber juice, fresh mint, lime juice, and simple syrup; strain.", "Pour into a shallow pan and freeze, scraping every 30 minutes until granita texture.", "Serve in chilled glasses with a mint sprig, fresh strawberry, and thin cucumber ribbon."]),

    ("cucumber","mint","tomato",
     "Cucumber, mint, and tomato share hexanal — the green aldehyde compound that defines garden freshness in all three — while mint's menthol adds cooling contrast and tomato's acidity brightens the combination. The triple hexanal alignment with menthol cooling creates the most refreshing vegetable-herb combination possible.",
     "Mint Cucumber Tomato Gazpacho",
     ["Blend ripe tomatoes with cucumber, fresh mint, garlic, and olive oil until smooth.", "Season with sherry vinegar, salt, and white pepper; strain for silky texture.", "Serve very cold with diced tomato, cucumber, and a fresh mint garnish."]),

    ("cucumber","mint","truffle",
     "Cucumber's (E)-2-nonenal and mint's menthol both provide cooling contrast to truffle's dimethyl sulfide earthiness — a double-cooling mechanism against the dense earthy-funky register — while mint's linalool connects to cucumber's herbal freshness. The trio creates a surprisingly light luxury preparation where cool-herbal lifts truffle.",
     "Truffle Mint Cucumber Bruschetta",
     ["Toast sourdough; drizzle generously with truffle oil while still warm.", "Top with thin cucumber slices and a few small fresh mint leaves.", "Shave truffle over; finish with fleur de sel — the mint and cucumber give truffle unexpected lightness."]),

    ("cucumber","mint","vanilla",
     "Cucumber and mint share linalool while mint and vanilla share linalool through their separate herbal and floral terpene families — creating a linalool chain from cool-watery cucumber through cooling-herbal mint to warm-sweet vanilla. The trio creates an unusual cool-sweet combination in a spa-style dessert or beverage.",
     "Vanilla Mint Cucumber Panna Cotta",
     ["Infuse cream with split vanilla bean and fresh mint; steep 20 minutes and strain.", "Add cucumber juice for a subtle fresh note; dissolve gelatin and pour into molds.", "Set 4 hours; unmold and serve with thin cucumber ribbons and a vanilla bean curl."]),

    ("cucumber","oyster","parmesan",
     "Cucumber and oyster share (E)-2-nonenal — the clean watery compound in both — while Parmesan and oyster share dimethyl sulfide and free glutamates for a double-umami connection. Cucumber's cool freshness cuts Parmesan's rich dairy fat simultaneously with oyster's brine, creating a balance of marine, dairy, and fresh registers.",
     "Parmesan Cucumber Oyster Crostini",
     ["Toast crostini; top with a thin smear of Parmesan cream and a freshly shucked raw oyster.", "Add thin cucumber slices and a squeeze of lemon.", "Finish with a shaving of Parmesan and cracked pepper; serve immediately."]),

    ("cucumber","oyster","rose",
     "Cucumber, oyster, and rose all share phenylacetaldehyde — the rosy-fermented compound appearing in cucumber's minor aromatics, oyster's marine bivalve chemistry, and rose petal biosynthesis. This three-way shared compound creates unusual aromatic coherence in a perfumed oyster preparation.",
     "Rose Cucumber Oyster Mignonette",
     ["Mix rose water with white wine vinegar, finely minced shallot, and cracked white pepper.", "Add very finely diced cucumber and a tiny pinch of flaky salt; rest 5 minutes.", "Spoon over freshly shucked oysters on ice; the rose-cucumber creates a perfumed freshness."]),

    ("cucumber","oyster","salmon",
     "Cucumber, oyster, and salmon all share (E)-2-nonenal — the clean watery compound spanning cucumber flesh, fresh oyster, and premium salmon — creating a three-way alignment of the same fresh marine-vegetable compound. The trio creates a refined seafood preparation where cucumber's freshness is chemically native to both proteins.",
     "Cucumber Oyster Salmon Crudo",
     ["Slice sushi-grade salmon paper thin; arrange with freshly shucked oysters on a chilled plate.", "Dress with cucumber water (blended and strained cucumber), lemon juice, and fleur de sel.", "Add cucumber ribbons, a drop of good olive oil, and serve immediately chilled."]),

    ("cucumber","oyster","strawberry",
     "Cucumber and oyster share (E)-2-nonenal while strawberry and oyster share no direct compound — making cucumber the bridge between the marine and fruit registers through its own fresh-watery character. Strawberry's furaneol sweetness applies the sweet-salt principle against oyster's brine with cucumber's freshness as the neutral connector.",
     "Strawberry Cucumber Oyster Shooter",
     ["Blend muddled strawberry with cucumber water and a splash of rice vinegar; strain.", "Add a pinch of flaky salt and a drop of sesame oil.", "Pour into shot glasses; slip in a freshly shucked oyster and a cucumber ribbon; serve immediately."]),

    ("cucumber","oyster","tomato",
     "Cucumber, tomato, and oyster share hexanal — the green aldehyde compound that defines garden freshness in cucumber and tomato and appears as a minor compound in premium oyster. Tomato's glutamates add umami that compounds with oyster's own glutamates, while cucumber's freshness bridges vegetable and marine.",
     "Tomato Cucumber Oyster Stew",
     ["Sauté garlic in olive oil; add crushed tomatoes, cucumber water, and simmer 10 minutes.", "Add shucked oysters with their liquor; cook 2 minutes until just done.", "Season with herbs and salt; serve immediately with crusty bread — the cucumber softens the brine."]),

    ("cucumber","oyster","truffle",
     "Cucumber's (E)-2-nonenal clean freshness and oyster's marine (E)-2-nonenal share the same compound while truffle's dimethyl sulfide connects to oyster's marine dimethyl sulfide through the sulfurous compound family. The trio creates a luxury raw bar preparation where clean freshness and earthy depth bracket the brine.",
     "Truffle Cucumber Oyster on the Half Shell",
     ["Shuck oysters and arrange on crushed ice; top each with a thin sliver of truffle cream.", "Add a ribbon of cucumber and a drop of truffle oil on top.", "Shave fresh truffle over each oyster generously; serve immediately with champagne."]),

    ("cucumber","oyster","vanilla",
     "Cucumber's (E)-2-nonenal clean freshness and oyster's marine (E)-2-nonenal share the same compound while vanilla's vanillin sweetness applies the sweet-salt principle against oyster's brine. Cucumber's freshness bridges the unusual sweet-marine combination through its natural presence in both vegetable and oyster.",
     "Vanilla Cucumber Oyster Mignonette",
     ["Dissolve a tiny amount of vanilla sugar into white wine vinegar; add finely minced shallot.", "Add very finely diced cucumber; rest 5 minutes for flavors to meld.", "Spoon sparingly over raw oysters on ice — the vanilla-cucumber creates a surprising sweet-fresh-brine combination."]),

    ("cucumber","parmesan","rose",
     "Cucumber's (E)-2-nonenal cool freshness cuts Parmesan's butyric acid richness while rose's 2-phenylethanol and geraniol connect to Parmesan's fermentation esters through shared rosy-floral compounds. The trio creates a sophisticated Italian summer salad where cool-vegetable and dairy umami are lifted by floral perfume.",
     "Rose Parmesan Cucumber Salad",
     ["Shave Parmesan into wide curls; arrange over cucumber ribbons on a platter.", "Dress with a splash of rose water, lemon juice, and good olive oil.", "Scatter dried rose petals and fleur de sel; the rose bridges Parmesan's richness to cucumber's freshness."]),

    ("cucumber","parmesan","salmon",
     "Cucumber and salmon share (E)-2-nonenal — the clean watery compound in both — while Parmesan and salmon share dimethyl sulfide and butyric acid through their respective fermentation and fatty-acid chemistries. Cucumber's freshness bridges the dairy-fish combination while Parmesan's umami deepens salmon's savory register.",
     "Parmesan Cucumber Salmon Crudo",
     ["Slice salmon paper thin; arrange on a chilled plate with Parmesan shavings and cucumber ribbons.", "Dress with lemon juice, olive oil, and fleur de sel.", "The Parmesan adds umami depth while cucumber's freshness ties to the salmon's (E)-2-nonenal register."]),

    ("cucumber","parmesan","strawberry",
     "Cucumber and strawberry contrast through cool-watery against sweet-fruity while Parmesan and strawberry share furaneol — the sweet-caramel compound at the heart of both aged cheese and ripe strawberry. Cucumber's freshness cuts Parmesan's richness while strawberry's sweetness bridges the dairy-vegetable combination.",
     "Strawberry Parmesan Cucumber Salad",
     ["Slice ripe strawberries and cucumber; arrange on a platter with Parmesan shavings.", "Dress with aged balsamic, olive oil, and a pinch of flaky salt.", "Add fresh mint or basil; the strawberry bridges Parmesan's umami to cucumber's freshness."]),

    ("cucumber","parmesan","tomato",
     "Cucumber, Parmesan, and tomato are the three foundations of Italian summer caprese variations — cucumber's (E)-2-nonenal freshness amplifying tomato's garden green notes, Parmesan's umami deepening tomato's savory register through shared furaneol, and cucumber's cooling freshness preventing the cheese-tomato combination from being heavy.",
     "Cucumber Parmesan Tomato Caprese",
     ["Slice ripe tomatoes and cucumber; arrange in alternating layers with Parmesan shavings.", "Drizzle with aged balsamic, good olive oil, and flaky salt.", "Add fresh basil and cracked pepper; let sit 5 minutes before serving."]),

    ("cucumber","parmesan","truffle",
     "Cucumber's (E)-2-nonenal cool freshness contrasts with truffle's dimethyl sulfide earthiness — the ultimate clean-watery against earthy-funky opposition — while Parmesan and truffle share dimethyl sulfide and phenylacetaldehyde for umami-earthy depth. Cucumber's freshness prevents Parmesan-truffle's richness from becoming too heavy.",
     "Truffle Parmesan Cucumber Crostini",
     ["Spread truffle-Parmesan cream on toasted sourdough.", "Top with thin cucumber ribbons and a drizzle of truffle oil.", "Shave more Parmesan and fresh truffle over; finish with fleur de sel — cucumber lifts the luxury register."]),

    ("cucumber","parmesan","vanilla",
     "Cucumber's (E)-2-nonenal cool freshness contrasts with vanilla's vanillin warmth and Parmesan's butyric acid richness — the cool-watery against warm-sweet-dairy opposition — while Parmesan and vanilla share vanillin and furaneol for a sweet-savory compound connection. The trio creates an unusual savory-sweet cheese preparation.",
     "Vanilla Parmesan Cucumber Salad",
     ["Make a vanilla dressing: vanilla bean seeds, white wine vinegar, and good olive oil whisked together.", "Dress cucumber ribbons and Parmesan shavings with the vanilla vinaigrette.", "Add flaky salt and a tiny drizzle of honey; the vanilla bridges Parmesan's umami to cucumber's freshness."]),

    ("cucumber","rose","salmon",
     "Cucumber and salmon share (E)-2-nonenal — the clean watery compound in both — while rose's 2-phenylethanol and geraniol suppress salmon's trimethylamine through floral displacement, and cucumber's freshness provides a second non-compound-based TMA moderation through olfactory cooling. The trio creates a delicate Persian-inspired salmon preparation.",
     "Rose Cucumber Salmon Crudo",
     ["Slice sushi-grade salmon paper thin; arrange on a chilled plate.", "Dress with rose water, cucumber water, lemon juice, and fleur de sel.", "Add cucumber ribbons and rose petals; the rose-cucumber creates a clean floral freshness over the salmon."]),
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
print(f"Batch 042 done: inserted {len(TRIPLETS)} triplets.")
