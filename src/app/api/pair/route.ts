import { NextRequest, NextResponse } from "next/server";
import { getCompounds, getPair } from "@/lib/store";

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

  const setA = getCompounds(a);
  const setB = getCompounds(b);

  if (!setA) return NextResponse.json({ error: `Unknown ingredient: ${a}` }, { status: 404 });
  if (!setB) return NextResponse.json({ error: `Unknown ingredient: ${b}` }, { status: 404 });

  const pair = getPair(a, b);
  const shared = pair ? JSON.parse(pair.shared_compounds) as string[] : [...setA].filter(c => setB.has(c));
  const score = pair?.score ?? 0;

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
