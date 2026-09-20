"""
Nova Overview — Executive Cryptographic Posture View.
"""
import os
import json
from typing import Any

import pandas as pd
import streamlit as st

from ..charts import donut_chart
from ..data import compute_kpis, get_risk_distribution, process_findings
from ..theme import THEME, nova_kpi, raw_html, render_semi_gauge_svg

FEED_STYLES = {
    "VULNERABLE": ("CRITICAL", "neon_red"),
    "PARTIAL": ("WARNING", "neon_orange"),
    "SAFE": ("SUCCESS", "neon_green"),
}

def _build_feed(findings: list) -> list:
    items = []
    for f in findings[:6]:
        sev, color_key = FEED_STYLES.get(f["quantum_risk"], ("INFO", "neon_blue"))
        loc = f"{os.path.basename(f['file_path'])}:L{f['line_number']}"
        if f["quantum_risk"] == "SAFE":
            msg = f"Quantum-safe {f['algorithm']} verified in {loc}"
        else:
            msg = f"{f['algorithm']} in {loc} — {f['recommended_action']}"
        items.append((sev, msg, THEME[color_key]))
    return items


def _scan_history(current_scan_id: str | None) -> pd.DataFrame:
    """Read recent completed scans for comparison and trend reporting."""
    try:
        from api import db

        with db.get_connection() as conn:
            rows = conn.execute(
                """SELECT scan_id, completed_at, migration_readiness_score, summary
                   FROM scans WHERE status = 'completed'
                   ORDER BY completed_at DESC LIMIT 8"""
            ).fetchall()
        records = []
        for row in rows:
            summary = json.loads(row["summary"] or "{}")
            records.append({
                "scan_id": row["scan_id"],
                "completed_at": row["completed_at"],
                "readiness": row["migration_readiness_score"] or 0,
                "critical": summary.get("critical", 0),
                "vulnerable": summary.get("vulnerable", 0),
                "is_current": row["scan_id"] == current_scan_id,
            })
        return pd.DataFrame(records)
    except Exception:
        return pd.DataFrame()


def _application_summary(findings: list[dict]) -> pd.DataFrame:
    grouped: dict[str, dict[str, int]] = {}
    for finding in findings:
        directory = os.path.dirname(finding["file_path"])
        application = os.path.basename(directory) or "Repository root"
        item = grouped.setdefault(application, {"Findings": 0, "Critical / high": 0})
        item["Findings"] += 1
        if finding["severity"] in {"CRITICAL", "HIGH"}:
            item["Critical / high"] += 1
    columns = ["Application", "Findings", "Critical / high"]
    return pd.DataFrame(
        [{"Application": app, **metrics} for app, metrics in grouped.items()],
        columns=columns,
    ).sort_values(["Critical / high", "Findings"], ascending=False)

def render_overview(results: dict[str, Any]):
    findings = results.get("findings", [])
    processed_findings = process_findings(findings)
    kpis = compute_kpis(results)
    risk_dist = get_risk_distribution(findings)
    history = _scan_history(results.get("scan_id"))

    # ─── HEADER: SECURITY POSTURE ───
    st.markdown(f"""
        <div style="margin-bottom: 30px;">
            <div style="color: {THEME['text_muted']}; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2px;">Executive Summary</div>
            <div style="color: #fff; font-size: 2.2rem; font-weight: 800; letter-spacing: -1.5px; margin-top: 5px;">Cryptographic <span style="color: {THEME['neon_blue']}">Posture</span></div>
        </div>
    """, unsafe_allow_html=True)

    # ─── TOP SECTION: KPI CARDS & GAUGE ───
    col_metrics, col_gauge = st.columns([7, 3], gap="large")

    with col_metrics:
        c1, c2 = st.columns(2)
        with c1:
            nova_kpi("Total Assets", str(kpis.get("total_assets", 0)), "🛡️", THEME["neon_blue"])
            nova_kpi("Critical Findings", str(kpis.get("critical_findings", 0)), "💀", THEME["neon_red"])
        with c2:
            nova_kpi("Unique Algos", str(kpis.get("unique_algos", 0)), "🧩", THEME["neon_purple"])
            nova_kpi("Compliant Assets", f"{kpis.get('pqc_ready', 0):.0f}%", "✅", THEME["neon_green"])

    with col_gauge:
        raw_html(f"""
            <div style="background: {THEME['bg_card']}; border: 1px solid {THEME['border_dim']}; border-radius: 24px; padding: 25px; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; left: 0; width: 100%; height: 4px; background: linear-gradient(90deg, {THEME['neon_green']}, transparent);"></div>
                {render_semi_gauge_svg(kpis.get("pqc_ready", 0.0))}
            </div>
        """)

    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

    # ─── DECISION SUPPORT ───
    previous = history[~history["is_current"]].iloc[0] if not history.empty and (~history["is_current"]).any() else None
    priority = sorted(
        processed_findings,
        key=lambda f: ({"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}.get(f["severity"], 0), f["confidence"]),
        reverse=True,
    )
    change_col, action_col, scope_col = st.columns([3, 4, 3], gap="large")
    with change_col:
        st.markdown("#### Change since last scan")
        with st.container(border=True):
            if previous is None:
                st.caption("Run another scan of this scope to establish a baseline.")
            else:
                critical_delta = kpis["critical_findings"] - int(previous["critical"])
                readiness_delta = kpis["pqc_ready"] - float(previous["readiness"])
                st.metric("Critical findings", kpis["critical_findings"], f"{critical_delta:+d}")
                st.metric("Readiness score", f"{kpis['pqc_ready']:.0f}%", f"{readiness_delta:+.1f} pts")
    with action_col:
        st.markdown("#### Recommended next action")
        with st.container(border=True):
            if priority:
                first = priority[0]
                st.markdown(f"**Address {first['algorithm']} first**")
                st.caption(
                    f"{os.path.basename(first['file_path'])}, line {first['line_number']} · "
                    f"{first['recommended_action']}"
                )
            else:
                st.success("No cryptographic findings require remediation in this scan.")
    with scope_col:
        st.markdown("#### Scan scope")
        with st.container(border=True):
            st.metric("Files scanned", results.get("total_files_scanned", 0))
            st.caption(f"{results.get('files_with_findings', 0)} files with cryptographic findings")
            st.caption(f"{len(processed_findings)} findings · {len({f['category'] for f in processed_findings})} asset classes")
            st.caption(f"Completed in {results.get('completed_at', 'current session')}")

    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

    # ─── MIDDLE SECTION: DISTRIBUTION & FINDINGS ───
    col_dist, col_chart = st.columns([4, 6], gap="large")

    with col_dist:
        st.markdown('<div style="color:#fff;font-weight:700;font-size:1rem;margin-bottom:15px;text-transform:uppercase;letter-spacing:1px;">Risk Distribution</div>', unsafe_allow_html=True)
        with st.container(border=True):
            chart = donut_chart(risk_dist, height=280)
            st.altair_chart(chart, width="stretch")

    with col_chart:
        st.markdown('<div style="color:#fff;font-weight:700;font-size:1rem;margin-bottom:15px;text-transform:uppercase;letter-spacing:1px;">Priority findings</div>', unsafe_allow_html=True)
        with st.container(border=True):
            feed_items = _build_feed(processed_findings)
            if not feed_items:
                st.info("No cryptographic activity detected in the current scope.")
            for sev, msg, color in feed_items:
                raw_html(f"""
                    <div style="display: flex; align-items: center; gap: 15px; padding: 12px; margin-bottom: 8px; background: rgba(255,255,255,0.02); border-radius: 10px;">
                        <div style="width: 8px; height: 8px; border-radius: 50%; background: {color}; box-shadow: 0 0 8px {color};"></div>
                        <div style="font-size: 0.7rem; font-weight: 800; color: {color}; text-transform: uppercase; letter-spacing: 1px; min-width: 70px;">{sev}</div>
                        <div style="font-size: 0.85rem; color: #fff; font-weight: 500;">{msg}</div>
                    </div>
                """)

    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

    applications_col, compliance_col = st.columns([6, 4], gap="large")
    with applications_col:
        st.markdown("#### Top affected applications")
        with st.container(border=True):
            app_df = _application_summary(processed_findings)
            if app_df.empty:
                st.caption("No affected applications in this scan.")
            else:
                st.dataframe(app_df.head(5), hide_index=True, width="stretch")
    with compliance_col:
        st.markdown("#### Compliance posture")
        with st.container(border=True):
            deprecated = sum(1 for f in processed_findings if f["algorithm"] in {"MD5", "SHA-1", "DES", "3DES"})
            st.metric("PQC readiness", f"{kpis['pqc_ready']:.0f}%")
            st.caption(f"{deprecated} deprecated-algorithm findings")
            st.caption("CBOM export available for this scan")

    if not history.empty:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        st.markdown("#### Audit & Scan History")
        with st.container(border=True):
            if len(history) > 1:
                trend = history.sort_values("completed_at")
                st.line_chart(trend.set_index("completed_at")["readiness"], color=THEME["neon_blue"], height=180)

            hist_df = pd.DataFrame([{
                "Scan ID": r["scan_id"],
                "Completed At": r["completed_at"],
                "Readiness Score": f"{r['readiness']:.1f}%",
                "Critical Findings": r.get("critical", 0),
                "Vulnerable Findings": r.get("vulnerable", 0),
                "Current Scan": "ACTIVE" if r.get("is_current") else "—"
            } for r in history.to_dict("records")])

            st.dataframe(hist_df, hide_index=True, width="stretch")


    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

    # ─── BOTTOM SECTION: THREAT MANIFEST ───
    st.markdown('<div style="color:#fff;font-weight:700;font-size:1rem;margin-bottom:15px;text-transform:uppercase;letter-spacing:1px;">Vulnerability Manifest</div>', unsafe_allow_html=True)
    if not processed_findings:
        st.info("No threats detected in the current scope.")
        return

    filter_one, filter_two, filter_three = st.columns(3)
    with filter_one:
        selected_risks = st.multiselect(
            "Quantum risk",
            sorted({f["quantum_risk"] for f in processed_findings}),
            placeholder="All risk levels",
        )
    with filter_two:
        selected_algorithms = st.multiselect(
            "Algorithm",
            sorted({f["algorithm"] for f in processed_findings}),
            placeholder="All algorithms",
        )
    with filter_three:
        selected_severities = st.multiselect(
            "Severity",
            sorted({f["severity"] for f in processed_findings}),
            placeholder="All severities",
        )

    filtered_findings = [
        f for f in processed_findings
        if (not selected_risks or f["quantum_risk"] in selected_risks)
        and (not selected_algorithms or f["algorithm"] in selected_algorithms)
        and (not selected_severities or f["severity"] in selected_severities)
    ]
    st.caption(f"Showing {len(filtered_findings)} of {len(processed_findings)} findings")

    df = pd.DataFrame([{
        "Asset ID": f.get("asset_id", "CRYPTO-000"),
        "Algorithm": f.get("algorithm", "UNKNOWN"),
        "Category": f.get("category", "General"),
        "Location": f"{f.get('file_path', 'unknown')} (L{f.get('line_number', 1)})",
        "Risk": f.get("quantum_risk", "SAFE"),
        "Migration": f.get("recommended_action", "N/A")
    } for f in filtered_findings[:100]])

    st.dataframe(
        df,
        hide_index=True,
        width="stretch",
        column_config={
            "Asset ID": st.column_config.TextColumn("ID", width="small"),
            "Location": st.column_config.TextColumn("Source Origin", width="large"),
            "Risk": st.column_config.TextColumn("Status", width="small"),
            "Migration": st.column_config.TextColumn("Strategy", width="medium"),
        }
    )

    st.download_button(
        "Download findings CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="ecdat-findings.csv",
        mime="text/csv",
    )
    executive_summary = pd.DataFrame([{
        "Scan ID": results.get("scan_id", "Current scan"),
        "Cryptographic findings": kpis["total_assets"],
        "Critical findings": kpis["critical_findings"],
        "Migration readiness": f"{kpis['pqc_ready']:.1f}%",
        "Files scanned": results.get("total_files_scanned", 0),
        "Files with findings": results.get("files_with_findings", 0),
    }])
    st.download_button(
        "Download executive summary",
        data=executive_summary.to_csv(index=False).encode("utf-8"),
        file_name="ecdat-executive-summary.csv",
        mime="text/csv",
    )

    if filtered_findings:
        selected_asset = st.selectbox(
            "Inspect code context",
            filtered_findings,
            format_func=lambda f: f"{f['asset_id']} · {f['algorithm']} · {os.path.basename(f['file_path'])}:L{f['line_number']}",
        )
        context = findings[selected_asset["original_idx"]].get("context", [])
        with st.expander("View matched code context"):
            if context:
                st.code("".join(context), language="text")
            else:
                st.caption("No source context was stored for this finding.")

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("#### Remediation ownership")
    remediation_df = pd.DataFrame([
        {
            "Asset": f["asset_id"],
            "Recommended action": f["recommended_action"],
            "Owner": "Unassigned",
            "Status": "Open",
        }
        for f in priority[:10]
    ])
    if not remediation_df.empty:
        st.data_editor(
            remediation_df,
            hide_index=True,
            width="stretch",
            key=f"remediation_{results.get('scan_id', 'current')}",
            column_config={
                "Owner": st.column_config.TextColumn("Owner"),
                "Status": st.column_config.SelectboxColumn("Status", options=["Open", "In progress", "Risk accepted", "Resolved"]),
            },
        )
        st.caption("Assignments are maintained for this browser session. Persistent workflow integration can be added to the API next.")
