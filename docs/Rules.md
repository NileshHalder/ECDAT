# Rules.md — Boundaries for the AI while building ECDAT

## Libraries — Use
- **Backend:** `fastapi`, `uvicorn`, `pydantic`, `sqlite3` (stdlib) or `sqlalchemy` if it simplifies things
- **Scanner:** stdlib `re`, `ast`, `os`, `pathlib` — avoid heavy dependencies for the core scanning logic
- **Dashboard:** `streamlit` + `plotly` or `altair` for charts (if going the Streamlit route)
- **Testing:** `pytest`

## Libraries — Avoid
- Do **not** pull in a live blockchain/crypto-wallet library — this project is about detecting cryptography usage, not implementing cryptography
- Do **not** use any library that requires a paid API key or external network call for core functionality (scanning must work fully offline — this matches the NTRO air-gapped/offline expectation)
- Avoid heavyweight ML frameworks (TensorFlow/PyTorch) unless a specific stretch feature genuinely needs them — this is a rule-based + pattern-matching tool at its core, not an ML classification problem

## Error Handling
- The scanner must **never crash the whole run** because one file is unreadable, binary, or malformed — catch and skip with a logged warning, continue scanning the rest
- API endpoints must return clear JSON error responses (`{"error": "..."}`) with appropriate HTTP status codes, not raw stack traces
- If a scan path doesn't exist or is empty, return a friendly error, not a 500

## Code Style / Conventions
- Python: follow PEP 8, use type hints on function signatures
- Keep scanner logic **pure functions** where possible (input → output, no hidden state) — makes it testable and easier for the AI to reason about in isolation
- Every new regex pattern added to `patterns.py` must include: `id`, `algorithm`, `category`, `regex`, `quantum_risk`, `severity` — no partial pattern entries

## What the AI Should NOT Do
- Do not silently change the folder structure defined in `Architecture.md` — if a change is needed, flag it first
- Do not invent cryptographic risk classifications not grounded in the actual quantum-vulnerability facts (RSA/ECC/DH = VULNERABLE via Shor's; AES/SHA = PARTIAL via Grover's only if undersized) — this is a common mistake that breaks credibility, treat it as a hard rule, not a guess
- Do not fabricate scan results or hardcode fake "demo" findings inside the core scanner logic — sample vulnerable files belong in `samples/`, kept clearly separate from production logic
- Do not add authentication/login systems — explicitly out of scope for the hackathon MVP
- Do not skip writing to `Memory.md` after completing a phase — see `Memory.md` for the update protocol

## When Stuck / Ambiguous
- If a requirement in `PRD.md` is unclear, make the most reasonable assumption, state it explicitly in `Memory.md`, and continue — don't block progress waiting for clarification
- If a phase in `Phases.md` turns out to be bigger than expected, split it into sub-steps rather than silently cutting scope — flag the scope change in `Tracker.md`
