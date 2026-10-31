# What-if: filter threshold under tested rule set (sender authentication + verified lane)

_Each row replays the full crisis timeline as if the operator had set the filter to that threshold at every filter change. Synthetic data; Readiness Report 2.0 Dimension 10 (simulated timeline, target vs achievement)._

**Targets:** 0 genuine essential messages lost; 0 scams delivered; T1 within clinical limit; equal treatment in 6 languages

| Threshold | Genuine delivered | Held for a human | Lost | Scams stopped | T1 within limit | Languages equal | Gap to target |
|---|---|---|---|---|---|---|---|
| 0.10 | 4/4 | 0 | **0** | 5/5 | yes | yes | none |
| 0.15 | 4/4 | 0 | **0** | 5/5 | yes | yes | none |
| 0.20 | 4/4 | 0 | **0** | 5/5 | yes | yes | none |
| 0.25 | 4/4 | 0 | **0** | 5/5 | yes | yes | none |
| 0.30 | 4/4 | 0 | **0** | 5/5 | yes | yes | none |
| 0.40 | 4/4 | 0 | **0** | 5/5 | yes | yes | none |

## Simulated timeline: genuine messages held, by act

No genuine message was held at any threshold.

**Conclusion:** thresholds meeting every target: 0.10, 0.15, 0.20, 0.25, 0.30, 0.40.

_Audit chains verified for all runs: True._
