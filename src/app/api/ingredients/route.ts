import { NextResponse } from "next/server";
import { getDb, isSeeded } from "@/lib/db";
import { seed } from "@/lib/seed";

interface IngredientRow { name: string; category: string }

export async function GET() {
  if (!isSeeded()) seed();
  const db = getDb();
  const rows = db.prepare("SELECT name, category FROM ingredient ORDER BY category, name").all() as IngredientRow[];
  return NextResponse.json({ ingredients: rows });
}
