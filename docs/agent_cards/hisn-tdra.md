# HISN TDRA (telecommunications regulator) agent

**id** `hisn-tdra` · **version** 1.0.0 · **type** institutional agent (retrieve / propose / log gap) · **added** 2026-11-01

Regulates telecom licensees, including their obligations on unsolicited electronic communications and network operations.

- **models**: ["qwen2.5:14b (reference) or qwen2.5:7b via Ollama", "nomic-embed-text (ITU reference ingest)"]
- **dataset**: HISN knowledge base: 15 hash-pinned records (UAE, India, Singapore; 1 Saudi historical draft), 37 verbatim clauses (kb/manifest.csv)
- **tools**: ["retrieve (ITU KnowledgeBase, UAE filter, clause-first)", "propose action", "log gap"]
- **event kinds**: ["complaint", "network_summary", "override_dispute", "referral"]
- **actions**: ["ASSIGN_OVERRIDE_AUTHORITY", "DIRECT_OPERATOR", "LOG_GAP", "MONITOR", "REQUEST_INFO"]
- **decisive actions**: ["ASSIGN_OVERRIDE_AUTHORITY", "DIRECT_OPERATOR"]
- **competence norms**: {"ASSIGN_OVERRIDE_AUTHORITY": "none in UAE pack -> logged gap", "DIRECT_OPERATOR": ["UAE-TDRA-"]}
- **guardrail**: Evidence-or-gap: cites only retrieved evidence; decisive actions need a binding source (FEDERAL_LAW, NATIONAL_LAW, REGULATOR_POLICY) within competence; actions limited by mandate and event kind; self-consistency check (action vs own scam-likelihood rating -> CONFLICT -> named human); proposes only; every decision sealed in a SHA-256 hash-chained log.
- **mapping**: {"y3172_nodes": ["P", "MLFO"], "readiness": ["D10 AI & Policies (d10_m02, d10_m06, d10_m09)", "D7 Strategy Alignment (d7_m01)"]}
- **evaluation**: Pre-registered gold (dev + held-out), see docs/eval_log_v3.md and docs/baselines.md
- **data**: Synthetic only
- **licence**: Apache-2.0
