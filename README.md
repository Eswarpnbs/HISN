# HISN — governance for the telecom AI that decides what reaches citizens

**Team Sankalp** · ITU AI for Good Lab Hackathon (UAE) · Telecommunications + Healthcare + Public services
Eswar Panchakarla (team leader, engineering) · P. Prudhvi Krishna (knowledge base, policy, report)
Contact: Eswar Panchakarla, eswarpnbs@gmail.com (Team Sankalp) · **Synthetic data only. Fictional senders. No real phishing content is generated.**

**Live report:** https://hisn-report.netlify.app/ (static, synthetic data; live demos run locally or in the ITU Sandbox)

## What it is
AI filters and network AI now decide whether hospital and government messages reach citizens. HISN governs those decisions:
- a deterministic **policy node** (ITU-T Y.3172 *P*) blocks only on verbatim, hash-pinned UAE legal clauses, and logs a **gap** when no provision exists;
- **institutional agents** (TDRA, health authority, Federal AI & Data Authority) see only their own events, cite only retrieved evidence, and only propose: fixed code checks evidence, mandate, binding basis, competence and consistency;
- a **gap engine** finds loopholes over an abstract tactic catalogue, re-runs the scenario with candidate provisions, and measures protection, access and the **MIZAN** balance score;
- a **regulatory wind tunnel** gives every draft rule a test suite: plain-language draft -> validated mechanism mapping -> conflict scan against verified law (with hierarchy of norms) -> regression tests on public-interest invariants -> sealed Regulatory Impact Card;
- a **named human** signs off; sign-off is refused without measured evidence and is recorded in ITU's own `kb_decisions` collection.

## Quick start
```bash
bash setup.sh                    # venv, ITU reference repo, models, knowledge base, tests
python run_demo.py               # governed vs ungoverned twin, same events
python inject_console.py         # judge console: add events or type a custom SMS
python run_agents.py --model qwen2.5:14b   # institutional agents + pre-registered evaluation
python run_gap_engine.py         # loopholes, counterfactual provisions, load-bearing rules
python run_baselines.py --model qwen2.5:14b  # rules vs LLM-only vs RAG-no-gate vs full HISN
python run_interop.py            # UAE vs India rule packs: agreement, divergences, gap coverage
python verify_message.py --sender H0SPITAL-A --text "Pay at http://x.example" --lang hi   # citizen verifier (6 languages)
python run_smpp.py               # real SMPP 3.4 server (then: python smpp_demo.py in another tab)
python build_dataset.py          # synthetic SMS dataset in ITU catalogue format
python export_itu_game.py        # export to ITU AI Readiness Simulation Game formats
python wind_tunnel.py "During a declared emergency, health message logs may be stored at a backup site abroad for 72 hours." --level regulation   # regulatory impact card
python selftest.py               # re-derives every headline number -> docs/headline_numbers.md
python build_dashboard.py && open docs/dashboard.html   # offline single-file dashboard
```

## Headline results (provenance: docs/headline_numbers.md; re-derived by `python selftest.py`)
- **Twin run (same events, with and without HISN):** legitimate essential messages silently lost **10 -> 0**; offshore health-data transfers not blocked **2 -> 0**.
- **Baselines on 33 gold items (qwen2.5:14b, ITU reference model):** an LLM without knowledge base or gate scored 16/33 with 10 harmful decisions and 41 unsupported legal citations; fixed rules 23/33 with 10 harmful; RAG without gates 23/33 with 9 harmful; **full HISN 26/33 with 1 harmful decision and 0 unsupported citations** (docs/baselines.md). Accuracy intervals overlap (62-89% vs 53-83%), so we claim a difference in harm and citation support, not in accuracy.
- **Development vs held-out:** development set 9/10. Pre-registered held-out sets (gold committed before any scored run, checked by `tools/verify_all.py`): v2 4/4, v3 1/2, v4 6/9, paraphrase 6/8; combined 17/23 (95% interval about 54-87%). These sets are small.
- **Known failure (held-out v4):** all three errors were spoofed messages. For an unauthenticated message claiming to be a hospital and asking for an ID number, the agent recommended release by a named officer, which our pre-registered severity rule counts as harmful (the one harmful decision above). A second spoof was caught by the deterministic gate, and a third got a request for more information. The model relied on surface cues (no link, local route) that do not prove sender identity. A release recommendation only records a request for a named human; the prototype does not release messages on an agent's recommendation. We did not tune on the held-out set.
- **Stability:** agent decisions were identical across repeated runs (44/44).
- **Wind tunnel:** the same emergency-offshore draft is DO NOT ISSUE AS DRAFTED as a regulation (conflicts with Federal Law 2/2019 Art. 13) but READY FOR NAMED HUMAN REVIEW as a Health Authority resolution; sender authentication + verified lane fixes spoofing invariants I3, I7 and I9 with no regressions (docs/impact_cards/).
- **Gap engine:** sender authentication + verified-sender lane raised the MIZAN balance score 76.7 -> 94.2; a blunt fraud duty lowered it by 0.5.
- **UAE-India:** 56% decision agreement; the health-data localisation conflict is documented (docs/interoperability.md).
- **Network evidence:** in 985,308 operator link-days (proxy), heat did not raise link failures (RR 0.54); rain did (RR 4.49).
- **Retrieval:** hybrid retrieval is the default, adopted under a decision rule committed before running (pre-registered v3 set: Recall@5 11/12 hybrid vs 10/12 clause-first). On the 46-question set, clause-first scored Recall@1 21/46 and Recall@5 41/46.
- **Gaps:** G1-G7 in docs/gap_register.yaml, each with its evidence status and source clauses; G7 (cross-border recognition of essential senders) is measured in docs/cross_border.md.

## Repository map
| path | contents |
|---|---|
| `app/core/` | enums, hash-chained audit log, policy gateway (P node), event bus, coordinator (MLFO), SMS firewall |
| `app/agents/` | institutional agents, retriever over the ITU KB, LLM wrapper, baselines |
| `app/gapengine/` | tactic catalogue, candidate provisions, engine, sign-off |
| `kb/` | manifest (SHA-256), verbatim clauses, rule packs, ingest via ITU pipeline, verify, retrieval eval |
| `scenarios/` | Crisis Exploit (Acts 1–4), injects, pre-registered gold (dev, held-out), ground truth (dashboard only) |
| `docs/` | evaluation logs, baselines, retrieval eval, counterfactual results, gap register, dashboard |
| `app/windtunnel/` | regulatory wind tunnel: draft rule -> mechanism mapping -> conflict scan -> regression tests -> Regulatory Impact Card |
| `app/smpp/` | SMPP 3.4 server for the SMS firewall demo |
| `drafts/` | example draft rules used by the wind tunnel |
| `open_kb/` | open knowledge-base package (checksums, datasheet, gap register copy, agent cards) |
| `tools/` | verification, fairness, stability and report-building scripts (`verify_all.py`, `fairness_check.py`, ...) |

## Knowledge base and copyright
Source PDFs are **not redistributed**. `kb/manifest.csv` lists each official URL and SHA-256; download into `kb/sources/` and run `python kb/verify.py`. Only short verbatim clauses are stored, with article references. English versions of UAE laws are translations; the Arabic text is authoritative.

## Limitations (honest)
Synthetic battery and scoring weights: results show direction, not real-world magnitudes. Global examples in docs/global_examples.yaml were checked against official sources (30 Oct - 1 Nov 2026); two items are flagged for recheck (the EU regulation number and a regulator report cited for the Australian scam-SMS code). Comparators on the gap engine's candidate provisions are marked "verify text" or "verification: pending" and are illustrative only. The 0.25 retrieval threshold does not transfer across embedding models and is not claimed as a safeguard. The SMS firewall accepts SMPP `submit_sm`-shaped messages; it is not a production SMSC.

## Verify our claims yourself

```bash
python tools/verify_all.py
```

Checks, without trusting us: every source file against its pinned SHA-256; every verbatim clause against its source PDF (normalisation rules printed); every audit-log hash chain; that each held-out gold file was committed before its first scored result (git history); and the open knowledge-base checksums.

## Key documents

| Document | What it shows |
|---|---|
| [`docs/gap_register.yaml`](docs/gap_register.yaml), [`docs/global_examples.yaml`](docs/global_examples.yaml) | Domain-level policy gaps with verbatim evidence, and verified global examples (Australia, EU) |
| [`docs/y3172_mapping.md`](docs/y3172_mapping.md), [`docs/readiness_mapping.md`](docs/readiness_mapping.md) | All 9 Y.3172 nodes; Readiness 2.0 metrics (ITU-verified IDs and metrics named in the report text) |
| [`docs/automation_levels.md`](docs/automation_levels.md) | ITU-T Y.3173 levels per component, computed by the standard's method |
| [`docs/what_if_none.md`](docs/what_if_none.md), [`docs/what_if_adopted.md`](docs/what_if_adopted.md) | Simulated timeline per filter threshold vs targets (Report 2.0, Dimension 10) |
| [`docs/case_brief_filter_threshold.md`](docs/case_brief_filter_threshold.md) | Governance case brief: the filter-threshold lesson |
| [`docs/cross_border.md`](docs/cross_border.md) | Gap G7: essential-sender recognition does not cross borders (India to UAE, measured) |
| [`docs/daily_report_none.md`](docs/daily_report_none.md), [`docs/fairness_check.md`](docs/fairness_check.md) | Regulator's daily assurance page; cross-language fairness check |
| [`docs/agent_cards/`](docs/agent_cards/), [`docs/datasheet_sms_dataset.md`](docs/datasheet_sms_dataset.md) | Agent cards (ITU-T Y.3176 fields); dataset datasheet |
| [`open_kb/`](open_kb/) | Open knowledge-base contribution for the ITU AI for Good Lab (acknowledgement to the UAE) |
| [`docs/onboarding_guide.md`](docs/onboarding_guide.md) | How to add a country or a domain |

## Principles

- **Domain-level gaps, not national recommendations.** HISN identifies domain-level policy gaps. National instruments (UAE, India, Singapore) are used as evidence, and verified global examples (e.g. Australia, EU) show how others have addressed each gap. Draft rules tested in the wind tunnel are illustrative and demonstrate the method; HISN makes no country-specific recommendations.
- **AI validates impact; humans decide** (ITU AI Readiness Report 2.0, FAQ 7). Language models only propose; deterministic code checks evidence and legal basis; a named human confirms every mechanism mapping and signs off every decision. The policy and legal adviser cites law but never makes it.

## Licence
Apache-2.0 (code). Knowledge-base metadata and clauses are provided for research; source documents remain the property of their issuers.
Synthetic SMS dataset (generated by `build_dataset.py`): CC-BY-4.0.

**Reproducing the exact headline numbers:** source documents are not redistributed. Download them from the URLs in `kb/manifest.csv` into `kb/sources/` and run `python kb/verify.py` to check their SHA-256 hashes. Without them, `setup.sh` still builds a working knowledge base from the 38 verbatim clauses, all tests pass, and agent results may differ slightly.
