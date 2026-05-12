import { NextResponse } from "next/server";
import { getIngredients } from "@/lib/store";

export async function GET() {
  return NextResponse.json({ ingredients: getIngredients() });
}
