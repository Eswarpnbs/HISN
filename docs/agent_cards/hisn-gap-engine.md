# HISN Gap Engine (loophole hunt + counterfactual tests)

**id** `hisn-gap-engine` · **version** 1.0.0 · **type** deterministic adversarial search + policy sandbox · **added** 2026-10-28

Searches an abstract tactic catalogue for loopholes, re-runs the battery with candidate provisions, measures protection, access and MIZAN.

- **dataset**: Abstract tactic battery (no phishing text)
- **tools**: ["run battery", "apply provision patch", "load-bearing rule removal"]
- **candidate provisions**: [{"id": "P-AUTH", "mechanism": "Protected (essential) sender IDs accepted only when authenticated by the registered sender", "comparator": "Inspired by Singapore SMS Sender ID Registry (verify text)"}, {"id": "P-ROUTE", "mechanism": "Protected sender IDs rejected when arriving via unregistered / foreign aggregator routes", "comparator": "Inspired by Singapore SSIR / India TRAI DLT header registration (verify text)"}, {"id": "P-FRAUD", "mechanism": "Operator filtering duty extended from marketing spam to fraud: payment demands from unregistered senders blocked", "comparator": "Inspired by Singapore Shared Responsibility Framework telco duties (verify text)"}, {"id": "P-VERIFIED", "mechanism": "Authenticated essential senders bypass content-based scoring (verified-sender lane); added after the baseline revealed access harms", "comparator": "Inspired by registered / verified sender schemes (verify text)"}]
- **guardrail**: Placeholder message text only; comparators marked verify-text; every patch awaits named human sign-off; sign-off refused without measured evidence.
- **mapping**: {"y3172_nodes": ["Sandbox"], "readiness": ["D10 (d10_m01 Policy Sandbox, d10_m02 Policy Evaluation, d10_m03 Policy Extrapolation)"]}
- **evaluation**: docs/counterfactual_results.md
- **data**: Synthetic only
- **licence**: Apache-2.0
