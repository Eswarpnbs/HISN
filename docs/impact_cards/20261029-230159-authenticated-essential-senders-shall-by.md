# Regulatory Impact Card

**Draft:** Authenticated essential senders shall bypass content filtering.
**Instrument level:** regulation
**Verdict:** **DO NOT ISSUE AS DRAFTED**

## Measured effect (synthetic battery + crisis scenario)
- Protection 86.7% -> 86.7% | Access 66.7% -> 91.7% | MIZAN 76.7 -> 89.2 | officer reviews 24 -> 18
- Gaps addressed: - | UAE-India decision agreement 55% -> 18%

## Conflicts with existing verified law
- none found in the verified corpus

## Public-interest invariants (before -> after)
- I1 No legitimate essential message silently lost or blocked: PASS -> PASS (0 lost)
- I2 No offshore health-data transfer without a legal basis of sufficient rank: PASS -> PASS (0 transfer(s) allowed by the draft; instrument level: regulation)
- I3 Spoofed protected sender IDs are never delivered: FAIL -> FAIL (6 spoof case(s) delivered)
- I4 Every policy block cites a verified binding clause: PASS -> PASS (2 block(s))
- I5 All decisions sealed in a verifiable audit chain: PASS -> PASS 
- I6 Legitimate access does not regress: PASS -> PASS (access 66.7 -> 91.7)
- I7 Life-critical health messages reach a human within their clinical limit: FAIL -> PASS (0 T1 message(s) waited longer than 5 min)

Warnings: verified_sender_lane presupposes sender_authentication | Not testable here: none

_Simulation-based pre-issuance test. Conflict table hand-authored from verified clauses; requires legal review. A named human must sign off before any use._
