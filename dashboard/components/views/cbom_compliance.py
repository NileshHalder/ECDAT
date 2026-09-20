"""
CBOM & Compliance View.
"""
import json

import streamlit as st

from ..data import fetch_cbom
from ..theme import THEME, nova_kpi, raw_html

FIPS_STANDARDS = [
    ("FIPS 203", "ML-KEM", "Lattice-based Key Encapsulation Mechanism for key exchange."),
    ("FIPS 204", "ML-DSA", "Lattice-based Digital Signature Algorithm."),
    ("FIPS 205", "SLH-DSA", "Stateless hash-based signatures for fallback paths."),
]


def _executive_summary(scan_id: str, cbom: dict, components: list) -> str:
    summary = cbom.get("summary", {})
    lines = [
        f"# ECDAT Cryptographic Posture Summary — {scan_id}",
        "",
        f"- CBOM format: {cbom.get('bomFormat')} {cbom.get('specVersion')}",
        f"- Generated: {cbom.get('timestamp')}",
        f"- Distinct algorithms: {summary.get('totalAlgorithms', 0)}",
        f"- Quantum safe: {summary.get('quantumSafe', 0)}",
        f"- Quantum vulnerable: {summary.get('quantumVulnerable', 0)}",
        "",
        "## Components",
    ]
    for c in components:
        rec = c.get("recommendation") or {}
        status = "SAFE" if c.get("quantumSafe") else "AT RISK"
        repl = rec.get("replacement", "no mapping")
        lines.append(f"- {c.get('name')} [{c.get('category')}] {status} x{c.get('occurrences')} -> {repl}")
    return "\n".join(lines)


def render_cbom_and_compliance(scan_id: str):
    raw_html(f"""
        <div style="margin-bottom: 30px;">
            <div style="color: {THEME['text_muted']}; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2px;">Governance & Standards</div>
            <div style="color: #fff; font-size: 2.2rem; font-weight: 800; letter-spacing: -1.5px; margin-top: 5px;">CBOM <span style="color: {THEME['neon_blue']}">Compliance</span></div>
        </div>
    """)

    cbom = fetch_cbom(scan_id)
    if "error" in cbom:
        st.warning(f"CBOM unavailable for scan `{scan_id}`: {cbom['error']}")
        return

    components = cbom.get("components", [])
    graph = cbom.get("graph", {})
    summary = cbom.get("summary", {})
    total = summary.get("totalAlgorithms", len(components))
    safe = summary.get("quantumSafe", 0)
    at_risk = summary.get("quantumVulnerable", 0)

    # ─── TOP METRICS ───
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        nova_kpi("Algorithms", str(total), "🧩", THEME["neon_blue"])
    with k2:
        nova_kpi("Quantum Safe", str(safe), "✅", THEME["neon_green"])
    with k3:
        nova_kpi("At Risk", str(at_risk), "🚨", THEME["neon_orange"])
    with k4:
        nova_kpi("CBOM Spec", f"{cbom.get('bomFormat')} {cbom.get('specVersion')}", "🏷️", THEME["neon_purple"])

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1], gap="large")

    with col1:
        st.markdown('<div style="color:#fff;font-weight:700;font-size:1rem;margin-bottom:15px;text-transform:uppercase;letter-spacing:1px;">NIST PQC Standards Mapping</div>', unsafe_allow_html=True)
        with st.container(border=True):
            for code, name, blurb in FIPS_STANDARDS:
                mapped = [c for c in components if (c.get("recommendation") or {}).get("fips") == code]
                if mapped:
                    color = THEME["neon_green"]
                    detail = ", ".join(sorted(c["name"] for c in mapped))
                else:
                    color = THEME["text_dim"]
                    detail = "No current algorithms require this standard"
                raw_html(f"""
                <div style="margin-bottom:15px; padding:12px; background:rgba(255,255,255,0.02); border-left:4px solid {color}; border-radius:4px;">
                    <div style="font-weight:700; color:#fff;">{code}: {name} — {len(mapped)} algorithm(s)</div>
                    <div style="font-size:0.8rem; color:{THEME['text_muted']};">{blurb}</div>
                    <div style="font-size:0.75rem; color:{color}; margin-top:4px;">{detail}</div>
                </div>
                """)

    with col2:
        st.markdown('<div style="color:#fff;font-weight:700;font-size:1rem;margin-bottom:15px;text-transform:uppercase;letter-spacing:1px;">Export Artifacts</div>', unsafe_allow_html=True)
        with st.container(border=True):
            raw_html(f"""
            <div style="text-align:center; padding:20px;">
                <div style="font-size:2.5rem; margin-bottom:15px;">📄</div>
                <div style="font-size:0.85rem; color:{THEME['text_muted']}; margin-bottom:20px;">
                    Export the Cryptographic Bill of Materials generated from scan {scan_id} for internal audit or regulatory submission.
                </div>
            </div>
            """)
            st.download_button(
                label="DOWNLOAD CBOM JSON",
                data=json.dumps(cbom, indent=2),
                file_name=f"cbom_{scan_id}.json",
                mime="application/json",
                width="stretch",
            )
            st.download_button(
                label="DOWNLOAD EXECUTIVE SUMMARY (MARKDOWN)",
                data=_executive_summary(scan_id, cbom, components),
                file_name=f"cbom_summary_{scan_id}.md",
                mime="text/markdown",
                width="stretch",
            )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div style="color:#fff;font-weight:700;font-size:1rem;margin-bottom:15px;text-transform:uppercase;letter-spacing:1px;">Component Inventory</div>', unsafe_allow_html=True)
    if not components:
        st.info("No cryptographic components recorded in this CBOM.")
        return

    import pandas as pd
    df = pd.DataFrame([{
        "Algorithm": c.get("name", "UNKNOWN"),
        "Category": c.get("category", "General"),
        "Quantum Safe": "YES" if c.get("quantumSafe") else "NO",
        "Occurrences": c.get("occurrences", 0),
        "Replacement": (c.get("recommendation") or {}).get("replacement", "—"),
        "FIPS": (c.get("recommendation") or {}).get("fips") or "—",
    } for c in components])

    st.dataframe(
        df,
        hide_index=True,
        width="stretch",
        column_config={
            "Algorithm": st.column_config.TextColumn("Algorithm", width="medium"),
            "Quantum Safe": st.column_config.TextColumn("Quantum Safe", width="small"),
            "Occurrences": st.column_config.NumberColumn("Occurrences", width="small"),
            "Replacement": st.column_config.TextColumn("PQC Replacement", width="medium"),
            "FIPS": st.column_config.TextColumn("FIPS", width="small"),
        },
    )

    st.markdown('<div style="color:#fff;font-weight:700;font-size:1rem;margin:22px 0 15px;text-transform:uppercase;letter-spacing:1px;">Evidence Relationships Graph & Lineage</div>', unsafe_allow_html=True)
    relationships = graph.get("relationships", [])
    raw_nodes = graph.get("nodes", [])
    nodes_map = {node["id"]: node for node in raw_nodes}

    if relationships and raw_nodes:
        from .evidence_graph import _render_force_graph
        graph_nodes = []
        for n in raw_nodes:
            ntype = n.get("type", "Component")
            color = THEME["neon_blue"] if ntype in ("File", "Application") else THEME["neon_pink"] if ntype == "Algorithm" else THEME["neon_orange"]
            graph_nodes.append({
                "id": n["id"],
                "label": n.get("name", n["id"]),
                "type": ntype,
                "color": color,
                "detail": f"{ntype}: {n.get('name', n['id'])}"
            })
        graph_edges = [{"source": edge["from"], "target": edge["to"]} for edge in relationships]
        _render_force_graph(graph_nodes, graph_edges)

        graph_df = pd.DataFrame([{
            "From": nodes_map.get(edge["from"], {}).get("name", edge["from"]),
            "Relationship": edge["type"],
            "To": nodes_map.get(edge["to"], {}).get("name", edge["to"]),
        } for edge in relationships])
        st.dataframe(graph_df, hide_index=True, width="stretch")
    elif relationships:
        graph_df = pd.DataFrame([{
            "From": nodes_map.get(edge["from"], {}).get("name", edge["from"]),
            "Relationship": edge["type"],
            "To": nodes_map.get(edge["to"], {}).get("name", edge["to"]),
        } for edge in relationships])
        st.dataframe(graph_df, hide_index=True, width="stretch")
    else:
        st.info("No evidence relationships were recorded in this scan.")

