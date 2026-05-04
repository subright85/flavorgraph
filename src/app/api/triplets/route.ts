import { NextRequest, NextResponse } from "next/server";
import { getDb, isSeeded } from "@/lib/db";
import { seed } from "@/lib/seed";

interface IngredientRow { id: number; name: string; category: string }
interface CompoundRow { name: string }

export async function GET(req: NextRequest) {
  const limit = Math.min(100, Number(req.nextUrl.searchParams.get("limit") ?? "50"));

  if (!isSeeded()) seed();
  const db = getDb();

  const ingredients = db.prepare("SELECT id, name, category FROM ingredient ORDER BY name").all() as IngredientRow[];

  const compoundMap = new Map<number, Set<string>>();
  for (const ing of ingredients) {
    const compounds = db.prepare(
      "SELECT c.name FROM compound c JOIN ingredient_compound ic ON ic.compound_id = c.id WHERE ic.ingredient_id = ?"
    ).all(ing.id) as CompoundRow[];
    compoundMap.set(ing.id, new Set(compounds.map(r => r.name)));
  }

  const triplets: {
    a: string; b: string; c: string;
    a_category: string; b_category: string; c_category: string;
    shared_count: number; shared_compounds: string[];
    avg_pair_score: number;
  }[] = [];

  for (let i = 0; i < ingredients.length; i++) {
    for (let j = i + 1; j < ingredients.length; j++) {
      for (let k = j + 1; k < ingredients.length; k++) {
        const ia = ingredients[i], ib = ingredients[j], ic = ingredients[k];
        const sa = compoundMap.get(ia.id)!;
        const sb = compoundMap.get(ib.id)!;
        const sc = compoundMap.get(ic.id)!;
        const shared = [...sa].filter(c => sb.has(c) && sc.has(c));

        // avg pair score
        const pairScore = (setA: Set<string>, setB: Set<string>) => {
          const s = [...setA].filter(c => setB.has(c)).length;
          const t = new Set([...setA, ...setB]).size;
          return t > 0 ? Math.round((s / t) * 100) : 0;
        };
        const avg = Math.round((pairScore(sa, sb) + pairScore(sb, sc) + pairScore(sa, sc)) / 3);

        triplets.push({ a: ia.name, b: ib.name, c: ic.name, a_category: ia.category, b_category: ib.category, c_category: ic.category, shared_count: shared.length, shared_compounds: shared, avg_pair_score: avg });
      }
    }
  }

  triplets.sort((a, b) => b.avg_pair_score - a.avg_pair_score || b.shared_count - a.shared_count);
  return NextResponse.json({ total: triplets.length, triplets: triplets.slice(0, limit) });
}
