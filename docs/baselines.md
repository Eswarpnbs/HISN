# Baselines comparison (qwen2.5:14b, 2026-11-01 10:53)

Same events, same pre-registered gold (dev + held-out v2 + held-out v3). Synthetic data.

| system | accuracy (all) | held-out v2 | harmful | out-of-mandate | unsupported citations | decisive w/o binding basis | held-out v3 |
|---|---|---|---|---|---|---|---|
| B0 fixed rules (no AI) | 12/16 | 3/4 | 4 | 0 | 0 | 9 | 1/2 |
| B1 LLM only (no KB, no gate) | 8/16 | 1/4 | 6 | 0 | 19 | 11 | 1/2 |
| B2 LLM + KB (RAG, no gate) | 10/16 | 2/4 | 6 | 0 | 0 | 0 | 1/2 |
| B3 full HISN (RAG + 5 safeguards) | 14/16 | 4/4 | 0 | 0 | 0 | 0 | 1/2 |
