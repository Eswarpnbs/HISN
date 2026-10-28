# HISN Policy Gateway (deterministic, no LLM)

**id** `hisn-policy-gateway` · **version** 1.0.0 · **type** deterministic policy node (Y.3172 P) · **added** 2026-10-29

Blocks only on verified verbatim clauses with blocking basis; unverified citations never block; uncovered events become POTENTIAL_GAP (fail-visible).

- **dataset**: kb/rulepacks/uae/rules.yaml
- **tools**: ["evaluate event against rule pack"]
- **guardrail**: No model in the decision path; foreign comparators and soft law never block.
- **mapping**: {"y3172_nodes": ["P"], "readiness": ["D10 (d10_m06 Safety Policies, d10_m10 Data Sovereignty)"]}
- **evaluation**: Load-bearing test: removing Art.13 rule unblocks 2 offshore transfers (docs/headline_numbers.md)
- **data**: Synthetic only
- **licence**: Apache-2.0
