# HISN Policy and Legal Adviser agent

**id** `hisn-policy-adviser` · **version** 1.0.0 · **type** policy and legal adviser agent (query, answer with citations) · **added** 2026-10-31

Answers legal questions about the scenario from retrieved, verified evidence only, for the UAE, India or Singapore.

- **models**: ["qwen2.5:14b via Ollama", "nomic-embed-text (ITU reference ingest)"]
- **dataset**: HISN knowledge base: 15 hash-pinned records (UAE, India, Singapore; 1 Saudi historical draft), 37 verbatim clauses (kb/manifest.csv)
- **tools**: ["retrieve (clause-first)", "answer", "link related gaps and verified global examples"]
- **guardrail**: Invented citations withheld; soft-law-only answers reported as no binding basis; never makes policy (Readiness Report 2.0 FAQ 7); every answer sealed in the audit chain.
- **mapping**: {"y3172_nodes": ["M", "P"], "readiness": ["D10 (d10_m07 Explainability Metrics)"]}
- **evaluation**: tests/test_adviser.py; live answers for UAE and India logged in runs/adviser.jsonl
- **data**: Synthetic scenario; public legal texts
- **licence**: Apache-2.0
