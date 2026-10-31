# HISN and the ITU AI Readiness Framework

## The eight perspectives named in the hackathon brief

| Perspective | HISN evidence | Where |
|---|---|---|
| Open data and open-source management | Code Apache-2.0; synthetic SMS dataset CC-BY-4.0; knowledge base built with ITU's unmodified ingest pipeline; approved fixes written to ITU `kb_decisions`; rule-pack schema and UAE country pattern offered back to ITU | `LICENSE`, `build_dataset.py`, `kb/` |
| Generative AI content ecosystem | LLMs only propose; deterministic code decides; invented citations rejected or withheld; no real phishing text generated | `app/agents/`, `app/agents/adviser.py` |
| Contextualization and regional development focus | First UAE legal corpus in ITU's inputs (7 UAE instruments, 19 verbatim clauses); UAE institutions as agents; messages in 6 languages used in the UAE | `kb/`, `scenarios/fairness_pairs.yaml` |
| AI integration in domains and cross-domain analysis | Telecom, health and government in one governed workflow; audited referral protocol between authorities; three-country interoperability | `app/core/coordinator.py`, `run_interop.py` |
| Human interaction and supervision in AI | Held messages go to a named human; second review within the clinical tier limit; accountable receipts to the sender; sign-off refused without evidence | `app/core/tiers.py`, `app/smpp/`, `signoff.py` |
| AI policy and implementation opportunity identification | Six domain-level gaps with verbatim evidence and verified global examples (Australia, EU); wind tunnel tests draft rules; G3 and G5 proposed for ITU standards work | `docs/gap_register.yaml`, `docs/global_examples.yaml`, `app/windtunnel/` |
| AI for social inclusion | Cross-language fairness check: content scoring treats identical messages unequally by language; identity-based rules are equal in all 6 languages; filter-change gate blocks biased changes | `tools/fairness_check.py`, `tools/filter_change_check.py` |
| Digital infrastructure and energy considerations | Act 1 energy-saving cell sleep; rain-driven link failures from 985,308 real operator link-days; emergency during grid instability; health-data localisation | `app/network/act1.py`, `scenarios/` |

## Readiness 2.0 metrics claimed (names verified against ITU's dimensions.json)

| Metric | Name | Evidence |
|---|---|---|
| d3_m01 | Integrated Workflow | One governed event workflow across telecom, health and government |
| d3_m07 | Coverage and Scale | 3 countries, 15 records, 36 verbatim clauses, 6 languages |
| d7_m01 | Coordination Level | Referral protocol between authorities, routed once and audited |
| d7_m03 | Intent Representations | Machine-readable rule packs and wind-tunnel mechanism vocabulary |
| d7_m04 | Interoperability Standards | SMPP 3.4, HL7 FHIR priority, Y.3172 export |
| d7_m08 | International Cooperation | UAE, India and Singapore packs; Australia and EU global examples |
| d10_m01 | Policy Sandbox | Governed vs ungoverned twin; regulatory wind tunnel |
| d10_m02 | Policy Evaluation | Measured effect of each draft (invariants, MIZAN, interoperability) |
| d10_m03 | Policy Extrapolation | Same drafts tested against India and Singapore packs |
| d10_m06 | Safety Policies | Never silently drop essential messages; I1 to I8 |
| d10_m07 | Explainability Metrics | Every decision cites its clause; impact cards explain verdicts |
| d10_m09 | Audit Metrics | Hash-chained audit, verified on every run |
| d10_m10 | Data Sovereignty | Offshore health-data transfers blocked under Art. 13; sunset test |
| d11_m07 | Language Repository | 6-language message sets for verifier and fairness check |
| d11_m08 | Regional Language Support | Claim only after the Arabic review |
| d13_m07 | Uptime | Daily essential-message assurance (0 silently lost) |
| d13_m08 | Area Coverage | Act 1 cell sleep scenario |
| d13_m09 | Network Quality | Rain and heat link-failure risk from real operator data |

## Metrics named in the text of ITU AI Readiness Report 2.0 (January 2026)

Metrics described in the report's text, separate from the metric IDs in ITU's dimensions.json above.

| Report 2.0 metric (dimension) | HISN evidence | Where |
|---|---|---|
| Levels of automation [Y.3173] (Digital Infrastructure) | Levels computed by the Y.3173 method: network functions L2; agents, adviser, wind tunnel, gap engine L0 | docs/automation_levels.md |
| Sandbox for policy interventions with a simulated timeline (Dim. 10, User story 2) | Regulatory wind tunnel; what-if replay per filter threshold with targets and gaps | app/windtunnel/, docs/what_if_none.md |
| Policies on the AI lifecycle incl. upgrade (Dim. 10) | Missing upgrade policy = gap G5; the filter-change gate is a working one | docs/gap_register.yaml, tools/filter_change_check.py |
| Policy inputs from case briefs (Dim. 10) | One-page brief on the filter-threshold lesson | docs/case_brief_filter_threshold.md |
| Accountability of final decisions remains with humans (Dim. 10) | Named-human release, second review, sign-off refused without evidence | app/core/coordinator.py, signoff.py |
| Data sovereignty metrics (Dim. 10) | Offshore health-data transfers blocked under Art. 13; sunset test I8 | app/core/gateway.py, app/windtunnel/ |
| Inference-to-action latency (Dim. 9) | Held message reaches a human within 5 / 15 / 60 minutes; invariant I7 | app/core/tiers.py |
| Bias audits; bias documentation; corrective mechanisms (Data governance) | Fairness check; dataset datasheet; filter-change gate | docs/fairness_check.md, docs/datasheet_sms_dataset.md |
| Local data share (Data representativeness) | 0% local, 100% synthetic, stated openly | docs/datasheet_sms_dataset.md |
| Language repository as branches of one template (Dim. 11) | One template in 6 languages; non-English pending native review | scenarios/fairness_pairs.yaml |
| Model and dataset metadata (Dim. 1) | Agent cards with ITU-T Y.3176 fields; Gebru-style datasheet | docs/agent_cards/, docs/datasheet_sms_dataset.md |
| Uptime (Dim. 13) | Daily essential-message assurance: 0 silently lost | docs/daily_report_none.md |
