import { NextRequest, NextResponse } from "next/server";
import { getIngredient, getTripletsByPair } from "@/lib/store";

export async function GET(req: NextRequest) {
  const a = req.nextUrl.searchParams.get("a")?.toLowerCase().trim();
  const b = req.nextUrl.searchParams.get("b")?.toLowerCase().trim();

  if (!a || !b) return NextResponse.json({ error: "Provide ?a=<ingredient>&b=<ingredient>" }, { status: 400 });
  if (!getIngredient(a)) return NextResponse.json({ error: `Unknown ingredient: ${a}` }, { status: 404 });
  if (!getIngredient(b)) return NextResponse.json({ error: `Unknown ingredient: ${b}` }, { status: 404 });

  const triplets = getTripletsByPair(a, b, 10);
  const candidates = triplets.map((t) => {
    const third = t.ing_a === a || t.ing_a === b ? (t.ing_b === a || t.ing_b === b ? t.ing_c : t.ing_b) : t.ing_a;
    const cat = t.ing_a === third ? t.a_category : t.ing_b === third ? t.b_category : t.c_category;
    return { name: third, category: cat, avg_score: t.avg_pair_score };
  });

  return NextResponse.json({ candidates });
}
