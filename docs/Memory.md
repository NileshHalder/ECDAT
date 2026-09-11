# Memory.md — ECDAT Build Progress Log

*This file is updated after every work session to record completed work, decisions, and system state.*

---

## Current State

- **Current phase:** Phase 7 — Polish & Demo Prep (Complete)
- **Last completed phase:** Phase 6 & Wireframe Suite — Full 9-Screen Dashboard & System Architecture Implementation
- **Blocking issues:** None (0 compile errors, clean syntax across app.py and backend)
- **Key features implemented:**
  - Full 9-Screen Wireframe Specification Suite in Streamlit (`dashboard/app.py`).
  - 8-Module Sidebar Navigation (`OVERVIEW`, `DISCOVERY`, `ASSET INTELLIGENCE`, `EVIDENCE GRAPH`, `BLIND SPOTS & RISK`, `MIGRATION & SIMULATOR`, `SYSTEM ARCHITECTURE`, `CBOM & COMPLIANCE`).
  - 3-Layer Enterprise Cryptographic Discovery & Correlation Architecture.
  - Page 8 Migration Priority Scoring Breakdown (`Why #1?` formula = Priority Score 95).
  - Page 9 What-If Migration Simulator with Scenario Comparison across `NOW`, `+6 MONTHS`, and `+12 MONTHS`.
  - Inventory Coverage Map Tree Hierarchy Map ("We know where we are blind.").
  - Evidence Graph Relationship Tree (`RSA-2048` -> `Source/Binary/Certificate` -> `Auth Service` -> `API Gateway` -> `Customer Data`).
  - 3x3 Quantum Risk vs Business Criticality Matrix Grid with cell highlight (73 Assets 🔴).
  - Web ZIP/Folder Drag-and-Drop upload backend API (`POST /scan/upload`).
  - CycloneDX CBOM Export (JSON).
  - 3 Demo Repositories (Legacy Fintech 0%, Hybrid Cloud 27%, Quantum-Safe Defense 100%).

---

## Log

### 2026-09-05 — Session 1: End-to-End Pipeline & Dashboard Styling
- **What was done:**
  - Verified and confirmed implementation of Phases 0 through 6 (Scanner Engine, Risk Classification, PQC Recommendations, CBOM Export, FastAPI backend, and Streamlit Dashboard).
  - Configured Streamlit custom theme ("Midnight Executive" dark palette with Inter and Fira Code fonts, custom border radii, and risk palette tokens).
  - Polished dashboard UI: upgraded risk level and severity filters to interactive Material Symbols `st.pills`, added `CRITICAL` risk level option, improved spacing, and cleaned up layout wrappers.
  - Synchronized `Tracker.md` and `Memory.md`.

### 2026-09-05 — Session 2: Smoke Testing, Demo Repos, Folder Upload & Chart Polish
- **What was done:**
  - Executed full automated smoke test against `samples/` (verified 8 findings, 37.5% score, CBOM output).
  - Built 3 realistic demo repositories under `demo_repos/`.
  - Added NIST Post-Quantum Cryptography patterns for ML-KEM, ML-DSA, and SLH-DSA to `scanner/patterns.py`.
  - Added folder upload capability (`POST /scan/upload`).
  - Polished Altair charts and standardized unit tests with `unittest.TestCase`.

### 2026-09-06 — Session 3: Complete Wireframe Suite (Pages 1–9) & Architecture
- **What was done:**
  - Implemented the complete 9-screen wireframe design suite in `dashboard/app.py`.
  - Added Page 1 Overview with 6 terminal KPI metrics, posture donut chart, asset risk bar chart, and top priorities table.
  - Added Page 2 & 3 Discovery view with 8-channel coverage bar chart, discovery state metrics, and the Enterprise Inventory Coverage tree hierarchy map with quote callout.
  - Added Page 4 Asset Intelligence deep-dive card (`CRYPTO-481`, attributes, verified evidence checklist, blind spot warnings).
  - Added Page 5 Evidence Graph tree mapping cipher to application data layer.
  - Added Page 6 Cryptographic Blind Spots (`88.4%` confidence, high risk blind spots, recommended actions).
  - Added Page 7 Risk Matrix 3x3 grid (`QUANTUM RISK` vs `BUSINESS CRITICALITY` with cell 73 🔴 callout).
  - Added Page 8 Migration Priority breakdown with weighted formula (`Why #1?` Priority Score 95).
  - Added Page 9 What-if Simulator with interactive `[ Replace now ]` action and timeline scenario comparison across `NOW`, `+6 MONTHS`, and `+12 MONTHS`.
  - Built System Architecture View detailing the 3-Layer Discovery, Normalization, and Asset Correlation Engine.
  - Built 8-module sidebar navigation for instant single-click access across all screens.
  - Updated all markdown documentation (`README.md`, `docs/Architecture.md`, `docs/Tracker.md`, `docs/Memory.md`, `docs/Walkthrough_Script.md`).

---

## Assumptions Register

1. **Dashboard framework**: Streamlit selected for fast iteration and clean integration with backend API.
2. **PQC Target Standards**: NIST FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA).
3. **Risk Categories**: 4-tier model (`CRITICAL`, `VULNERABLE`, `PARTIAL`, `SAFE`).
4. **Upload Handling**: ZIP files automatically extracted into temporary directories and removed after scan completion.
