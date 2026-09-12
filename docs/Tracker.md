# Tracker.md — ECDAT Task Tracker

*Lightweight, task-level tracker — complements `Memory.md` (which logs context/decisions) and `Phases.md` (which defines the plan). Status: what's done, in progress, blocked, or todo.*

## Status Legend
🔴 Not started · 🟡 In progress · 🟢 Done · ⛔ Blocked

## Phase 0 — Setup
| Task | Status | Owner | Notes |
|---|---|---|---|
| Repo + folder structure | 🟢 | AI | All dirs created per Architecture.md |
| requirements.txt | 🟢 | AI | Core deps: fastapi, uvicorn, streamlit, altair, requests, pandas |
| Sample vulnerable code files | 🟢 | AI | `samples/sample_vulnerable.py`, `sample_vulnerable.java`, `sample_safe.py` |

## Phase 1 — Scanner Engine
| Task | Status | Owner | Notes |
|---|---|---|---|
| walker.py | 🟢 | AI | Recursively walks dirs, skips .git/node_modules/vendor/binaries |
| patterns.py (15-20 patterns) | 🟢 | AI | RSA, ECC, AES, DES, MD5, SHA-1/256, HMAC, DH, DSA, ML-KEM, ML-DSA |
| analyzer.py | 🟢 | AI | Extracts file path, line number, 3-line context per finding |
| Manual test against samples/ | 🟢 | AI | Verified end-to-end (8 findings caught across Python and Java) |

## Phase 2 — Risk Classification
| Task | Status | Owner | Notes |
|---|---|---|---|
| risk.py — VULNERABLE/PARTIAL/SAFE tagging | 🟢 | AI | All three levels implemented |
| Mosca's algorithm function | 🟢 | AI | Default lifetime/migration-time values per algorithm category |
| Migration Readiness Score function | 🟢 | AI | Returns 0-100 score (calculated 37.5% for samples) |
| Test against known cases | 🟢 | AI | Verified with automated test script |

## Phase 3 — PQC Recommendation
| Task | Status | Owner | Notes |
|---|---|---|---|
| recommend.py lookup table | 🟢 | AI | RSA→ML-KEM, ECDSA→ML-DSA, weak AES/SHA→larger size |
| Attach recommendation to findings | 🟢 | AI | Wired into analyzer output |

## Phase 4 — CBOM Export
| Task | Status | Owner | Notes |
|---|---|---|---|
| cbom/export.py | 🟢 | AI | CycloneDX-style JSON structure |
| Validate JSON output | 🟢 | AI | Verified 6 algorithm components generated properly |

## Phase 5 — Backend API
| Task | Status | Owner | Notes |
|---|---|---|---|
| FastAPI app skeleton | 🟢 | AI | `api/main.py` + `routes.py` + `db.py` |
| /scan endpoint | 🟢 | AI | POST /scan?path=... triggers scanner |
| /scan/upload endpoint | 🟢 | AI | POST /scan/upload unpacks ZIP archive or multi-files and triggers scanner |
| /results endpoint | 🟢 | AI | GET /results/{scan_id} |
| /cbom endpoint | 🟢 | AI | GET /cbom/{scan_id} |
| SQLite storage | 🟢 | AI | `api/db.py` with `ecdat.db` |

## Phase 6 — Dashboard (Full 9-Wireframe Suite)
| Task | Status | Owner | Notes |
|---|---|---|---|
| Page 1 — Overview & Posture | 🟢 | AI | Readiness score, 6 KPI cards, donut chart, asset risk bars, top priorities |
| Page 2 — Discovery & Coverage | 🟢 | AI | 8 channel bars, state metrics, Inventory map tree |
| Page 3 — Inventory & Domain Map | 🟢 | AI | Enterprise domain matrix & asset distribution |
| Page 4 — Asset Intelligence | 🟢 | AI | Deep-dive metadata card, evidence checklist, blind spot warnings |
| Page 5 — Evidence Graph | 🟢 | AI | End-to-end cipher-to-data relationship graph tree |
| Page 6 — Cryptographic Blind Spots | 🟢 | AI | Overall discovery confidence (88.4%), blind spots table, recommended actions |
| Page 7 — Risk Matrix | 🟢 | AI | 3x3 Quantum Risk vs Business Criticality matrix grid with cell 73 🔴 callout |
| Page 8 — Migration Priority | 🟢 | AI | Weighted priority scoring breakdown (Priority Score 95) |
| Page 9 — What-if Simulator | 🟢 | AI | Interactive `[ Replace now ]` simulator & scenario timeline comparison |
| System Architecture View | 🟢 | AI | 3-Layer collection, normalization & correlation engine flow |
| CBOM Export & Compliance | 🟢 | AI | CycloneDX JSON report viewer & download button |
| 8-Module Sidebar Navigation | 🟢 | AI | Single-click sidebar navigation bar |

## Phase 7 — Polish & Demo Prep
| Task | Status | Owner | Notes |
|---|---|---|---|
| Demo repos prepared | 🟢 | AI | 3 realistic repos (0% legacy fintech, 27% hybrid cloud, 100% quantum-safe defense) |
| Walkthrough script written | 🟢 | AI | 60-90 sec judge script in `docs/Walkthrough_Script.md` |
| Differentiation slide updated | 🟢 | AI | Feature comparison matrix in `docs/Walkthrough_Script.md` & `README.md` |
| Full end-to-end dry run | 🟢 | AI | Verified via automated test suite against all demo repos |
