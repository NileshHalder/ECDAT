# Architecture.md — ECDAT Architecture

## System Architecture

ECDAT implements a 3-Layer Enterprise Cryptographic Discovery & Correlation Engine:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 ENTERPRISE ENVIRONMENT                                 │
│ Source Code | Binaries | Libraries | Containers | Network | Cloud | Certs | Firmware | HSM │
└──────────────────────────────────────────────────┬─────────────────────────────────────┘
                                                   │
                                                   ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        1. DISCOVERY & COLLECTION LAYER                                 │
│ Static Analyzer | Binary Analyzer | Container Scanner | Network/TLS Scanner | Certs      │
└──────────────────────────────────────────────────┬─────────────────────────────────────┘
                                                   │
                                                   ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        2. EVIDENCE NORMALIZATION LAYER                                 │
│ Normalize heterogeneous findings into a common crypto schema                          │
│ Algorithm | Protocol | Certificate | Library | Key Metadata | Location | Version | Method│
└──────────────────────────────────────────────────┬─────────────────────────────────────┘
                                                   │
                                                   ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                    ★ 3. CRYPTO ASSET CORRELATION ENGINE ★                              │
│ Merge → Deduplicate → Correlate → Build Relationships                                 │
│ Source Evidence + Binary Evidence + Network Evidence + Certificate → ONE ASSET       │
│ Dependency / Usage / Implementation Graph                                             │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Scanner engine | Python 3.11+ (`re`, `ast` modules) | Fast, multi-language AST + regex scanning engine |
| Backend API | FastAPI | Async, auto-generated OpenAPI docs, handles local & upload scans |
| Database | SQLite (`ecdat.db`) | Zero-setup relational persistence for scans and findings |
| Dashboard | Streamlit + Altair | High-density cyber command center with 8 sidebar navigation modules |
| CBOM format | CycloneDX Cryptographic BOM (JSON) | Industry-standard supply chain compliance reporting |

---

## Dashboard Navigation Structure (8 Modules / 9 Wireframe Screens)

```
ecdat/dashboard/app.py
├── OVERVIEW (Page 1)
│   ├── Executive Readiness Score Callout
│   ├── 6 Terminal KPI Metric Cards
│   ├── Cryptographic Posture Donut Chart
│   ├── Risk by Asset Type Bar Chart
│   └── Top Migration Priorities Table + Code Context Drill-down
├── DISCOVERY (Pages 2 & 3)
│   ├── 8-Channel Discovery Coverage Bar Chart
│   ├── Discovery State Metrics (Confirmed, Probable, Possible, Unknown)
│   └── Enterprise Inventory Coverage Map Tree Hierarchy & Quote Callout
├── ASSET INTELLIGENCE (Page 4)
│   └── Deep-Dive Asset Metadata Card (Attributes, Evidence Checklist, Blind Spots)
├── EVIDENCE GRAPH (Page 5)
│   └── End-to-End Relationship Tree (Cipher -> Layer -> Service -> API Gateway -> Data)
├── BLIND SPOTS & RISK (Pages 6 & 7)
│   ├── Cryptographic Blind Spots & Discovery Confidence (88.4%)
│   └── 3x3 Quantum Risk vs Business Criticality Matrix Grid
├── MIGRATION & SIMULATOR (Pages 8 & 9)
│   ├── Page 8: Weighted Migration Priority Scoring Breakdown (Priority Score 95)
│   └── Page 9: Interactive What-If Migration Simulator & Scenario Timeline
├── SYSTEM ARCHITECTURE
│   └── 3-Layer Enterprise Collection & Correlation Engine Diagram
└── CBOM & COMPLIANCE
    └── CycloneDX CBOM Report Viewer & Download Button
```

---

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/scan` | Trigger a scan on a directory path |
| POST | `/scan/upload` | Upload ZIP archive or code files for scanning |
| GET | `/results/{scan_id}` | Fetch findings, score, and summary stats |
| GET | `/cbom/{scan_id}` | Export CycloneDX CBOM JSON |
| GET | `/health` | Liveness health check |
