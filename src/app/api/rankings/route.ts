import { NextResponse } from "next/server";
import { getDb, isSeeded } from "@/lib/db";
import { seed } from "@/lib/seed";

interface IngredientRow { id: number; name: string; category: string }
interface CompoundRow { name: string }

export async function GET() {
  if (!isSeeded()) seed();
  const db = getDb();

  const ingredients = db.prepare("SELECT id, name, category FROM ingredient ORDER BY name").all() as IngredientRow[];

  // preload all compound sets
  const compoundMap = new Map<number, Set<string>>();
  for (const ing of ingredients) {
    const compounds = db.prepare(
      "SELECT c.name FROM compound c JOIN ingredient_compound ic ON ic.compound_id = c.id WHERE ic.ingredient_id = ?"
    ).all(ing.id) as CompoundRow[];
    compoundMap.set(ing.id, new Set(compounds.map(r => r.name)));
  }

  const pairs: {
    a: string; b: string;
    a_category: string; b_category: string;
    score: number; label: string;
    shared_count: number; shared_compounds: string[];
  }[] = [];

  for (let i = 0; i < ingredients.length; i++) {
    for (let j = i + 1; j < ingredients.length; j++) {
      const ia = ingredients[i];
      const ib = ingredients[j];
      const sa = compoundMap.get(ia.id)!;
      const sb = compoundMap.get(ib.id)!;
      const shared = [...sa].filter(c => sb.has(c));
      const total = new Set([...sa, ...sb]).size;
      const score = total > 0 ? Math.round((shared.length / total) * 100) : 0;
      let label = "Unlikely";
      if (score >= 30) label = "Excellent";
      else if (score >= 15) label = "Good";
      else if (score >= 5) label = "Decent";
      pairs.push({ a: ia.name, b: ib.name, a_category: ia.category, b_category: ib.category, score, label, shared_count: shared.length, shared_compounds: shared });
    }
  }

  pairs.sort((a, b) => b.score - a.score || b.shared_count - a.shared_count);
  return NextResponse.json({ total: pairs.length, pairs });
}
