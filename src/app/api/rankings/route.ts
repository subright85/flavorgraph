import { NextResponse } from "next/server";
import { getIngredients, getCompounds } from "@/lib/store";

export async function GET() {
  const ingredients = getIngredients();

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
      const sa = getCompounds(ia.name)!;
      const sb = getCompounds(ib.name)!;
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
