# Evidence gate and deterministic policy enforcement

This change hardens two control points in the HISN simulation.

## 1. Evidence gate for institutional-agent proposals

Institutional agents remain advisory: they propose; they do not execute operator or regulator actions. Decisive proposals must cite evidence IDs returned by the retriever and must be grounded in a binding instrument within the role/action competence map. A decisive proposal without that basis is converted to `LOG_GAP` and recorded as a potential gap.

The release/keep-quarantined actions for essential health messages now require UAE health-law or health-executive-regulation evidence. This is a deliberately narrow competence rule, not a claim that every possible health decision is covered by the current corpus.

## 2. Deterministic policy gateway

At construction time, every rule in the configured policy pack must resolve to:
- an existing `clause_id` in `kb/clauses/clauses.yaml`;
- the same `record_id` in the clause and `kb/manifest.csv`;
- the same article label; and
- an exact normalized match between the rule quote and the clause text.

The source record must carry a 64-character SHA-256 value in the manifest. That hash is attached to the decision citation for traceability. This startup check validates the pack-to-KB link; it does not independently re-download or re-hash the original source PDF.

A non-binding basis cannot compel a blocking decision. The current UAE health-localisation rule remains grounded in Federal Law No. 2 of 2019, Article (13).

## 3. Human approval of filter-policy changes

The coordinator now fails closed by default for filter-threshold changes. A plain `approved_by` string is not accepted as proof of authority. A caller must supply both an approval object and a trusted `approval_verifier` callback that authenticates/authorizes it. If no verifier is configured, the change is held for approval.

The hackathon demo and agent runner explicitly enable enforcement. The ungoverned comparison twin remains ungoverned by design.

**Integration boundary:** the repository does not yet contain a production identity provider, signature-verification key registry, or UAE institutional authorization service. The runner passes no verifier, so threshold changes are held. Do not add a fabricated verifier or present a self-attested name as authenticated approval.

## 4. Regression tests

Run from the repository root:

```bash
python -m unittest discover -s tests -p 'test_governance_gates.py' -v
```

The tests cover default fail-closed behavior, rejection of legacy name-only approval, acceptance only through an injected verifier, fail-closed behavior if verification raises an error, exact clause/manifest linkage, deterministic blocking under the cited federal-law rule, and rejection of a modified rule quote.

These tests have been added but were not executed in the remote GitHub editing session. Re-run them locally/CI before relying on the patch or using it in a judging demo.
