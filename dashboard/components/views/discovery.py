"""
Discovery page view component.
"""
from datetime import datetime
from typing import Any
import os

import streamlit as st

from ..charts import horizontal_bar_chart
from ..theme import THEME, nova_kpi


def _scan_duration(results: dict[str, Any]) -> str:
    started, completed = results.get("started_at"), results.get("completed_at")
    if not started or not completed:
        return "—"
    try:
        delta = datetime.fromisoformat(completed) - datetime.fromisoformat(started)
    except ValueError:
        return "—"
    return f"{delta.total_seconds():.2f}s"


def render_discovery(results: dict[str, Any]):
    """Render the Discovery page (Pages 2 & 3)."""
    st.markdown(f"""
        <div style="margin-bottom: 30px;">
            <div style="color: {THEME['text_muted']}; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2px;">Asset Discovery</div>
            <div style="color: #fff; font-size: 2.2rem; font-weight: 800; letter-spacing: -1.5px; margin-top: 5px;">Inventory <span style="color: {THEME['neon_blue']}">Coverage</span></div>
        </div>
    """, unsafe_allow_html=True)

    findings = results.get("findings", [])

    # Discovery State Metrics
    d1, d2, d3, d4 = st.columns(4)

    conf = sum(1 for f in findings if float(f.get("confidence", f.get("Confidence", 0))) > 0.8)
    prob = sum(1 for f in findings if 0.5 < float(f.get("confidence", f.get("Confidence", 0))) <= 0.8)
    poss = sum(1 for f in findings if 0.2 < float(f.get("confidence", f.get("Confidence", 0))) <= 0.5)
    unkn = sum(1 for f in findings if float(f.get("confidence", f.get("Confidence", 0))) <= 0.2)

    with d1:
        nova_kpi("CONFIRMED", str(conf), "✅", THEME["neon_green"])
    with d2:
        nova_kpi("PROBABLE", str(prob), "🔍", THEME["neon_blue"])
    with d3:
        nova_kpi("POSSIBLE", str(poss), "⚡", THEME["neon_purple"])
    with d4:
        nova_kpi("UNKNOWN", str(unkn), "❓", THEME["text_muted"])

    st.markdown("<br/>", unsafe_allow_html=True)

    # Coverage Map and Quote Row
    c1, c2 = st.columns([2, 1])

    files_with_findings: dict[str, list[str]] = {}
    for f in findings:
        files_with_findings.setdefault(f.get("file_path", "unknown"), []).append(f.get("algorithm", "UNKNOWN"))

    with c1:
        st.markdown('<div style="color:#fff;font-weight:700;font-size:1rem;margin-bottom:15px;text-transform:uppercase;letter-spacing:1px;">Inventory Topology</div>', unsafe_allow_html=True)
        with st.container(border=True):
            total_files = results.get("total_files_scanned", 0) or len(files_with_findings)
            files_with_crypto = results.get("files_with_findings", len(files_with_findings))
            lines = [f"{total_files} files scanned · {files_with_crypto} with cryptographic findings"]
            for path, algos in files_with_findings.items():
                lines.append(f"└─ {os.path.basename(path)}: {', '.join(sorted(set(algos)))}")
            tree_ascii = "\n".join(lines) if lines else "No files scanned yet."
            st.markdown(f'<div class="tree-box">{tree_ascii}</div>', unsafe_allow_html=True)

    with c2:
        st.markdown(
            f"""
            <div style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                <div class="blind-quote" style="margin-top: 0;">
                    <span style="color:{THEME['text_muted']}; font-size:0.85rem;">Post-Quantum Intelligence:</span><br/>
                    <strong style="color:{THEME['text_hero']}; font-size:1.15rem; letter-spacing:0.5px; line-height: 1.4;">"We know where we are blind. That's more valuable than a false sense of security."</strong><br/>
                    <div style="margin-top: 10px; height: 2px; width: 40px; background: {THEME['neon_blue']};"></div>
                </div>
                <div style="margin-top: 20px; padding: 20px; background: {THEME['bg_card']}; border: 1px solid {THEME['border_dim']}; border-radius: 12px;">
                    <div style="color: {THEME['text_muted']}; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px;">Last Scan Duration</div>
                    <div style="color: {THEME['neon_green']}; font-size: 1.2rem; font-weight: 800;">{_scan_duration(results)}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Findings by primitive class
    st.markdown('<div style="color:#fff;font-weight:700;font-size:1rem;margin-bottom:15px;text-transform:uppercase;letter-spacing:1px;">Crypto Primitive Classes</div>', unsafe_allow_html=True)
    with st.container(border=True):
        class_counts: dict[str, int] = {}
        for f in findings:
            key = str(f.get("category", f.get("Category", "general"))).title()
            class_counts[key] = class_counts.get(key, 0) + 1

        chart = horizontal_bar_chart(
            [{"Class": k, "Findings": v} for k, v in sorted(class_counts.items(), key=lambda kv: -kv[1])],
            x_field="Findings",
            y_field="Class",
            color=THEME["neon_blue"],
            height=320,
            x_title="Findings",
        )
        st.altair_chart(chart, width="stretch")
