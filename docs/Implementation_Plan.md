# Implementation_Plan.md — ECDAT

*This is the concrete, code-level companion to `Phases.md`. Phases.md says WHAT to build and in what order; this file says HOW.*

## 1. Pattern Definition Format

Every entry in `scanner/patterns.py` follows this exact shape (enforced by `Rules.md`):

```python
PATTERNS = [
    {
        "id": "RSA-001",
        "algorithm": "RSA",
        "category": "asymmetric",
        "regex": r"(rsa\.generate_private_key|RSA\.generate|Cipher\.getInstance\([\"']RSA)",
        "quantum_risk": "VULNERABLE",
        "severity": "critical",
    },
    # ...target 40-60 total patterns by end of Phase 1, starting with these ~15:
    # RSA, ECDSA, DH/ECDH, AES (+ mode detection: ECB flagged separately as weak),
    # DES, 3DES, ChaCha20, MD5, SHA-1, SHA-256, SHA-3, HMAC, PBKDF2, bcrypt, Argon2
]
```

## 2. Scanning Algorithm (walker.py + analyzer.py)

```python
SKIP_DIRS = {".git", "node_modules", "vendor", "__pycache__", ".venv", "dist", "build"}
SKIP_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".lock", ".min.js"}

def walk_files(root_path):
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if not any(fname.endswith(ext) for ext in SKIP_EXTENSIONS):
                yield os.path.join(dirpath, fname)

def scan_file(file_path, patterns):
    findings = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return findings  # skip unreadable files, never crash (per Rules.md)

    full_text = "".join(lines)
    for pattern in patterns:
        for match in re.finditer(pattern["regex"], full_text):
            line_no = full_text[:match.start()].count("\n") + 1
            context_start = max(0, line_no - 4)
            context_end = min(len(lines), line_no + 3)
            findings.append({
                "pattern_id": pattern["id"],
                "algorithm": pattern["algorithm"],
                "category": pattern["category"],
                "file_path": file_path,
                "line_number": line_no,
                "context": lines[context_start:context_end],
                "quantum_risk": pattern["quantum_risk"],
                "severity": pattern["severity"],
                "confidence": score_confidence(lines[line_no - 1], file_path),
            })
    return findings
```

## 3. Confidence Scoring (analyzer.py)

```python
def score_confidence(line, file_path):
    stripped = line.strip()
    if stripped.startswith(("#", "//", "/*", "*")):
        return 0.3
    if "test" in file_path.lower() or "_test." in file_path:
        return 0.5
    return 1.0
```

## 4. Mosca's Algorithm (risk.py)

```python
DEFAULT_LIFETIMES = {
    "asymmetric": {"data_lifetime": 10, "migration_time": 3},
    "symmetric": {"data_lifetime": 5, "migration_time": 1},
    "hash": {"data_lifetime": 5, "migration_time": 1},
}
CRQC_ARRIVAL_ESTIMATE = 10  # years — cite NIST/industry estimates in your PPT

def mosca_score(category, crqc_arrival=CRQC_ARRIVAL_ESTIMATE):
    defaults = DEFAULT_LIFETIMES.get(category, {"data_lifetime": 5, "migration_time": 2})
    total_exposure = defaults["data_lifetime"] + defaults["migration_time"]
    if total_exposure > crqc_arrival:
        label = "CRITICAL - At risk now"
    elif total_exposure > crqc_arrival * 0.7:
        label = "HIGH - Migrate soon"
    else:
        label = "LOW - Monitor"
    return {**defaults, "crqc_arrival_years": crqc_arrival, "risk_label": label}
```

## 5. Migration Readiness Score (risk.py)

```python
WEIGHTS = {"SAFE": 1.0, "HYBRID": 0.8, "PARTIAL": 0.3, "VULNERABLE": 0.0, "CRITICAL": 0.0}

def readiness_score(findings):
    if not findings:
        return 100.0
    total = sum(WEIGHTS.get(f["quantum_risk"], 0) for f in findings)
    return round((total / len(findings)) * 100, 1)
```

## 6. FastAPI Endpoint Skeleton (api/routes.py)

```python
from fastapi import FastAPI, BackgroundTasks
import uuid

app = FastAPI()
SCANS = {}  # swap for SQLite once Phase 5 is stable

@app.post("/scan")
def start_scan(path: str, background_tasks: BackgroundTasks):
    scan_id = str(uuid.uuid4())
    SCANS[scan_id] = {"status": "running"}
    background_tasks.add_task(run_scan_job, scan_id, path)
    return {"scan_id": scan_id}

@app.get("/results/{scan_id}")
def get_results(scan_id: str):
    return SCANS.get(scan_id, {"error": "scan not found"})

@app.get("/cbom/{scan_id}")
def get_cbom(scan_id: str):
    scan = SCANS.get(scan_id)
    if not scan:
        return {"error": "scan not found"}
    return build_cbom(scan["findings"])
```

## 7. Streamlit Dashboard Skeleton (dashboard/app.py)

```python
import streamlit as st
import requests

st.set_page_config(page_title="ECDAT", layout="wide")
st.title("ECDAT — Enterprise Cryptographic Discovery & Analysis Tool")

path = st.text_input("Path to scan")
if st.button("Run Scan") and path:
    resp = requests.post("http://localhost:8000/scan", params={"path": path})
    scan_id = resp.json()["scan_id"]
    st.session_state["scan_id"] = scan_id

if "scan_id" in st.session_state:
    results = requests.get(f"http://localhost:8000/results/{st.session_state['scan_id']}").json()
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Migration Readiness Score", f"{results.get('migration_readiness_score', 0)}%")
    with col2:
        st.bar_chart(results.get("summary", {}))
    st.dataframe(results.get("findings", []))
```

## Build Order Reminder
Follow `Phases.md` strictly — don't build the dashboard (Phase 6) before the scanner (Phase 1) produces real, verified output. Wire real data through every layer before polishing any single layer.
