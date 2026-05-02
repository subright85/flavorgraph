import { NextRequest, NextResponse } from "next/server";
import { getDb, isSeeded } from "@/lib/db";
import { seed } from "@/lib/seed";

interface CompoundRow { name: string }

export async function GET(req: NextRequest) {
  const { searchParams } = req.nextUrl;
  const a = searchParams.get("a")?.toLowerCase().trim();
  const b = searchParams.get("b")?.toLowerCase().trim();

  if (!a || !b) {
    return NextResponse.json({ error: "Provide ?a=<ingredient>&b=<ingredient>" }, { status: 400 });
  }
  if (a === b) {
    return NextResponse.json({ error: "Choose two different ingredients" }, { status: 400 });
  }

  if (!isSeeded()) seed();

  const db = getDb();

  const ingredientA = db.prepare("SELECT id FROM ingredient WHERE name = ?").get(a) as { id: number } | undefined;
  const ingredientB = db.prepare("SELECT id FROM ingredient WHERE name = ?").get(b) as { id: number } | undefined;

  if (!ingredientA) return NextResponse.json({ error: `Unknown ingredient: ${a}` }, { status: 404 });
  if (!ingredientB) return NextResponse.json({ error: `Unknown ingredient: ${b}` }, { status: 404 });

  const compoundsA = db.prepare(
    "SELECT c.name FROM compound c JOIN ingredient_compound ic ON ic.compound_id = c.id WHERE ic.ingredient_id = ?"
  ).all(ingredientA.id) as CompoundRow[];

  const compoundsB = db.prepare(
    "SELECT c.name FROM compound c JOIN ingredient_compound ic ON ic.compound_id = c.id WHERE ic.ingredient_id = ?"
  ).all(ingredientB.id) as CompoundRow[];

  const setA = new Set(compoundsA.map(r => r.name));
  const setB = new Set(compoundsB.map(r => r.name));
  const shared = [...setA].filter(c => setB.has(c));

  const total = new Set([...setA, ...setB]).size;
  const score = total > 0 ? Math.round((shared.length / total) * 100) : 0;

  let label: string;
  if (score >= 30) label = "Excellent pairing";
  else if (score >= 15) label = "Good pairing";
  else if (score >= 5) label = "Decent pairing";
  else label = "Unlikely pairing";

  return NextResponse.json({
    a,
    b,
    shared_compounds: shared,
    shared_count: shared.length,
    score,
    label,
    compounds_a: [...setA],
    compounds_b: [...setB],
  });
}
