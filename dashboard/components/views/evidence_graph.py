"""Interactive evidence lineage graph built from the active scan findings."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import PurePath
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from ..theme import THEME, nova_kpi


RISK_COLORS = {
    "SAFE": THEME["neon_green"],
    "PARTIAL": THEME["neon_orange"],
    "VULNERABLE": THEME["neon_red"],
    "CRITICAL": THEME["neon_red"],
}


def _value(finding: dict[str, Any], key: str, fallback: str = "UNKNOWN") -> str:
    """Read API and display-cased finding fields consistently."""
    return str(finding.get(key) or finding.get(key.replace("_", " ").title()) or fallback)


def _build_graph(findings: list[dict[str, Any]]) -> tuple[list[dict[str, str]], list[dict[str, str]], set[str]]:
    """Create the file → evidence → algorithm graph for selected findings."""
    nodes: list[dict[str, str]] = []
    edges: list[dict[str, str]] = []
    seen_files: set[str] = set()
    seen_algorithms: set[str] = set()
    critical_files: set[str] = set()

    for index, finding in enumerate(findings, start=1):
        file_path = _value(finding, "file_path", "unknown file")
        algorithm = _value(finding, "algorithm").upper()
        risk = _value(finding, "quantum_risk").upper()
        severity = _value(finding, "severity").upper()
        line_number = _value(finding, "line_number", "?")
        file_id, algorithm_id, finding_id = f"file:{file_path}", f"algorithm:{algorithm}", f"finding:{index}"

        if file_path not in seen_files:
            seen_files.add(file_path)
            nodes.append({"id": file_id, "label": PurePath(file_path).name or file_path,
                          "type": "File", "color": THEME["neon_blue"], "detail": file_path})
        if algorithm not in seen_algorithms:
            seen_algorithms.add(algorithm)
            nodes.append({"id": algorithm_id, "label": algorithm, "type": "Algorithm",
                          "color": THEME["neon_pink"], "detail": f"Algorithm: {algorithm}"})

        nodes.append({"id": finding_id, "label": f"{algorithm} · L{line_number}", "type": "Evidence",
                      "color": RISK_COLORS.get(risk, THEME["text_muted"]),
                      "detail": f"{algorithm} at {file_path}:{line_number} · {risk} / {severity}"})
        edges.extend(({"source": file_id, "target": finding_id}, {"source": finding_id, "target": algorithm_id}))
        if risk in {"VULNERABLE", "CRITICAL"} or severity == "CRITICAL":
            critical_files.add(file_path)
    return nodes, edges, critical_files


def _render_force_graph(nodes: list[dict[str, str]], edges: list[dict[str, str]]) -> None:
    """Render a draggable, zoomable force graph with no external frontend dependency."""
    graph_data = json.dumps({"nodes": nodes, "edges": edges}).replace("</", "<\\/")
    html = """<!doctype html><html><head><style>
html,body{height:100%;margin:0;background:#172033;font-family:Inter,system-ui,sans-serif;overflow:hidden}#graph{width:100%;height:100%;display:block;background:radial-gradient(circle at 50% 40%,#1e2d4b 0,#172033 48%,#0f172a 100%)}.edge{stroke:#64748b;stroke-opacity:.4;stroke-width:1.35}.node{cursor:grab}.node:active{cursor:grabbing}.label{fill:#e2e8f0;font-size:11px;font-weight:650;paint-order:stroke;stroke:#172033;stroke-width:4px;stroke-linejoin:round;pointer-events:none}#tip{position:fixed;display:none;max-width:290px;padding:9px 11px;border:1px solid #475569;border-radius:8px;background:#0b1220ef;color:#e2e8f0;font-size:12px;line-height:1.35;pointer-events:none;z-index:2}#hint{position:fixed;right:15px;bottom:12px;color:#94a3b8;font-size:11px;pointer-events:none}#legend{position:fixed;top:14px;left:14px;padding:10px 12px;border:1px solid #334155;border-radius:10px;background:#0b1220df;color:#cbd5e1;font-size:11px;line-height:1.8;pointer-events:none;box-shadow:0 8px 18px #0005}.legend-title{font-size:10px;font-weight:800;letter-spacing:1.2px;color:#f8fafc}.swatch{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:7px}.file{background:#60a5fa}.algorithm{background:#c084fc}.safe{background:#4ade80}.partial{background:#fbbf24}.vulnerable{background:#f87171}
</style></head><body><svg id="graph" aria-label="Interactive evidence lineage graph"><g id="viewport"><g id="links"></g><g id="nodes"></g></g></svg><div id="tip"></div><div id="legend"><div class="legend-title">NODE LEGEND</div><div><span class="swatch file"></span>File</div><div><span class="swatch algorithm"></span>Algorithm</div><div><span class="swatch safe"></span>Safe evidence</div><div><span class="swatch partial"></span>Partial evidence</div><div><span class="swatch vulnerable"></span>Vulnerable / critical evidence</div></div><div id="hint">Scroll to zoom · drag nodes to inspect lineages</div><script>
const data=__GRAPH_DATA__,svg=document.getElementById('graph'),viewport=document.getElementById('viewport'),tip=document.getElementById('tip');let width=900,height=590,scale=1,panX=0,panY=0,dragged=null;
const nodes=data.nodes.map((n,i)=>({...n,x:100+(i*79)%720,y:80+(i*131)%430,vx:0,vy:0})),byId=new Map(nodes.map(n=>[n.id,n])),edges=data.edges.map(e=>({...e,source:byId.get(e.source),target:byId.get(e.target)})),linkLayer=document.getElementById('links'),nodeLayer=document.getElementById('nodes');
const linkEls=edges.map(e=>{const line=document.createElementNS('http://www.w3.org/2000/svg','line');line.setAttribute('class','edge');linkLayer.appendChild(line);return{e,line}}),nodeEls=nodes.map(n=>{const g=document.createElementNS('http://www.w3.org/2000/svg','g'),c=document.createElementNS('http://www.w3.org/2000/svg','circle'),t=document.createElementNS('http://www.w3.org/2000/svg','text');g.setAttribute('class','node');c.setAttribute('r',n.type==='File'?12:n.type==='Algorithm'?14:8);c.setAttribute('fill',n.color);c.setAttribute('stroke','#e2e8f0');c.setAttribute('stroke-opacity','.35');c.setAttribute('stroke-width','1');t.setAttribute('class','label');t.setAttribute('x','15');t.setAttribute('y','4');t.textContent=n.label.length>28?n.label.slice(0,27)+'…':n.label;g.append(c,t);g.addEventListener('mouseenter',e=>{tip.textContent=n.type+' — '+n.detail;tip.style.display='block';tip.style.left=(e.clientX+14)+'px';tip.style.top=(e.clientY+14)+'px'});g.addEventListener('mouseleave',()=>tip.style.display='none');g.addEventListener('pointerdown',e=>{dragged=n;g.setPointerCapture(e.pointerId);e.stopPropagation()});g.addEventListener('pointermove',e=>{if(dragged){const p=toGraph(e);dragged.x=p.x;dragged.y=p.y;dragged.vx=dragged.vy=0}});g.addEventListener('pointerup',()=>dragged=null);nodeLayer.appendChild(g);return{n,g}});
function toGraph(e){const r=svg.getBoundingClientRect();return{x:(e.clientX-r.left-panX)/scale,y:(e.clientY-r.top-panY)/scale}}function transform(){viewport.setAttribute('transform',`translate(${panX} ${panY}) scale(${scale})`)}function resize(){const r=svg.getBoundingClientRect();width=r.width;height=r.height}new ResizeObserver(resize).observe(svg);resize();
function tick(){for(const e of edges){const dx=e.target.x-e.source.x,dy=e.target.y-e.source.y,d=Math.max(1,Math.hypot(dx,dy)),f=(d-145)*.003,fx=dx/d*f,fy=dy/d*f;if(e.source!==dragged){e.source.vx+=fx;e.source.vy+=fy}if(e.target!==dragged){e.target.vx-=fx;e.target.vy-=fy}}for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++){const a=nodes[i],b=nodes[j],dx=b.x-a.x,dy=b.y-a.y,d2=Math.max(180,dx*dx+dy*dy),f=900/d2;a.vx-=dx*f*.01;a.vy-=dy*f*.01;b.vx+=dx*f*.01;b.vy+=dy*f*.01}for(const n of nodes)if(n!==dragged){n.vx+=(width/2-n.x)*.0009;n.vy+=(height/2-n.y)*.0009;n.vx*=.86;n.vy*=.86;n.x=Math.max(25,Math.min(width-25,n.x+n.vx));n.y=Math.max(25,Math.min(height-25,n.y+n.vy))}for(const i of linkEls){i.line.setAttribute('x1',i.e.source.x);i.line.setAttribute('y1',i.e.source.y);i.line.setAttribute('x2',i.e.target.x);i.line.setAttribute('y2',i.e.target.y)}for(const i of nodeEls)i.g.setAttribute('transform',`translate(${i.n.x} ${i.n.y})`);requestAnimationFrame(tick)}tick();
svg.addEventListener('wheel',e=>{e.preventDefault();scale=Math.max(.45,Math.min(2.8,scale*(e.deltaY<0?1.12:.89)));transform()},{passive:false});let moving=false,last={x:0,y:0};svg.addEventListener('pointerdown',e=>{if(e.target===svg){moving=true;last={x:e.clientX,y:e.clientY}}});svg.addEventListener('pointermove',e=>{if(moving){panX+=e.clientX-last.x;panY+=e.clientY-last.y;last={x:e.clientX,y:e.clientY};transform()}});svg.addEventListener('pointerup',()=>moving=false);
</script></body></html>""".replace("__GRAPH_DATA__", graph_data)
    components.html(html, height=590, scrolling=False)


def render_evidence_graph(results: dict[str, Any]):
    """Render live lineage evidence and controls for the current scan."""
    findings = results.get("findings", [])
    risks = sorted({_value(finding, "quantum_risk").upper() for finding in findings})
    selected_risks = st.multiselect("Show evidence by quantum risk", options=risks, default=risks,
                                  key="evidence_graph_risk_filter", help="Filtering changes the graph and graph metrics.")
    visible_findings = [f for f in findings if _value(f, "quantum_risk").upper() in selected_risks]
    nodes, edges, critical_files = _build_graph(visible_findings)
    degree = Counter(edge["source"] for edge in edges) + Counter(edge["target"] for edge in edges)
    hubs = sum(1 for node in nodes if degree[node["id"]] >= 3)

    st.markdown(f"""<div style="margin-bottom:20px"><div style="color:{THEME['text_muted']};font-size:.75rem;font-weight:800;text-transform:uppercase;letter-spacing:2px">Lineage & Dependency</div><div style="color:#fff;font-size:2.2rem;font-weight:800;letter-spacing:-1.5px;margin-top:5px">Evidence <span style="color:{THEME['neon_purple']}">Relationships</span></div><div style="color:{THEME['text_muted']};margin-top:7px">Live file → evidence → algorithm lineage from the active scan.</div></div>""", unsafe_allow_html=True)
    k1,k2,k3,k4=st.columns(4)
    with k1: nova_kpi("Total Nodes", f"{len(nodes):,}", color=THEME["neon_blue"])
    with k2: nova_kpi("Key Lineages", f"{len(visible_findings):,}", color=THEME["neon_purple"])
    with k3: nova_kpi("Critical File Hubs", f"{len(critical_files):,}", color=THEME["neon_red"])
    with k4: nova_kpi("Graph Depth", "3 layers" if visible_findings else "0 layers", color=THEME["neon_green"])
    if not visible_findings:
        st.info("No evidence matches the selected risk filter.")
        return
    _render_force_graph(nodes, edges)
    st.caption(f"{len(edges):,} relationships · {hubs:,} hubs (three or more relationships) · Blue: files · Purple: algorithms · Risk-colored: evidence.")
