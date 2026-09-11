"""Evidence fusion across source, binary, certificate, network, and config signals."""
from __future__ import annotations

from collections import defaultdict


SOURCE_WEIGHTS = {
    "source code": 0.75,
    "binary": 0.85,
    "certificate": 0.90,
    "network": 0.95,
    "configuration": 0.80,
    "dependency manifest": 0.65,
    "container definition": 0.70,
}


def normalize_source_type(finding: dict) -> str:
    source_type = str(finding.get("source_type", "source code")).lower()
    if source_type in {"api endpoint", "protocol", "network"}:
        return "network"
    if source_type in SOURCE_WEIGHTS:
        return source_type
    return "source code"


def _group_key(finding: dict) -> str:
    return str(finding.get("application") or "repository root")


def fuse_evidence(findings: list[dict]) -> list[dict]:
    """Attach an evidence-fusion record to each finding and return findings."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for finding in findings:
        groups[_group_key(finding)].append(finding)

    for group_findings in groups.values():
        observations: dict[str, set[str]] = defaultdict(set)
        source_findings: dict[str, list[dict]] = defaultdict(list)
        for finding in group_findings:
            source = normalize_source_type(finding)
            algorithm = str(finding.get("algorithm", "UNKNOWN"))
            observations[source].add(algorithm)
            source_findings[source].append(finding)

        observed_algorithms = {algorithm for algorithms in observations.values() for algorithm in algorithms}
        conflict = len(observed_algorithms) > 1
        sources = sorted(observations)
        weighted_confidence = sum(SOURCE_WEIGHTS.get(source, 0.7) for source in sources) / len(sources)
        if len(sources) > 1 and not conflict:
            weighted_confidence += 0.05
        if conflict:
            weighted_confidence -= 0.15

        reasons = []
        if conflict:
            source_algorithms = {source: sorted(algorithms) for source, algorithms in observations.items()}
            if "source code" in observations and any(source in observations for source in ("network", "certificate", "configuration")):
                reasons.extend(["Old source code may differ from runtime", "Runtime configuration differs", "Source implementation may be unused"])
            if "certificate" in observations and len(observations["certificate"]) > 0:
                reasons.append("Certificate may have been recently rotated")
            if "binary" in observations and "source code" in observations:
                reasons.append("Built binary may not match current source")
            if not reasons:
                reasons.append("Multiple algorithms observed across evidence sources")
        elif len(sources) == 1:
            reasons.append("No corroborating evidence was available from another channel")
        else:
            reasons.append("Independent evidence channels agree")

        fusion = {
            "status": "Evidence conflict detected" if conflict else "Evidence corroborated" if len(sources) > 1 else "Single-source evidence",
            "confidence": round(max(0.0, min(1.0, weighted_confidence)), 2),
            "sources": sources,
            "observations": {source: sorted(algorithms) for source, algorithms in observations.items()},
            "reasons": reasons,
            "conflict": conflict,
        }
        for finding in group_findings:
            finding["evidence_source"] = normalize_source_type(finding)
            finding["evidence_fusion"] = fusion
            finding["fused_confidence"] = fusion["confidence"]
    return findings