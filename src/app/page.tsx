"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import dynamic from "next/dynamic";
import { INGREDIENT_EMOJI } from "@/lib/emojis";

const FlavorGraph = dynamic(() => import("@/components/FlavorGraph"), { ssr: false });

/* ── Types ── */
interface Ingredient { name: string; category: string }
interface Pairing { name: string; category: string; score: number; label: string; shared_count: number; shared_compounds: string[] }
interface MapResult { ingredient: string; category: string; compound_count: number; pairings: Pairing[] }
interface Pair { a: string; b: string; a_category: string; b_category: string; score: number; label: string; shared_count: number; shared_compounds: string[] }
interface Triplet { a: string; b: string; c: string; a_category: string; b_category: string; c_category: string; shared_count: number; shared_compounds: string[]; avg_pair_score: number }

/* ── Shared constants ── */
const CATEGORY_COLOR: Record<string, string> = {
  confection: "#c97a3c", dairy: "#d4a843", fruit: "#5cb85c",
  beverage: "#7b68ee", spice: "#e07b39", meat: "#c0392b",
  seafood: "#2980b9", fungi: "#8e6c3e", vegetable: "#27ae60",
  herb: "#1abc9c", floral: "#d46db3",
};
function scoreColor(s: number) { return s >= 30 ? "#22c55e" : s >= 15 ? "#f59e0b" : s >= 5 ? "#f97316" : "#94a3b8"; }
function scoreLabel(s: number) { return s >= 30 ? "Excellent" : s >= 15 ? "Good" : s >= 5 ? "Decent" : "Unlikely"; }

/* ── Glass card style ── */
const glass: React.CSSProperties = {
  background: "var(--glass-bg)",
  backdropFilter: "blur(20px)",
  WebkitBackdropFilter: "blur(20px)",
  border: "1px solid var(--glass-border)",
  borderRadius: "var(--radius)",
  boxShadow: "var(--glass-shadow)",
};

/* ── Pill badge ── */
function CategoryPill({ cat }: { cat: string }) {
  const c = CATEGORY_COLOR[cat] ?? "#888";
  return (
    <span style={{ background: c + "20", color: c, border: `1px solid ${c}40`, borderRadius: 20, padding: "1px 8px", fontSize: 11, fontWeight: 600 }}>
      {cat}
    </span>
  );
}

/* ── Score badge ── */
function ScoreBadge({ score }: { score: number }) {
  return (
    <span style={{ background: scoreColor(score) + "22", color: scoreColor(score), border: `1px solid ${scoreColor(score)}44`, borderRadius: 20, padding: "2px 10px", fontSize: 12, fontWeight: 700 }}>
      {score} <span style={{ fontWeight: 400, opacity: 0.8 }}>{scoreLabel(score)}</span>
    </span>
  );
}

/* ══════════════════════════════════
   EXPLORE TAB
══════════════════════════════════ */
function ExploreTab() {
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [selected, setSelected] = useState("");
  const [result, setResult] = useState<MapResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [minScore, setMinScore] = useState(0);
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetch("/api/ingredients").then(r => r.json()).then(d => setIngredients(d.ingredients ?? []));
  }, []);

  const loadMap = useCallback(async (name: string) => {
    setLoading(true); setResult(null);
    const res = await fetch(`/api/map?a=${encodeURIComponent(name)}`);
    const data = await res.json();
    setLoading(false);
    if (res.ok) setResult(data);
  }, []);

  const grouped = ingredients
    .filter(i => i.name.includes(search.toLowerCase()))
    .reduce<Record<string, Ingredient[]>>((acc, ing) => { (acc[ing.category] ??= []).push(ing); return acc; }, {});

  return (
    <div style={{ display: "flex", flex: 1, gap: 16, overflow: "hidden" }}>
      {/* Sidebar */}
      <aside style={{ ...glass, width: 220, flexShrink: 0, display: "flex", flexDirection: "column", overflow: "hidden" }}>
        <div style={{ padding: "14px 14px 10px" }}>
          <input
            placeholder="Search…"
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{
              width: "100%", padding: "7px 10px", borderRadius: 8,
              border: "1px solid rgba(100,80,200,0.15)",
              background: "rgba(255,255,255,0.5)",
              fontSize: 13, color: "var(--text-primary)",
              outline: "none",
            }}
          />
        </div>
        <div style={{ flex: 1, overflowY: "auto", padding: "0 8px 12px" }}>
          {Object.entries(grouped).sort().map(([cat, items]) => (
            <div key={cat} style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.1em", padding: "4px 6px" }}>{cat}</div>
              {items.map(ing => {
                const isActive = ing.name === selected;
                const c = CATEGORY_COLOR[ing.category] ?? "#888";
                return (
                  <button key={ing.name} onClick={() => { setSelected(ing.name); loadMap(ing.name); }}
                    style={{
                      display: "flex", alignItems: "center", gap: 8,
                      width: "100%", padding: "7px 8px", borderRadius: 8,
                      background: isActive ? c + "20" : "transparent",
                      border: "none", color: isActive ? c : "var(--text-secondary)",
                      cursor: "pointer", textAlign: "left", transition: "all 0.1s",
                    }}>
                    <span style={{ fontSize: 16 }}>{INGREDIENT_EMOJI[ing.name] ?? "🍽️"}</span>
                    <span style={{ fontSize: 13, fontWeight: isActive ? 600 : 400, textTransform: "capitalize" }}>{ing.name}</span>
                  </button>
                );
              })}
            </div>
          ))}
        </div>
      </aside>

      {/* Graph panel */}
      <div style={{ ...glass, flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
        {/* toolbar */}
        {result && (
          <div style={{ display: "flex", alignItems: "center", gap: 16, padding: "12px 18px", borderBottom: "1px solid var(--glass-border)", flexShrink: 0 }}>
            <span style={{ fontSize: 20 }}>{INGREDIENT_EMOJI[result.ingredient]}</span>
            <span style={{ fontWeight: 700, fontSize: 15, textTransform: "capitalize" }}>{result.ingredient}</span>
            <span style={{ color: "var(--text-muted)", fontSize: 12 }}>
              {result.compound_count} compounds · {result.pairings.filter(p => p.score >= minScore).length} pairings
            </span>
            <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ fontSize: 12, color: "var(--text-muted)" }}>Min score</span>
              <input type="range" min={0} max={35} step={5} value={minScore} onChange={e => setMinScore(+e.target.value)}
                style={{ width: 90, accentColor: "var(--accent)" }} />
              <span style={{ fontSize: 12, color: "var(--accent)", fontWeight: 700, minWidth: 20 }}>{minScore}</span>
            </div>
          </div>
        )}
        <div style={{ flex: 1, overflow: "hidden", borderRadius: "0 0 var(--radius) var(--radius)" }}>
          {!result && !loading && (
            <div style={{ height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", color: "var(--text-muted)", gap: 12 }}>
              <div style={{ fontSize: 52 }}>🧪</div>
              <div style={{ fontSize: 14 }}>Select an ingredient to explore its flavor connections</div>
            </div>
          )}
          {loading && (
            <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-muted)", fontSize: 14 }}>
              Calculating flavor graph…
            </div>
          )}
          {result && !loading && <FlavorGraph result={result} minScore={minScore} light />}
        </div>
      </div>
    </div>
  );
}

/* ══════════════════════════════════
   ALL PAIRS TAB
══════════════════════════════════ */
function PairsTab() {
  const [pairs, setPairs] = useState<Pair[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [minScore, setMinScore] = useState(0);
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  useEffect(() => {
    fetch("/api/rankings").then(r => r.json()).then(d => { setPairs(d.pairs ?? []); setLoading(false); });
  }, []);

  const filtered = pairs.filter(p =>
    p.score >= minScore &&
    (search === "" || p.a.includes(search) || p.b.includes(search))
  );

  return (
    <div style={{ ...glass, flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
      {/* toolbar */}
      <div style={{ display: "flex", gap: 12, padding: "14px 18px", borderBottom: "1px solid var(--glass-border)", flexShrink: 0, flexWrap: "wrap", alignItems: "center" }}>
        <input placeholder="Search ingredient…" value={search} onChange={e => setSearch(e.target.value.toLowerCase())}
          style={{ padding: "7px 12px", borderRadius: 8, border: "1px solid rgba(100,80,200,0.15)", background: "rgba(255,255,255,0.5)", fontSize: 13, color: "var(--text-primary)", outline: "none", width: 180 }} />
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 12, color: "var(--text-muted)" }}>Min score</span>
          <input type="range" min={0} max={35} step={5} value={minScore} onChange={e => { setMinScore(+e.target.value); setExpandedIdx(null); }}
            style={{ width: 100, accentColor: "var(--accent)" }} />
          <span style={{ fontSize: 12, color: "var(--accent)", fontWeight: 700 }}>{minScore}</span>
        </div>
        <span style={{ marginLeft: "auto", fontSize: 12, color: "var(--text-muted)" }}>
          {loading ? "Loading…" : `${filtered.length} pairs`}
        </span>
      </div>

      {/* table */}
      <div style={{ flex: 1, overflowY: "auto", padding: "8px 18px 18px" }}>
        {filtered.map((p, i) => (
          <div key={i} onClick={() => setExpandedIdx(expandedIdx === i ? null : i)}
            style={{
              borderRadius: 10, padding: "12px 16px", marginBottom: 6,
              background: expandedIdx === i ? "rgba(255,255,255,0.8)" : "rgba(255,255,255,0.4)",
              border: `1px solid ${expandedIdx === i ? "rgba(0,102,255,0.25)" : "rgba(255,255,255,0.7)"}`,
              cursor: "pointer", transition: "background 0.1s",
            }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
              <span style={{ fontSize: 20 }}>{INGREDIENT_EMOJI[p.a] ?? "🍽️"}</span>
              <span style={{ fontWeight: 600, fontSize: 14, textTransform: "capitalize" }}>{p.a}</span>
              <CategoryPill cat={p.a_category} />
              <span style={{ color: "var(--text-muted)", fontSize: 14 }}>+</span>
              <span style={{ fontSize: 20 }}>{INGREDIENT_EMOJI[p.b] ?? "🍽️"}</span>
              <span style={{ fontWeight: 600, fontSize: 14, textTransform: "capitalize" }}>{p.b}</span>
              <CategoryPill cat={p.b_category} />
              <div style={{ marginLeft: "auto" }}>
                <ScoreBadge score={p.score} />
              </div>
            </div>
            {expandedIdx === i && (
              <div style={{ marginTop: 12, paddingTop: 12, borderTop: "1px solid rgba(100,80,200,0.1)" }}>
                <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 8 }}>
                  {p.shared_count} shared compound{p.shared_count !== 1 ? "s" : ""}
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                  {p.shared_compounds.map(c => (
                    <span key={c} style={{ background: "#0066ff15", color: "#0066ff", border: "1px solid #0066ff30", borderRadius: 5, padding: "2px 8px", fontSize: 12 }}>{c}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ══════════════════════════════════
   TRIPLETS TAB
══════════════════════════════════ */
function TripletsTab() {
  const [triplets, setTriplets] = useState<Triplet[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  useEffect(() => {
    fetch("/api/triplets?limit=60").then(r => r.json()).then(d => { setTriplets(d.triplets ?? []); setLoading(false); });
  }, []);

  return (
    <div style={{ ...glass, flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
      <div style={{ padding: "14px 18px", borderBottom: "1px solid var(--glass-border)", flexShrink: 0 }}>
        <span style={{ fontWeight: 600, fontSize: 14 }}>Top Flavor Triplets</span>
        <span style={{ color: "var(--text-muted)", fontSize: 12, marginLeft: 8 }}>
          {loading ? "Computing…" : `Top ${triplets.length} of 1,140 combinations`}
        </span>
      </div>
      <div style={{ flex: 1, overflowY: "auto", padding: "8px 18px 18px", display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: 10, alignContent: "start" }}>
        {triplets.map((t, i) => (
          <div key={i} onClick={() => setExpandedIdx(expandedIdx === i ? null : i)}
            style={{
              borderRadius: 10, padding: "14px 16px",
              background: expandedIdx === i ? "rgba(255,255,255,0.85)" : "rgba(255,255,255,0.5)",
              border: `1px solid ${expandedIdx === i ? "rgba(0,102,255,0.25)" : "rgba(255,255,255,0.7)"}`,
              cursor: "pointer", transition: "background 0.1s",
            }}>
            <div style={{ display: "flex", gap: 4, marginBottom: 8 }}>
              {[t.a, t.b, t.c].map((name, idx) => (
                <span key={idx} style={{ fontSize: 20 }}>{INGREDIENT_EMOJI[name] ?? "🍽️"}</span>
              ))}
              <div style={{ marginLeft: "auto" }}>
                <ScoreBadge score={t.avg_pair_score} />
              </div>
            </div>
            <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)", textTransform: "capitalize", marginBottom: 4 }}>
              {t.a} · {t.b} · {t.c}
            </div>
            <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
              <CategoryPill cat={t.a_category} />
              <CategoryPill cat={t.b_category} />
              <CategoryPill cat={t.c_category} />
            </div>
            {expandedIdx === i && (
              <div style={{ marginTop: 12, paddingTop: 12, borderTop: "1px solid rgba(100,80,200,0.1)" }}>
                <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 8 }}>
                  {t.shared_count > 0 ? `${t.shared_count} shared by all three` : "No compound shared by all three — paired by avg score"}
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                  {t.shared_compounds.map(c => (
                    <span key={c} style={{ background: "#0066ff15", color: "#0066ff", border: "1px solid #0066ff30", borderRadius: 5, padding: "2px 8px", fontSize: 12 }}>{c}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ══════════════════════════════════
   ROOT PAGE
══════════════════════════════════ */
type Tab = "explore" | "pairs" | "triplets";

export default function Home() {
  const [tab, setTab] = useState<Tab>("explore");

  const navBtn = (id: Tab, label: string) => (
    <button onClick={() => setTab(id)} style={{
      padding: "7px 18px", borderRadius: 20, border: "none", cursor: "pointer", fontSize: 13, fontWeight: 600,
      background: tab === id ? "var(--accent)" : "transparent",
      color: tab === id ? "#fff" : "var(--text-secondary)",
      transition: "all 0.15s",
    }}>{label}</button>
  );

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column", padding: 16, gap: 12 }}>
      {/* Nav */}
      <nav style={{ ...glass, display: "flex", alignItems: "center", padding: "10px 20px", gap: 8, flexShrink: 0 }}>
        <div style={{ marginRight: 12 }}>
          <span style={{ fontWeight: 800, fontSize: 17, color: "var(--accent)", letterSpacing: "-0.02em" }}>FlavorGraph</span>
          <span style={{ fontSize: 11, color: "var(--text-muted)", marginLeft: 8 }}>Flavor chemistry pairing</span>
        </div>
        <div style={{ display: "flex", gap: 4, background: "rgba(100,80,200,0.07)", borderRadius: 24, padding: "3px" }}>
          {navBtn("explore", "🔬 Explore")}
          {navBtn("pairs", "📊 All Pairs")}
          {navBtn("triplets", "✨ Triplets")}
        </div>
        <div style={{ marginLeft: "auto", fontSize: 12, color: "var(--text-muted)" }}>
          20 ingredients · 190 pairs · 1,140 triplets
        </div>
      </nav>

      {/* Content */}
      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        {tab === "explore"  && <ExploreTab />}
        {tab === "pairs"    && <PairsTab />}
        {tab === "triplets" && <TripletsTab />}
      </div>
    </div>
  );
}
