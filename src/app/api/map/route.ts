import { NextRequest, NextResponse } from "next/server";
import { getCompounds, getIngredient, getPairs } from "@/lib/store";

export async function GET(req: NextRequest) {
  const a = req.nextUrl.searchParams.get("a")?.toLowerCase().trim();
  if (!a) return NextResponse.json({ error: "Provide ?a=<ingredient>" }, { status: 400 });

  const base = getIngredient(a);
  if (!base) return NextResponse.json({ error: `Unknown ingredient: ${a}` }, { status: 404 });

  const compounds = getCompounds(a)!;

  const pairings = getPairs(a).map((r) => ({
    name: r.ing_b,
    category: getIngredient(r.ing_b)?.category ?? "",
    score: r.score,
    label:
      r.score >= 30 ? "Excellent" :
      r.score >= 15 ? "Good" :
      r.score >= 5  ? "Decent" : "Unlikely",
    shared_count: r.shared_count,
    shared_compounds: JSON.parse(r.shared_compounds) as string[],
  }));

  return NextResponse.json({
    ingredient: a,
    category: base.category,
    compound_count: compounds.size,
    pairings,
  });
}
