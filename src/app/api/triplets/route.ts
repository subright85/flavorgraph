import { NextRequest, NextResponse } from "next/server";
import { getAllTriplets } from "@/lib/store";

export async function GET(req: NextRequest) {
  const limit = Math.min(200, Number(req.nextUrl.searchParams.get("limit") ?? "50"));
  const all = getAllTriplets();
  const triplets = all.slice(0, limit).map((r) => ({
    a: r.ing_a, b: r.ing_b, c: r.ing_c,
    a_category: r.a_category, b_category: r.b_category, c_category: r.c_category,
    shared_count: r.shared_count,
    shared_compounds: r.shared_compounds,
    avg_pair_score: r.avg_pair_score,
  }));
  return NextResponse.json({ total: all.length, triplets });
}
