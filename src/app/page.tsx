"use client";

import { useEffect, useState, useCallback } from "react";
import dynamic from "next/dynamic";
import { INGREDIENT_EMOJI } from "@/lib/emojis";

const FlavorGraph = dynamic(() => import("@/components/FlavorGraph"), { ssr: false });

interface Ingredient { name: string; category: string }
interface Pairing {
  name: string; category: string; score: number;
  label: string; shared_count: number; shared_compounds: string[];
}
interface MapResult {
  ingredient: string; category: string;
  compound_count: number; pairings: Pairing[];
}

const CATEGORY_COLOR: Record<string, string> = {
  confection: "#c97a3c", dairy: "#d4a843", fruit: "#5cb85c",
  beverage: "#7b68ee", spice: "#e07b39", meat: "#c0392b",
  seafood: "#2980b9", fungi: "#8e6c3e", vegetable: "#27ae60",
  herb: "#1abc9c", floral: "#d46db3",
};

export default function Home() {
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [selected, setSelected] = useState("");
  const [result, setResult] = useState<MapResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [minScore, setMinScore] = useState(0);

  useEffect(() => {
    fetch("/api/ingredients").then(r => r.json()).then(d => setIngredients(d.ingredients ?? []));
  }, []);

  const loadMap = useCallback(async (name: string) => {
    setLoading(true);
    setResult(null);
    const res = await fetch(`/api/map?a=${encodeURIComponent(name)}`);
    const data = await res.json();
    setLoading(false);
    if (res.ok) setResult(data);
  }, []);

  const grouped = ingredients.reduce<Record<string, Ingredient[]>>((acc, ing) => {
    (acc[ing.category] ??= []).push(ing);
    return acc;
  }, {});

  return (
    <div style={{ display: "flex", height: "100vh", overflow: "hidden", background: "#0a0a0c", color: "#e8e8ea" }}>

      {/* ── Left sidebar ── */}
      <aside style={{
        width: 240, flexShrink: 0, borderRight: "1px solid #1e1e21",
        display: "flex", flexDirection: "column", overflow: "hidden",
      }}>
        <div style={{ padding: "24px 16px 12px", borderBottom: "1px solid #1e1e21" }}>
          <h1 style={{ fontSize: 20, fontWeight: 700, letterSpacing: "-0.02em" }}>FlavorGraph</h1>
          <p style={{ color: "#555", fontSize: 12, marginTop: 4 }}>Select an ingredient to explore pairings</p>
        </div>

        {/* Ingredient list */}
        <div style={{ flex: 1, overflowY: "auto", padding: "12px 10px" }}>
          {Object.entries(grouped).sort().map(([cat, items]) => (
            <div key={cat} style={{ marginBottom: 16 }}>
              <div style={{
                fontSize: 10, color: "#444", textTransform: "uppercase",
                letterSpacing: "0.1em", marginBottom: 6, paddingLeft: 4,
              }}>{cat}</div>
              {items.map(ing => {
                const isActive = ing.name === selected;
                const c = CATEGORY_COLOR[ing.category] ?? "#888";
                return (
                  <button
                    key={ing.name}
                    onClick={() => { setSelected(ing.name); loadMap(ing.name); }}
                    style={{
                      display: "flex", alignItems: "center", gap: 8,
                      width: "100%", padding: "7px 10px",
                      background: isActive ? c + "18" : "transparent",
                      border: "none", borderRadius: 7,
                      color: isActive ? c : "#aaa",
                      cursor: "pointer", textAlign: "left",
                      transition: "background 0.1s, color 0.1s",
                    }}
                  >
                    <span style={{ fontSize: 18, width: 24, textAlign: "center" }}>
                      {INGREDIENT_EMOJI[ing.name] ?? "🍽️"}
                    </span>
                    <span style={{ fontSize: 13, fontWeight: isActive ? 600 : 400, textTransform: "capitalize" }}>
                      {ing.name}
                    </span>
                  </button>
                );
              })}
            </div>
          ))}
        </div>
      </aside>

      {/* ── Main graph area ── */}
      <main style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>

        {/* Toolbar */}
        <div style={{
          display: "flex", alignItems: "center", gap: 20,
          padding: "14px 20px", borderBottom: "1px solid #1e1e21",
          flexShrink: 0,
        }}>
          {result ? (
            <>
              <div>
                <span style={{ fontSize: 18, marginRight: 8 }}>{INGREDIENT_EMOJI[result.ingredient]}</span>
                <span style={{ fontWeight: 600, fontSize: 15, textTransform: "capitalize" }}>{result.ingredient}</span>
                <span style={{ color: "#555", fontSize: 12, marginLeft: 10 }}>
                  {result.compound_count} compounds · {result.pairings.filter(p => p.score >= minScore).length} visible pairings
                </span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginLeft: "auto" }}>
                <label style={{ fontSize: 12, color: "#666" }}>Min score</label>
                <input
                  type="range" min={0} max={35} step={5} value={minScore}
                  onChange={e => setMinScore(Number(e.target.value))}
                  style={{ width: 100, accentColor: "#4ade80" }}
                />
                <span style={{ fontSize: 12, color: "#4ade80", minWidth: 20 }}>{minScore}</span>
              </div>
            </>
          ) : (
            <span style={{ color: "#444", fontSize: 14 }}>
              {loading ? "Loading…" : "← Select an ingredient"}
            </span>
          )}
        </div>

        {/* Graph */}
        <div style={{ flex: 1, padding: 16, overflow: "hidden" }}>
          {!result && !loading && (
            <div style={{
              height: "100%", display: "flex", alignItems: "center", justifyContent: "center",
              color: "#2a2a2d", fontSize: 48, flexDirection: "column", gap: 16,
            }}>
              <div style={{ fontSize: 64 }}>🧪</div>
              <div style={{ fontSize: 14, color: "#333" }}>Pick an ingredient to see its flavor connections</div>
            </div>
          )}
          {loading && (
            <div style={{
              height: "100%", display: "flex", alignItems: "center", justifyContent: "center",
              color: "#555", fontSize: 14,
            }}>
              Calculating flavor graph…
            </div>
          )}
          {result && !loading && (
            <FlavorGraph result={result} minScore={minScore} />
          )}
        </div>
      </main>
    </div>
  );
}
