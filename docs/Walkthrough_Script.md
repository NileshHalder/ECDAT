# ECDAT — 60–90 Second Live Presentation Script

*Prepared for SIH 2026 Evaluation & Live Demo · Problem Statement SIH26164 (NTRO)*

---

## 🎙️ Spoken Script (Timer: ~75 seconds)

### [00:00 - 00:15] The Quantum Threat Hook
> *"Respected judges, quantum computing will break RSA, ECC, and Diffie-Hellman encryption via Shor's algorithm. Organizations face an immediate threat: **'Harvest Now, Decrypt Later'**. But before an enterprise can migrate to Post-Quantum Cryptography, they must first know: **where is their vulnerable crypto?** That is why we built **ECDAT** — the Enterprise Cryptographic Discovery & Analysis Tool."*

---

### [00:15 - 00:35] Live Scan & Multi-Channel Discovery
> *(Action: Point to `demo_repos/1_legacy_fintech_core` or drag & drop a ZIP folder in the dashboard sidebar)*
>
> *"With ECDAT, an organization points to a repository or drags & drops their zipped codebase. 
> Within seconds, our scanner parses multi-language codebases — Python, Java, JavaScript, C/C++ — identifying every cryptographic primitive and mapping discovery coverage across source code, binaries, containers, network endpoints, and cloud workloads."*

---

### [00:35 - 00:55] Evidence Graph & Migration Priority Scoring
> *(Action: Click 'ASSET INTELLIGENCE', 'EVIDENCE GRAPH', and 'MIGRATION & SIMULATOR' in sidebar)*
>
> *"Instead of simple flat lists, ECDAT constructs an end-to-end **Evidence Graph** mapping cipher findings from source code up to sensitive customer data layers.
> Our **Migration Priority Engine** quantifies quantum risk using **Mosca's theorem**, calculating an explicit Priority Score — showing judges not just what is vulnerable, but exactly **WHY #1 is prioritized** with NIST FIPS 203 ML-KEM migration specs."*

---

### [00:55 - 01:15] What-If Simulator & CBOM Compliance
> *(Action: Demonstrate 'What-if Simulator' scenario timeline and click 'Download CBOM JSON Report')*
>
> *"Furthermore, ECDAT features an interactive **What-If Migration Simulator** comparing risk, cost, and exposure across 6 and 12-month timelines. 
> Finally, with one click, ECDAT exports a standardized **CycloneDX Cryptographic Bill of Materials (CBOM)** ready for NTRO compliance."*

---

## 📊 Key Differentiator Slide Matrix

| Feature | CryptoScan (CSNP) | IBM CBOMkit | ECDAT (Our Solution) |
|---|---|---|---|
| **GUI Command Center** | ❌ CLI only | ❌ CLI only | ✅ **Interactive 8-Module Web Dashboard** (Streamlit / FastAPI) |
| **Mosca's Theorem Scoring** | ❌ None | ❌ None | ✅ **Automated Migration Readiness Score (0–100%)** |
| **NIST PQC Standards Alignment** | ⚠️ Generic advice | ⚠️ Generic advice | ✅ **Explicit NIST FIPS 203/204/205 Mapping** |
| **Evidence Graph & Hierarchy Tree** | ❌ None | ❌ None | ✅ **End-to-End Cipher-to-Data Evidence Graph** |
| **Migration Priority Engine** | ❌ None | ❌ None | ✅ **Weighted Priority Formula Scoring (Why #1?)** |
| **What-If Migration Simulator** | ❌ None | ❌ None | ✅ **Interactive Scenario Timeline & Cost/Risk Simulator** |
| **CBOM Export** | ❌ None | ✅ CBOM | ✅ **CycloneDX-Compliant CryptoBOM JSON** |
| **Folder / ZIP Drag & Drop** | ❌ | ❌ | ✅ **In-Browser ZIP Unpacking & Scanning** |
