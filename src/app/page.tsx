"use client";

import { useEffect, useState, useCallback } from "react";
import { INGREDIENT_EMOJI } from "@/lib/emojis";

interface Ingredient { name: string; category: string }
interface Pairing {
  name: string;
  category: string;
  score: number;
  label: string;
  shared_count: number;
  shared_compounds: string[];
}
interface MapResult {
  ingredient: string;
  category: string;
  compound_count: number;
  pairings: Pairing[];
}

const CATEGORY_COLOR: Record<string, string> = {
  confection: "#c97a3c", dairy: "#d4a843", fruit: "#5cb85c",
  beverage: "#7b68ee", spice: "#e07b39", meat: "#c0392b",
  seafood: "#2980b9", fungi: "#8e6c3e", vegetable: "#27ae60",
  herb: "#1abc9c", floral: "#d46db3",
};

function scoreColor(score: number) {
  if (score >= 30) return "#4ade80";
  if (score >= 15) return "#facc15";
  if (score >= 5)  return "#fb923c";
  return "#64748b";
}

function ScoreBar({ score }: { score: number }) {
  return (
    <div style={{ width: "100%", height: 4, background: "#2a2a2d", borderRadius: 2, overflow: "hidden" }}>
      <div style={{
        height: "100%", width: `${score}%`, maxWidth: "100%",
        background: scoreColor(score), borderRadius: 2,
        transition: "width 0.4s ease",
      }} />
    </div>
  );
}

export default function Home() {
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [selected, setSelected] = useState("");
  const [result, setResult] = useState<MapResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/ingredients").then(r => r.json()).then(d => setIngredients(d.ingredients ?? []));
  }, []);

  const loadMap = useCallback(async (name: string) => {
    if (!name) return;
    setLoading(true);
    setResult(null);
    setExpanded(null);
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
    <main style={{ maxWidth: 780, margin: "0 auto", padding: "48px 20px 80px" }}>
      <header style={{ marginBottom: 40, textAlign: "center" }}>
        <h1 style={{ fontSize: 32, fontWeight: 700, letterSpacing: "-0.02em" }}>FlavorGraph</h1>
        <p style={{ color: "#666", marginTop: 6, fontSize: 14 }}>
          Pick an ingredient — see everything it pairs with, ranked by shared flavor compounds
        </p>
      </header>

      {/* Ingredient grid selector */}
      <section style={{ marginBottom: 40 }}>
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(110px, 1fr))",
          gap: 10,
        }}>
          {ingredients.map(ing => {
            const isSelected = ing.name === selected;
            const catColor = CATEGORY_COLOR[ing.category] ?? "#888";
            return (
              <button
                key={ing.name}
                onClick={() => { setSelected(ing.name); loadMap(ing.name); }}
                style={{
                  background: isSelected ? catColor + "22" : "#1c1c1f",
                  border: `1px solid ${isSelected ? catColor : "#2a2a2d"}`,
                  borderRadius: 10, padding: "12px 8px",
                  cursor: "pointer", textAlign: "center",
                  transition: "all 0.15s",
                  color: isSelected ? catColor : "#ccc",
                }}
              >
                <div style={{ fontSize: 28, marginBottom: 4 }}>{INGREDIENT_EMOJI[ing.name] ?? "🍽️"}</div>
                <div style={{ fontSize: 12, fontWeight: isSelected ? 600 : 400 }}>{ing.name}</div>
                <div style={{ fontSize: 10, color: "#555", marginTop: 2 }}>{ing.category}</div>
              </button>
            );
          })}
        </div>
      </section>

      {loading && (
        <div style={{ textAlign: "center", color: "#555", padding: 40 }}>Calculating pairings…</div>
      )}

      {result && (
        <section>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
            <span style={{ fontSize: 36 }}>{INGREDIENT_EMOJI[result.ingredient] ?? "🍽️"}</span>
            <div>
              <h2 style={{ fontSize: 22, fontWeight: 700, textTransform: "capitalize" }}>{result.ingredient}</h2>
              <p style={{ color: "#666", fontSize: 13 }}>
                {result.compound_count} flavor compounds · {result.pairings.length} pairings ranked
              </p>
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {result.pairings.map(p => {
              const isOpen = expanded === p.name;
              const catColor = CATEGORY_COLOR[p.category] ?? "#888";
              return (
                <div
                  key={p.name}
                  onClick={() => setExpanded(isOpen ? null : p.name)}
                  style={{
                    background: "#1c1c1f",
                    border: `1px solid ${isOpen ? scoreColor(p.score) + "44" : "#2a2a2d"}`,
                    borderRadius: 10, padding: "14px 16px", cursor: "pointer",
                    transition: "border-color 0.15s",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <span style={{ fontSize: 22, flexShrink: 0 }}>{INGREDIENT_EMOJI[p.name] ?? "🍽️"}</span>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 6 }}>
                        <span style={{ fontWeight: 600, fontSize: 15, textTransform: "capitalize" }}>{p.name}</span>
                        <span style={{ fontSize: 12, color: "#555" }}>{p.category}</span>
                      </div>
                      <ScoreBar score={p.score} />
                    </div>
                    <div style={{ textAlign: "right", flexShrink: 0, marginLeft: 12 }}>
                      <div style={{ fontSize: 20, fontWeight: 700, color: scoreColor(p.score) }}>{p.score}</div>
                      <div style={{ fontSize: 10, color: "#555" }}>{p.label}</div>
                    </div>
                  </div>

                  {isOpen && (
                    <div style={{ marginTop: 14, paddingTop: 14, borderTop: "1px solid #2a2a2d" }}>
                      <div style={{ fontSize: 11, color: "#666", marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.06em" }}>
                        {p.shared_count} shared compound{p.shared_count !== 1 ? "s" : ""}
                      </div>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                        {p.shared_count === 0
                          ? <span style={{ color: "#444", fontSize: 13 }}>No shared compounds</span>
                          : p.shared_compounds.map(c => (
                            <span key={c} style={{
                              background: "#4ade8018", color: "#4ade80",
                              border: "1px solid #4ade8033",
                              borderRadius: 5, padding: "3px 9px", fontSize: 12,
                            }}>{c}</span>
                          ))
                        }
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </section>
      )}

      <footer style={{ marginTop: 60, textAlign: "center", color: "#333", fontSize: 12 }}>
        Flavor data from published volatile compound research.
      </footer>
    </main>
  );
}
