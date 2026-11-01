# What-if: filter threshold under current rules

_Each row replays the full crisis timeline as if the operator had set the filter to that threshold at every filter change. Synthetic data; Readiness Report 2.0 Dimension 10 (simulated timeline, target vs achievement)._

**Targets:** 0 genuine essential messages lost; 0 scams delivered; T1 within clinical limit; equal treatment in 6 languages

| Threshold | Genuine delivered | Held for a human | Lost | Scams stopped | T1 within limit | Languages equal | Gap to target |
|---|---|---|---|---|---|---|---|
| 0.10 | 0/10 | 10 | **0** | 12/12 | yes | **no** | unequal by language |
| 0.15 | 0/10 | 10 | **0** | 12/12 | yes | **no** | unequal by language |
| 0.20 | 0/10 | 10 | **0** | 12/12 | yes | **no** | unequal by language |
| 0.25 | 0/10 | 10 | **0** | 12/12 | yes | **no** | unequal by language |
| 0.30 | 10/10 | 0 | **0** | 11/12 | yes | yes | scams delivered |
| 0.40 | 10/10 | 0 | **0** | 11/12 | yes | yes | scams delivered |

## Simulated timeline: genuine messages held, by act

| Threshold | Act 3 | Act 4 |
|---|---|---|
| 0.10 | 7 | 3 |
| 0.15 | 7 | 3 |
| 0.20 | 7 | 3 |
| 0.25 | 7 | 3 |
| 0.30 | 0 | 0 |
| 0.40 | 0 | 0 |

**Conclusion:** no threshold meets every target under these rules; the gap is structural, not a tuning problem.

_Audit chains verified for all runs: True._
