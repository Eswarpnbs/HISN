# HISN Gap Engine (loophole hunt + counterfactual tests)

**id** `hisn-gap-engine` · **version** 1.0.0 · **type** deterministic adversarial search + policy sandbox · **added** 2026-10-29

Searches an abstract tactic catalogue for loopholes, re-runs the battery with candidate provisions, measures protection, access and MIZAN.

- **dataset**: Abstract tactic battery (no phishing text)
- **tools**: ["run battery", "apply provision patch", "load-bearing rule removal"]
- **candidate provisions**: [{"id": "P-AUTH", "mechanism": "Protected (essential) sender IDs accepted only when authenticated by the registered sender", "comparator": "Partly verified: Singapore SRF footnote 9 (Sender ID Registry via licensed aggregators); per-sender cryptographic authentication is HISN's own extension"}, {"id": "P-ROUTE", "mechanism": "Protected sender IDs rejected when arriving via unregistered / foreign aggregator routes", "comparator": "Verified: Singapore SRF 5.2.1-5.2.2 (authorised aggregators) and India TRAI header register (consolidated text)"}, {"id": "P-FRAUD", "mechanism": "Operator filtering duty extended from marketing spam to fraud: payment demands from unregistered senders blocked", "comparator": "Partly verified: Singapore SRF scope covers impersonation scams and 5.2.3 mandates a URL filter on all SMS; a payment-demand duty for unregistered senders is HISN's own variant"}, {"id": "P-VERIFIED", "mechanism": "Authenticated essential senders bypass content-based scoring (verified-sender lane); added after the baseline revealed access harms", "comparator": "Inspired by registered / verified sender schemes (verify text)"}]
- **guardrail**: Placeholder message text only; comparators marked verify-text; every patch awaits named human sign-off; sign-off refused without measured evidence.
- **mapping**: {"y3172_nodes": ["Sandbox"], "readiness": ["D10 (d10_m01 Policy Sandbox, d10_m02 Policy Evaluation, d10_m03 Policy Extrapolation)"]}
- **evaluation**: docs/counterfactual_results.md
- **data**: Synthetic only
- **licence**: Apache-2.0
