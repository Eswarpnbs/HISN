# Adding a country or a domain to HISN

HISN is a method: the steps that added India and Singapore to the UAE pack add any country, and new events add any domain. Nothing enters the knowledge base unless it is verified verbatim against an official source.

## Add a country
1. **Register sources** in `kb/register.py` (ID, title, issuer, country, type, basis, official URL, status). Download PDFs from official sites into `kb/sources/<ID>.pdf` (use a browser if a portal blocks scripts).
2. **Pin and verify:** `python kb/register.py`, then `python kb/verify.py`.
3. **Extract verbatim clauses** into `kb/clauses/clauses.yaml`, checking each appears verbatim in its PDF.
4. **Write the rule pack** (`kb/rulepacks/<country>/rules.yaml`, `senders.yaml`) citing only verified clauses; register it in `app/core/packs.py`.
5. **Assess the gaps** in `kb/rulepacks/gap_mechanisms.yaml` (none / partial / present, with clauses and a note).
6. **Rebuild the knowledge base:** `python kb/ingest_uae.py` (never during agent or baseline runs).
7. **Pre-register retrieval questions** in `kb/retrieval_gold.yaml`, commit, then `python kb/eval_retrieval.py`.
8. **Use it:** `python run_interop.py`; `python ask_adviser.py "<question>" --country <code>` (add the code to `ask_adviser.py`); the wind tunnel.

## Add a domain
1. **Events:** add injects in `scenarios/injects/`.
2. **Gold first:** write expected actions in a new held-out gold file and commit it before any run.
3. **Priority:** add urgency classes to a tiers file and have a domain expert review them.
4. **Mandates:** extend institutional agents in `app/agents/institution.py`.
5. **Automation levels:** add components to `kb/automation_levels.yaml` (computed by the ITU-T Y.3173 method).
6. **Evaluate:** `python run_agents.py --model qwen2.5:14b`, `python run_baselines.py --model qwen2.5:14b`.

## Checklist
- [ ] Every clause verified verbatim against a pinned official PDF
- [ ] Gold labels committed before the first run
- [ ] Gaps written at domain level, with global examples
- [ ] Tests pass (`python -m pytest -q`)
