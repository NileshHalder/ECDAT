"""
PQC replacement lookup — NIST FIPS 203/204/205/206 mappings.
See data/pqc_mappings.json for the canonical data (loaded here).
"""
import json
import os

_MAPPINGS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "pqc_mappings.json")


def load_mappings() -> dict:
    with open(_MAPPINGS_PATH, "r") as f:
        return json.load(f)


def get_recommendation(algorithm: str, mappings: dict | None = None) -> dict | None:
    mappings = mappings or load_mappings()
    return mappings.get(algorithm)


def attach_recommendations(findings: list[dict]) -> list[dict]:
    mappings = load_mappings()
    for f in findings:
        if f["quantum_risk"] in ("VULNERABLE", "PARTIAL"):
            recommendation = get_recommendation(f["algorithm"], mappings)
            if recommendation:
                recommendation = dict(recommendation)
                if f["algorithm"] in {"RSA", "ECDSA", "Diffie-Hellman"}:
                    recommendation["hybrid_option"] = f"{f['algorithm']} + {recommendation['replacement']}"
                    recommendation["migration_order"] = "Deploy hybrid protection, then retire the classical algorithm"
            f["recommendation"] = recommendation
        else:
            f["recommendation"] = None
    return findings
