# HISN Coordinator (MLFO, deterministic, no LLM)

**id** `hisn-coordinator` · **version** 1.0.0 · **type** machine learning function orchestrator (Y.3172 MLFO) · **added** 2026-10-31

Advances the simulated clock, releases time-gated role-scoped events, routes escalations, routes referrals once between authorities (audited), enforces clinical-tier second review and emergency age.

- **dataset**: scenarios/crisis_exploit.yaml and scenarios/injects/
- **tools**: ["dispatch events", "route escalation", "route referral", "second review", "emergency state"]
- **guardrail**: Pre-agreed rules only; no re-referral; essential messages never silently dropped.
- **mapping**: {"y3172_nodes": ["MLFO"], "readiness": ["D7 (d7_m01 Coordination Level)"]}
- **evaluation**: tests/test_referrals.py, tests/test_tiers.py
- **data**: Synthetic only
- **licence**: Apache-2.0
