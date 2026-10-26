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

## v0.9 — 2026-10-27
- Decisive vs procedural actions: legal citation required only for decisions affecting a message or data
- Deterministic retrieval intents per event kind; evidence IDs shown per decision

## v0.10 — 2026-10-27
- Self-consistency check: action vs the agent's own scam_likelihood rating -> CONFLICT -> named human
- Eval history: 1/4 -> 2/4 -> 3/4 (7b); unsafe passes tracked per run

## v1.0 — 2026-10-27
- Agents reach 4/4 vs pre-registered gold on the DEVELOPMENT scenario (5 measured iterations), 0 unsafe passes; stable over 3 repeats
- Self-consistency CONFLICT guard kept as a safety net
- Held-out evaluation pending (Act 4 + injects, gold pre-registered)

## v1.1 — 2026-10-27
- Reference-model check: qwen2.5:14b also 4/4 on dev gold, 0 unsafe passes (108s vs 46s for 7b)

## v1.2 — 2026-10-27
- Act 4 drift, inject library, judge console
- HELD-OUT v1 (pre-registered): 3/6 with qwen2.5:7b - 2 harmful (decisive actions grounded in soft law / out-of-mandate sources), 1 conservative miss
- Dev regression on A3 caught by CONFLICT guard (prompt sensitivity of 7b)

## v1.3 — 2026-10-27
- Safeguards: soft law can inform, never compel (binding basis required); competence needs a competence norm (ASSIGN_OVERRIDE_AUTHORITY -> logged gap G5)
- Severity split (harmful vs conservative) defined before held-out v2
- Held-out v1 moved to dev; held-out v2 pre-registered and committed before running
