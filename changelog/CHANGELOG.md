# Changelog
## v0.1 — 2026-10-25
- Verdict / Action / Basis / Zone enums
- SHA-256 hash-chained audit log with verify()
- Deterministic policy gateway: unverified citations never block; uncovered events become gap candidates
- First UAE rule (health data localisation), citation pending verification

## v0.2 — 2026-10-26
- UAE corpus (5 records, 98 chunks + 2 verbatim clauses) ingested via unmodified ITU ingest pipeline
- Retrieval test: Federal Law 2/2019 Art.13 at rank 1

## v0.3 — 2026-10-26
- ITU-compatible clause metadata: numeric dimension_id, factor, official metric IDs (d10_m10, d10_m06), Y.3172 node tags
- ITU use-case corpus loaded (kb_usecase: 1779 chunks)
- Verified: ITU search_by_dimension(10) returns Art.13 and Art.24
