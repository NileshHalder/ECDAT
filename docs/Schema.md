# Schema.md — ECDAT Data Models

## Finding (core internal object — produced by the scanner)

```json
{
  "id": "finding_0001",
  "pattern_id": "RSA-001",
  "algorithm": "RSA",
  "category": "asymmetric",
  "file_path": "src/auth/jwt.py",
  "line_number": 45,
  "context": [
    "def generate_keys():",
    "    key = rsa.generate_private_key(",
    "        public_exponent=65537, key_size=2048",
    "    )",
    "    return key"
  ],
  "matched_line_index": 1,
  "quantum_risk": "VULNERABLE",
  "severity": "critical",
  "confidence": 1.0,
  "mosca_score": {
    "data_lifetime_years": 10,
    "migration_time_years": 3,
    "crqc_arrival_years": 10,
    "risk_label": "CRITICAL - At risk now"
  },
  "recommendation": {
    "replacement": "ML-KEM (Kyber)",
    "fips_standard": "FIPS 203",
    "use_case": "key exchange"
  }
}
```

**Field notes:**
- `quantum_risk`: one of `VULNERABLE`, `PARTIAL`, `SAFE`, `UNKNOWN`
- `severity`: one of `critical`, `high`, `medium`, `low`, `info`
- `confidence`: float 0.0-1.0 (lower for matches in comments/tests)
- `recommendation`: `null` if `quantum_risk` is `SAFE`

## Scan (a full run, contains many Findings)

```json
{
  "scan_id": "scan_20260905_001",
  "target_path": "/uploads/sample-repo",
  "started_at": "2026-09-05T10:00:00Z",
  "completed_at": "2026-09-05T10:00:42Z",
  "status": "completed",
  "total_files_scanned": 128,
  "total_findings": 37,
  "summary": {
    "safe": 12,
    "partial": 15,
    "vulnerable": 8,
    "critical": 2
  },
  "migration_readiness_score": 41.9
}
```

## CBOM Export (CycloneDX-style, produced from a completed Scan)

```json
{
  "bomFormat": "CryptoBOM",
  "specVersion": "1.0",
  "serialNumber": "urn:uuid:<generated-uuid>",
  "timestamp": "2026-09-05T10:00:42Z",
  "components": [
    {
      "type": "algorithm",
      "name": "RSA-2048",
      "category": "asymmetric",
      "quantumSafe": false,
      "occurrences": 12,
      "locations": ["src/auth/jwt.py:45", "src/tls/config.py:23"],
      "recommendation": "ML-KEM (Kyber) — FIPS 203"
    }
  ],
  "summary": {
    "totalAlgorithms": 15,
    "quantumVulnerable": 7,
    "quantumSafe": 8
  }
}
```

## PQC Mapping Table (static reference data — `data/pqc_mappings.json`)

```json
{
  "RSA": { "replacement": "ML-KEM (Kyber)", "fips": "FIPS 203", "use_case": "key exchange" },
  "ECDSA": { "replacement": "ML-DSA (Dilithium)", "fips": "FIPS 204", "use_case": "signatures" },
  "DH": { "replacement": "ML-KEM (Kyber)", "fips": "FIPS 203", "use_case": "key exchange" },
  "DES": { "replacement": "AES-256", "fips": null, "use_case": "symmetric encryption" },
  "3DES": { "replacement": "AES-256", "fips": null, "use_case": "symmetric encryption" },
  "MD5": { "replacement": "SHA-3 or SHA-256", "fips": null, "use_case": "hashing" },
  "SHA-1": { "replacement": "SHA-3 or SHA-256", "fips": null, "use_case": "hashing" },
  "AES-128": { "replacement": "AES-256", "fips": null, "use_case": "increase key size for Grover's resistance" }
}
```

## Database Tables (if using SQLite/Postgres instead of flat JSON)

**scans**
| column | type |
|---|---|
| scan_id | TEXT PRIMARY KEY |
| target_path | TEXT |
| started_at | TIMESTAMP |
| completed_at | TIMESTAMP |
| status | TEXT |
| total_files_scanned | INTEGER |
| migration_readiness_score | REAL |

**findings**
| column | type |
|---|---|
| id | TEXT PRIMARY KEY |
| scan_id | TEXT (FK → scans.scan_id) |
| pattern_id | TEXT |
| algorithm | TEXT |
| category | TEXT |
| file_path | TEXT |
| line_number | INTEGER |
| context | TEXT (JSON-encoded array) |
| quantum_risk | TEXT |
| severity | TEXT |
| confidence | REAL |
| recommendation | TEXT (JSON-encoded object, nullable) |
