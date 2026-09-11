# PRD.md — ECDAT Project Requirements Document

## Project Name
**ECDAT** — Enterprise Cryptographic Discovery & Analysis Tool
*(SIH 2026, Problem Statement SIH26164, Organization: NTRO)*

## One-Line Summary
A tool that scans an organization's codebase to discover every cryptographic asset in use, assesses which ones are vulnerable to quantum computing attacks, and recommends post-quantum-safe replacements — all shown through an interactive visual dashboard.

## Problem Statement (Source)
Transitioning to Post-Quantum Cryptography (PQC) requires preparedness, risk assessment, and investment. The critical first step is **discovery and inventory** of cryptographic artefacts (algorithms, keys, certificates, protocols, libraries) across an organization's applications and infrastructure — most organizations currently have no visibility into this.

## Target Users
- **Primary:** Security teams / CISOs at organizations preparing for PQC migration (government agencies, enterprises with compliance obligations)
- **Secondary (for demo/judging):** NTRO evaluators assessing technical feasibility and completeness against the PS requirements
- **Tertiary:** Developers who need to know which lines of their code use vulnerable cryptography

## Core Features (Must-Have — MVP for hackathon)

1. **Cryptographic Discovery Scanner**
   - Scan a local directory or uploaded codebase (Python, Java, JavaScript to start)
   - Detect algorithm usage: RSA, ECC/ECDSA, Diffie-Hellman, AES, DES/3DES, ChaCha20, MD5, SHA-1/256/3, HMAC, PBKDF2/bcrypt/Argon2
   - Capture file path, line number, and surrounding code context for every finding

2. **Quantum Risk Classification**
   - Classify every finding: VULNERABLE (broken by Shor's algorithm), PARTIAL (weakened by Grover's algorithm), SAFE
   - Apply Mosca's algorithm logic (data lifetime + migration time vs. estimated quantum-computer arrival) to assign urgency

3. **PQC Recommendation Engine**
   - Map each vulnerable algorithm to its NIST-standardized replacement (ML-KEM/Kyber, ML-DSA/Dilithium, etc.)

4. **CBOM Export**
   - Generate a Cryptographic Bill of Materials in a CycloneDX-style JSON format

5. **Interactive Dashboard (key differentiator)**
   - Migration Readiness Score (overall %, big visual callout)
   - Risk breakdown chart (Safe / Partial / Vulnerable / Critical counts)
   - Sortable/filterable findings table
   - Drill-down view: code context + recommended replacement per finding
   - Export CBOM report button

## Nice-to-Have (Stretch goals, if time permits)
- Certificate (X.509) expiry/signature-algorithm scanning
- Container/binary scanning (currently unsolved even by prior art — flag as future work if not attempted)
- CI/CD integration example (GitHub Action)
- Confidence scoring (lower confidence for matches in comments/test files)

## Explicitly Out of Scope (for hackathon timeframe)
- Live/production cloud KMS scanning (AWS/Azure/GCP)
- Full binary disassembly analysis
- Multi-tenant user accounts / authentication system
- Real-time continuous monitoring (this is a point-in-time scan tool)

## Success Criteria (how you'll know it's "done")
- Can scan a sample multi-language repo and produce at least 20+ correctly classified findings
- Dashboard loads scan results and renders the risk breakdown + findings table without errors
- CBOM JSON export is valid and downloadable
- Can explain, live, why any given finding was classified the way it was (defensibility in Q&A)

## Known Prior Art (be upfront about this in the pitch)
- **CryptoScan (CSNP, open-source, Go, CLI-only)** — github.com/csnp/cryptoscan — does most of the scanning/classification already; **has no GUI**. ECDAT's differentiation is the visual dashboard + Mosca's-algorithm-based prioritization.
- **IBM CBOMkit** (open-source) and **IBM Guardium/Quantum Safe Explorer** (commercial) — similar discovery tools.
- **Keyfactor AgileSec Analytics** — commercial equivalent with crypto-agility focus.
