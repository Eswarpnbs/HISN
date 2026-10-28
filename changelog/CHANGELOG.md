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

## v1.3 — 2026-10-27
- Safeguards: binding basis required for decisive actions; competence norm required (no norm -> logged gap)
- Results (qwen2.5:7b): dev 10/10, 0 harmful; HELD-OUT v2 (pre-registered) 3/4, 1 harmful (genuine urgent surgery SMS kept quarantined)
- G5 discovered by agents: no instrument assigns authority over operator AI filter changes
- Next: deterministic quarantine time limit for essential senders (evaluate on new held-out v3)

## v1.4 — 2026-10-27
- qwen2.5:14b (ITU reference): dev 8/10 (0 harmful, 1 conservative, 1 gate catch); HELD-OUT v2 4/4, 0 harmful
- 7b shows dev overfitting (10/10 dev vs 3/4 held-out); 14b adopted for final runs, video and booth

## v1.5 — 2026-10-27
- GAP ENGINE (deterministic, no LLM): loophole hunt over abstract tactic catalogue x filter states; counterfactual provision patches (P-AUTH, P-ROUTE, P-FRAUD + combos) measured by protection/access/MIZAN/officer reviews; load-bearing rule analysis
- No phishing text generated; comparators marked verify-text; patches await named human sign-off

## v1.6 — 2026-10-27
- Gap engine findings: P-AUTH closes G2 at zero access cost; blunt P-FRAUD closes G1 but lowers MIZAN (over-blocks legitimate businesses)
- P-VERIFIED (verified-sender lane) added after baseline revealed access harms; authentication enables both protection and access
- Load-bearing metric fixed (counts transfers not blocked); Art.13 rule load-bearing; removal is fail-visible (FLAG, not silent allow)

## v1.7 — 2026-10-27
- Essential-sender quarantine time limit (15 min): held essential messages go to a second human regardless of the agent's proposal (addresses held-out v2 harmful miss)
- Named human sign-off: refused without measured gap-engine evidence; approvals sealed in audit chain, recorded in ITU kb_decisions, written to a simulation-only overlay

## v1.7 — 2026-10-27
- Essential-sender quarantine time limit (15 min): held essential messages go to a second human regardless of the agent's proposal
- Named human sign-off: refused without measured gap-engine evidence; approvals sealed in audit chain, recorded in ITU kb_decisions, written to simulation-only overlay
- Demo: P-ROUTE+P-FRAUD refused (untested); P-AUTH+P-VERIFIED approved by synthetic officer

## v1.8 — 2026-10-27
- Offline single-file dashboard (docs/dashboard.html) generated from real runs: twins, agents, gap engine, evaluation, KB provenance, gap register, sign-offs

## v1.9 — 2026-10-27
- Dashboard: consequence-based colours using ground-truth labels hidden from agents/firewall; top scoreboard

## v2.0 — 2026-10-27
- Baselines comparison (B0 rules, B1 LLM-only, B2 RAG no gate, B3 full HISN) on same events and pre-registered gold: accuracy, harmful, out-of-mandate, unsupported citations, decisive actions without binding basis

## v2.0 — 2026-10-27
- Baselines (7b): B0 rules 11/14 (3 harmful), B1 LLM-only 6/14 (5 harmful, 20 unsupported citations), B2 RAG-no-gate 9/14 (5 harmful), B3 full HISN 13/14 (1 harmful, 0 unsupported, 0 unbound)
- Finding: an ungoverned LLM performed worse than fixed rules; RAG fixes evidence but not judgment; the gate fixes authority

## v2.1 — 2026-10-27
- kb/verify.py: all 7 sources verified against manifest hashes
- Retrieval eval (24 in-corpus + 2 out-of-corpus): Recall@5 22/24, Recall@1 16/24, MRR 0.78
- Calibration finding: similarity threshold does not transfer across embedding models; ranges overlap; 0.25 threshold not claimed as a safeguard

## v2.2 — 2026-10-27
- selftest.py: re-derives every headline number with provenance -> docs/headline_numbers.md
- setup.sh one-command setup; pinned requirements-lock.txt; README with quick start, results, repo map, limitations

## v2.3 — 2026-10-27
- Agent cards generated from code (ITU Sandbox catalogue style): 3 institutional agents, policy gateway, gap engine -> docs/agents.json + docs/agent_cards/

## v2.4 — 2026-10-28
- India pack: 3 hash-pinned records (DPDP Act 2023, Telecom Act 2023, TRAI TCCCPR consolidated), 9 verbatim clauses, NATIONAL_LAW basis
- Multi-country ingest (country from record prefix); India rule pack (DPDP s.16 transfer rule), firewall route binding (TCCCPR header register)
- run_interop.py: decision agreement, divergences, gap coverage per country -> docs/interoperability.md

## v2.4 — 2026-10-28
- India pack: DPDP Act 2023, Telecom Act 2023, TRAI TCCCPR consolidated (3 records, 9 verbatim clauses), NATIONAL_LAW basis
- Multi-country ingest; India rule pack (DPDP s.16) and route binding (TCCCPR header register)
- Interop: 56% decision agreement; health-data localisation conflict (UAE block vs India allow); forged senders: UAE human review vs India automatic block; 4 of 5 gaps shared or partial in both

## v2.5 — 2026-10-28
- Citizen verifier (D11 Inclusion): deterministic verdict, templates in EN/AR/HI/TE/UR/ML with per-language review status; optional English LLM explanation discarded if it contradicts the verdict; message text never logged

## v2.6 — 2026-10-28
- Synthetic SMS governance dataset (91 rows: 64 malicious, 27 legitimate) with ITU-style metadata.yaml; no personal data; imbalance documented

## v2.7 — 2026-10-28
- ITU game export: decisions.json (DecisionRecord fields + evidence), delegate narrative, causal preview via ITU CausalGraph (D10 reaches D7 0.5, D8 0.375, D5 0.13, D12 0.125, D6 0.013)

## v2.8 — 2026-10-28
- Real SMPP 3.4 listener: bind, submit_sm, enquire_link, unbind; GSM/UCS-2; governed firewall on the wire; authentication = bound account authorised for sender ID; quarantine -> Q-ids, block -> 0x45; text never logged
- Live demo: genuine delivered, exact spoof and lookalike rejected 0x45, Arabic UCS-2 government receipt delivered
