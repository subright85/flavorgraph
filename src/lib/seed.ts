import { getDb } from "./db";

// Flavor compound data derived from published food pairing research.
// Each ingredient lists its primary volatile flavor compounds (simplified subset).
const INGREDIENTS: { name: string; category: string; compounds: string[] }[] = [
  { name: "chocolate", category: "confection", compounds: ["phenylacetaldehyde", "dimethyl sulfide", "trimethylamine", "acetic acid", "linalool", "vanillin", "furaneol", "2-phenylethanol"] },
  { name: "blue cheese", category: "dairy", compounds: ["dimethyl sulfide", "trimethylamine", "acetic acid", "butyric acid", "2-heptanone", "2-nonanone", "phenylacetaldehyde"] },
  { name: "strawberry", category: "fruit", compounds: ["furaneol", "linalool", "ethyl butanoate", "methyl anthranilate", "2-phenylethanol", "vanillin", "benzaldehyde"] },
  { name: "coffee", category: "beverage", compounds: ["furfural", "2-furanmethanol", "acetic acid", "dimethyl sulfide", "phenylacetaldehyde", "vanillin", "4-vinylguaiacol", "guaiacol"] },
  { name: "vanilla", category: "spice", compounds: ["vanillin", "4-hydroxybenzaldehyde", "anisaldehyde", "furaneol", "2-phenylethanol", "linalool"] },
  { name: "lamb", category: "meat", compounds: ["4-methyloctanoic acid", "4-ethyloctanoic acid", "octanoic acid", "dimethyl sulfide", "butyric acid", "trimethylamine"] },
  { name: "salmon", category: "seafood", compounds: ["dimethyl sulfide", "trimethylamine", "hexanal", "1-penten-3-ol", "linalool", "acetic acid"] },
  { name: "truffle", category: "fungi", compounds: ["dimethyl sulfide", "2-methylbutanal", "phenylacetaldehyde", "anisaldehyde", "2,4-dithiapentane", "bis(methylthio)methane"] },
  { name: "parmesan", category: "dairy", compounds: ["butyric acid", "acetic acid", "furaneol", "dimethyl sulfide", "4-hydroxybenzaldehyde", "phenylacetaldehyde"] },
  { name: "tomato", category: "vegetable", compounds: ["hexanal", "2-isobutylthiazole", "furaneol", "linalool", "1-penten-3-one", "beta-ionone", "geranylacetone"] },
  { name: "basil", category: "herb", compounds: ["linalool", "eugenol", "methyl chavicol", "1,8-cineole", "fenchyl acetate", "2-phenylethanol", "benzaldehyde"] },
  { name: "garlic", category: "vegetable", compounds: ["allicin", "diallyl disulfide", "dimethyl sulfide", "methyl allyl disulfide", "acetic acid"] },
  { name: "butter", category: "dairy", compounds: ["diacetyl", "butyric acid", "acetic acid", "dimethyl sulfide", "delta-decalactone", "delta-dodecalactone", "furaneol"] },
  { name: "caramel", category: "confection", compounds: ["furaneol", "diacetyl", "acetic acid", "vanillin", "delta-decalactone", "2-acetyl furan", "furfural"] },
  { name: "lemon", category: "fruit", compounds: ["limonene", "citral", "linalool", "4-terpineol", "geraniol", "nerylacetate", "beta-pinene"] },
  { name: "rose", category: "floral", compounds: ["2-phenylethanol", "geraniol", "citronellol", "linalool", "nerol", "beta-ionone", "benzaldehyde"] },
  { name: "oyster", category: "seafood", compounds: ["dimethyl sulfide", "trimethylamine", "1-octen-3-ol", "hexanal", "phenylacetaldehyde", "benzaldehyde"] },
  { name: "lavender", category: "herb", compounds: ["linalool", "linalyl acetate", "1,8-cineole", "beta-ocimene", "terpinen-4-ol", "2-phenylethanol"] },
  { name: "cucumber", category: "vegetable", compounds: ["hexanal", "(E)-2-nonenal", "(E,Z)-2,6-nonadienal", "1-penten-3-ol", "linalool", "benzaldehyde"] },
  { name: "mint", category: "herb", compounds: ["menthol", "menthone", "1,8-cineole", "limonene", "linalool", "pulegone"] },
];

export function seed() {
  const db = getDb();

  const insertIngredient = db.prepare(
    "INSERT OR IGNORE INTO ingredient (name, category) VALUES (?, ?)"
  );
  const insertCompound = db.prepare(
    "INSERT OR IGNORE INTO compound (name) VALUES (?)"
  );
  const insertLink = db.prepare(
    "INSERT OR IGNORE INTO ingredient_compound (ingredient_id, compound_id) VALUES (?, ?)"
  );
  const getIngredientId = db.prepare(
    "SELECT id FROM ingredient WHERE name = ?"
  ) as Database.Statement<[string], { id: number }>;
  const getCompoundId = db.prepare(
    "SELECT id FROM compound WHERE name = ?"
  ) as Database.Statement<[string], { id: number }>;

  const run = db.transaction(() => {
    for (const { name, category, compounds } of INGREDIENTS) {
      insertIngredient.run(name, category);
      const ing = getIngredientId.get(name)!;
      for (const c of compounds) {
        insertCompound.run(c);
        const comp = getCompoundId.get(c)!;
        insertLink.run(ing.id, comp.id);
      }
    }
  });
  run();
  console.log(`Seeded ${INGREDIENTS.length} ingredients.`);
}
