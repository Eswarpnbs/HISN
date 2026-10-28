# Retrieval evaluation (2026-10-28 22:48)

26 questions (24 in-corpus, 2 out-of-corpus). nomic-embed-text via ITU pipeline.

- plain ITU search       Recall@1 16/24 | Recall@3 22/24 | Recall@5 22/24 | MRR 0.78 | out-of-corpus top similarity 0.698, 0.597
- HISN clause-first      Recall@1 16/24 | Recall@3 22/24 | Recall@5 22/24 | MRR 0.78 | out-of-corpus top similarity 0.698, 0.597

## Misses (scored as misses; gold not changed after seeing results)
- "Penalty for unlawfully processing health data abroad": expected clause UAE-FL-2-2019-ART24; top result was UAE-FL-2-2019#c11, a full-text chunk of the same law (likely containing Art. 24).
- "AI safety and removing risky systems": expected Charter Principle 2; retrieved Principle 6 (Human Oversight). P2's two-column PDF layout was already flagged for manual check.

## Threshold calibration finding
- In-corpus top similarity: min 0.659, median 0.79, max 0.955. Out-of-corpus: 0.698, 0.597.
- The ranges overlap, so no absolute similarity threshold separates relevant from irrelevant queries with nomic-embed-text.
- The 0.25 refusal threshold mirrored from the ITU reference agent (which uses a different embedding model) is therefore effectively inactive and is NOT claimed as a safeguard.
- Irrelevant evidence is stopped downstream by the binding-basis, competence and self-consistency gates. Future work: re-ranking or margin-based checks.
- Clause-first retrieval gave no measurable retrieval gain on this set; its value is guaranteeing article-level evidence for citation.
