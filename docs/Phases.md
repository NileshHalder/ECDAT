# Phases.md — ECDAT Build Plan

Each phase should be fully working and testable before moving to the next. Do not start Phase N+1 until Phase N's checklist is complete.

## Phase 0 — Setup
- [ ] Initialize repo with the folder structure from `Architecture.md`
- [ ] Set up `requirements.txt` with core dependencies
- [ ] Create 3-5 sample files in `samples/` containing known vulnerable + safe crypto usage (Python + Java + JS), for testing the scanner against known-correct results

## Phase 1 — Core Scanner Engine
- [ ] Build `walker.py`: recursively walk a directory, skip `.git/`, `node_modules/`, `vendor/`, binary files
- [ ] Build `patterns.py`: define 15-20 initial regex patterns covering RSA, ECC, AES, DES, MD5, SHA-1/256, HMAC (expand later)
- [ ] Build `analyzer.py`: match patterns against file contents, extract file path + line number + 3 lines of context
- [ ] **Test:** run scanner against `samples/` and manually verify every expected finding is caught, with no crashes

## Phase 2 — Risk Classification
- [ ] Build `risk.py`: tag each finding VULNERABLE / PARTIAL / SAFE based on algorithm type
- [ ] Implement Mosca's algorithm scoring function with sensible default lifetime/migration-time values per algorithm category
- [ ] Compute an overall Migration Readiness Score for a full scan
- [ ] **Test:** verify RSA → VULNERABLE, AES-256 → SAFE/PARTIAL correctly, confirm the readiness score changes sensibly when you add/remove vulnerable findings

## Phase 3 — PQC Recommendation Engine
- [ ] Build `recommend.py` with the lookup table (RSA→ML-KEM, ECDSA→ML-DSA, weak AES/SHA→larger size)
- [ ] Attach a recommendation to every VULNERABLE/PARTIAL finding
- [ ] **Test:** confirm every non-SAFE finding has a non-null recommendation

## Phase 4 — CBOM Export
- [ ] Build `cbom/export.py`: convert a list of findings into the CycloneDX-style JSON structure
- [ ] Add a way to trigger this (CLI flag or API endpoint)
- [ ] **Test:** validate the JSON output is well-formed and contains all required fields

## Phase 5 — Backend API
- [ ] Build FastAPI app with `/scan`, `/results/{scan_id}`, `/cbom/{scan_id}`, `/health`
- [ ] Wire scanner + risk + recommend + cbom modules together behind these endpoints
- [ ] Store results in SQLite (or in-memory dict if time is very short — SQLite preferred)
- [ ] **Test:** hit each endpoint with `curl` or FastAPI's built-in `/docs` UI, confirm correct responses

## Phase 6 — Dashboard
- [ ] Build the summary view: Migration Readiness Score callout + risk breakdown chart
- [ ] Build the findings table: sortable/filterable by severity, algorithm, file
- [ ] Build the drill-down: click a finding → see code context + recommendation
- [ ] Add CBOM export/download button
- [ ] **Test:** run a full scan through the dashboard end-to-end, confirm no broken states

## Phase 7 — Polish & Demo Prep
- [ ] Visual pass on the dashboard (see `Design.md`)
- [ ] Prepare 2-3 demo repos with a good mix of findings (not too few, not overwhelming) for the live demo
- [ ] Write a 60-90 second walkthrough script for the judges
- [ ] Update `PRD.md`'s "Known Prior Art" section into your pitch deck's differentiation slide

## Stretch Phases (only if ahead of schedule)
- [ ] Confidence scoring (lower confidence for comments/test files)
- [ ] Certificate (X.509) scanning
- [ ] Basic GitHub Action / CI example
- [ ] Docker packaging
