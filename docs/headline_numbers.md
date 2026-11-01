# Headline numbers (selftest, 2026-11-01 10:53)

Every figure in the report traces to a row here.

| figure | value | produced by |
|---|---|---|
| Unit tests | 74 passed, 2 warnings | `python -m pytest -q` |
| Knowledge-base sources match manifest hashes | yes | `python kb/verify.py` |
| Hash-pinned records / verbatim clauses | 15 / 37 | `kb/manifest.csv, kb/clauses/clauses.yaml` |
| Legitimate essential messages silently lost | ungoverned 4 -> HISN 0 | `twin run (all injects, 15-min limit)` |
| Offshore health-data transfers not blocked | ungoverned 2 -> HISN 0 | `twin run (all injects)` |
| Audit chains verify (governed / ungoverned) | True / True | `AuditLog.verify()` |
| Gap engine baseline (protection/access/MIZAN) | 86.7/66.7/76.7 | `app/gapengine (deterministic)` |
| P-AUTH+P-VERIFIED (protection/access/MIZAN) | 96.7/91.7/94.2 | `app/gapengine (deterministic)` |
| P-FRAUD alone MIZAN change | -0.5 | `app/gapengine (deterministic)` |
| Art.13 rule load-bearing (transfers not blocked when removed) | 2 | `rule-removal re-run` |
| Retrieval (HISN clause-first) | Recall@1 22/46 | Recall@5 41/46 | `python kb/eval_retrieval.py` |
| Agents qwen2.5:14b dev (accuracy / harmful) | 9/10 (60-98%) / 0 | `docs/eval_log_v3.md (2026-11-01 10:29)` |
| Agents qwen2.5:14b heldout_v2 (accuracy / harmful) | 4/4 (51-100%) / 0 | `docs/eval_log_v3.md (2026-11-01 10:29)` |
| Agents qwen2.5:14b heldout_v3 (accuracy / harmful) | 1/2 (9-91%) / 0 | `docs/eval_log_v3.md (2026-11-01 10:29)` |
| Baseline B0 fixed rules (no AI) | acc 12/16 (51-90%) | held-out v2 3/4 (30-95%) | held-out v3 1/2 (9-91%) | harmful 4 | unsupported 0 | `docs/baselines.md` |
| Baseline B1 LLM only (no KB, no gate) | acc 8/16 (28-72%) | held-out v2 1/4 (5-70%) | held-out v3 1/2 (9-91%) | harmful 6 | unsupported 19 | `docs/baselines.md` |
| Baseline B2 LLM + KB (RAG, no gate) | acc 10/16 (39-82%) | held-out v2 2/4 (15-85%) | held-out v3 1/2 (9-91%) | harmful 6 | unsupported 0 | `docs/baselines.md` |
| Baseline B3 full HISN (RAG + 5 safeguar | acc 14/16 (64-97%) | held-out v2 4/4 (51-100%) | held-out v3 1/2 (9-91%) | harmful 0 | unsupported 0 | `docs/baselines.md` |
| Network evidence: relative risk heat / rain | 0.54 / 4.49 (985308 link-days, proxy) | `tools/build_rlf_profile.py` |
| UAE-India decision agreement | 56% | `python run_interop.py` |
| Citizen verifier languages / reviewed | 6 / 3 | `kb/verifier_templates.yaml` |
| Wind tunnel: emergency offshore as regulation | DO NOT ISSUE AS DRAFTED | unresolved conflicts 1 | `app/windtunnel (deterministic)` |
| Wind tunnel: emergency offshore as health_authority_resolution | READY FOR NAMED HUMAN REVIEW | unresolved conflicts 0 | `app/windtunnel (deterministic)` |
| Wind tunnel: authentication + verified lane | READY FOR NAMED HUMAN REVIEW | fixed ['I3', 'I7'] broken [] | interop 55->45% | `app/windtunnel (deterministic)` |
