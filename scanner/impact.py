"""What-if impact analysis over the cryptographic inventory."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path


def _service_name(finding: dict) -> str:
    application = finding.get("application") or "repository root"
    path_parts = Path(finding.get("file_path", "")).parts
    for part in reversed(path_parts[:-1]):
        if part.lower() not in {"src", "lib", "app", "services", "service"}:
            return part
    return application


def _business_function(finding: dict) -> str:
    usage = finding.get("purpose") or finding.get("usage") or "Cryptographic usage"
    return str(usage).title()


def analyze_what_if(findings: list[dict], prohibited_algorithm: str) -> dict:
    """Calculate blast radius if one algorithm is prohibited."""
    affected = [
        finding for finding in findings
        if str(finding.get("algorithm", "")).casefold() == prohibited_algorithm.casefold()
    ]
    applications: dict[str, set[str]] = defaultdict(set)
    services: dict[str, set[str]] = defaultdict(set)
    certificates: dict[str, set[str]] = defaultdict(set)
    business_functions: dict[str, set[str]] = defaultdict(set)
    paths = []

    for finding in affected:
        application = finding.get("application") or "repository root"
        service = _service_name(finding)
        certificate = finding.get("certificate") or finding.get("certificate_info", {}).get("subject")
        business_function = _business_function(finding)
        asset = f"{finding.get('file_path', 'unknown')}:{finding.get('line_number', '?')}"
        applications[application].add(asset)
        services[service].add(asset)
        business_functions[business_function].add(asset)
        if certificate:
            certificates[certificate].add(asset)
        paths.append({
            "asset": asset,
            "algorithm": prohibited_algorithm,
            "application": application,
            "service": service,
            "business_function": business_function,
            "certificate": certificate or "No certificate evidence",
            "risk": finding.get("risk_level", finding.get("quantum_risk", "UNKNOWN")),
            "critical": finding.get("business_criticality") == "HIGH" or finding.get("risk_level") == "CRITICAL",
        })

    critical_systems = {path["application"] for path in paths if path["critical"]}
    return {
        "algorithm": prohibited_algorithm,
        "affected_assets": len(affected),
        "affected_applications": len(applications),
        "affected_services": len(services),
        "affected_certificates": len(certificates),
        "critical_systems": len(critical_systems),
        "affected_business_functions": len(business_functions),
        "paths": paths,
        "applications": sorted(applications),
        "services": sorted(services),
        "certificates": sorted(certificates),
        "business_functions": sorted(business_functions),
    }