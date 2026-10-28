# Regulatory Impact Card

**Draft:** Operators shall accept protected sender IDs only when authenticated by the registered sender, and authenticated essential senders shall bypass content filtering.
**Instrument level:** regulation
**Verdict:** **READY FOR NAMED HUMAN REVIEW**

## Measured effect (synthetic battery + crisis scenario)
- Protection 86.7% -> 96.7% | Access 66.7% -> 91.7% | MIZAN 76.7 -> 94.2 | officer reviews 24 -> 0
- Gaps addressed: G2 | UAE-India decision agreement 56% -> 44%

## Conflicts with existing verified law
- none found in the verified corpus

## Public-interest invariants (before -> after)
- I1 No legitimate essential message silently lost or blocked: PASS -> PASS (0 lost)
- I2 No offshore health-data transfer without a legal basis of sufficient rank: PASS -> PASS (0 transfer(s) allowed by the draft; instrument level: regulation)
- I3 Spoofed protected sender IDs are never delivered: FAIL -> PASS (0 spoof case(s) delivered)
- I4 Every policy block cites a verified binding clause: PASS -> PASS (2 block(s))
- I5 All decisions sealed in a verifiable audit chain: PASS -> PASS 
- I6 Legitimate access does not regress: PASS -> PASS (access 66.7 -> 91.7)

Warnings: none | Not testable here: none

_Simulation-based pre-issuance test. Conflict table hand-authored from verified clauses; requires legal review. A named human must sign off before any use._
