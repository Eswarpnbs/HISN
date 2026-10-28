# UAE-India interoperability (2026-10-29 00:19, deterministic layers)

Decision agreement on 9 decisive events: **56%**

| event | UAE | India |
|---|---|---|
| INJ-FORGED | QUARANTINE | BLOCK_OVERRIDABLE |
| INJ-GOVFORGED | QUARANTINE | BLOCK_OVERRIDABLE |
| A3-E3 | BLOCK_PROHIBITED | ALLOW |
| INJ-EMERG-XFER | BLOCK_PROHIBITED | ALLOW |

Gap-engine baseline MIZAN: UAE 76.7, India 78.3

| gap | UAE | India | India clauses | note |
|---|---|---|---|---|
| G1 | none | partial | IN-TEL-S28-1, IN-TEL-S28-2 | specified messages include offers whether or not real; impersonation payment demands not clearly covered |
| G2 | none | partial | IN-TRAI-HEADER-REGISTER, IN-DPDP-S17-2A | header registration binds sender IDs; state instrumentalities can be exempted from DPDP (shared pattern) |
| G3 | none | partial | IN-DPDP-S4-1, IN-DPDP-S7-FGH | medical emergency / epidemic legitimate uses; telecom fraud filtering not named |
| G4 | none | present | IN-DPDP-S16, IN-DPDP-S7-FGH, IN-TEL-S20-1 | open-by-default transfers; emergency legitimate uses; priority routing for responders |
| G5 | none | partial | IN-TRAI-REG33-1 | regulator may direct access providers against senders; not specific to AI filter changes |

Scope: gateway, firewall and gap engine only; India institutional agents are future work. Comparator status as tagged in kb/manifest.csv.
