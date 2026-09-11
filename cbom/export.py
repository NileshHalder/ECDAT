"""
CycloneDX-style Cryptographic Bill of Materials (CBOM) export.
Takes a list of findings, returns valid CBOM-shaped JSON. No side effects.
"""
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def _node_id(kind: str, value: str) -> str:
    return f"urn:ecdat:{kind}:{uuid.uuid5(uuid.NAMESPACE_URL, f'{kind}:{value}')}"


def build_cbom(findings: list[dict]) -> dict:
    grouped = defaultdict(lambda: {"occurrences": 0, "locations": [], "meta": {}})
    nodes = {}
    relationships = []

    for f in findings:
        key = f["algorithm"]
        grouped[key]["occurrences"] += 1
        grouped[key]["locations"].append(f"{f['file_path']}:{f['line_number']}")
        grouped[key]["meta"] = {
            "category": f["category"],
            "quantumSafe": f["quantum_risk"] == "SAFE",
            "recommendation": f.get("recommendation"),
            "sourceType": f.get("source_type", "source code"),
            "keyType": f.get("key_type"),
            "keySize": f.get("key_size"),
            "protocol": f.get("protocol"),
            "usage": f.get("usage"),
            "application": f.get("application"),
            "certificateInfo": f.get("certificate_info", {}),
            "evidenceFusion": f.get("evidence_fusion", {}),
        }

        application_name = f.get("application", "repository root")
        library_name = f.get("library") or Path(f.get("file_path", "unknown")).name
        component_name = f.get("asset_id") or f"{key} at {f.get('file_path')}:{f.get('line_number')}"
        application_id = _node_id("application", application_name)
        library_id = _node_id("library", library_name)
        component_id = _node_id("component", component_name)
        algorithm_id = _node_id("algorithm", key)
        nodes[application_id] = {"id": application_id, "type": "application", "name": application_name}
        nodes[library_id] = {"id": library_id, "type": "library", "name": library_name}
        nodes[component_id] = {
            "id": component_id,
            "type": "cryptographic-component",
            "name": component_name,
            "location": f"{f.get('file_path')}:{f.get('line_number')}",
            "purpose": f.get("purpose", f.get("usage")),
            "risk": f.get("risk_level", f.get("quantum_risk")),
        }
        nodes[algorithm_id] = {"id": algorithm_id, "type": "algorithm", "name": key}
        relationships.extend([
            {"from": application_id, "to": library_id, "type": "uses"},
            {"from": library_id, "to": component_id, "type": "contains-evidence"},
            {"from": component_id, "to": algorithm_id, "type": "implements"},
        ])

        certificate = f.get("certificate") or f.get("certificate_info", {}).get("subject")
        if certificate:
            certificate_id = _node_id("certificate", certificate)
            nodes[certificate_id] = {"id": certificate_id, "type": "certificate", "name": certificate}
            relationships.append({"from": algorithm_id, "to": certificate_id, "type": "secured-by"})
        if f.get("key_size"):
            key_id = _node_id("key", f"{component_name}:{f['key_size']}")
            nodes[key_id] = {"id": key_id, "type": "key", "name": f"{key} {f['key_size']}"}
            relationships.append({"from": component_id, "to": key_id, "type": "uses-key"})

    components = [
        {
            "type": "algorithm",
            "name": algo,
            "category": data["meta"]["category"],
            "quantumSafe": data["meta"]["quantumSafe"],
            "occurrences": data["occurrences"],
            "locations": data["locations"],
            "recommendation": data["meta"]["recommendation"],
            "sourceType": data["meta"]["sourceType"],
            "keyType": data["meta"]["keyType"],
            "keySize": data["meta"]["keySize"],
            "protocol": data["meta"]["protocol"],
            "usage": data["meta"]["usage"],
            "application": data["meta"]["application"],
            "certificateInfo": data["meta"]["certificateInfo"],
            "evidenceFusion": data["meta"]["evidenceFusion"],
        }
        for algo, data in grouped.items()
    ]

    total = len(components)
    quantum_safe = sum(1 for c in components if c["quantumSafe"])

    return {
        "bomFormat": "CryptoBOM",
        "specVersion": "1.0",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": components,
        "graph": {
            "nodes": list(nodes.values()),
            "relationships": relationships,
        },
        "summary": {
            "totalAlgorithms": total,
            "quantumVulnerable": total - quantum_safe,
            "quantumSafe": quantum_safe,
        },
    }
