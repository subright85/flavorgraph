"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import * as d3 from "d3";
import { INGREDIENT_EMOJI } from "@/lib/emojis";

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

interface GraphNode extends d3.SimulationNodeDatum {
  id: string;
  name: string;
  category: string;
  score: number;
  shared_count: number;
  shared_compounds: string[];
  isCenter: boolean;
}

interface GraphLink extends d3.SimulationLinkDatum<GraphNode> {
  score: number;
  shared_count: number;
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
  return "#334155";
}

function scoreLabel(score: number) {
  if (score >= 30) return "Excellent";
  if (score >= 15) return "Good";
  if (score >= 5)  return "Decent";
  return "Unlikely";
}

interface Props {
  result: MapResult;
  minScore: number;
  light?: boolean;
}

export default function FlavorGraph({ result, minScore, light = false }: Props) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selected, setSelected] = useState<GraphNode | null>(null);
  const [tooltip, setTooltip] = useState<{ x: number; y: number; node: GraphNode } | null>(null);
  const simRef = useRef<d3.Simulation<GraphNode, GraphLink> | null>(null);

  const buildGraph = useCallback(() => {
    const svg = svgRef.current;
    if (!svg) return;

    const W = svg.clientWidth || 600;
    const H = svg.clientHeight || 520;

    d3.select(svg).selectAll("*").remove();

    const visiblePairings = result.pairings.filter(p => p.score >= minScore);

    const nodes: GraphNode[] = [
      {
        id: result.ingredient,
        name: result.ingredient,
        category: result.category,
        score: 100,
        shared_count: result.compound_count,
        shared_compounds: [],
        isCenter: true,
        x: W / 2,
        y: H / 2,
      },
      ...visiblePairings.map(p => ({
        id: p.name,
        name: p.name,
        category: p.category,
        score: p.score,
        shared_count: p.shared_count,
        shared_compounds: p.shared_compounds,
        isCenter: false,
      })),
    ];

    const links: GraphLink[] = visiblePairings.map(p => ({
      source: result.ingredient,
      target: p.name,
      score: p.score,
      shared_count: p.shared_count,
    }));

    const root = d3.select(svg);

    // defs for glow filter
    const defs = root.append("defs");
    const filter = defs.append("filter").attr("id", "glow");
    filter.append("feGaussianBlur").attr("stdDeviation", "3").attr("result", "coloredBlur");
    const feMerge = filter.append("feMerge");
    feMerge.append("feMergeNode").attr("in", "coloredBlur");
    feMerge.append("feMergeNode").attr("in", "SourceGraphic");

    const g = root.append("g");

    // zoom
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.4, 2.5])
      .on("zoom", (e) => g.attr("transform", e.transform));
    root.call(zoom);

    const sim = d3.forceSimulation<GraphNode>(nodes)
      .force("link", d3.forceLink<GraphNode, GraphLink>(links)
        .id(d => d.id)
        .distance(d => Math.max(80, 280 - d.score * 2.2))
        .strength(0.6)
      )
      .force("charge", d3.forceManyBody().strength(-180))
      .force("center", d3.forceCenter(W / 2, H / 2))
      .force("collision", d3.forceCollide<GraphNode>(d => d.isCenter ? 45 : 26));

    simRef.current = sim;

    // links
    const linkEl = g.append("g").selectAll<SVGLineElement, GraphLink>("line")
      .data(links)
      .join("line")
      .attr("stroke", d => scoreColor(d.score))
      .attr("stroke-opacity", d => Math.max(0.15, d.score / 100))
      .attr("stroke-width", d => Math.max(1, d.shared_count * 0.9));

    // node groups
    const nodeEl = g.append("g").selectAll<SVGGElement, GraphNode>("g")
      .data(nodes)
      .join("g")
      .style("cursor", "pointer")
      .call(
        d3.drag<SVGGElement, GraphNode>()
          .on("start", (e, d) => { if (!e.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
          .on("drag", (e, d) => { d.fx = e.x; d.fy = e.y; })
          .on("end", (e, d) => { if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null; })
      )
      .on("click", (_, d) => setSelected(prev => prev?.id === d.id ? null : d))
      .on("mouseenter", (e, d) => {
        if (d.isCenter) return;
        const rect = svg.getBoundingClientRect();
        setTooltip({ x: e.clientX - rect.left, y: e.clientY - rect.top, node: d });
      })
      .on("mouseleave", () => setTooltip(null));

    // circles
    nodeEl.append("circle")
      .attr("r", d => d.isCenter ? 38 : 18 + (d.score / 100) * 10)
      .attr("fill", d => d.isCenter
        ? (light ? "rgba(255,255,255,0.95)" : "#fff")
        : (CATEGORY_COLOR[d.category] ?? "#888") + (light ? "28" : "33"))
      .attr("stroke", d => d.isCenter
        ? (light ? "#0066ff" : "#fff")
        : CATEGORY_COLOR[d.category] ?? "#888")
      .attr("stroke-width", d => d.isCenter ? 2.5 : 1.5)
      .style("filter", d => d.isCenter ? "url(#glow)" : "none");

    // emoji text
    nodeEl.append("text")
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "central")
      .attr("font-size", d => d.isCenter ? "26px" : "16px")
      .attr("dy", d => d.isCenter ? "-4px" : "0px")
      .style("user-select", "none")
      .text(d => INGREDIENT_EMOJI[d.name] ?? "🍽️");

    // name label below center
    nodeEl.filter(d => d.isCenter).append("text")
      .attr("text-anchor", "middle")
      .attr("dy", "20px")
      .attr("font-size", "9px")
      .attr("fill", "#999")
      .style("user-select", "none")
      .text(d => d.name);

    // score badge for non-center
    nodeEl.filter(d => !d.isCenter).append("text")
      .attr("text-anchor", "middle")
      .attr("dy", "32px")
      .attr("font-size", "10px")
      .attr("fill", d => scoreColor(d.score))
      .attr("font-weight", "600")
      .style("user-select", "none")
      .text(d => d.score);

    sim.on("tick", () => {
      linkEl
        .attr("x1", d => (d.source as GraphNode).x ?? 0)
        .attr("y1", d => (d.source as GraphNode).y ?? 0)
        .attr("x2", d => (d.target as GraphNode).x ?? 0)
        .attr("y2", d => (d.target as GraphNode).y ?? 0);
      nodeEl.attr("transform", d => `translate(${d.x ?? 0},${d.y ?? 0})`);
    });

    return () => { sim.stop(); };
  }, [result, minScore]);

  useEffect(() => {
    const cleanup = buildGraph();
    return cleanup;
  }, [buildGraph]);

  return (
    <div style={{ position: "relative", width: "100%", height: "100%" }}>
      <svg
        ref={svgRef}
        style={{ width: "100%", height: "100%", background: "transparent", borderRadius: 12 }}
      />

      {/* tooltip */}
      {tooltip && (
        <div style={{
          position: "absolute", left: tooltip.x + 12, top: tooltip.y - 10,
          background: light ? "rgba(255,255,255,0.95)" : "#1c1c1f",
          border: light ? "1px solid rgba(100,80,200,0.15)" : "1px solid #333",
          borderRadius: 8, padding: "8px 12px", fontSize: 13, pointerEvents: "none",
          zIndex: 10, minWidth: 160,
          boxShadow: "0 4px 20px rgba(80,60,120,0.12)",
          color: light ? "#1a1a2e" : "#e8e8ea",
        }}>
          <div style={{ fontWeight: 600, marginBottom: 2, textTransform: "capitalize" }}>
            {INGREDIENT_EMOJI[tooltip.node.name]} {tooltip.node.name}
          </div>
          <div style={{ color: scoreColor(tooltip.node.score), fontSize: 12 }}>
            {tooltip.node.score} · {scoreLabel(tooltip.node.score)}
          </div>
          <div style={{ color: light ? "#9898b8" : "#666", fontSize: 11, marginTop: 2 }}>
            {tooltip.node.shared_count} shared compound{tooltip.node.shared_count !== 1 ? "s" : ""}
          </div>
        </div>
      )}

      {/* selected detail panel */}
      {selected && !selected.isCenter && (
        <div style={{
          position: "absolute", bottom: 12, left: 12, right: 12,
          background: light ? "rgba(255,255,255,0.9)" : "#1c1c1f",
          border: `1px solid ${scoreColor(selected.score)}44`,
          borderRadius: 10, padding: "14px 16px",
          backdropFilter: light ? "blur(12px)" : "none",
          color: light ? "#1a1a2e" : "#e8e8ea",
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
            <div style={{ fontWeight: 600, fontSize: 15, textTransform: "capitalize" }}>
              {INGREDIENT_EMOJI[selected.name]} {selected.name}
              <span style={{ marginLeft: 8, fontSize: 12, color: "#666" }}>{selected.category}</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ fontSize: 18, fontWeight: 700, color: scoreColor(selected.score) }}>
                {selected.score}
              </span>
              <span style={{ fontSize: 11, color: "#666" }}>{scoreLabel(selected.score)}</span>
              <button onClick={() => setSelected(null)} style={{
                background: "none", border: "none", color: "#555", cursor: "pointer", fontSize: 16, padding: "0 4px",
              }}>×</button>
            </div>
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {selected.shared_count === 0
              ? <span style={{ color: "#444", fontSize: 13 }}>No shared compounds</span>
              : selected.shared_compounds.map(c => (
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
}
