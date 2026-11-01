# HISN Health Authority (DoH / DHA) agent

**id** `hisn-health-authority` · **version** 1.0.0 · **type** institutional agent (retrieve / propose / log gap) · **added** 2026-11-01

Protects patients and governs health information under Federal Law No. 2 of 2019. Weighs patient harm from undelivered genuine health messages against scam risk. Quarantined essential health messages may only be released by a named human officer.

- **models**: ["qwen2.5:14b (reference) or qwen2.5:7b via Ollama", "nomic-embed-text (ITU reference ingest)"]
- **dataset**: HISN knowledge base: 16 hash-pinned records (UAE, India, Singapore; 1 Saudi historical draft), 38 verbatim clauses (kb/manifest.csv)
- **tools**: ["retrieve (ITU KnowledgeBase, UAE filter, clause-first)", "propose action", "log gap"]
- **event kinds**: ["complaint", "escalation", "override_dispute"]
- **actions**: ["KEEP_QUARANTINED", "LOG_GAP", "ORDER_OPERATOR_WHITELIST", "RECOMMEND_RELEASE_BY_NAMED_OFFICER", "REFER_TO_TDRA", "REQUEST_INFO"]
- **decisive actions**: ["KEEP_QUARANTINED", "ORDER_OPERATOR_WHITELIST", "RECOMMEND_RELEASE_BY_NAMED_OFFICER"]
- **competence norms**: {"ORDER_OPERATOR_WHITELIST": ["UAE-TDRA-"]}
- **guardrail**: Evidence-or-gap: cites only retrieved evidence; decisive actions need a binding source (CABINET_RESOLUTION, FEDERAL_LAW, NATIONAL_LAW, REGULATOR_POLICY) within competence; actions limited by mandate and event kind; self-consistency check (action vs own scam-likelihood rating -> CONFLICT -> named human); proposes only; every decision sealed in a SHA-256 hash-chained log.
- **mapping**: {"y3172_nodes": ["P", "MLFO"], "readiness": ["D10 AI & Policies (d10_m02, d10_m06, d10_m09)", "D7 Strategy Alignment (d7_m01)"]}
- **evaluation**: Pre-registered gold (dev + held-out), see docs/eval_log_v3.md and docs/baselines.md
- **data**: Synthetic only
- **licence**: Apache-2.0
