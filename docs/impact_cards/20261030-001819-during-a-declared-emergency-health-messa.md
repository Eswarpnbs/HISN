# Regulatory Impact Card

**Draft:** During a declared emergency, health message logs may be stored at a backup site abroad for 72 hours.
**Instrument level:** health_authority_resolution
**Verdict:** **READY FOR NAMED HUMAN REVIEW**

## Measured effect (synthetic battery + crisis scenario)
- Protection 86.7% -> 86.7% | Access 66.7% -> 66.7% | MIZAN 76.7 -> 76.7 | officer reviews 24 -> 24
- Gaps addressed: G4 | UAE-India decision agreement 55% -> 64%

## Conflicts with existing verified law
- RESOLVED by instrument level: UAE-FL-2-2019-ART13 (Article (13)) - Article 13 permits offshore processing only where a resolution is issued by the Health Authority in coordination with the Ministry.
  > It is not permissible to store, process, generate or transform the health data and information outside State -which are related to the health services provided inside State- except in the case where a resolution is issued from the Health Authority in coordination with the Ministr

## Public-interest invariants (before -> after)
- I1 No legitimate essential message silently lost or blocked: PASS -> PASS (0 lost)
- I2 No offshore health-data transfer without a legal basis of sufficient rank: PASS -> PASS (1 transfer(s) allowed by the draft; instrument level: health_authority_resolution)
- I3 Spoofed protected sender IDs are never delivered: FAIL -> FAIL (6 spoof case(s) delivered)
- I4 Every policy block cites a verified binding clause: PASS -> PASS (2 block(s))
- I5 All decisions sealed in a verifiable audit chain: PASS -> PASS 
- I6 Legitimate access does not regress: PASS -> PASS (access 66.7 -> 66.7)
- I7 Life-critical health messages reach a human within their clinical limit: FAIL -> FAIL (1 T1 message(s) waited longer than 5 min)
- I8 Emergency exceptions expire (sunset): PASS -> PASS (transfer after the emergency window: BLOCK_PROHIBITED)

Warnings: none | Not testable here: none

_Simulation-based pre-issuance test. Conflict table hand-authored from verified clauses; requires legal review. A named human must sign off before any use._
