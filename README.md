# HISN — governance for the telecom AI that decides what reaches citizens

**Team Sankalp** · ITU AI for Good Lab Hackathon (UAE) · Telecommunications + Healthcare + Public services
Eswar Panchakarla (team leader, engineering) · P. Prudhvi Krishna (knowledge base, policy, report)
Contact: [add emails] · **Synthetic data only. Fictional senders. No real phishing content is generated.**

## What it is
AI filters and network AI now decide whether hospital and government messages reach citizens. HISN governs those decisions:
- a deterministic **policy node** (ITU-T Y.3172 *P*) blocks only on verbatim, hash-pinned UAE legal clauses, and logs a **gap** when no provision exists;
- **institutional agents** (TDRA, health authority, Federal AI & Data Authority) see only their own events, cite only retrieved evidence, and only propose: fixed code checks evidence, mandate, binding basis, competence and consistency;
- a **gap engine** finds loopholes over an abstract tactic catalogue, re-runs the scenario with candidate provisions, and measures protection, access and the **MIZAN** balance score;
- a **named human** signs off; sign-off is refused without measured evidence and is recorded in ITU's own `kb_decisions` collection.

## Quick start
```bash
bash setup.sh                    # venv, ITU reference repo, models, knowledge base, tests
python run_demo.py               # governed vs ungoverned twin, same events
python inject_console.py         # judge console: add events or type a custom SMS
python run_agents.py --model qwen2.5:14b   # institutional agents + pre-registered evaluation
python run_gap_engine.py         # loopholes, counterfactual provisions, load-bearing rules
python run_baselines.py --model qwen2.5:14b  # rules vs LLM-only vs RAG-no-gate vs full HISN
python selftest.py               # re-derives every headline number -> docs/headline_numbers.md
python build_dashboard.py && open docs/dashboard.html   # offline single-file dashboard
```

## Headline results (see `docs/headline_numbers.md` for provenance)
- Twin: legitimate essential messages silently lost **3 → 0**; offshore health-data transfers not blocked **2 → 0**.
- Agents (qwen2.5:14b, ITU reference model): held-out v2 **4/4, 0 harmful**; pre-registered gold committed to git before each run.
- Baselines: an ungoverned LLM scored worse than fixed rules; RAG fixed citations but not judgment; full HISN was best (`docs/baselines.md`).
- Gap engine: authenticating essential senders plus a verified-sender lane raised MIZAN **76.7 → 94.2**; a blunt fraud duty lowered it (`docs/counterfactual_results.md`).
- Gaps G1–G5 (`docs/gap_register.yaml`): four verified within instruments, one discovered by the agents themselves.

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
