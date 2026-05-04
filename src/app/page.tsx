"use client";

import { useEffect, useState, useCallback } from "react";
import { INGREDIENT_EMOJI } from "@/lib/emojis";
import { KNOWN_IMAGES } from "@/lib/imageCache";

/* ── Types ── */
interface Ingredient { name: string; category: string }
interface Pairing { name: string; category: string; score: number; label: string; shared_count: number; shared_compounds: string[] }
interface MapResult { ingredient: string; category: string; compound_count: number; pairings: Pairing[] }
interface TripletCandidate { name: string; category: string; avg_score: number }

/* ── Constants ── */
const CATEGORY_COLOR: Record<string, string> = {
  confection: "#c97a3c", dairy: "#d4a843", fruit: "#5cb85c",
  beverage: "#7b68ee", spice: "#e07b39", meat: "#c0392b",
  seafood: "#2980b9", fungi: "#8e6c3e", vegetable: "#27ae60",
  herb: "#1abc9c", floral: "#d46db3",
};

function scoreColor(s: number) {
  return s >= 30 ? "#22c55e" : s >= 15 ? "#f59e0b" : s >= 5 ? "#f97316" : "#94a3b8";
}
function scoreLabel(s: number) {
  return s >= 30 ? "Excellent" : s >= 15 ? "Good" : s >= 5 ? "Decent" : "Unlikely";
}

const glass: React.CSSProperties = {
  background: "var(--glass-bg)",
  backdropFilter: "blur(20px)",
  WebkitBackdropFilter: "blur(20px)",
  border: "1px solid var(--glass-border)",
  borderRadius: "var(--radius)",
  boxShadow: "var(--glass-shadow)",
};

function CategoryPill({ cat }: { cat: string }) {
  const c = CATEGORY_COLOR[cat] ?? "#888";
  return (
    <span style={{
      background: c + "20", color: c, border: `1px solid ${c}40`,
      borderRadius: 20, padding: "1px 8px", fontSize: 10, fontWeight: 600, flexShrink: 0,
    }}>
      {cat}
    </span>
  );
}

/* ── Small thumbnail with error fallback ── */
function Thumb({ name, category, size, radius }: { name: string; category: string; size: number; radius: number }) {
  const [err, setErr] = useState(false);
  const img = KNOWN_IMAGES[name];
  const c = CATEGORY_COLOR[category] ?? "#888";
  return (
    <div style={{ width: size, height: size, borderRadius: radius, overflow: "hidden", flexShrink: 0, border: "1px solid rgba(0,0,0,0.08)" }}>
      {img && !err ? (
        <img src={img} alt={name} onError={() => setErr(true)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      ) : (
        <div style={{ width: "100%", height: "100%", background: c + "28", display: "flex", alignItems: "center", justifyContent: "center", fontSize: size * 0.45 }}>
          {INGREDIENT_EMOJI[name] ?? "🍽️"}
        </div>
      )}
    </div>
  );
}

/* ── Ingredient Card ── */
function IngredientCard({ ing, selected, onClick }: { ing: Ingredient; selected: boolean; onClick: () => void }) {
  const [imgErr, setImgErr] = useState(false);
  const img = KNOWN_IMAGES[ing.name];
  const c = CATEGORY_COLOR[ing.category] ?? "#888";

  return (
    <div
      onClick={onClick}
      style={{
        borderRadius: 12, aspectRatio: "1", position: "relative",
        overflow: "hidden", cursor: "pointer",
        border: selected ? "2.5px solid var(--accent)" : "2px solid rgba(255,255,255,0.5)",
        boxShadow: selected
          ? "0 0 0 4px rgba(0,102,255,0.18), 0 6px 24px rgba(80,60,120,0.18)"
          : "0 2px 10px rgba(80,60,120,0.08)",
        transform: selected ? "scale(1.04)" : "scale(1)",
        transition: "all 0.18s ease",
      }}
    >
      {img && !imgErr ? (
        <img src={img} alt={ing.name} onError={() => setImgErr(true)}
          style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }} />
      ) : (
        <div style={{
          width: "100%", height: "100%",
          background: `linear-gradient(135deg, ${c}35, ${c}15)`,
          display: "flex", alignItems: "center", justifyContent: "center",
        }}>
          <span style={{ fontSize: 36, opacity: 0.75 }}>{INGREDIENT_EMOJI[ing.name] ?? "🍽️"}</span>
        </div>
      )}
      <div style={{ position: "absolute", inset: 0, background: "linear-gradient(to top, rgba(0,0,0,0.82) 0%, rgba(0,0,0,0.15) 50%, transparent 100%)" }} />
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, padding: "10px 9px 8px" }}>
        <div style={{ color: "#fff", fontSize: 11, fontWeight: 700, textTransform: "capitalize", textShadow: "0 1px 4px rgba(0,0,0,0.7)", marginBottom: 3, lineHeight: 1.2 }}>
          {INGREDIENT_EMOJI[ing.name]} {ing.name}
        </div>
        <span style={{
          background: "rgba(0,0,0,0.35)", color: "rgba(255,255,255,0.8)",
          borderRadius: 8, padding: "0px 5px", fontSize: 9, fontWeight: 600,
          textTransform: "uppercase", letterSpacing: "0.06em",
        }}>
          {ing.category}
        </span>
      </div>
    </div>
  );
}

/* ── Triplet Chip (one candidate) ── */
function TripletChip({ c, rank }: { c: TripletCandidate; rank: number }) {
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 7,
      background: "rgba(255,255,255,0.88)",
      border: `1px solid ${scoreColor(c.avg_score)}33`,
      borderRadius: 9, padding: "6px 10px 6px 7px",
      boxShadow: "0 1px 5px rgba(80,60,120,0.07)",
    }}>
      <Thumb name={c.name} category={c.category} size={22} radius={6} />
      <span style={{ fontSize: 10, color: "var(--text-muted)", fontWeight: 700 }}>#{rank}</span>
      <span style={{ fontSize: 12, fontWeight: 600, textTransform: "capitalize" }}>{c.name}</span>
      <span style={{ fontSize: 11, color: scoreColor(c.avg_score), fontWeight: 700 }}>{c.avg_score}</span>
    </div>
  );
}

/* ── Triplet Expand ── */
function TripletExpand({ a, b }: { a: string; b: string }) {
  const [candidates, setCandidates] = useState<TripletCandidate[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    setCandidates([]);
    fetch(`/api/triplet-expand?a=${encodeURIComponent(a)}&b=${encodeURIComponent(b)}`)
      .then(r => r.json())
      .then(d => { setCandidates(d.candidates ?? []); setLoading(false); });
  }, [a, b]);

  return (
    <div style={{
      margin: "0 0 6px", padding: "12px 16px 14px",
      background: "rgba(0,102,255,0.04)",
      border: "1px solid rgba(0,102,255,0.14)", borderTop: "none",
      borderRadius: "0 0 10px 10px",
    }}>
      <div style={{ fontSize: 11, color: "var(--text-muted)", fontWeight: 600, marginBottom: 10 }}>
        ✨ Best third ingredient to complete this pair:
      </div>
      {loading ? (
        <div style={{ fontSize: 12, color: "var(--text-muted)" }}>Computing…</div>
      ) : (
        <div style={{ display: "flex", gap: 7, flexWrap: "wrap" }}>
          {candidates.slice(0, 6).map((c, idx) => (
            <TripletChip key={c.name} c={c} rank={idx + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

/* ── Pair Row (one row in the list) ── */
function PairRow({ p, rank, isExpanded, ingredient, onToggle }: {
  p: Pairing; rank: number; isExpanded: boolean; ingredient: string; onToggle: () => void;
}) {
  return (
    <div style={{ marginBottom: isExpanded ? 0 : 6 }}>
      <div
        onClick={onToggle}
        style={{
          display: "flex", alignItems: "center", gap: 10,
          padding: "10px 14px",
          borderRadius: isExpanded ? "10px 10px 0 0" : 10,
          background: isExpanded ? "rgba(0,102,255,0.07)" : "rgba(255,255,255,0.62)",
          border: `1px solid ${isExpanded ? "rgba(0,102,255,0.22)" : "rgba(255,255,255,0.85)"}`,
          borderBottom: isExpanded ? "none" : undefined,
          cursor: "pointer", transition: "all 0.12s",
        }}
      >
        <span style={{ fontSize: 10, color: "var(--text-muted)", fontWeight: 700, minWidth: 24, textAlign: "right" }}>
          #{rank}
        </span>
        <Thumb name={p.name} category={p.category} size={34} radius={8} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontWeight: 600, fontSize: 13, textTransform: "capitalize", color: "var(--text-primary)" }}>{p.name}</div>
          <div style={{ fontSize: 10, color: "var(--text-muted)" }}>
            {p.shared_count} shared compound{p.shared_count !== 1 ? "s" : ""}
          </div>
        </div>
        <CategoryPill cat={p.category} />
        <span style={{
          background: scoreColor(p.score) + "22", color: scoreColor(p.score),
          border: `1px solid ${scoreColor(p.score)}44`,
          borderRadius: 20, padding: "2px 10px", fontSize: 12, fontWeight: 700, flexShrink: 0,
        }}>
          {p.score} <span style={{ fontWeight: 400, opacity: 0.8, fontSize: 11 }}>{scoreLabel(p.score)}</span>
        </span>
        <div style={{ width: 52, height: 4, background: "rgba(0,0,0,0.07)", borderRadius: 4, overflow: "hidden", flexShrink: 0 }}>
          <div style={{ width: `${Math.min(100, p.score / 50 * 100)}%`, height: "100%", background: scoreColor(p.score), borderRadius: 4 }} />
        </div>
        <span style={{ fontSize: 9, color: "var(--text-muted)", transform: isExpanded ? "rotate(180deg)" : "rotate(0)", transition: "transform 0.2s", flexShrink: 0 }}>▼</span>
      </div>
      {isExpanded && <TripletExpand a={ingredient} b={p.name} />}
    </div>
  );
}

/* ── Pair Panel ── */
function PairPanel({ ingredient, result, loading }: { ingredient: string; result: MapResult | null; loading: boolean }) {
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);
  const [heroErr, setHeroErr] = useState(false);
  const img = KNOWN_IMAGES[ingredient];
  const c = CATEGORY_COLOR[result?.category ?? ""] ?? "#888";

  useEffect(() => { setExpandedIdx(null); setHeroErr(false); }, [ingredient]);

  return (
    <div style={{ ...glass, flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
      {/* Hero header */}
      <div style={{ height: 152, position: "relative", flexShrink: 0, overflow: "hidden", borderRadius: "var(--radius) var(--radius) 0 0" }}>
        {img && !heroErr ? (
          <img src={img} alt={ingredient} onError={() => setHeroErr(true)}
            style={{ width: "100%", height: "100%", objectFit: "cover", filter: "blur(28px) brightness(0.28)", transform: "scale(1.18)", position: "absolute", inset: 0 }} />
        ) : (
          <div style={{ position: "absolute", inset: 0, background: `linear-gradient(135deg, ${c}60, ${c}20)` }} />
        )}
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(to bottom, rgba(0,0,0,0.1), rgba(0,0,0,0.55))" }} />
        <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", gap: 20, padding: "20px 28px" }}>
          <div style={{ width: 76, height: 76, borderRadius: 16, overflow: "hidden", flexShrink: 0, border: "2px solid rgba(255,255,255,0.3)", boxShadow: "0 6px 24px rgba(0,0,0,0.35)" }}>
            {img && !heroErr ? (
              <img src={img} alt={ingredient} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            ) : (
              <div style={{ width: "100%", height: "100%", background: c + "50", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 34 }}>
                {INGREDIENT_EMOJI[ingredient] ?? "🍽️"}
              </div>
            )}
          </div>
          <div>
            <div style={{ fontSize: 10, color: "rgba(255,255,255,0.5)", textTransform: "uppercase", letterSpacing: "0.12em", fontWeight: 600, marginBottom: 5 }}>
              Selected Ingredient
            </div>
            <div style={{ color: "#fff", fontWeight: 800, fontSize: 26, textTransform: "capitalize", letterSpacing: "-0.02em", lineHeight: 1 }}>
              {ingredient}
            </div>
            {result && (
              <div style={{ color: "rgba(255,255,255,0.5)", fontSize: 12, marginTop: 6 }}>
                {result.compound_count} aromatic compounds · {result.pairings.length} flavor pairings ranked
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Pair list */}
      {loading ? (
        <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-muted)", fontSize: 13 }}>
          Calculating flavor pairings…
        </div>
      ) : result ? (
        <div style={{ flex: 1, overflowY: "auto", padding: "12px 14px 14px" }}>
          {result.pairings.map((p, i) => (
            <PairRow
              key={p.name}
              p={p}
              rank={i + 1}
              isExpanded={expandedIdx === i}
              ingredient={ingredient}
              onToggle={() => setExpandedIdx(expandedIdx === i ? null : i)}
            />
          ))}
        </div>
      ) : null}
    </div>
  );
}

/* ── ROOT PAGE ── */
export default function Home() {
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [mapResult, setMapResult] = useState<MapResult | null>(null);
  const [loadingMap, setLoadingMap] = useState(false);

  useEffect(() => {
    fetch("/api/ingredients").then(r => r.json()).then(d => setIngredients(d.ingredients ?? []));
  }, []);

  const selectIngredient = useCallback(async (name: string) => {
    if (selected === name) { setSelected(null); setMapResult(null); return; }
    setSelected(name);
    setMapResult(null);
    setLoadingMap(true);
    const res = await fetch(`/api/map?a=${encodeURIComponent(name)}`);
    if (res.ok) setMapResult(await res.json());
    setLoadingMap(false);
  }, [selected]);

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column", padding: 16, gap: 12 }}>
      {/* Nav */}
      <nav style={{ ...glass, display: "flex", alignItems: "center", padding: "10px 22px", gap: 8, flexShrink: 0 }}>
        <div>
          <span style={{ fontWeight: 800, fontSize: 17, color: "var(--accent)", letterSpacing: "-0.03em" }}>FlavorGraph</span>
          <span style={{ fontSize: 11, color: "var(--text-muted)", marginLeft: 8 }}>Flavor chemistry pairing</span>
        </div>
        <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 18 }}>
          <span style={{ fontSize: 12, color: "var(--text-muted)" }}>20 ingredients · 190 pairs · 1,140 triplets</span>
          <a href="/about" style={{ fontSize: 12, color: "var(--accent)", fontWeight: 600 }}>Methodology ↗</a>
        </div>
      </nav>

      {/* Main two-column layout */}
      <div style={{ flex: 1, display: "flex", gap: 14, overflow: "hidden" }}>
        {/* Left: ingredient card grid */}
        <div style={{
          width: 338, flexShrink: 0, overflowY: "auto", overflowX: "hidden",
          display: "grid", gridTemplateColumns: "1fr 1fr",
          gap: 9, alignContent: "start", padding: "2px 2px 6px",
        }}>
          {ingredients.map(ing => (
            <IngredientCard
              key={ing.name}
              ing={ing}
              selected={selected === ing.name}
              onClick={() => selectIngredient(ing.name)}
            />
          ))}
        </div>

        {/* Right: pair rankings */}
        {selected ? (
          <PairPanel ingredient={selected} result={mapResult} loading={loadingMap} />
        ) : (
          <div style={{ ...glass, flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 14 }}>
            <div style={{ fontSize: 60 }}>🧪</div>
            <div style={{ fontWeight: 700, fontSize: 18, color: "var(--text-primary)" }}>Explore Flavor Pairings</div>
            <div style={{ fontSize: 13, color: "var(--text-muted)", textAlign: "center", maxWidth: 260, lineHeight: 1.6 }}>
              Select any ingredient card to discover its best flavor matches — then click a pair to find the ideal third ingredient
            </div>
            {ingredients.length > 0 && (
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8, marginTop: 4 }}>
                <div style={{ fontSize: 11, color: "var(--text-muted)", fontWeight: 600, letterSpacing: "0.05em", textTransform: "uppercase" }}>Quick picks</div>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "center" }}>
                  {["chocolate", "strawberry", "vanilla", "coffee", "lemon"]
                    .filter(n => ingredients.some(i => i.name === n))
                    .map(name => (
                      <button key={name} onClick={() => selectIngredient(name)}
                        style={{
                          display: "flex", alignItems: "center", gap: 6,
                          padding: "6px 14px", borderRadius: 20,
                          border: "1px solid rgba(0,102,255,0.2)",
                          background: "rgba(0,102,255,0.06)",
                          cursor: "pointer", fontSize: 12, fontWeight: 600,
                          color: "var(--accent)", transition: "all 0.12s",
                        }}
                        onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = "rgba(0,102,255,0.13)"; }}
                        onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = "rgba(0,102,255,0.06)"; }}
                      >
                        {INGREDIENT_EMOJI[name] ?? "🍽️"} {name}
                      </button>
                    ))
                  }
                </div>
              </div>
            )}
            <div style={{ display: "flex", gap: 16, marginTop: 8 }}>
              {([["5+", "Decent", "#f97316"], ["15+", "Good", "#f59e0b"], ["30+", "Excellent", "#22c55e"]] as const).map(([score, label, color]) => (
                <div key={label} style={{ display: "flex", alignItems: "center", gap: 5 }}>
                  <div style={{ width: 8, height: 8, borderRadius: "50%", background: color }} />
                  <span style={{ fontSize: 11, color: "var(--text-muted)" }}>{score} {label}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
