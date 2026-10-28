# HISN Federal Authority for AI and Data agent

**id** `hisn-ai-data-authority` · **version** 1.0.0 · **type** institutional agent (retrieve / propose / log gap) · **added** 2026-10-29

Oversees AI and data governance, digital government and cross-border data questions. Its mandates are transitional since June 2026.

- **models**: ["qwen2.5:14b (reference) or qwen2.5:7b via Ollama", "nomic-embed-text (ITU reference ingest)"]
- **dataset**: UAE knowledge base: 10 hash-pinned records (UAE, India, Singapore), 32 verbatim clauses (kb/manifest.csv)
- **tools**: ["retrieve (ITU KnowledgeBase, UAE filter, clause-first)", "propose action", "log gap"]
- **event kinds**: ["data_transfer", "escalation", "override_dispute"]
- **actions**: ["ASSIGN_OVERRIDE_AUTHORITY", "KEEP_QUARANTINED", "LOG_GAP", "RECOMMEND_RELEASE_BY_NAMED_OFFICER", "REQUEST_INFO", "UPHOLD_BLOCK"]
- **decisive actions**: ["ASSIGN_OVERRIDE_AUTHORITY", "KEEP_QUARANTINED", "RECOMMEND_RELEASE_BY_NAMED_OFFICER", "UPHOLD_BLOCK"]
- **competence norms**: {"ASSIGN_OVERRIDE_AUTHORITY": "none in UAE pack -> logged gap", "UPHOLD_BLOCK": ["UAE-FL-", "UAE-PDPL-", "UAE-TDRA-"]}
- **guardrail**: Evidence-or-gap: cites only retrieved evidence; decisive actions need a binding source (FEDERAL_LAW, NATIONAL_LAW, REGULATOR_POLICY) within competence; actions limited by mandate and event kind; self-consistency check (action vs own scam-likelihood rating -> CONFLICT -> named human); proposes only; every decision sealed in a SHA-256 hash-chained log.
- **mapping**: {"y3172_nodes": ["P", "MLFO"], "readiness": ["D10 AI & Policies (d10_m02, d10_m06, d10_m09)", "D7 Strategy Alignment (d7_m01)"]}
- **evaluation**: Pre-registered gold (dev + held-out), see docs/eval_log_v3.md and docs/baselines.md
- **data**: Synthetic only
- **licence**: Apache-2.0
