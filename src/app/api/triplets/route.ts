import { NextRequest, NextResponse } from "next/server";
import { getDb, isSeeded, isPrecomputed } from "@/lib/db";
import { seed, precomputePairsAndTriplets } from "@/lib/seed";

// All triplets ranked by avg pair score, served from the pre-computed
// `triplet_score` table (~1,140 rows). No per-request cubic loop.
export async function GET(req: NextRequest) {
  const limit = Math.min(200, Number(req.nextUrl.searchParams.get("limit") ?? "50"));

  if (!isSeeded()) seed();
  if (!isPrecomputed()) precomputePairsAndTriplets();
  const db = getDb();

  const total = (db.prepare("SELECT COUNT(*) AS n FROM triplet_score").get() as { n: number }).n;

  const rows = db.prepare(`
    SELECT
      ts.ing_a, ts.ing_b, ts.ing_c,
      ts.avg_pair_score, ts.shared_count, ts.shared_compounds,
      ia.category AS a_category,
      ib.category AS b_category,
      ic.category AS c_category
    FROM triplet_score ts
    JOIN ingredient ia ON ia.name = ts.ing_a
    JOIN ingredient ib ON ib.name = ts.ing_b
    JOIN ingredient ic ON ic.name = ts.ing_c
    ORDER BY ts.avg_pair_score DESC, ts.shared_count DESC
    LIMIT ?
  `).all(limit) as {
    ing_a: string; ing_b: string; ing_c: string;
    avg_pair_score: number; shared_count: number; shared_compounds: string;
    a_category: string; b_category: string; c_category: string;
  }[];

  const triplets = rows.map((r) => ({
    a: r.ing_a, b: r.ing_b, c: r.ing_c,
    a_category: r.a_category, b_category: r.b_category, c_category: r.c_category,
    shared_count: r.shared_count,
    shared_compounds: JSON.parse(r.shared_compounds) as string[],
    avg_pair_score: r.avg_pair_score,
  }));

  return NextResponse.json({ total, triplets });
}
