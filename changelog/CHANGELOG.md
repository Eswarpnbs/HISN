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

## v0.4 — 2026-10-26
- Event bus: time-gated, role-scoped visibility (tested: no agent sees the future)
- Deterministic coordinator (MLFO) playing Crisis Exploit Acts 1-3
- submit_sm-compatible SMS firewall stub; essential senders never silently dropped when governed
- Governed vs ungoverned twin: first Policy-ON/OFF comparison

## v0.5 — 2026-10-26
- KB: 7 hash-pinned records, 13 verbatim clauses (TDRA UEC v1.1, PDPL Art.2, Law 2/2019 Art.1/13/16/24, AI Charter P2/P5/P6/P7)
- Retrieval: 3/3 policy questions return the exact clause at rank 1
- Gap register G1-G4 (instrument-verified; second pass pending)

## v0.7 — 2026-10-27
- Agents: actions constrained by event kind; full firewall facts on escalation; clause-first retrieval
- Pre-registered gold expectations; run reports agent accuracy and gate rejections
- First live run (7b) exposed relevant-citation and consistency failures; fixes applied
