# Baselines comparison (qwen2.5:14b, 2026-11-01 23:35)

Same events, same pre-registered gold (dev + held-out v2 + held-out v3). Synthetic data.

| system | accuracy (all) | held-out v2 | harmful | out-of-mandate | unsupported citations | decisive w/o binding basis | held-out v3 |
|---|---|---|---|---|---|---|---|
| B0 fixed rules (no AI) | 23/33 | 3/4 | 10 | 0 | 0 | 22 | 1/2 |
| B1 LLM only (no KB, no gate) | 16/33 | 1/4 | 10 | 0 | 41 | 19 | 1/2 |
| B2 LLM + KB (RAG, no gate) | 23/33 | 3/4 | 9 | 0 | 0 | 0 | 1/2 |
| B3 full HISN (RAG + 5 safeguards) | 26/33 | 4/4 | 1 | 0 | 0 | 0 | 1/2 |
