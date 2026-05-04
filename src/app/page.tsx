"use client";

import { useEffect, useState, useCallback } from "react";
import Image from "next/image";
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

/* ── Small thumbnail with category-color fallback (no emoji) ── */
function Thumb({ name, category, size, radius }: { name: string; category: string; size: number; radius: number }) {
  const [err, setErr] = useState(false);
  const img = KNOWN_IMAGES[name];
  const c = CATEGORY_COLOR[category] ?? "#888";
  return (
    <div style={{ width: size, height: size, borderRadius: radius, overflow: "hidden", flexShrink: 0, border: "1px solid rgba(0,0,0,0.08)" }}>
      {img && !err ? (
        <Image
          src={img}
          alt={name}
          width={size}
          height={size}
          onError={() => setErr(true)}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      ) : (
        <div style={{ width: "100%", height: "100%", background: `linear-gradient(135deg, ${c}55, ${c}22)` }} />
      )}
    </div>
  );
}

function nameHash(name: string) {
  let h = 5381;
  for (let i = 0; i < name.length; i++) h = (h * 33 ^ name.charCodeAt(i)) & 0xffffffff;
  return Math.abs(h);
}

/* ── Ingredient Card ── */

function IngredientCard({ ing, selected, onClick }: { ing: Ingredient; selected: boolean; onClick: () => void }) {
  const [hovered, setHovered] = useState(false);
  const c = CATEGORY_COLOR[ing.category] ?? "#888";
  const angle = nameHash(ing.name) % 360;

  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display: "flex", alignItems: "center", gap: 10,
        borderRadius: 10, padding: "8px 12px", cursor: "pointer",
        border: selected ? `1.5px solid ${c}99` : "1px solid rgba(255,255,255,0.08)",
        background: selected
          ? `linear-gradient(${angle}deg, ${c}2e 0%, ${c}12 100%)`
          : hovered ? "rgba(255,255,255,0.07)" : "rgba(255,255,255,0.03)",
        transition: "all 0.15s ease",
        boxShadow: selected ? `0 0 0 3px ${c}25` : "none",
      }}
    >
      <div style={{
        width: 30, height: 30, borderRadius: 8, flexShrink: 0,
        background: `linear-gradient(${angle}deg, ${c}88 0%, ${c}44 100%)`,
        border: `1px solid ${c}50`,
      }} />
      <div style={{ flex: 1, minWidth: 0, fontWeight: 600, fontSize: 13, textTransform: "capitalize", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
        {ing.name}
      </div>
      <CategoryPill cat={ing.category} />
    </div>
  );
}

/* ── Triplet Chip (one candidate) ── */
function TripletChip({ c, rank }: { c: TripletCandidate; rank: number }) {
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 7,
      background: "rgba(0,0,0,0.03)",
      border: `1px solid ${scoreColor(c.avg_score)}66`,
      borderRadius: 9, padding: "6px 10px 6px 7px",
      boxShadow: "0 1px 4px rgba(0,0,0,0.06)",
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
      background: "rgba(0,113,227,0.05)",
      border: "1px solid rgba(0,113,227,0.15)", borderTop: "none",
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
  const [hovered, setHovered] = useState(false);
  return (
    <div style={{ marginBottom: isExpanded ? 0 : 6, position: "relative" }}>
      <div
        onClick={onToggle}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        style={{
          display: "flex", alignItems: "center", gap: 10,
          padding: "10px 14px 10px 17px",
          borderRadius: isExpanded ? "10px 10px 0 0" : 10,
          background: isExpanded ? "rgba(0,113,227,0.07)" : hovered ? "rgba(0,0,0,0.04)" : "rgba(0,0,0,0.02)",
          border: `1px solid ${isExpanded ? "rgba(0,113,227,0.22)" : "rgba(0,0,0,0.06)"}`,
          borderBottom: isExpanded ? "none" : undefined,
          cursor: "pointer", transition: "all 0.12s",
          overflow: "hidden",
        }}
      >
        {/* Left accent bar — microinteraction: active state indicator */}
        <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: 3, background: isExpanded ? "var(--accent)" : hovered ? "rgba(0,113,227,0.40)" : "transparent", borderRadius: "3px 0 0 3px", transition: "background 0.15s" }} />
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
      {/* Hero header — full-bleed photo background, text only. No icon thumbnail. */}
      <div style={{ height: 148, position: "relative", flexShrink: 0, overflow: "hidden", borderRadius: "var(--radius) var(--radius) 0 0" }}>
        {img && !heroErr ? (
          <img src={img} alt={ingredient} onError={() => setHeroErr(true)}
            style={{ width: "100%", height: "100%", objectFit: "cover", filter: "brightness(0.55) saturate(1.1)", transform: "scale(1.05)", position: "absolute", inset: 0 }} />
        ) : (
          <div style={{ position: "absolute", inset: 0, background: `linear-gradient(135deg, ${c}60, ${c}20)` }} />
        )}
        {/* vignette + bottom darken so the title stays legible over the photo */}
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg, rgba(0,0,0,0.18) 0%, rgba(0,0,0,0.45) 55%, rgba(0,0,0,0.78) 100%)" }} />
        <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", justifyContent: "flex-end", padding: "16px 28px 18px" }}>
          <div style={{ fontSize: 10, color: "rgba(255,255,255,0.65)", textTransform: "uppercase", letterSpacing: "0.18em", fontWeight: 700, marginBottom: 5 }}>
            Selected Ingredient
          </div>
          <div style={{ color: "#fff", fontWeight: 900, fontSize: 32, textTransform: "capitalize", letterSpacing: "-0.03em", lineHeight: 1.05, textShadow: "0 2px 18px rgba(0,0,0,0.7)" }}>
            {ingredient}
          </div>
          {result && (
            <div style={{ color: "rgba(255,255,255,0.65)", fontSize: 12, marginTop: 9 }}>
              {result.compound_count} aromatic compounds · {result.pairings.length} flavor pairings ranked
            </div>
          )}
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
function useIsMobile() {
  const [isMobile, setIsMobile] = useState(false);
  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth < 768);
    check();
    window.addEventListener("resize", check);
    return () => window.removeEventListener("resize", check);
  }, []);
  return isMobile;
}

export default function Home() {
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [mapResult, setMapResult] = useState<MapResult | null>(null);
  const [loadingMap, setLoadingMap] = useState(false);
  const [search, setSearch] = useState("");
  const [filterCat, setFilterCat] = useState<string | null>(null);
  const categories = Array.from(new Set(ingredients.map(i => i.category))).sort();
  const filteredIngredients = ingredients.filter(ing =>
    ing.name.includes(search.toLowerCase()) && (!filterCat || ing.category === filterCat)
  );
  const isMobile = useIsMobile();

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

  const selectedImg = selected ? KNOWN_IMAGES[selected] : null;

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column", padding: "10px 12px", gap: 10, position: "relative" }}>
      {/* Full-page background image — swaps when an ingredient is selected.
           Two layered <img> would be ideal for crossfade, but simpler one-img
           with key + opacity transition reads as a clean dissolve. */}
      <div aria-hidden style={{
        position: "fixed", inset: 0, zIndex: -2,
        background: "var(--page-bg)",
      }} />
      {selectedImg && (
        <img
          key={selected}
          src={selectedImg}
          alt=""
          aria-hidden
          style={{
            position: "fixed", inset: 0, zIndex: -1,
            width: "100%", height: "100%", objectFit: "cover",
            filter: "blur(60px) brightness(1.15) saturate(0.6)",
            transform: "scale(1.12)",
            opacity: 0.18,
            animation: "bgFadeIn 0.6s ease",
          }}
        />
      )}
      <style>{`
        @keyframes bgFadeIn { from { opacity: 0 } to { opacity: 1 } }
      `}</style>
      {/* Nav */}
      <nav style={{ ...glass, display: "flex", alignItems: "center", padding: "12px 24px", gap: 14, flexShrink: 0 }}>
        {/* Logo — network graph mark */}
        <div style={{
          width: 38, height: 38, borderRadius: 11, flexShrink: 0,
          background: "linear-gradient(145deg, #0071E3 0%, #0093FF 100%)",
          display: "flex", alignItems: "center", justifyContent: "center",
          boxShadow: "0 2px 12px rgba(0,113,227,0.30)",
        }}>
          <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="11" cy="4"  r="2.6" fill="white" fillOpacity="0.95"/>
            <circle cx="3.5" cy="17" r="2.6" fill="white" fillOpacity="0.75"/>
            <circle cx="18.5" cy="17" r="2.6" fill="white" fillOpacity="0.75"/>
            <line x1="11" y1="6.6"  x2="3.5"  y2="14.4" stroke="white" strokeWidth="1.3" strokeOpacity="0.5" strokeLinecap="round"/>
            <line x1="11" y1="6.6"  x2="18.5" y2="14.4" stroke="white" strokeWidth="1.3" strokeOpacity="0.5" strokeLinecap="round"/>
            <line x1="3.5" y1="17"  x2="18.5" y2="17"   stroke="white" strokeWidth="1.3" strokeOpacity="0.28" strokeLinecap="round"/>
          </svg>
        </div>

        {/* Title + tagline */}
        <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
          <div style={{ lineHeight: 1, letterSpacing: "-0.055em", fontWeight: 900, fontSize: 22, color: "var(--text-primary)" }}>
            Pairfect
          </div>
          <div style={{ fontSize: 10.5, color: "var(--text-muted)", letterSpacing: "0.06em", textTransform: "uppercase", fontWeight: 600 }}>
            Ingredients that taste great together
          </div>
        </div>

        {/* Divider */}
        <div style={{ width: 1, height: 30, background: "rgba(0,0,0,0.10)", marginLeft: 2, flexShrink: 0 }} />

        {/* Stat badges — derived live from loaded data */}
        {ingredients.length > 0 && (
          <div style={{ display: "flex", gap: 6 }}>
            {([
              [String(ingredients.length), "ingredients"],
              [Math.round(ingredients.length * (ingredients.length - 1) / 2).toLocaleString(), "pairs"],
              [Math.round(ingredients.length * (ingredients.length - 1) * (ingredients.length - 2) / 6).toLocaleString(), "triplets"],
            ]).map(([num, label]) => (
              <div key={label} style={{
                display: "flex", flexDirection: "column", alignItems: "center",
                background: "rgba(0,0,0,0.04)", borderRadius: 8, padding: "4px 11px",
                border: "1px solid rgba(0,0,0,0.07)",
              }}>
                <span style={{ fontSize: 13, fontWeight: 800, color: "var(--accent)", lineHeight: 1.1 }}>{num}</span>
                <span style={{ fontSize: 9, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.07em", marginTop: 1 }}>{label}</span>
              </div>
            ))}
          </div>
        )}

        {/* Methodology link */}
        <a href="/about" style={{
          marginLeft: "auto", fontSize: 12, color: "var(--text-secondary)", fontWeight: 600,
          padding: "6px 13px", borderRadius: 8, textDecoration: "none",
          background: "rgba(0,0,0,0.04)", border: "1px solid rgba(0,0,0,0.08)",
        }}>Methodology ↗</a>
      </nav>

      {/* Main layout — desktop: side-by-side grid + panel.
                         mobile: panel on top, horizontal carousel at bottom. */}
      <div style={{ flex: 1, display: "flex", flexDirection: isMobile ? "column" : "row", gap: 10, overflow: "hidden" }}>
        {/* Right (or top on mobile): pair rankings */}
        <div style={{ order: isMobile ? 0 : 1, flex: 1, display: "flex", overflow: "hidden" }}>
          {selected ? (
            <PairPanel ingredient={selected} result={mapResult} loading={loadingMap} />
          ) : (
            <EmptyState ingredients={ingredients} onPick={selectIngredient} />
          )}
        </div>

        {isMobile ? (
          /* Mobile: horizontal-scroll carousel of ingredient cards at the bottom. */
          <div style={{ order: 1, flexShrink: 0, display: "flex", flexDirection: "column", gap: 8 }}>
            <input
              placeholder="Search…"
              value={search}
              onChange={e => setSearch(e.target.value)}
              style={{
                width: "100%", padding: "8px 12px", borderRadius: 10,
                border: "1px solid rgba(0,0,0,0.09)",
                background: "rgba(255,255,255,0.92)",
                backdropFilter: "blur(12px)",
                fontSize: 13, color: "var(--text-primary)",
                outline: "none",
              }}
            />
            <div style={{
              display: "flex", gap: 8, overflowX: "auto", overflowY: "hidden",
              padding: "2px 2px 8px",
              scrollSnapType: "x mandatory",
              WebkitOverflowScrolling: "touch",
            }}>
              {filteredIngredients.map(ing => (
                <div key={ing.name} style={{ width: 110, flexShrink: 0, scrollSnapAlign: "start" }}>
                  <IngredientCard
                    ing={ing}
                    selected={selected === ing.name}
                    onClick={() => selectIngredient(ing.name)}
                  />
                </div>
              ))}
            </div>
          </div>
        ) : (
          /* Desktop sidebar */
          <div style={{ order: 0, width: 440, flexShrink: 0, display: "flex", flexDirection: "column", gap: 8, overflow: "hidden" }}>
            <div style={{ position: "relative", flexShrink: 0 }}>
              <input
                placeholder="Search ingredients…"
                value={search}
                onChange={e => setSearch(e.target.value)}
                style={{
                  width: "100%", padding: "8px 36px 8px 30px", borderRadius: 10,
                  border: "1px solid rgba(0,0,0,0.09)",
                  background: "rgba(255,255,255,0.92)",
                  backdropFilter: "blur(12px)",
                  fontSize: 13, color: "var(--text-primary)",
                  outline: "none",
                  boxShadow: "0 1px 4px rgba(0,0,0,0.06)",
                }}
              />
              <svg style={{ position: "absolute", left: 11, top: "50%", transform: "translateY(-50%)", pointerEvents: "none", opacity: 0.35 }} width="14" height="14" viewBox="0 0 14 14" fill="none">
                <circle cx="6" cy="6" r="4.5" stroke="#1c1c1e" strokeWidth="1.5"/>
                <line x1="9.5" y1="9.5" x2="12.5" y2="12.5" stroke="#1c1c1e" strokeWidth="1.5" strokeLinecap="round"/>
              </svg>
              {search ? (
                <span style={{ position: "absolute", right: 10, top: "50%", transform: "translateY(-50%)", fontSize: 11, color: "var(--text-muted)", fontWeight: 600, pointerEvents: "none" }}>
                  {filteredIngredients.length}/{ingredients.length}
                </span>
              ) : (
                <span style={{ position: "absolute", right: 10, top: "50%", transform: "translateY(-50%)", fontSize: 11, color: "var(--text-muted)", pointerEvents: "none" }}>
                  ⌘K
                </span>
              )}
            </div>
            {/* Category filter tabs */}
            <div style={{ display: "flex", gap: 5, overflowX: "auto", flexShrink: 0, padding: "0 1px 2px", scrollbarWidth: "none" }}>
              <button
                onClick={() => setFilterCat(null)}
                style={{
                  padding: "4px 11px", borderRadius: 20, flexShrink: 0,
                  border: "1px solid " + (filterCat === null ? "var(--accent)" : "rgba(0,0,0,0.08)"),
                  background: filterCat === null ? "rgba(0,113,227,0.10)" : "rgba(0,0,0,0.03)",
                  color: filterCat === null ? "var(--accent)" : "var(--text-muted)",
                  fontSize: 11, fontWeight: 700, cursor: "pointer",
                  textTransform: "uppercase", letterSpacing: "0.05em",
                }}>All</button>
              {categories.map(cat => (
                <button key={cat}
                  onClick={() => setFilterCat(filterCat === cat ? null : cat)}
                  style={{
                    padding: "4px 11px", borderRadius: 20, flexShrink: 0,
                    border: "1px solid " + (filterCat === cat ? (CATEGORY_COLOR[cat] ?? "var(--accent)") + "88" : "rgba(0,0,0,0.07)"),
                    background: filterCat === cat ? (CATEGORY_COLOR[cat] ?? "#0071E3") + "18" : "rgba(0,0,0,0.03)",
                    color: filterCat === cat ? (CATEGORY_COLOR[cat] ?? "var(--accent)") : "var(--text-muted)",
                    fontSize: 11, fontWeight: 700, cursor: "pointer",
                    textTransform: "capitalize",
                  }}>{cat}</button>
              ))}
            </div>
            <div style={{
              flex: 1, overflowY: "auto", overflowX: "hidden",
              display: "flex", flexDirection: "column",
              gap: 4, padding: "2px 2px 6px",
            }}>
              {filteredIngredients.map(ing => (
                <IngredientCard
                  key={ing.name}
                  ing={ing}
                  selected={selected === ing.name}
                  onClick={() => selectIngredient(ing.name)}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function EmptyState({ ingredients, onPick }: { ingredients: Ingredient[]; onPick: (n: string) => void }) {
  return (
    <div style={{ ...glass, flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 16, padding: 32 }}>
      <div style={{
        width: 72, height: 72, borderRadius: 22,
        background: "linear-gradient(145deg, #0071E3 0%, #0093FF 100%)",
        display: "flex", alignItems: "center", justifyContent: "center",
        boxShadow: "0 4px 24px rgba(0,113,227,0.28)",
      }}>
        <svg width="38" height="38" viewBox="0 0 38 38" fill="none">
          <circle cx="19" cy="7"  r="4.5" fill="white" fillOpacity="0.95"/>
          <circle cx="6"  cy="29" r="4.5" fill="white" fillOpacity="0.7"/>
          <circle cx="32" cy="29" r="4.5" fill="white" fillOpacity="0.7"/>
          <circle cx="19" cy="23" r="3.5" fill="white" fillOpacity="0.45"/>
          <line x1="19" y1="11.5" x2="6"  y2="24.5" stroke="white" strokeWidth="1.6" strokeOpacity="0.45" strokeLinecap="round"/>
          <line x1="19" y1="11.5" x2="32" y2="24.5" stroke="white" strokeWidth="1.6" strokeOpacity="0.45" strokeLinecap="round"/>
          <line x1="6"  y1="29"   x2="32" y2="29"   stroke="white" strokeWidth="1.6" strokeOpacity="0.22" strokeLinecap="round"/>
          <line x1="19" y1="11.5" x2="19" y2="19.5" stroke="white" strokeWidth="1.6" strokeOpacity="0.35" strokeLinecap="round"/>
        </svg>
      </div>
      <div style={{ textAlign: "center", maxWidth: 560 }}>
        <div style={{ fontWeight: 900, fontSize: 28, color: "var(--text-primary)", letterSpacing: "-0.025em", lineHeight: 1.15 }}>
          Pick an ingredient to start
        </div>
        <div style={{ fontSize: 14, color: "var(--text-muted)", marginTop: 12, lineHeight: 1.7 }}>
          Pairfect tells you which ingredients taste great together — and <strong style={{ color: "var(--text-primary)", fontWeight: 700 }}>why</strong>.
          Each match is scored by how many aromatic compounds two ingredients share. The more they share, the more harmonious they feel together. No cooking experience required.
        </div>
        <div style={{ display: "flex", gap: 10, justifyContent: "center", marginTop: 16, flexWrap: "wrap" }}>
          {[
            { num: "1", label: "Tap an ingredient" },
            { num: "2", label: "See what pairs with it" },
            { num: "3", label: "Click any pair for a 3rd ingredient" },
          ].map(s => (
            <div key={s.num} style={{
              display: "flex", alignItems: "center", gap: 8,
              padding: "8px 14px 8px 8px",
              background: "rgba(0,0,0,0.03)",
              border: "1px solid rgba(0,0,0,0.07)",
              borderRadius: 999,
            }}>
              <span style={{
                width: 22, height: 22, borderRadius: "50%",
                background: "rgba(0,113,227,0.12)",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 11, fontWeight: 800, color: "var(--accent)",
              }}>{s.num}</span>
              <span style={{ fontSize: 12, color: "var(--text-secondary)", fontWeight: 600 }}>{s.label}</span>
            </div>
          ))}
        </div>
      </div>
      {ingredients.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8, marginTop: 4 }}>
          <div style={{ fontSize: 11, color: "var(--text-muted)", fontWeight: 600, letterSpacing: "0.05em", textTransform: "uppercase" }}>Quick picks</div>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "center" }}>
            {["chocolate", "strawberry", "vanilla", "coffee", "lemon"]
              .filter(n => ingredients.some(i => i.name === n))
              .map(name => {
                const ingr = ingredients.find(i => i.name === name);
                const cat = ingr?.category ?? "";
                const cc = CATEGORY_COLOR[cat] ?? "#888";
                const img = KNOWN_IMAGES[name];
                return (
                  <button key={name} onClick={() => onPick(name)}
                    style={{
                      display: "flex", alignItems: "center", gap: 8,
                      padding: "5px 14px 5px 5px", borderRadius: 20,
                      border: "1px solid rgba(0,113,227,0.28)",
                      background: "rgba(0,113,227,0.08)",
                      cursor: "pointer", fontSize: 12, fontWeight: 600,
                      color: "var(--accent)", transition: "all 0.12s",
                      textTransform: "capitalize",
                    }}
                    onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = "rgba(0,113,227,0.16)"; }}
                    onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = "rgba(0,113,227,0.08)"; }}
                  >
                    {img ? (
                      <img src={img} alt={name} style={{ width: 22, height: 22, borderRadius: "50%", objectFit: "cover", flexShrink: 0 }} />
                    ) : (
                      <span style={{ width: 22, height: 22, borderRadius: "50%", background: `linear-gradient(135deg, ${cc}55, ${cc}22)`, flexShrink: 0 }} />
                    )}
                    {name}
                  </button>
                );
              })
            }
          </div>
        </div>
      )}
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8, marginTop: 12, padding: "14px 18px", background: "rgba(0,0,0,0.03)", border: "1px solid rgba(0,0,0,0.07)", borderRadius: 12, maxWidth: 520 }}>
        <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: 700 }}>How to read the score</div>
        <div style={{ display: "flex", gap: 16, flexWrap: "wrap", justifyContent: "center" }}>
          {([
            ["30+", "Excellent", "#22c55e", "share many compounds"],
            ["15+", "Good", "#f59e0b", "share several"],
            ["5+", "Decent", "#f97316", "share a few"],
            ["<5", "Unlikely", "#94a3b8", "share little"],
          ] as const).map(([score, label, color, desc]) => (
            <div key={label} style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <div style={{ width: 8, height: 8, borderRadius: "50%", background: color }} />
              <span style={{ fontSize: 11, color: "var(--text-secondary)", fontWeight: 700 }}>{score} {label}</span>
              <span style={{ fontSize: 10, color: "var(--text-muted)" }}>· {desc}</span>
            </div>
          ))}
        </div>
      </div>
      <div style={{ marginTop: 14, fontSize: 11, color: "var(--text-muted)", textAlign: "center", maxWidth: 520, lineHeight: 1.6 }}>
        Pairings are based on shared aromatic compounds (Jaccard similarity) using flavor chemistry research. Not for allergen, dietary, or medical advice. <a href="/about" style={{ color: "var(--accent)", textDecoration: "none", fontWeight: 600 }}>Learn how it works ↗</a>
      </div>
    </div>
  );
}
