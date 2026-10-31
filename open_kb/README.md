# HISN open knowledge base contribution

Contributed by Team Sankalp to the ITU AI for Good Lab open knowledge base, **with acknowledgement to the United Arab Emirates**
for the leadership and coordination of the AI for Good Lab Hackathon (UAE edition, 2026).

**Domain:** governance of telecom AI that filters essential health and government messages (telecom, healthcare, public services).

## Contents
- `records_manifest.csv`: 15 official instruments (?: 15) with official URLs and SHA-256 of the pinned source files
- `verbatim_clauses.yaml`: 37 provisions, each verified verbatim against its pinned source, with article, legal basis, Y.3172 nodes and Readiness metric IDs
- `gap_register.yaml`, `gap_coverage_by_country.yaml`, `global_examples.yaml`: domain-level policy gaps with evidence, country coverage and verified global examples
- `retrieval_test_questions.yaml`: 50 pre-registered retrieval questions (46 answerable, 4 out-of-corpus)
- `automation_levels_y3173.yaml`: declared ITU-T Y.3173 capability levels per component
- `agent_cards.json`: agent cards with ITU-T Y.3176-style metadata
- `hisn_synthetic_sms.csv` + `dataset_datasheet.md`: synthetic SMS governance dataset (CC-BY-4.0)
- `SHA256SUMS`: checksums of every file in this folder

## Licences and sources
HISN-authored metadata, gaps, questions and the dataset: CC-BY-4.0. Legal texts quoted in `verbatim_clauses.yaml` remain the
property of their issuers; source documents are not redistributed and can be obtained from the official URLs in the manifest.
Synthetic data only; no real messages, senders or people. Ingest with the ITU AI Readiness reference pipeline (CrashingGuru/ITUAIReadiness).
