// In-memory data store — replaces SQLite (better-sqlite3) for Vercel compatibility.
// 20 ingredients, ~190 pairs, ~1140 triplets pre-computed at module load.

export interface Ingredient {
  name: string;
  category: string;
}

export interface PairScore {
  ing_a: string;
  ing_b: string;
  score: number;
  shared_count: number;
  shared_compounds: string; // JSON string
  total_count: number;
}

export interface TripletScore {
  ing_a: string; ing_b: string; ing_c: string;
  a_category: string; b_category: string; c_category: string;
  avg_pair_score: number;
  shared_count: number;
  shared_compounds: string[]; // already parsed
}

const INGREDIENTS_RAW: { name: string; category: string; compounds: string[] }[] = [
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

const categoryByName = new Map<string, string>();
const compoundsByName = new Map<string, Set<string>>();
for (const { name, category, compounds } of INGREDIENTS_RAW) {
  categoryByName.set(name, category);
  compoundsByName.set(name, new Set(compounds));
}

export const INGREDIENTS: Ingredient[] = INGREDIENTS_RAW
  .map(({ name, category }) => ({ name, category }))
  .sort((a, b) => a.category.localeCompare(b.category) || a.name.localeCompare(b.name));

const names = INGREDIENTS_RAW.map((i) => i.name);

// ── Pair pre-computation ──────────────────────────────────────────────────────

const pairMap = new Map<string, PairScore>();
const pairsByIngredient = new Map<string, PairScore[]>();
const pairScoreCache: Record<string, number> = {};

for (const n of names) pairsByIngredient.set(n, []);

for (let i = 0; i < names.length; i++) {
  for (let j = i + 1; j < names.length; j++) {
    const a = names[i], b = names[j];
    const sa = compoundsByName.get(a)!;
    const sb = compoundsByName.get(b)!;
    const shared = [...sa].filter((c) => sb.has(c));
    const total = new Set([...sa, ...sb]).size;
    const score = total > 0 ? Math.round((shared.length / total) * 100) : 0;
    const sharedJson = JSON.stringify(shared);

    const rowAB: PairScore = { ing_a: a, ing_b: b, score, shared_count: shared.length, shared_compounds: sharedJson, total_count: total };
    const rowBA: PairScore = { ing_a: b, ing_b: a, score, shared_count: shared.length, shared_compounds: sharedJson, total_count: total };

    pairMap.set(`${a}|${b}`, rowAB);
    pairMap.set(`${b}|${a}`, rowBA);
    pairsByIngredient.get(a)!.push(rowAB);
    pairsByIngredient.get(b)!.push(rowBA);
    pairScoreCache[`${a}|${b}`] = score;
    pairScoreCache[`${b}|${a}`] = score;
  }
}

for (const pairs of pairsByIngredient.values()) {
  pairs.sort((a, b) => b.score - a.score || a.ing_b.localeCompare(b.ing_b));
}

// ── Triplet pre-computation ───────────────────────────────────────────────────

const tripletsByPair = new Map<string, TripletScore[]>();
const allTriplets: TripletScore[] = [];

for (let i = 0; i < names.length; i++) {
  for (let j = i + 1; j < names.length; j++) {
    for (let k = j + 1; k < names.length; k++) {
      const a = names[i], b = names[j], c = names[k];
      const sa = compoundsByName.get(a)!;
      const sb = compoundsByName.get(b)!;
      const sc = compoundsByName.get(c)!;
      const shared = [...sa].filter((x) => sb.has(x) && sc.has(x));
      const avg = Math.round(
        ((pairScoreCache[`${a}|${b}`] ?? 0) +
          (pairScoreCache[`${b}|${c}`] ?? 0) +
          (pairScoreCache[`${a}|${c}`] ?? 0)) / 3,
      );
      const row: TripletScore = {
        ing_a: a, ing_b: b, ing_c: c,
        a_category: categoryByName.get(a)!,
        b_category: categoryByName.get(b)!,
        c_category: categoryByName.get(c)!,
        avg_pair_score: avg,
        shared_count: shared.length,
        shared_compounds: shared,
      };
      allTriplets.push(row);
      for (const [x, y] of [[a, b], [b, a], [a, c], [c, a], [b, c], [c, b]] as [string, string][]) {
        const key = `${x}|${y}`;
        if (!tripletsByPair.has(key)) tripletsByPair.set(key, []);
        tripletsByPair.get(key)!.push(row);
      }
    }
  }
}

allTriplets.sort((a, b) => b.avg_pair_score - a.avg_pair_score || b.shared_count - a.shared_count);
for (const triplets of tripletsByPair.values()) {
  triplets.sort((a, b) => b.avg_pair_score - a.avg_pair_score);
}

// ── Query API ────────────────────────────────────────────────────────────────

export function getIngredients(): Ingredient[] { return INGREDIENTS; }

export function getIngredient(name: string): Ingredient | undefined {
  return INGREDIENTS.find((i) => i.name === name.toLowerCase().trim());
}

export function getCompounds(name: string): Set<string> | undefined {
  return compoundsByName.get(name.toLowerCase().trim());
}

export function getPairs(ingName: string): PairScore[] {
  return pairsByIngredient.get(ingName.toLowerCase().trim()) ?? [];
}

export function getPair(a: string, b: string): PairScore | undefined {
  return pairMap.get(`${a.toLowerCase().trim()}|${b.toLowerCase().trim()}`);
}

export function getAllTriplets(): TripletScore[] { return allTriplets; }

export function getTripletsByPair(a: string, b: string, limit = 10): TripletScore[] {
  const key = `${a.toLowerCase().trim()}|${b.toLowerCase().trim()}`;
  return (tripletsByPair.get(key) ?? []).slice(0, limit);
}
