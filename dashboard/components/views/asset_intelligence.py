"""
Asset Intelligence View.
"""
from typing import Any

import pandas as pd
import streamlit as st

from ..data import process_findings
from ..theme import THEME, nova_kpi


def render_asset_intelligence(results: dict[str, Any]):
    findings = results.get("findings", [])
    processed = process_findings(findings)

    st.markdown(f"""
        <div style="margin-bottom: 30px;">
            <div style="color: {THEME['text_muted']}; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2px;">Identification & Triage</div>
            <div style="color: #fff; font-size: 2.2rem; font-weight: 800; letter-spacing: -1.5px; margin-top: 5px;">Asset <span style="color: {THEME['neon_blue']}">Intelligence</span></div>
        </div>
    """, unsafe_allow_html=True)

    if not processed:
        st.info("No cryptographic assets discovered in the latest scan.")
        return

    # ─── INTEL KPI ROW ───
    k1, k2, k3, k4 = st.columns(4)
    unique_algos = len({f["algorithm"] for f in processed})
    critical_assets = sum(1 for f in processed if f["risk_level"] == "CRITICAL")
    avg_conf = sum(f["confidence"] for f in processed) / len(processed)

    with k1:
        nova_kpi("Total Assets", str(len(processed)), "🛡️", THEME["neon_blue"])
    with k2:
        nova_kpi("Unique Algos", str(unique_algos), "🧩", THEME["neon_purple"])
    with k3:
        nova_kpi("Critical Risk", str(critical_assets), "💀", THEME["neon_red"])
    with k4:
        nova_kpi("Avg Confidence", f"{avg_conf*100:.0f}%", "🎯", THEME["neon_green"])

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── ASSET INVENTORY TABLE ───
    st.markdown('<div style="color:#fff;font-weight:700;font-size:1rem;margin-bottom:15px;text-transform:uppercase;letter-spacing:1px;">Inventory Manifest</div>', unsafe_allow_html=True)

    # Enrich for display
    display_df = pd.DataFrame([{
        "ID": f["asset_id"],
        "Algorithm": f["algorithm"],
        "Category": f["category"],
        "Source": f["source_type"],
        "Application": f["application"],
        "Key Type": f["key_type"],
        "Key Size": f["key_size"] or "—",
        "Protocol": f["protocol"] or "—",
        "Dependencies": f.get("dependency_count", 0),
        "Usage": f["usage"],
        "Purpose": f["purpose"],
        "Certificate": f["certificate"] or "—",
        "Evidence Source": f["evidence_source"],
        "Risk": f["quantum_risk"],
        "Risk Level": f["risk_level"],
        "Risk Score": f["risk_score"],
        "HNDL": "IMMEDIATE" if f["hndl"].get("hndl_risk") else "MONITOR",
        "Migration Priority": f["migration_priority"],
        "PQC Path": f["hybrid_option"] or f["recommendation"].get("replacement", "Monitor"),
        "Evidence Status": f["evidence_fusion"].get("status", "Single-source evidence"),
        "Fused Confidence": f'{f["fused_confidence"] * 100:.0f}%',
        "Location": f"{f['file_path']} (L{f['line_number']})",
        "Action": f["recommended_action"]
    } for f in processed])

    st.dataframe(
        display_df,
        hide_index=True,
        width="stretch",
        column_config={
            "ID": st.column_config.TextColumn("Asset ID", width="small"),
            "Algorithm": st.column_config.TextColumn("Algorithm", width="medium"),
            "Source": st.column_config.TextColumn("Evidence Source", width="medium"),
            "Application": st.column_config.TextColumn("Application", width="medium"),
            "Dependencies": st.column_config.NumberColumn("Deps", width="small"),
            "Risk": st.column_config.TextColumn("Quantum Risk Status", width="small"),
            "Location": st.column_config.TextColumn("Source Origin", width="large"),
            "Action": st.column_config.TextColumn("Remediation Strategy", width="medium"),
            "Risk Level": st.column_config.TextColumn("Composite Risk", width="small"),
            "HNDL": st.column_config.TextColumn("HNDL Status", width="small"),
            "Migration Priority": st.column_config.NumberColumn("Migration Priority", width="small"),
            "PQC Path": st.column_config.TextColumn("PQC / Hybrid Path", width="medium"),
            "Evidence Source": st.column_config.TextColumn("Evidence Channel", width="medium"),
            "Evidence Status": st.column_config.TextColumn("Evidence Fusion", width="medium"),
            "Fused Confidence": st.column_config.TextColumn("Fused Confidence", width="small"),
        }
    )

    # ─── CERTIFICATE DETAILS (If present) ───
    cert_findings = [f for f in processed if f.get("certificate_info") and isinstance(f["certificate_info"], dict) and f["certificate_info"].get("subject")]
    if cert_findings:
        st.markdown('<div style="color:#fff;font-weight:700;font-size:1rem;margin:22px 0 15px;text-transform:uppercase;letter-spacing:1px;">Certificate Intelligence & Validity</div>', unsafe_allow_html=True)
        cert_df = pd.DataFrame([{
            "Asset ID": f["asset_id"],
            "Subject": f["certificate_info"].get("subject", "—"),
            "Issuer": f["certificate_info"].get("issuer", "—"),
            "Serial": f["certificate_info"].get("serial_number", "—"),
            "Valid From": f["certificate_info"].get("not_before", "—"),
            "Valid Until": f["certificate_info"].get("not_after", "—"),
            "Signature Algo": f["certificate_info"].get("signature_algorithm", f.get("algorithm", "—")),
        } for f in cert_findings])
        st.dataframe(cert_df, hide_index=True, width="stretch")

    conflicts = []
    seen_conflicts = set()
    for finding in processed:
        fusion = finding["evidence_fusion"]
        conflict_key = (finding["application"], str(fusion.get("observations")))
        if fusion.get("conflict") and conflict_key not in seen_conflicts:
            seen_conflicts.add(conflict_key)
            conflicts.append({
                "Application": finding["application"],
                "Status": fusion.get("status", "Evidence conflict detected"),
                "Confidence": f'{finding["fused_confidence"] * 100:.0f}%',
                "Evidence": " | ".join(f'{source}: {", ".join(algorithms)}' for source, algorithms in fusion.get("observations", {}).items()),
                "Possible Reasons": " • ".join(fusion.get("reasons", [])),
            })
    if conflicts:
        st.markdown('<div style="color:#fff;font-weight:700;font-size:1rem;margin:22px 0 15px;text-transform:uppercase;letter-spacing:1px;">Evidence Fusion Alerts</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(conflicts), hide_index=True, width="stretch")

    st.markdown('<div style="color:#fff;font-weight:700;font-size:1rem;margin:22px 0 15px;text-transform:uppercase;letter-spacing:1px;">Risk Factors & HNDL Horizon</div>', unsafe_allow_html=True)
    rationale_df = pd.DataFrame([{
        "Asset": f["asset_id"],
        "Risk": f["risk_level"],
        "Risk Factors": " • ".join(f.get("risk_factors", [])) if f.get("risk_factors") else f["risk_reason"],
        "Data Lifetime": f'{f["hndl"].get("data_lifetime_years", "?")} years',
        "Migration Time": f'{f["hndl"].get("migration_time_years", "?")} years',
        "Threat Horizon": f'{f["hndl"].get("crqc_arrival_years", "?")} years',
        "Recommendation": "Immediate migration" if f["hndl"].get("hndl_risk") else "Plan migration",
    } for f in processed])
    st.dataframe(rationale_df, hide_index=True, width="stretch")

