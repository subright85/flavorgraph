#!/usr/bin/env python3
import sqlite3, json, os

DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flavorgraph.db"))

TRIPLETS = [
    ("cucumber","lavender","mint",
     "Cucumber, lavender, and mint all share linalool — the herbal-floral terpene connecting cool-watery cucumber, perfumed lavender, and cooling mint through the same dominant compound. This triple linalool alignment creates an intensely fresh, cool, and floral aromatic combination that defines Provençal summer beverages and refined spa-style preparations.",
     "Lavender Mint Cucumber Water",
     ["Combine fresh mint, cucumber slices, and dried lavender in a large pitcher of cold water.", "Add lemon slices; refrigerate 2 hours until fully infused and fragrant.", "Serve over ice, straining into glasses; the triple linalool creates an unusually aromatic still water."]),

    ("cucumber","lavender","oyster",
     "Cucumber and oyster share (E)-2-nonenal — the clean watery compound in both — while lavender's linalool provides floral aromatic bridging between the watery-cool and marine-brine registers. The trio creates a delicate Provençal oyster preparation where cucumber's freshness and lavender's floral warmth bracket the oceanic brine.",
     "Lavender Cucumber Oyster Mignonette",
     ["Make a mignonette: white wine vinegar, finely minced shallot, and a pinch of dried lavender.", "Add very finely diced cucumber and cracked white pepper; rest 10 minutes.", "Spoon over freshly shucked raw oysters on ice; serve with lemon and lavender sprig."]),

    ("cucumber","lavender","parmesan",
     "Cucumber's (E)-2-nonenal cool freshness cuts Parmesan's butyric acid richness — the clean-vegetable against rich-dairy contrast — while lavender's linalool provides floral bridging that lifts the cheese-vegetable combination into a Provençal aromatic register. The trio creates a refined summer cheese preparation.",
     "Lavender Parmesan Cucumber Salad",
     ["Slice cucumber ribbons with a peeler; toss with lavender honey and lemon juice.", "Arrange over a bed of shaved Parmesan Reggiano.", "Scatter dried lavender flowers and flaky salt; drizzle with good olive oil."]),

    ("cucumber","lavender","rose",
     "Cucumber and lavender share linalool while lavender and rose share linalool and 2-phenylethanol — creating a chain where cucumber's fresh-cool register connects through lavender to rose's warm-floral register. The trio creates a perfumed, feminine summer preparation where the three aromatics form a complete cool-to-warm floral arc.",
     "Rose Lavender Cucumber Sorbet",
     ["Blend cucumber with rose water, lavender simple syrup, and lemon juice until smooth.", "Strain; churn in an ice cream maker until the texture of soft sorbet.", "Freeze until firm; serve scooped with a rose petal, lavender sprig, and cucumber fan."]),

    ("cucumber","lavender","salmon",
     "Cucumber and lavender both share linalool — the herbal-floral terpene — while cucumber's (E)-2-nonenal cuts salmon's trimethylamine marine notes through watery freshness and lavender's linalool adds floral displacement as a second TMA suppressor. The trio creates a Provençal salmon preparation with double marine-note suppression.",
     "Lavender Cucumber Salmon",
     ["Rub salmon with dried lavender, lemon zest, and olive oil; rest 20 minutes.", "Bake at 400°F for 12 minutes until just opaque.", "Serve over thinly sliced cucumber dressed with lavender vinaigrette and lemon."]),

    ("cucumber","lavender","strawberry",
     "Cucumber and lavender share linalool while lavender and strawberry share linalool and furaneol — creating a chain where cucumber's cool freshness connects through lavender to strawberry's sweet-caramel register. The trio creates a refined summer dessert where cool-watery and sweet-floral balance precisely.",
     "Lavender Strawberry Cucumber Popsicles",
     ["Blend fresh strawberries with cucumber juice, lavender simple syrup, and lemon juice.", "Pour into popsicle molds and freeze 6 hours until firm.", "Unmold and serve; the lavender bridges cucumber's freshness and strawberry's sweetness."]),

    ("cucumber","lavender","tomato",
     "Cucumber and tomato share hexanal — the green aldehyde compound creating garden freshness in both — while lavender's linalool provides Provençal floral bridging between the fresh-cool cucumber and ripe-savory tomato registers. The trio creates a sophisticated Southern French salad where vegetable freshness and floral warmth balance.",
     "Lavender Cucumber Tomato Salad",
     ["Slice ripe tomatoes and cucumber; arrange in overlapping rows on a platter.", "Scatter finely chopped fresh lavender over (or use dried sparingly) and drizzle with olive oil.", "Add fleur de sel, cracked pepper, and a splash of lavender white wine vinegar."]),

    ("cucumber","lavender","truffle",
     "Cucumber's (E)-2-nonenal cool freshness contrasts with truffle's dimethyl sulfide earthiness — the most extreme clean-watery against earthy-funky opposition — while lavender's linalool provides floral bridging between the two extremes. The trio creates a luxury Provençal salad where truffle's earthiness is softened by both floral and cool-watery aromatics.",
     "Truffle Lavender Cucumber Tartine",
     ["Spread truffle cream on toasted sourdough; top with thinly sliced cucumber.", "Drizzle with lavender honey and truffle oil.", "Shave fresh truffle over; finish with fleur de sel and a dried lavender flower."]),

    ("cucumber","lavender","vanilla",
     "Cucumber and lavender share linalool while lavender and vanilla share linalool and linalyl acetate — creating a linalool chain from cucumber's fresh-herbal through lavender's floral to vanilla's lactonic-sweet register. The trio creates a sophisticated dessert where cool-watery freshness balances sweet-floral warmth.",
     "Lavender Vanilla Cucumber Panna Cotta",
     ["Infuse cream with dried lavender and vanilla bean; steep 20 minutes and strain.", "Dissolve gelatin; pour into molds and refrigerate 4 hours until set.", "Unmold; serve with thin cucumber ribbons dressed in lavender honey as a refreshing contrast."]),

    ("cucumber","lemon","mint",
     "Cucumber, lemon, and mint share linalool and geraniol — the herbal-floral and citrus-floral terpenes that connect all three through a green-fresh-citrus aromatic register — while mint's menthol adds cooling and lemon's citric acid adds brightness. This three-way terpene alignment defines the flavor of water infusions and Mediterranean summer drinks.",
     "Cucumber Lemon Mint Agua Fresca",
     ["Blend cucumber with lemon juice, fresh mint, and a touch of honey; strain clean.", "Add cold water and adjust lemon and sweetness to taste.", "Serve over ice with lemon wheels, mint sprigs, and cucumber rounds; the trio is instant summer."]),

    ("cucumber","lemon","oyster",
     "Cucumber and oyster share (E)-2-nonenal while lemon's citric acid performs its classic trimethylamine-suppressing function on oyster's marine notes, and lemon's geraniol connects to cucumber's terpene family through shared citrus-herbal aromatics. The trio creates the most refreshing possible raw oyster preparation.",
     "Cucumber Lemon Oyster Granita",
     ["Make a granita from cucumber juice, lemon juice, and a pinch of sea salt; freeze and scrape.", "Shuck oysters into half shells and arrange over crushed ice.", "Spoon cucumber-lemon granita onto each oyster; serve immediately for a refreshing bite."]),

    ("cucumber","lemon","parmesan",
     "Cucumber and lemon share geraniol — a floral-citrus terpene present in both — while lemon's citric acid cuts Parmesan's butyric fat through acid-fat balance and cucumber's (E)-2-nonenal provides watery freshness that further lightens the aged-dairy richness. The trio creates a bright, light summer cheese preparation.",
     "Lemon Cucumber Parmesan Salad",
     ["Shave Parmesan into wide curls with a vegetable peeler.", "Arrange over cucumber ribbons; dress with lemon juice, lemon zest, and good olive oil.", "Finish with flaky salt and cracked pepper; serve immediately while Parmesan is still firm."]),

    ("cucumber","lemon","rose",
     "Cucumber, lemon, and rose share geraniol — the floral-citrus terpene present in all three through different pathways — creating a triple geraniol alignment that makes this trio more aromatic than expected. The combination creates a perfumed, citrus-bright, cool preparation for summer drinks and elegant salads.",
     "Rose Lemon Cucumber Sorbet",
     ["Blend cucumber with rose water, lemon juice, lemon zest, and simple syrup until smooth.", "Strain; churn until sorbet texture and freeze until firm.", "Serve scooped with rose petals, a lemon curl, and a thin cucumber ribbon garnish."]),

    ("cucumber","lemon","salmon",
     "Cucumber's (E)-2-nonenal and lemon's citric acid both suppress salmon's trimethylamine through separate mechanisms — watery freshness and acid-driven TMA neutralization respectively — while cucumber's geraniol overlaps with lemon's geraniol through a shared citrus-herbal terpene. The double TMA suppression creates the cleanest-tasting possible salmon preparation.",
     "Lemon Cucumber Salmon Crudo",
     ["Slice sushi-grade salmon paper thin; arrange on a chilled plate.", "Dress with lemon juice, cucumber water (blended cucumber strained), and fleur de sel.", "Add cucumber ribbons, lemon zest, and a drizzle of olive oil; serve immediately."]),

    ("cucumber","lemon","strawberry",
     "Cucumber and strawberry both contain linalool — the floral-herbal terpene connecting their fresh registers — while lemon's citric acid amplifies strawberry's perceived brightness through acid-sweet contrast and connects to cucumber through shared geraniol. The trio creates a vibrant summer dessert where fresh and sweet-tart play in harmony.",
     "Strawberry Lemon Cucumber Salad",
     ["Slice ripe strawberries and cucumber; toss gently with lemon juice, zest, and a pinch of sugar.", "Add torn fresh mint and a drizzle of good olive oil.", "Rest 5 minutes; serve as a salad or over yogurt for a refreshing summer dessert."]),

    ("cucumber","lemon","tomato",
     "Cucumber, lemon, and tomato together form the classic Mediterranean salad acid structure — cucumber's (E)-2-nonenal freshness, tomato's malic and citric acids, and lemon's additional citric brightness all working in the same acid-fresh register. Lemon's geraniol overlaps with cucumber's minor aromatics for terpene coherence.",
     "Lemon Cucumber Tomato Fattoush",
     ["Dice cucumber and tomato; toss with lemon juice, lemon zest, and olive oil.", "Add torn toasted pita, fresh herbs, and sumac; toss gently.", "Season with flaky salt; rest 5 minutes and serve immediately while pita is still slightly crisp."]),

    ("cucumber","lemon","truffle",
     "Cucumber's (E)-2-nonenal cool freshness and lemon's citric brightness both contrast with truffle's dimethyl sulfide earthiness — double clean against earthy — while lemon's limonene provides aromatic lift that prevents truffle's density from dominating. The trio creates an elegant light luxury preparation where truffle is surprisingly approachable.",
     "Truffle Lemon Cucumber Bruschetta",
     ["Toast sourdough; drizzle with truffle oil and a squeeze of fresh lemon while still warm.", "Top with very thinly sliced cucumber and a pinch of fleur de sel.", "Shave truffle over; the lemon and cucumber refresh truffle's density into a lighter register."]),

    ("cucumber","lemon","vanilla",
     "Cucumber and lemon share geraniol — the floral-citrus terpene in both — while vanilla's linalool connects to both through the herbal-floral terpene family, and lemon's citric acidity prevents vanilla's sweetness from being cloying against cucumber's fresh-watery register. The trio creates an elegant, light dessert.",
     "Vanilla Lemon Cucumber Sorbet",
     ["Blend cucumber with vanilla bean seeds, lemon juice, lemon zest, and simple syrup.", "Strain very clean; churn in an ice cream maker until firm.", "Serve scooped with a lemon curl and thin cucumber ribbon; clean, aromatic, and light."]),

    ("cucumber","mint","oyster",
     "Cucumber and mint share (E)-2-nonenal and linalool — the cool-watery and herbal-floral compounds that create double freshness — while both independently cut oyster's marine brine through olfactory cooling: cucumber through watery freshness and mint through menthol's palate-cleansing. The trio achieves maximum marine-note moderation.",
     "Mint Cucumber Oyster Shooter",
     ["Blend cucumber with fresh mint, lime juice, and a pinch of salt; strain clean.", "Serve in shot glasses with a raw oyster slipped in and a fresh mint leaf.",
      "The mint-cucumber doubles as both a mignonette and a palate cleanser in one bite."]),

    ("cucumber","mint","parmesan",
     "Cucumber and mint share linalool — the herbal-floral terpene in both — while both provide cool contrast to Parmesan's butyric acid richness through different mechanisms: cucumber's watery freshness and mint's menthol cooling. The trio creates a refreshing summer cheese preparation where cool-herbal and dairy register in sequence.",
     "Mint Cucumber Parmesan Crostini",
     ["Toast crostini; rub with garlic and top with shaved Parmesan curls.", "Add thin cucumber slices and a few small fresh mint leaves.", "Drizzle with lemon-infused olive oil, flaky salt, and cracked pepper; serve immediately."]),
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
print(f"Batch 041 done: inserted {len(TRIPLETS)} triplets.")
