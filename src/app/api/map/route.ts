import { NextRequest, NextResponse } from "next/server";
import { getDb, isSeeded, isPrecomputed } from "@/lib/db";
import { seed, precomputePairsAndTriplets } from "@/lib/seed";

interface IngredientRow { id: number; name: string; category: string }

// Pair list for one ingredient. Reads from pre-computed `pair_score` so
// each request is a single indexed SELECT — no per-request Jaccard recompute.
export async function GET(req: NextRequest) {
  const a = req.nextUrl.searchParams.get("a")?.toLowerCase().trim();
  if (!a) return NextResponse.json({ error: "Provide ?a=<ingredient>" }, { status: 400 });

  if (!isSeeded()) seed();
  if (!isPrecomputed()) precomputePairsAndTriplets();
  const db = getDb();

  const base = db.prepare("SELECT id, name, category FROM ingredient WHERE name = ?").get(a) as IngredientRow | undefined;
  if (!base) return NextResponse.json({ error: `Unknown ingredient: ${a}` }, { status: 404 });

  const compoundCount = (db.prepare(
    "SELECT COUNT(*) AS n FROM ingredient_compound WHERE ingredient_id = ?"
  ).get(base.id) as { n: number }).n;

  const rows = db.prepare(`
    SELECT
      i.name     AS name,
      i.category AS category,
      ps.score   AS score,
      ps.shared_count,
      ps.shared_compounds
    FROM pair_score ps
    JOIN ingredient i ON i.name = ps.ing_b
    WHERE ps.ing_a = ?
    ORDER BY ps.score DESC, i.name ASC
  `).all(a) as { name: string; category: string; score: number; shared_count: number; shared_compounds: string }[];

  const pairings = rows.map((r) => ({
    name: r.name,
    category: r.category,
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
    compound_count: compoundCount,
    pairings,
  });
}
