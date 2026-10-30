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
