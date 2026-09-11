"""
Quantum risk classification + Mosca's algorithm + Migration Readiness Score.
Hard rule (docs/Rules.md): RSA/ECC/DH = VULNERABLE (Shor's algorithm).
AES/SHA = PARTIAL only, unless undersized. Never invented classifications.
"""

DEFAULT_LIFETIMES = {
    "asymmetric": {"data_lifetime": 12, "migration_time": 4},
    "symmetric": {"data_lifetime": 5, "migration_time": 1},
    "hash": {"data_lifetime": 5, "migration_time": 1},
    "mac": {"data_lifetime": 5, "migration_time": 1},
    "kdf": {"data_lifetime": 5, "migration_time": 1},
}
CRQC_ARRIVAL_ESTIMATE = 9

WEIGHTS = {"SAFE": 1.0, "HYBRID": 0.8, "PARTIAL": 0.3, "VULNERABLE": 0.0, "CRITICAL": 0.0}


def mosca_score(category: str, crqc_arrival: int = CRQC_ARRIVAL_ESTIMATE) -> dict:
    defaults = DEFAULT_LIFETIMES.get(category, {"data_lifetime": 5, "migration_time": 2})
    total_exposure = defaults["data_lifetime"] + defaults["migration_time"]
    if total_exposure > crqc_arrival:
        label = "CRITICAL - At risk now"
    elif total_exposure > crqc_arrival * 0.7:
        label = "HIGH - Migrate soon"
    else:
        label = "LOW - Monitor"
    return {
        **defaults,
        "data_lifetime_years": defaults["data_lifetime"],
        "migration_time_years": defaults["migration_time"],
        "crqc_arrival_years": crqc_arrival,
        "hndl_risk": total_exposure > crqc_arrival,
        "risk_label": label,
    }


def _contains_any(text: str, values: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(value in lowered for value in values)


def assess_finding(finding: dict, dependency_count: int = 0) -> dict:
    """Add explainable business and HNDL risk metadata to one finding."""
    context = " ".join(finding.get("context", []))
    evidence = " ".join((finding.get("file_path", ""), finding.get("application", ""), context))
    usage = finding.get("usage", "cryptographic usage")
    category = finding.get("category", "unknown")
    key_size = finding.get("key_size")
    exposure = "HIGH" if finding.get("source_type") == "API endpoint" or _contains_any(evidence, ("api", "gateway", "internet", "http")) else "MEDIUM"
    sensitivity = "HIGH" if _contains_any(evidence, ("payment", "transaction", "customer", "credential", "password", "secret", "auth")) else "MEDIUM"
    criticality = "HIGH" if _contains_any(evidence, ("payment", "transaction", "billing", "identity", "auth", "production")) else "MEDIUM"
    difficulty = "HIGH" if category == "asymmetric" else "MEDIUM" if category in {"protocol", "certificate"} else "LOW"
    hndl = mosca_score(category)

    factors = []
    risk_points = 0
    if finding.get("quantum_risk") in {"VULNERABLE", "CRITICAL"}:
        risk_points += 35
        factors.append("Quantum-vulnerable algorithm")
    elif finding.get("quantum_risk") == "PARTIAL":
        risk_points += 15
        factors.append("Partial quantum exposure")
    if key_size and ((category == "asymmetric" and key_size < 2048) or (category == "symmetric" and key_size < 256)):
        risk_points += 15
        factors.append(f"Undersized key ({key_size})")
    if exposure == "HIGH":
        risk_points += 15
        factors.append("Internet-facing evidence")
    if sensitivity == "HIGH":
        risk_points += 15
        factors.append("Long-lived sensitive data")
    if criticality == "HIGH":
        risk_points += 10
        factors.append("High business criticality")
    if hndl["hndl_risk"]:
        risk_points += 10
        factors.append("HNDL window is already exceeded")
    if dependency_count > 1:
        factors.append(f"{dependency_count} related cryptographic dependencies")

    if risk_points >= 70:
        risk_level = "CRITICAL"
    elif risk_points >= 45:
        risk_level = "HIGH"
    elif risk_points >= 20:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    finding["purpose"] = usage.title()
    finding["certificate"] = finding.get("certificate_info", {}).get("subject") or finding.get("protocol")
    finding["internet_exposure"] = exposure
    finding["data_sensitivity"] = sensitivity
    finding["business_criticality"] = criticality
    finding["migration_difficulty"] = difficulty
    finding["dependency_count"] = dependency_count
    finding["hndl"] = hndl
    finding["risk_score"] = min(risk_points, 100)
    finding["risk_level"] = risk_level
    finding["risk_factors"] = factors or ["No elevated risk factors detected"]
    finding["risk_reason"] = " + ".join(factors) if factors else "No elevated risk factors detected"
    finding["migration_priority"] = round(min(risk_points + (10 if difficulty == "LOW" else 0), 100), 1)
    return finding


def assess_findings(findings: list[dict]) -> list[dict]:
    """Assess findings together so dependency context is available."""
    applications: dict[str, int] = {}
    for finding in findings:
        application = finding.get("application", "repository root")
        applications[application] = applications.get(application, 0) + 1
    for finding in findings:
        assess_finding(finding, applications.get(finding.get("application", "repository root"), 1))
    return findings


def readiness_score(findings: list[dict]) -> float:
    scored_findings = [finding for finding in findings if finding.get("quantum_risk") in WEIGHTS]
    if not scored_findings:
        return 100.0
    total = sum(WEIGHTS[finding["quantum_risk"]] for finding in scored_findings)
    return round((total / len(scored_findings)) * 100, 1)


def summarize(findings: list[dict]) -> dict:
    summary = {"safe": 0, "partial": 0, "vulnerable": 0, "critical": 0}
    for f in findings:
        risk = f["quantum_risk"].lower()
        if risk == "safe":
            summary["safe"] += 1
        elif risk == "partial":
            summary["partial"] += 1
        elif risk == "vulnerable" and f["severity"] == "critical":
            summary["critical"] += 1
        elif risk == "vulnerable":
            summary["vulnerable"] += 1
    return summary
