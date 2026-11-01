# HISN Regulatory Wind Tunnel (policy sandbox)

**id** `hisn-wind-tunnel` · **version** 1.0.0 · **type** regulatory sandbox (deterministic; a model only proposes the mechanism mapping, a human confirms) · **added** 2026-11-01

Tests a draft rule before issuance against verified law (hierarchy of norms), eight public-interest invariants, measured effect and UAE-India interoperability; runs in CI on pull requests.

- **models**: ["qwen2.5:14b (mapping proposal only; skipped in CI where the human-confirmed mapping is in the draft file)"]
- **dataset**: HISN knowledge base: 15 hash-pinned records (UAE, India, Singapore; 1 Saudi historical draft), 37 verbatim clauses (kb/manifest.csv)
- **tools**: ["compile draft", "conflict scan", "invariants I1-I8", "metrics", "interop", "impact card"]
- **guardrail**: Illustrative drafts only; no national recommendations; AI validates impact, humans decide (Report 2.0 FAQ 7); missing prerequisites refused.
- **mapping**: {"y3172_nodes": ["Sandbox", "P"], "readiness": ["D10 (d10_m01 Policy Sandbox, d10_m02 Policy Evaluation, d10_m03 Policy Extrapolation)"]}
- **evaluation**: tests/test_sunset.py, tests/test_confirmed.py; CI pull request #1 refused automatically
- **data**: Synthetic only
- **licence**: Apache-2.0
