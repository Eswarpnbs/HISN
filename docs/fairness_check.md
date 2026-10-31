# Cross-language fairness check

Same genuine message from an authenticated hospital, six languages, four policy states. Synthetic; non-English texts are machine-drafted and pending native review.

## today's rules, normal

| Message | en | ar | hi | te | ur | ml | Equal? |
|---|---|---|---|---|---|---|---|
| appointment | delivered (0.00) | delivered (0.00) | delivered (0.00) | delivered (0.00) | delivered (0.00) | delivered (0.00) | yes |
| critical_lab | delivered (0.25) | delivered (0.00) | delivered (0.00) | delivered (0.00) | delivered (0.00) | delivered (0.00) | yes |

## today's rules, after panic (Act 3)

| Message | en | ar | hi | te | ur | ml | Equal? |
|---|---|---|---|---|---|---|---|
| appointment | delivered (0.00) | delivered (0.00) | delivered (0.00) | delivered (0.00) | delivered (0.00) | delivered (0.00) | yes |
| critical_lab | held (0.25) | delivered (0.00) | delivered (0.00) | delivered (0.00) | delivered (0.00) | delivered (0.00) | **NO** |

## today's rules, after drift (Act 4)

| Message | en | ar | hi | te | ur | ml | Equal? |
|---|---|---|---|---|---|---|---|
| appointment | delivered (0.00) | delivered (0.00) | delivered (0.00) | delivered (0.00) | delivered (0.00) | delivered (0.00) | yes |
| critical_lab | held (0.25) | delivered (0.00) | delivered (0.00) | delivered (0.00) | delivered (0.00) | delivered (0.00) | **NO** |

## tested rule set (authentication + verified lane), after panic

| Message | en | ar | hi | te | ur | ml | Equal? |
|---|---|---|---|---|---|---|---|
| appointment | delivered (0.00) | delivered (0.00) | delivered (0.00) | delivered (0.00) | delivered (0.00) | delivered (0.00) | yes |
| critical_lab | delivered (0.25) | delivered (0.00) | delivered (0.00) | delivered (0.00) | delivered (0.00) | delivered (0.00) | yes |

**Unequal treatment found in 2 message/state combination(s).**

