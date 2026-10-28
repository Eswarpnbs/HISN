# Interoperability across UAE, IN, SG (2026-10-29 01:27, deterministic layers)

UAE-India decision agreement: **56%**

| pair | agreement |
|---|---|
| UAE-IN | 56% |
| UAE-SG | 56% |
| IN-SG | 78% |

| event | UAE | IN | SG |
|---|---|---|---|
| INJ-FORGED | QUARANTINE | BLOCK_OVERRIDABLE | BLOCK_OVERRIDABLE |
| INJ-GOVFORGED | QUARANTINE | BLOCK_OVERRIDABLE | BLOCK_OVERRIDABLE |
| A3-E3 | BLOCK_PROHIBITED | ALLOW | QUARANTINE |
| INJ-EMERG-XFER | BLOCK_PROHIBITED | ALLOW | QUARANTINE |

| gap | UAE | IN | SG | notes |
|---|---|---|---|---|
| G1 | none | partial | present | IN: specified messages include offers whether or not real; SG: framework built around impersonation scams; URL filter on all SMS |
| G2 | none | partial | present | IN: header registration binds sender IDs; SG: sender ID registry + authorised aggregators; government agencies named as impersonated entities |
| G3 | none | partial | partial | IN: medical emergency / epidemic legitimate uses; SG: URL-level scanning of all SMS is a stated duty; full content scanning of health SMS not addressed |
| G4 | none | present | present | IN: open by default; emergency legitimate uses; priority routing; SG: conditional on comparable protection; Commission exemption route; emergency vital interests |
| G5 | none | partial | partial | IN: regulator may direct access providers against senders; SG: telco duties stem from IMDA Directions; not specific to AI filter changes |
| G6 | none | none | present | UAE: absence to be confirmed in second search pass; IN: not found in verified corpus; SG: telco bears SMS-scam losses when it breached its filtering duties and the bank complied |

Scope: gateway, firewall and gap engine only; institutional agents for India and Singapore are future work.
