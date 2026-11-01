# Retrieval decision rule (committed BEFORE the hybrid retriever was run)

- Method: reciprocal rank fusion of (a) embedding similarity and (b) BM25 over verbatim clauses of the selected country.
- Parameters fixed at textbook defaults, not tuned: BM25 k1 = 1.5, b = 0.75; fusion constant 60.
- Primary test: kb/retrieval_gold_v3.yaml (pre-registered in commit df6759e, 2026-11-01 11:45:34 +0530).
- Each v3 question is searched in its own country's knowledge base, taken from the prefix of its expected clause
  (UAE-, IN-, SG-); out-of-corpus questions use the UAE base (as the adviser's --country flag would be set by a user).
- Rule: hybrid becomes the default for agents and adviser only if its Recall@5 on v3 is >= clause-first's Recall@5 on v3.
- The 50-question v2 set is also reported, marked as not independent (it was seen during development).
