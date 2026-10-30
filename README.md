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

## Headline results (provenance: docs/headline_numbers.md)
- Baselines on qwen2.5:14b (ITU reference model): an ungoverned LLM scored 7/14 with 18 unsupported legal citations, worse than fixed rules (11/14); RAG without gates 8/14 with 5 harmful decisions; **full HISN 12/14, held-out 4/4, 0 harmful, 0 unsupported citations** (docs/baselines_14b.md).
- Wind tunnel: the same emergency-offshore draft is DO NOT ISSUE as a regulation (conflicts with Federal Law 2/2019 Art. 13) but READY FOR HUMAN REVIEW as a Health Authority resolution (Art. 13's own route); sender authentication + verified lane fixes the spoofing invariant with no regressions (docs/impact_cards/).
- Twin: legitimate essential messages silently lost **3 -> 0**; offshore health-data transfers not blocked **2 -> 0**.
- Gap engine: sender authentication + verified-sender lane raised MIZAN **76.7 -> 94.2**; a blunt fraud duty lowered it.
- UAE-India: 56% decision agreement; health-data localisation conflict; 4 of 5 gaps shared or partial in both (docs/interoperability.md).
- Network evidence: in 985,308 real operator link-days (proxy), heat did not raise link failures (RR 0.54); rain did (RR 4.49).
- Retrieval: Recall@5 22/24; similarity threshold found not to transfer across embedding models (documented, not claimed).
- Gaps G1-G5 (docs/gap_register.yaml): four verified within instruments, one discovered by the agents.

## Repository map
| path | contents |
|---|---|
| `app/core/` | enums, hash-chained audit log, policy gateway (P node), event bus, coordinator (MLFO), SMS firewall |
| `app/agents/` | institutional agents, retriever over the ITU KB, LLM wrapper, baselines |
| `app/gapengine/` | tactic catalogue, candidate provisions, engine, sign-off |
| `kb/` | manifest (SHA-256), verbatim clauses, rule packs, ingest via ITU pipeline, verify, retrieval eval |
| `scenarios/` | Crisis Exploit (Acts 1–4), injects, pre-registered gold (dev, held-out), ground truth (dashboard only) |
| `docs/` | evaluation logs, baselines, retrieval eval, counterfactual results, gap register, dashboard |

## Knowledge base and copyright
Source PDFs are **not redistributed**. `kb/manifest.csv` lists each official URL and SHA-256; download into `kb/sources/` and run `python kb/verify.py`. Only short verbatim clauses are stored, with article references. English versions of UAE laws are translations; the Arabic text is authoritative.

## Limitations (honest)
Synthetic battery and scoring weights: results show direction, not real-world magnitudes. Comparator texts are marked "verify text" until checked. The 0.25 retrieval threshold does not transfer across embedding models and is not claimed as a safeguard. The SMS firewall accepts SMPP `submit_sm`-shaped messages; it is not a production SMSC.

## Licence
Apache-2.0 (code). Knowledge-base metadata and clauses are provided for research; source documents remain the property of their issuers.
Synthetic SMS dataset (generated by `build_dataset.py`): CC-BY-4.0.

**Reproducing the exact headline numbers:** source documents are not redistributed. Download them from the URLs in `kb/manifest.csv` into `kb/sources/` and run `python kb/verify.py` to check their SHA-256 hashes. Without them, `setup.sh` still builds a working knowledge base from the 33 verbatim clauses, all tests pass, and agent results may differ slightly.
