# Retrieval evaluation (2026-11-09 22:08)

50 questions (46 in-corpus, 4 out-of-corpus). nomic-embed-text via ITU pipeline.

- plain ITU search       Recall@1 21/46 | Recall@3 32/46 | Recall@5 35/46 | MRR 0.58 | out-of-corpus top similarity 0.698, 0.597, 0.578, 0.462
- plain, passage contains clause Recall@1 21/46 | Recall@3 32/46 | Recall@5 35/46 | MRR 0.58 | out-of-corpus top similarity 0.698, 0.597, 0.578, 0.462
- HISN clause-first      Recall@1 21/46 | Recall@3 32/46 | Recall@5 35/46 | MRR 0.58 | out-of-corpus top similarity 0.698, 0.597, 0.578, 0.462
- HISN hybrid (v2, not independent) Recall@1 21/46 | Recall@3 31/46 | Recall@5 34/46 | MRR 0.57 | out-of-corpus top similarity 0.698, 0.597, 0.578, 0.401
- v3 HISN clause-first   Recall@1 9/12 | Recall@3 9/12 | Recall@5 10/12 | MRR 0.77 | out-of-corpus top similarity 0.561, 0.634, 0.555
- v3 HISN hybrid         Recall@1 8/12 | Recall@3 10/12 | Recall@5 10/12 | MRR 0.72 | out-of-corpus top similarity 0.561, 0.634, 0.555
- Decision: ADOPT hybrid as default (v3 Recall@5 10 >= 10)
