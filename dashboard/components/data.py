"""
Data fetching, caching, and processing utilities for ECDAT dashboard.
Supports FastAPI backend with seamless local SQLite database fallback.
"""
from datetime import datetime, timezone
from typing import Any

import requests
import streamlit as st

API_BASE = "http://localhost:8000"


@st.cache_data(ttl=3, show_spinner=False)
def fetch_results(scan_id: str) -> dict[str, Any]:
    """Fetch scan results from API, falling back to local SQLite DB."""
    # 1. Try FastAPI
    try:
        r = requests.get(f"{API_BASE}/results/{scan_id}", timeout=2)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass

    # 2. Try Local DB directly
    try:
        from api import db
        scan = db.get_scan(scan_id)
        if scan:
            return scan
    except Exception:
        pass

    return {"error": "Scan not found or server offline"}


@st.cache_data(ttl=3, show_spinner=False)
def fetch_cbom(scan_id: str) -> dict[str, Any]:
    """Fetch CBOM from API or generate locally."""
    try:
        r = requests.get(f"{API_BASE}/cbom/{scan_id}", timeout=2)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass

    try:
        from api import db
        from cbom.export import build_cbom
        scan = db.get_scan(scan_id)
        if scan:
            return build_cbom(scan["findings"])
    except Exception:
        pass

    return {"error": "CBOM not available"}


def get_scan_data() -> dict[str, Any] | None:
    """Get current scan data from session state cache, direct DB, or API."""
    if st.session_state.get("show_scan_intake"):
        return None

    # 1. Check local session cache first
    cached = st.session_state.get("results_cache")
    if cached and cached.get("status") != "running":
        return cached

    # 2. Check session scan_id
    scan_id = st.session_state.get("scan_id")
    if scan_id:
        results = fetch_results(scan_id)
        if results and "error" not in results:
            if results.get("status") != "running":
                st.session_state["results_cache"] = results
            return results
        if results.get("status") == "running":
            return {"status": "running"}

    # 3. Check if there is any latest scan in SQLite DB
    try:
        from api import db
        with db.get_connection() as conn:
            row = conn.execute("SELECT * FROM scans ORDER BY started_at DESC LIMIT 1").fetchone()
            if row:
                import json
                scan_record = {
                    "scan_id": row["scan_id"],
                    "target_path": row["target_path"],
                    "started_at": row["started_at"],
                    "completed_at": row["completed_at"],
                    "status": row["status"],
                    "total_files_scanned": row["total_files_scanned"],
                    "files_with_findings": row["files_with_findings"] or 0,
                    "migration_readiness_score": row["migration_readiness_score"],
                    "findings": json.loads(row["findings"]) if row["findings"] else [],
                    "summary": json.loads(row["summary"]) if row["summary"] else {},
                }
                st.session_state["scan_id"] = scan_record["scan_id"]
                st.session_state["results_cache"] = scan_record
                return scan_record
    except Exception:
        pass

    return None


def process_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Process and enrich findings with unified keys and display attributes."""
    if not findings:
        return []

    processed = []
    for idx, f in enumerate(findings):
        # Handle all possible case styles safely
        algo = f.get("Algorithm") or f.get("algorithm") or f.get("name") or "UNKNOWN"
        fpath = f.get("File Path") or f.get("file_path") or f.get("path") or "unknown"
        line = f.get("Line") or f.get("line_number") or f.get("line") or 1
        cat = f.get("Category") or f.get("category") or "General"
        risk = str(f.get("Quantum Risk") or f.get("quantum_risk") or "UNKNOWN").upper()
        sev = str(f.get("Severity") or f.get("severity") or "MEDIUM").upper()
        conf = float(f.get("Confidence") or f.get("confidence") or 0.85)
        rec = f.get("Recommendation") or f.get("recommendation") or {}
        hybrid_option = rec.get("hybrid_option") if isinstance(rec, dict) else None
        migration_order = rec.get("migration_order") if isinstance(rec, dict) else None

        # Determine recommended action
        if isinstance(rec, dict) and rec.get("replacement"):
            action = f"Replace with {rec['replacement']}"
        elif risk in ("CRITICAL", "HIGH"):
            action = "Migrate Immediately"
        elif risk == "VULNERABLE":
            action = "Plan PQC Migration"
        elif risk == "PARTIAL":
            action = "Upgrade Parameters / Hybrid"
        else:
            action = "Monitor Post-Quantum"

        asset_id = f.get("Asset ID") or f.get("asset_id") or f"CRYPTO-{(idx + 1) * 117 % 899 + 100:03d}"

        processed.append({
            "asset_id": asset_id,
            "algorithm": algo,
            "category": cat,
            "severity": sev,
            "quantum_risk": risk,
            "confidence": conf,
            "recommended_action": action,
            "file_path": fpath,
            "line_number": line,
            "recommendation": rec,
            "source_type": f.get("source_type", "source code"),
            "key_type": f.get("key_type", "unknown"),
            "key_size": f.get("key_size"),
            "protocol": f.get("protocol"),
            "usage": f.get("usage", "cryptographic usage"),
            "purpose": f.get("purpose", str(f.get("usage", "cryptographic usage")).title()),
            "certificate": f.get("certificate") or f.get("certificate_info", {}).get("subject") or f.get("protocol"),
            "internet_exposure": f.get("internet_exposure", "UNKNOWN"),
            "data_sensitivity": f.get("data_sensitivity", "UNKNOWN"),
            "business_criticality": f.get("business_criticality", "UNKNOWN"),
            "migration_difficulty": f.get("migration_difficulty", "UNKNOWN"),
            "dependency_count": f.get("dependency_count", 0),
            "hndl": f.get("hndl", {}),
            "risk_score": f.get("risk_score", 0),
            "risk_level": f.get("risk_level", sev),
            "risk_factors": f.get("risk_factors", []),
            "risk_reason": f.get("risk_reason", "No risk explanation available"),
            "migration_priority": f.get("migration_priority", 0),
            "hybrid_option": hybrid_option,
            "migration_order": migration_order,
            "evidence_source": f.get("evidence_source", f.get("source_type", "source code")),
            "evidence_fusion": f.get("evidence_fusion", {}),
            "fused_confidence": f.get("fused_confidence", f.get("confidence", 0.0)),
            "application": f.get("application", "repository root"),
            "certificate_info": f.get("certificate_info", {}),
            "original_idx": idx,
            # Dual-cased keys for backwards compatibility in all views
            "Asset ID": asset_id,
            "Algorithm": algo,
            "File Path": fpath,
            "Line": line,
            "Category": cat,
            "Severity": sev,
            "Quantum Risk": risk,
            "Confidence": conf,
            "Recommended Action": action,
            "Recommendation": rec,
            "Hybrid Option": hybrid_option,
            "Migration Order": migration_order,
            "Evidence Source": f.get("evidence_source", f.get("source_type", "source code")),
            "Evidence Fusion": f.get("evidence_fusion", {}),
            "Fused Confidence": f.get("fused_confidence", f.get("confidence", 0.0)),
            "Source Type": f.get("source_type", "source code"),
            "Key Type": f.get("key_type", "unknown"),
            "Key Size": f.get("key_size"),
            "Protocol": f.get("protocol"),
            "Usage": f.get("usage", "cryptographic usage"),
            "Purpose": f.get("purpose", str(f.get("usage", "cryptographic usage")).title()),
            "Certificate": f.get("certificate") or f.get("certificate_info", {}).get("subject") or f.get("protocol"),
            "Application": f.get("application", "repository root"),
            "Certificate Info": f.get("certificate_info", {}),
            "Risk Factors": f.get("risk_factors", []),
            "Dependency Count": f.get("dependency_count", 0),
        })

    return processed


def compute_kpis(results: dict[str, Any]) -> dict[str, Any]:
    """Compute KPI metrics from scan results."""
    findings = results.get("findings", [])
    summary = results.get("summary", {})
    n_files = results.get("total_files_scanned", 0)
    score = results.get("migration_readiness_score", 0.0)

    unique_algos = len({str(f.get("algorithm", f.get("Algorithm", ""))).upper() for f in findings})

    if findings:
        total_crypto_assets = len(findings)
        quantum_vulnerable = summary.get("vulnerable", 0) + summary.get("critical", 0)
        high_risk = sum(
            1 for f in findings
            if str(f.get("severity", f.get("Severity", ""))).lower() in ("critical", "high")
        )
        critical_findings = summary.get("critical", 0)
        conf_sum = sum(float(f.get("confidence", 0.85)) for f in findings)
        discovery_conf = (conf_sum / len(findings)) * 100
        blind_spots = max(0, n_files - len({f.get("file_path", "") for f in findings}))
        pqc_ready = score
    else:
        total_crypto_assets = 0
        quantum_vulnerable = 0
        high_risk = 0
        critical_findings = 0
        discovery_conf = 0.0
        blind_spots = 0
        pqc_ready = 100.0

    return {
        "total_assets": total_crypto_assets,
        "critical_findings": critical_findings,
        "unique_algos": unique_algos,
        "pqc_ready": round(pqc_ready, 1),
        "total_crypto_assets": total_crypto_assets,
        "quantum_vulnerable": quantum_vulnerable,
        "high_risk": high_risk,
        "discovery_confidence": round(discovery_conf, 1),
        "blind_spots": blind_spots,
        "migration_readiness_score": round(score, 1),
    }


def get_risk_distribution(findings: list[dict[str, Any]]) -> dict[str, int]:
    """Get count of findings by risk level."""
    dist = {"Safe": 0, "Partial": 0, "Vulnerable": 0, "Critical": 0}

    for f in findings:
        risk = str(f.get("quantum_risk", f.get("Quantum Risk", ""))).lower()
        sev = str(f.get("severity", f.get("Severity", ""))).lower()

        if "safe" in risk:
            dist["Safe"] += 1
        elif "partial" in risk:
            dist["Partial"] += 1
        elif "critical" in risk or sev == "critical":
            dist["Critical"] += 1
        elif "vulnerable" in risk or sev == "high":
            dist["Vulnerable"] += 1
        else:
            dist["Partial"] += 1

    return dist


def format_time_ago(dt: datetime) -> str:
    """Format datetime as relative time string."""
    delta = datetime.now(timezone.utc) - dt
    seconds = int(delta.total_seconds())

    if seconds < 60:
        return f"{seconds}s ago"
    elif seconds < 3600:
        return f"{seconds // 60}m ago"
    elif seconds < 86400:
        return f"{seconds // 3600}h ago"
    else:
        return f"{seconds // 86400}d ago"


def get_last_scan_string() -> str:
    """Get formatted last scan time string."""
    if "last_scan_time" in st.session_state:
        return format_time_ago(st.session_state["last_scan_time"])
    return "Recently"
