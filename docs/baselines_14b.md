# Baselines comparison (qwen2.5:14b, 2026-10-29 18:36)

Same events, same pre-registered gold (dev + held-out v2). Synthetic data.

| system | accuracy (all) | held-out v2 | harmful | out-of-mandate | unsupported citations | decisive w/o binding basis |
|---|---|---|---|---|---|---|
| B0 fixed rules (no AI) | 11/14 | 3/4 | 3 | 0 | 0 | 7 |
| B1 LLM only (no KB, no gate) | 7/14 | 1/4 | 5 | 0 | 17 | 9 |
| B2 LLM + KB (RAG, no gate) | 9/14 | 2/4 | 5 | 0 | 0 | 0 |
| B3 full HISN (RAG + 5 safeguards) | 13/14 | 4/4 | 0 | 0 | 0 | 0 |
