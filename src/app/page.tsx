"use client";

import { useEffect, useState, useCallback } from "react";

interface Ingredient { name: string; category: string }
interface PairResult {
  a: string;
  b: string;
  shared_compounds: string[];
  shared_count: number;
  score: number;
  label: string;
  compounds_a: string[];
  compounds_b: string[];
}

const CATEGORY_COLORS: Record<string, string> = {
  confection: "#c97a3c",
  dairy:      "#d4a843",
  fruit:      "#5cb85c",
  beverage:   "#7b68ee",
  spice:      "#e07b39",
  meat:       "#c0392b",
  seafood:    "#2980b9",
  fungi:      "#8e6c3e",
  vegetable:  "#27ae60",
  herb:       "#1abc9c",
  floral:     "#d46db3",
};

function scoreColor(score: number) {
  if (score >= 30) return "#4ade80";
  if (score >= 15) return "#facc15";
  if (score >= 5)  return "#fb923c";
  return "#f87171";
}

export default function Home() {
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [a, setA] = useState("");
  const [b, setB] = useState("");
  const [result, setResult] = useState<PairResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/api/ingredients")
      .then(r => r.json())
      .then(d => setIngredients(d.ingredients ?? []));
  }, []);

  const pair = useCallback(async () => {
    if (!a || !b) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await fetch(`/api/pair?a=${encodeURIComponent(a)}&b=${encodeURIComponent(b)}`);
      const data = await res.json();
      if (!res.ok) { setError(data.error ?? "Unknown error"); return; }
      setResult(data);
    } catch {
      setError("Network error");
    } finally {
      setLoading(false);
    }
  }, [a, b]);

  const grouped = ingredients.reduce<Record<string, Ingredient[]>>((acc, ing) => {
    (acc[ing.category] ??= []).push(ing);
    return acc;
  }, {});

  return (
    <main style={{ maxWidth: 720, margin: "0 auto", padding: "48px 20px" }}>
      <header style={{ marginBottom: 48, textAlign: "center" }}>
        <h1 style={{ fontSize: 36, fontWeight: 700, letterSpacing: "-0.02em" }}>
          FlavorGraph
        </h1>
        <p style={{ color: "#888", marginTop: 8, fontSize: 15 }}>
          Ingredient pairings through flavor chemistry — shared volatile compounds
        </p>
      </header>

      <section style={{ display: "flex", gap: 12, alignItems: "flex-end", flexWrap: "wrap" }}>
        {(["a", "b"] as const).map((slot) => (
          <div key={slot} style={{ flex: 1, minWidth: 180 }}>
            <label style={{ display: "block", fontSize: 12, color: "#888", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.08em" }}>
              Ingredient {slot.toUpperCase()}
            </label>
            <select
              value={slot === "a" ? a : b}
              onChange={e => slot === "a" ? setA(e.target.value) : setB(e.target.value)}
              style={{
                width: "100%", padding: "10px 12px", borderRadius: 8,
                background: "#1c1c1f", border: "1px solid #333", color: "#e8e8ea",
                fontSize: 15, cursor: "pointer",
              }}
            >
              <option value="">— choose —</option>
              {Object.entries(grouped).sort().map(([cat, items]) => (
                <optgroup key={cat} label={cat}>
                  {items.map(i => (
                    <option key={i.name} value={i.name}>{i.name}</option>
                  ))}
                </optgroup>
              ))}
            </select>
          </div>
        ))}

        <button
          onClick={pair}
          disabled={!a || !b || a === b || loading}
          style={{
            padding: "10px 24px", borderRadius: 8, border: "none",
            background: a && b && a !== b ? "#4ade80" : "#2a2a2d",
            color: a && b && a !== b ? "#0f0f11" : "#555",
            fontWeight: 600, fontSize: 15, cursor: a && b && a !== b ? "pointer" : "default",
            transition: "background 0.15s",
          }}
        >
          {loading ? "…" : "Pair"}
        </button>
      </section>

      {error && (
        <p style={{ marginTop: 20, color: "#f87171", fontSize: 14 }}>{error}</p>
      )}

      {result && (
        <section style={{ marginTop: 36 }}>
          <div style={{
            background: "#1c1c1f", borderRadius: 12, padding: 28,
            border: `1px solid ${scoreColor(result.score)}33`,
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
              <div>
                <span style={{
                  display: "inline-block",
                  background: CATEGORY_COLORS[ingredients.find(i => i.name === result.a)?.category ?? ""] + "22",
                  color: CATEGORY_COLORS[ingredients.find(i => i.name === result.a)?.category ?? ""],
                  borderRadius: 6, padding: "2px 8px", fontSize: 12, marginRight: 8,
                }}>{ingredients.find(i => i.name === result.a)?.category}</span>
                <strong style={{ fontSize: 20 }}>{result.a}</strong>
                <span style={{ color: "#555", margin: "0 12px" }}>+</span>
                <strong style={{ fontSize: 20 }}>{result.b}</strong>
                <span style={{
                  display: "inline-block",
                  background: CATEGORY_COLORS[ingredients.find(i => i.name === result.b)?.category ?? ""] + "22",
                  color: CATEGORY_COLORS[ingredients.find(i => i.name === result.b)?.category ?? ""],
                  borderRadius: 6, padding: "2px 8px", fontSize: 12, marginLeft: 8,
                }}>{ingredients.find(i => i.name === result.b)?.category}</span>
              </div>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: 36, fontWeight: 700, color: scoreColor(result.score) }}>
                  {result.score}
                </div>
                <div style={{ fontSize: 12, color: "#888" }}>{result.label}</div>
              </div>
            </div>

            <div style={{ marginTop: 20 }}>
              <div style={{ fontSize: 12, color: "#888", marginBottom: 10, textTransform: "uppercase", letterSpacing: "0.08em" }}>
                {result.shared_count} shared compound{result.shared_count !== 1 ? "s" : ""}
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                {result.shared_count === 0
                  ? <span style={{ color: "#555", fontSize: 14 }}>No shared compounds — the odd-couple factor.</span>
                  : result.shared_compounds.map(c => (
                    <span key={c} style={{
                      background: "#4ade8022", color: "#4ade80",
                      borderRadius: 6, padding: "4px 10px", fontSize: 13,
                      border: "1px solid #4ade8044",
                    }}>{c}</span>
                  ))
                }
              </div>
            </div>

            <details style={{ marginTop: 24 }}>
              <summary style={{ fontSize: 13, color: "#666", cursor: "pointer", userSelect: "none" }}>
                All compounds
              </summary>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 16 }}>
                {([["a", result.compounds_a], ["b", result.compounds_b]] as [string, string[]][]).map(([slot, comps]) => (
                  <div key={slot}>
                    <div style={{ fontSize: 12, color: "#888", marginBottom: 8 }}>
                      {slot === "a" ? result.a : result.b}
                    </div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                      {comps.map(c => (
                        <span key={c} style={{
                          background: result.shared_compounds.includes(c) ? "#4ade8022" : "#2a2a2d",
                          color: result.shared_compounds.includes(c) ? "#4ade80" : "#888",
                          borderRadius: 5, padding: "3px 8px", fontSize: 12,
                        }}>{c}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </details>
          </div>
        </section>
      )}

      <footer style={{ marginTop: 80, textAlign: "center", color: "#444", fontSize: 13 }}>
        Flavor data derived from published food-pairing research on volatile compounds.
      </footer>
    </main>
  );
}
