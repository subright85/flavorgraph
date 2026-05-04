import { NextRequest, NextResponse } from "next/server";
import { getDb, isSeeded } from "@/lib/db";
import { seed } from "@/lib/seed";

interface IngredientRow { id: number; name: string; category: string }
interface CompoundRow { name: string }

export async function GET(req: NextRequest) {
  const a = req.nextUrl.searchParams.get("a")?.toLowerCase().trim();
  if (!a) return NextResponse.json({ error: "Provide ?a=<ingredient>" }, { status: 400 });

  if (!isSeeded()) seed();
  const db = getDb();

  const base = db.prepare("SELECT id, name, category FROM ingredient WHERE name = ?").get(a) as IngredientRow | undefined;
  if (!base) return NextResponse.json({ error: `Unknown ingredient: ${a}` }, { status: 404 });

  const others = db.prepare("SELECT id, name, category FROM ingredient WHERE name != ?").all(a) as IngredientRow[];

  const baseCompounds = new Set(
    (db.prepare("SELECT c.name FROM compound c JOIN ingredient_compound ic ON ic.compound_id = c.id WHERE ic.ingredient_id = ?")
      .all(base.id) as CompoundRow[]).map(r => r.name)
  );

  const pairings = others.map(other => {
    const otherCompounds = new Set(
      (db.prepare("SELECT c.name FROM compound c JOIN ingredient_compound ic ON ic.compound_id = c.id WHERE ic.ingredient_id = ?")
        .all(other.id) as CompoundRow[]).map(r => r.name)
    );
    const shared = [...baseCompounds].filter(c => otherCompounds.has(c));
    const total = new Set([...baseCompounds, ...otherCompounds]).size;
    const score = total > 0 ? Math.round((shared.length / total) * 100) : 0;

    let label: string;
    if (score >= 30) label = "Excellent";
    else if (score >= 15) label = "Good";
    else if (score >= 5) label = "Decent";
    else label = "Unlikely";

    return { name: other.name, category: other.category, score, label, shared_count: shared.length, shared_compounds: shared };
  }).sort((a, b) => b.score - a.score);

  return NextResponse.json({
    ingredient: a,
    category: base.category,
    compound_count: baseCompounds.size,
    pairings,
  });
}
