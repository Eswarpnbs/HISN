# Knowledge-base expansion plan (UAE first, Arabic included)

The knowledge base holds only documents downloaded from an official source, pinned by SHA-256 and checked clause by clause.
Nothing is added from memory, news articles or machine translation.

## Candidates (check the issuer's official page before adding; titles and numbers must match the source)

| Priority | Candidate | Why HISN needs it | Where to look |
|---|---|---|---|
| 1 | Arabic editions of Federal Law No. 2 of 2019, the Telecommunications Law, the PDPL and the Cybercrime Law | The Arabic text is authoritative; `kb/arabic.py` stores and verifies the key articles | uaelegislation.gov.ae (Arabic pages) |
| 2 | AI Adoption Guideline in Government Services (UAE AI Office) | Guidance for the agentic-government frame; soft law, so it informs and never blocks | ai.gov.ae or the publishing ministry's site |
| 3 | Federal Decree-Law on Electronic Transactions and Trust Services (2021) | Possible legal basis for signed approval records (electronic signatures) | uaelegislation.gov.ae |
| 4 | Cabinet resolution regulating telemarketing (2024) and TDRA's Do Not Call Register rules | What the UAE already does for unwanted messages; context for G1 and G2 | uaelegislation.gov.ae, tdra.gov.ae |
| 5 | Abu Dhabi Department of Health health-data protection and confidentiality policy | Health messages and patient data on the last mile | doh.gov.ae |

## Steps for each document (about 20 minutes each)

1. Download the PDF in a browser from the official page into `kb/sources/` (the UAE portal blocks scripted downloads).
2. Add a row to `DOCS` in `kb/register.py`: record id, title, issuer, jurisdiction, type, **basis** (FEDERAL_LAW, CABINET_RESOLUTION, REGULATOR_POLICY or SOFT_LAW), official URL, how obtained.
3. `python kb/register.py && python kb/verify.py` pins and checks the hash.
4. Find the clauses: `python kb/find_clause.py kb/sources/<file>.pdf "term"`. Copy short verbatim clauses into `kb/clauses/clauses.yaml`.
   For Arabic: `python kb/arabic.py extract --record <ID> --article <N> --pdf kb/sources/<file>.pdf`, then a native reader checks it.
5. `python tools/verify_all.py` confirms every clause against its source.
6. Rebuild and re-measure: `python kb/ingest_uae.py`, then `python kb/eval_retrieval.py`, `python selftest.py`.

**Timing:** adding documents changes retrieval, so agent and baseline figures must be re-run afterwards.
Do this after the first-round submission (or re-run everything before submitting), never between a run and the report.
