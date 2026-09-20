"""
Blind Spots & Risk View.
"""
from typing import Any

import pandas as pd
import streamlit as st

from ..data import process_findings
from ..theme import THEME, nova_kpi, raw_html


def render_blind_spots_and_risk(results: dict[str, Any]):
    st.markdown(f"""
        <div style="margin-bottom: 30px;">
            <div style="color: {THEME['text_muted']}; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2px;">Exposure Analysis</div>
            <div style="color: #fff; font-size: 2.2rem; font-weight: 800; letter-spacing: -1.5px; margin-top: 5px;">Blind Spots <span style="color: {THEME['neon_orange']}">& Risk</span></div>
        </div>
    """, unsafe_allow_html=True)

    findings = results.get("findings", [])
    processed = process_findings(findings)

    total_files = results.get("total_files_scanned", 0)
    files_with_findings = results.get("files_with_findings", 0)
    if not files_with_findings and processed:
        files_with_findings = len({f["file_path"] for f in processed if f.get("file_path")})
    if not total_files:
        total_files = max(files_with_findings, 1)

    blind_spots_count = max(0, total_files - files_with_findings)
    coverage_gap_pct = round((blind_spots_count / max(1, total_files)) * 100, 1)

    shadow_crypto_count = sum(
        1 for f in processed
        if float(f.get("confidence", 1.0)) <= 0.5 or f.get("source_type") in ("unknown", "unverified")
    )

    crit_count = sum(1 for f in processed if f.get("severity") == "CRITICAL" or f.get("quantum_risk") == "CRITICAL")
    high_count = sum(1 for f in processed if f.get("severity") == "HIGH" or f.get("quantum_risk") == "VULNERABLE")

    if crit_count > 0:
        risk_density = "Critical"
        density_color = THEME["neon_red"]
    elif high_count > 0:
        risk_density = "High"
        density_color = THEME["neon_orange"]
    elif processed:
        risk_density = "Medium"
        density_color = THEME["neon_purple"]
    else:
        risk_density = "Low"
        density_color = THEME["neon_green"]

    # ─── TOP METRICS ───
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        nova_kpi("Blind Spots", str(blind_spots_count), "👁️", THEME["neon_orange"])
    with k2:
        nova_kpi("Coverage Gap", f"{coverage_gap_pct}%", "📉", THEME["neon_red"])
    with k3:
        nova_kpi("Shadow Crypto", str(shadow_crypto_count), "👻", THEME["neon_purple"])
    with k4:
        nova_kpi("Risk Density", risk_density, "☣️", density_color)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div style="color:#fff;font-weight:700;font-size:1rem;margin-bottom:15px;text-transform:uppercase;letter-spacing:1px;">Source Type Coverage & Exposure</div>', unsafe_allow_html=True)
        with st.container(border=True):
            source_type_counts: dict[str, int] = {}
            for f in processed:
                stype = str(f.get("source_type", "source code")).replace("_", " ").title()
                source_type_counts[stype] = source_type_counts.get(stype, 0) + 1

            known_types = [
                ("Source Code", THEME["neon_blue"]),
                ("Configuration", THEME["neon_orange"]),
                ("Certificate", THEME["neon_red"]),
                ("Binary / Firmware", THEME["neon_purple"]),
                ("Dependency Manifest", THEME["neon_green"]),
            ]

            total_findings = len(processed) or 1
            bars_html = ""
            for name, color in known_types:
                cnt = source_type_counts.get(name, 0)
                # Check for alternate keys
                if name == "Binary / Firmware":
                    cnt += source_type_counts.get("Binary", 0) + source_type_counts.get("Firmware", 0)
                pct = round((cnt / total_findings) * 100) if processed else 0
                bars_html += f"""
                <div style="margin-bottom:20px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                        <span style="color:#fff; font-size:0.85rem; font-weight:600;">{name}</span>
                        <span style="color:{color}; font-size:0.85rem; font-weight:700;">{cnt} findings ({pct}%)</span>
                    </div>
                    <div style="height:6px; background:rgba(255,255,255,0.05); border-radius:3px;">
                        <div style="width:{max(pct, 4 if cnt > 0 else 0)}%; height:100%; background:{color}; border-radius:3px; box-shadow:0 0 10px {color}44;"></div>
                    </div>
                </div>
                """
            raw_html(bars_html)

    with col2:
        st.markdown('<div style="color:#fff;font-weight:700;font-size:1rem;margin-bottom:15px;text-transform:uppercase;letter-spacing:1px;">Critical Risk Concentrations</div>', unsafe_allow_html=True)
        with st.container(border=True):
            high_risk_findings = [
                f for f in processed
                if f.get("severity") in ("CRITICAL", "HIGH") or f.get("quantum_risk") in ("CRITICAL", "VULNERABLE")
            ]
            if not high_risk_findings:
                st.success("No high-risk critical cryptographic concentrations detected in current scan.")
            else:
                for f in high_risk_findings[:4]:
                    file_name = f.get("file_path", "").split("/")[-1].split("\\")[-1]
                    line = f.get("line_number", 1)
                    algo = f.get("algorithm", "Unknown Algorithm")
                    risk_txt = f.get("risk_reason", f.get("recommended_action", "Quantum Vulnerable"))
                    if f.get("severity") == "CRITICAL" or f.get("quantum_risk") == "CRITICAL":
                        st.error(f"**{algo}** in `{file_name}:L{line}` — {risk_txt}")
                    else:
                        st.warning(f"**{algo}** in `{file_name}:L{line}` — {risk_txt}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── 3x3 RISK MATRIX (Quantum Risk vs Business Criticality) ───
    st.markdown('<div style="color:#fff;font-weight:700;font-size:1rem;margin-bottom:15px;text-transform:uppercase;letter-spacing:1px;">Quantum Risk × Business Criticality Matrix</div>', unsafe_allow_html=True)
    with st.container(border=True):
        crit_levels = ["HIGH", "MEDIUM", "LOW"]
        risk_levels = ["VULNERABLE", "PARTIAL", "SAFE"]
        matrix: dict[str, dict[str, int]] = {c: {r: 0 for r in risk_levels} for c in crit_levels}

        for f in processed:
            bc = str(f.get("business_criticality", "MEDIUM")).upper()
            if bc not in matrix:
                bc = "MEDIUM"
            qr = str(f.get("quantum_risk", "PARTIAL")).upper()
            if qr not in risk_levels:
                if qr in ("CRITICAL", "VULNERABLE"):
                    qr = "VULNERABLE"
                elif qr == "SAFE":
                    qr = "SAFE"
                else:
                    qr = "PARTIAL"
            matrix[bc][qr] += 1

        cols = st.columns(4)
        cols[0].markdown("<div style='color:#aaa; font-weight:700; text-align:center; padding-top:10px;'>Criticality \\ Risk</div>", unsafe_allow_html=True)
        cols[1].markdown(f"<div style='color:{THEME['neon_red']}; font-weight:700; text-align:center;'>Vulnerable</div>", unsafe_allow_html=True)
        cols[2].markdown(f"<div style='color:{THEME['neon_orange']}; font-weight:700; text-align:center;'>Partial / Hybrid</div>", unsafe_allow_html=True)
        cols[3].markdown(f"<div style='color:{THEME['neon_green']}; font-weight:700; text-align:center;'>PQC Safe</div>", unsafe_allow_html=True)

        for bc in crit_levels:
            r_cols = st.columns(4)
            r_cols[0].markdown(f"<div style='color:#fff; font-weight:700; padding:10px;'>{bc}</div>", unsafe_allow_html=True)
            for i, qr in enumerate(risk_levels, start=1):
                count = matrix[bc][qr]
                bg_color = (
                    "rgba(255, 75, 75, 0.2)" if qr == "VULNERABLE" and bc == "HIGH"
                    else "rgba(255, 165, 0, 0.15)" if qr in ("VULNERABLE", "PARTIAL") and bc in ("HIGH", "MEDIUM")
                    else "rgba(0, 255, 128, 0.1)"
                )
                border_color = (
                    THEME["neon_red"] if qr == "VULNERABLE" and bc == "HIGH"
                    else THEME["neon_orange"] if qr in ("VULNERABLE", "PARTIAL")
                    else THEME["neon_green"]
                )
                r_cols[i].markdown(f"""
                    <div style="background:{bg_color}; border:1px solid {border_color}; border-radius:8px; text-align:center; padding:10px; font-weight:800; font-size:1.1rem; color:#fff;">
                        {count}
                    </div>
                """, unsafe_allow_html=True)

