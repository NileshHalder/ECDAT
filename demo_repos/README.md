# ECDAT Demo Repositories

These 3 demo repositories are curated for live demonstrations to showcase the entire spectrum of ECDAT's cryptographic discovery and migration readiness scoring capabilities.

---

## 1. Legacy Fintech Core (High Quantum Risk — Score: 0.0%)
- **Path to paste into dashboard**: `d:\ecdat_starter\ecdat\demo_repos\1_legacy_fintech_core`
- **Languages**: Python, Java, JavaScript
- **Algorithms Detected**:
  - `RSA 2048` (Critical / Asymmetric) -> Replacement: **NIST FIPS 203 ML-KEM (Kyber)**
  - `Diffie-Hellman` (Critical / Asymmetric) -> Replacement: **NIST FIPS 203 ML-KEM**
  - `DES` & `3DES` (High / Symmetric) -> Replacement: **AES-256**
  - `MD5` & `SHA-1` (High / Hash) -> Replacement: **SHA-3 / SHA-256**
- **Badge**: :red-badge[High risk — act now]

---

## 2. Hybrid Cloud Microservice (Moderate Risk — Score: 26.9%)
- **Path to paste into dashboard**: `d:\ecdat_starter\ecdat\demo_repos\2_hybrid_cloud_microservice`
- **Languages**: Python
- **Algorithms Detected**:
  - `ECDSA (NIST P-256)` (Critical / Asymmetric) -> Replacement: **NIST FIPS 204 ML-DSA (Dilithium)**
  - `AES-GCM` (Medium / Symmetric) -> Replacement: **AES-256 key size validation**
  - `ChaCha20` (Low / Symmetric) -> Adequate 256-bit strength
  - `HMAC-SHA-256` & `SHA-256` (Info / Hash & MAC)
  - `PBKDF2` (Low / KDF) -> Replacement: **Argon2id**
- **Badge**: :red-badge[High risk — act now] / :orange-badge[Moderate risk]

---

## 3. Quantum-Ready Defense App (Quantum-Safe — Score: 100.0%)
- **Path to paste into dashboard**: `d:\ecdat_starter\ecdat\demo_repos\3_quantum_ready_defense_app`
- **Languages**: Python
- **Algorithms Detected**:
  - `ML-KEM (Kyber)` -> **NIST FIPS 203 Compliant**
  - `ML-DSA (Dilithium)` -> **NIST FIPS 204 Compliant**
  - `SLH-DSA (SPHINCS+)` -> **NIST FIPS 205 Compliant**
  - `SHA-3 (Keccak)` -> **Safe Hash**
  - `Argon2id` & `bcrypt` -> **Safe Memory-Hard KDFs**
- **Badge**: :green-badge[Low quantum risk]
