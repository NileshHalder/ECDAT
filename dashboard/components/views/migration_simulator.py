"""
Migration & Simulator View.
"""
import math
from datetime import datetime, timedelta, timezone
from typing import Any

import pandas as pd
import streamlit as st

from ..data import get_risk_distribution, process_findings
from ..theme import THEME, nova_kpi
from scanner.impact import analyze_what_if

ALLOCATION_FTE = {"Limited": 2, "Moderate": 4, "Aggressive": 8}
ALLOCATION_THROUGHPUT = {"Limited": 2.0, "Moderate": 4.0, "Aggressive": 8.0}
RISK_WEIGHTS = {"Critical": 4.0, "Vulnerable": 3.0, "Partial": 1.0}
COST_PER_FINDING = 25_000


def _simulate(dist: dict[str, int], timeline: int, allocation: str,
              priority_critical: bool, hybrid: bool, auto_swap: bool) -> dict[str, Any]:
    throughput = ALLOCATION_THROUGHPUT[allocation]
    if hybrid:
        throughput *= 1.25
    if auto_swap:
        throughput *= 1.5

    remaining = {k: float(dist.get(k, 0)) for k in RISK_WEIGHTS}
    work_items = sum(remaining.values())
    initial_weighted = sum(remaining[k] * RISK_WEIGHTS[k] for k in remaining)

    curve = []
    duration = 0
    for month in range(timeline + 1):
        if month > 0 and sum(remaining.values()) > 0:
            if priority_critical:
                order = ["Critical", "Vulnerable", "Partial"]
            else:
                order = sorted(remaining, key=remaining.get, reverse=True)
            capacity = throughput
            for key in order:
                take = min(remaining[key], capacity)
                remaining[key] -= take
                capacity -= take
            if sum(remaining.values()) == 0:
                duration = month
        weighted = sum(remaining[k] * RISK_WEIGHTS[k] for k in remaining)
        curve.append({
            "Month": month,
            "Risk Score": 100 * weighted / initial_weighted if initial_weighted else 0.0,
        })

    if duration == 0 and work_items > 0:
        duration = math.ceil(work_items / throughput)

    final_score = curve[-1]["Risk Score"]
    return {
        "curve": pd.DataFrame(curve),
        "work_items": int(work_items),
        "throughput": throughput,
        "duration": duration,
        "roi_velocity": 100 - final_score,
        "tech_debt_reduction": 100 * (1 - sum(remaining.values()) / work_items) if work_items else 100.0,
        "cost": int(work_items) * COST_PER_FINDING,
    }


def _render_what_if(findings: list[dict[str, Any]]) -> None:
    algorithms = sorted({str(f.get("algorithm", "UNKNOWN")) for f in findings if f.get("algorithm")})
    if not algorithms:
        return
    default_index = algorithms.index("RSA") if "RSA" in algorithms else 0
    with st.container(border=True):
        st.markdown(f'<div style="color:{THEME["neon_orange"]};font-size:0.7rem;font-weight:900;text-transform:uppercase;letter-spacing:2px;">Blast Radius Intelligence</div>', unsafe_allow_html=True)
        st.markdown('<div style="color:#fff;font-size:1.8rem;font-weight:800;margin:5px 0 6px;">Crypto <span style="color:#ffb000;">What-If</span> Engine</div>', unsafe_allow_html=True)
        st.caption("Model the organizational impact if an algorithm becomes prohibited, using only evidence from this scan.")
        algorithm = st.selectbox("What if this algorithm becomes prohibited?", algorithms, index=default_index, key="what_if_algorithm")
        impact = analyze_what_if(findings, algorithm)

        kpis = st.columns(5)
        metrics = [
            ("Affected Assets", impact["affected_assets"]),
            ("Applications", impact["affected_applications"]),
            ("Services", impact["affected_services"]),
            ("Certificates", impact["affected_certificates"]),
            ("Critical Systems", impact["critical_systems"]),
        ]
        for column, (label, value) in zip(kpis, metrics):
            with column:
                st.metric(label, value)

        if not impact["paths"]:
            st.info(f"No scanned assets currently depend on {algorithm}.")
            return

        st.markdown('<div style="color:#fff;font-weight:700;font-size:0.95rem;margin:18px 0 10px;text-transform:uppercase;letter-spacing:1px;">Why affected?</div>', unsafe_allow_html=True)
        path_df = pd.DataFrame([{
            "Crypto Dependency": f"{path['algorithm']} asset {path['asset']}",
            "Application": path["application"],
            "Service": path["service"],
            "Business Function": path["business_function"],
            "Certificate / Key": path["certificate"],
            "Risk": path["risk"],
        } for path in impact["paths"]])
        st.dataframe(path_df, hide_index=True, width="stretch")
        st.caption(f"Dependency chain: {algorithm} dependency -> application -> service -> business function. {impact['affected_business_functions']} business function(s) are in scope.")


def render_migration_and_simulator(results: dict[str, Any]):
    st.markdown(f"""
        <div style="margin-bottom: 30px;">
            <div style="color: {THEME['text_muted']}; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2px;">Predictive Remediation</div>
            <div style="color: #fff; font-size: 2.2rem; font-weight: 800; letter-spacing: -1.5px; margin-top: 5px;">Migration <span style="color: {THEME['neon_blue']}">Simulator</span></div>
        </div>
    """, unsafe_allow_html=True)

    raw_findings = results.get("findings", [])
    _render_what_if(raw_findings)
    st.markdown("<br>", unsafe_allow_html=True)

    dist = get_risk_distribution(process_findings(raw_findings))
    work_items = dist.get("Critical", 0) + dist.get("Vulnerable", 0) + dist.get("Partial", 0)
    if work_items == 0:
        st.info("No quantum-vulnerable findings in the current scan — nothing to simulate.")
        return

    kpi_row = st.container()

    col_sim, col_params = st.columns([7, 3], gap="large")

    with col_params:
        st.markdown('<div style="color:#fff;font-weight:700;font-size:1rem;margin-bottom:15px;text-transform:uppercase;letter-spacing:1px;">Control Panel</div>', unsafe_allow_html=True)
        with st.container(border=True):
            timeline = st.slider("Migration Timeline (Months)", 6, 36, 18, key="mig_timeline")
            allocation = st.select_slider("Resource Allocation", options=list(ALLOCATION_FTE), value="Moderate", key="mig_allocation")
            st.markdown("---")
            priority_critical = st.checkbox("Priority: Critical Systems", value=True, key="mig_priority")
            hybrid = st.checkbox("Hybrid Deployment Mode", value=True, key="mig_hybrid")
            auto_swap = st.checkbox("Automated Cipher Swap", value=False, key="mig_auto_swap")
        st.caption(
            f"Model: {ALLOCATION_THROUGHPUT['Limited']:.0f}/{ALLOCATION_THROUGHPUT['Moderate']:.0f}/"
            f"{ALLOCATION_THROUGHPUT['Aggressive']:.0f} findings per month for Limited/Moderate/Aggressive; "
            "hybrid +25% and automated swap +50% throughput; "
            f"${COST_PER_FINDING:,} engineering effort per finding."
        )

    sim = _simulate(dist, timeline, allocation, priority_critical, hybrid, auto_swap)

    # ─── TOP METRICS ───
    cost = sim["cost"]
    cost_str = f"${cost / 1e6:.1f}M" if cost >= 1e6 else f"${cost / 1e3:.0f}K"
    with kpi_row:
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            nova_kpi("Est. Duration", f"{sim['duration']} Mos", "📅", THEME["neon_blue"])
        with k2:
            nova_kpi("Resource Gap", f"{ALLOCATION_FTE[allocation]} FTEs", "👥", THEME["neon_purple"])
        with k3:
            nova_kpi("Migration Cost", cost_str, "💰", THEME["neon_orange"])
        with k4:
            nova_kpi("ROI Velocity", f"{sim['roi_velocity']:.0f}%", "🚀", THEME["neon_green"])

    st.markdown("<br>", unsafe_allow_html=True)

    with col_sim:
        st.markdown('<div style="color:#fff;font-weight:700;font-size:1rem;margin-bottom:15px;text-transform:uppercase;letter-spacing:1px;">Risk Reduction Projection</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.line_chart(sim["curve"].set_index("Month"), height=300, color=THEME["neon_blue"])
        if sim["duration"] > timeline:
            st.warning(
                f"Selected timeline ({timeline} months) cannot clear {sim['work_items']} findings at "
                f"{sim['throughput']:.1f} findings/month — needs {sim['duration']} months."
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── IMPACT SUMMARY ───
    st.markdown('<div style="color:#fff;font-weight:700;font-size:1rem;margin-bottom:15px;text-transform:uppercase;letter-spacing:1px;">Strategic Impact Assessment</div>', unsafe_allow_html=True)
    readiness = "High" if sim["roi_velocity"] >= 80 else "Medium" if sim["roi_velocity"] >= 50 else "Low"
    ready_date = datetime.now(timezone.utc) + timedelta(days=sim["duration"] * 30)
    slack = timeline - sim["duration"]
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Tech Debt Reduction", f"{sim['tech_debt_reduction']:.0f}%",
                  delta=f"{sim['work_items']} findings in scope")
    with c2:
        st.metric("Regulatory Readiness", readiness, delta=f"{sim['roi_velocity']:.0f}% risk cleared")
    with c3:
        st.metric("Est. Ready Date", ready_date.strftime("%b %Y"),
                  delta=f"{abs(slack)} mo {'ahead of' if slack >= 0 else 'behind'} plan")
