# Counterfactual policy tests (deterministic, synthetic)

Baseline: protection 86.7%, access 66.7%, MIZAN 76.7, officer reviews 24

| patch | protection | access | MIZAN | Δ MIZAN | reviews | loopholes closed | status |
|---|---|---|---|---|---|---|---|
| P-AUTH | 96.7% | 66.7% | 81.7 | +5.0 | 6 | exact_spoof_essential/G2 | awaiting_named_human_signoff |
| P-ROUTE | 90.0% | 66.7% | 78.3 | +1.6 | 14 | - | awaiting_named_human_signoff |
| P-FRAUD | 90.0% | 62.5% | 76.2 | -0.5 | 24 | unregistered_payment_demand/G1 | awaiting_named_human_signoff |
| P-AUTH+P-FRAUD | 100.0% | 62.5% | 81.2 | +4.5 | 6 | exact_spoof_essential/G2, unregistered_payment_demand/G1 | awaiting_named_human_signoff |
| P-AUTH+P-ROUTE+P-FRAUD | 100.0% | 62.5% | 81.2 | +4.5 | 6 | exact_spoof_essential/G2, unregistered_payment_demand/G1 | awaiting_named_human_signoff |

Comparators are marked 'verify text' until checked against official sources. Patches are candidate mechanisms, not legal drafting.
