"""Generate agent cards (ITU Sandbox catalogue style) from the code, so cards never drift from behaviour."""
import datetime, json
from pathlib import Path
from app.agents.institution import ROLE_SPECS, CITATION_REQUIRED, COMPETENT_SOURCES, BINDING
from app.gapengine.patches import PATCHES

TODAY = datetime.date.today().isoformat()
import csv as _csv, yaml as _yaml
_N_REC = len(list(_csv.DictReader(open("kb/manifest.csv", encoding="utf-8"))))
_N_CL = len(_yaml.safe_load(open("kb/clauses/clauses.yaml", encoding="utf-8")))
DATASET = f"HISN knowledge base: {_N_REC} hash-pinned records (UAE, India, Singapore; 1 Saudi historical draft), {_N_CL} verbatim clauses (kb/manifest.csv)"
COMMON_GUARD = ("Evidence-or-gap: cites only retrieved evidence; decisive actions need a binding source "
                f"({', '.join(sorted(BINDING))}) within competence; actions limited by mandate and event kind; "
                "self-consistency check (action vs own scam-likelihood rating -> CONFLICT -> named human); "
                "proposes only; every decision sealed in a SHA-256 hash-chained log.")
cards = []
for role, spec in ROLE_SPECS.items():
    acts = sorted({a for v in spec["actions_by_kind"].values() for a in v})
    cards.append({
        "id": f"hisn-{role.replace('_', '-')}", "name": f"HISN {spec['name']} agent", "version": "1.0.0",
        "type": "institutional agent (retrieve / propose / log gap)",
        "description": spec["mandate"],
        "models": ["qwen2.5:14b (reference) or qwen2.5:7b via Ollama", "nomic-embed-text (ITU reference ingest)"],
        "dataset": DATASET,
        "tools": ["retrieve (ITU KnowledgeBase, UAE filter, clause-first)", "propose action", "log gap"],
        "event_kinds": sorted(spec["actions_by_kind"]), "actions": acts,
        "decisive_actions": sorted(a for a in acts if a in CITATION_REQUIRED),
        "competence_norms": {a: (list(COMPETENT_SOURCES[a]) or "none in UAE pack -> logged gap") for a in acts if a in COMPETENT_SOURCES},
        "guardrail": COMMON_GUARD,
        "mapping": {"y3172_nodes": ["P", "MLFO"], "readiness": ["D10 AI & Policies (d10_m02, d10_m06, d10_m09)", "D7 Strategy Alignment (d7_m01)"]},
        "evaluation": "Pre-registered gold (dev + held-out), see docs/eval_log_v3.md and docs/baselines.md",
        "data": "Synthetic only", "licence": "Apache-2.0", "added": TODAY})
cards.append({
    "id": "hisn-policy-gateway", "name": "HISN Policy Gateway (deterministic, no LLM)", "version": "1.0.0",
    "type": "deterministic policy node (Y.3172 P)",
    "description": "Blocks only on verified verbatim clauses with blocking basis; unverified citations never block; uncovered events become POTENTIAL_GAP (fail-visible).",
    "models": [], "dataset": "kb/rulepacks/uae/rules.yaml", "tools": ["evaluate event against rule pack"],
    "guardrail": "No model in the decision path; foreign comparators and soft law never block.",
    "mapping": {"y3172_nodes": ["P"], "readiness": ["D10 (d10_m06 Safety Policies, d10_m10 Data Sovereignty)"]},
    "evaluation": "Load-bearing test: removing Art.13 rule unblocks 2 offshore transfers (docs/headline_numbers.md)",
    "data": "Synthetic only", "licence": "Apache-2.0", "added": TODAY})
cards.append({
    "id": "hisn-gap-engine", "name": "HISN Gap Engine (loophole hunt + counterfactual tests)", "version": "1.0.0",
    "type": "deterministic adversarial search + policy sandbox",
    "description": "Searches an abstract tactic catalogue for loopholes, re-runs the battery with candidate provisions, measures protection, access and MIZAN.",
    "models": [], "dataset": "Abstract tactic battery (no phishing text)",
    "tools": ["run battery", "apply provision patch", "load-bearing rule removal"],
    "candidate_provisions": [{"id": p["id"], "mechanism": p["mechanism"], "comparator": p["comparator"]} for p in PATCHES],
    "guardrail": "Placeholder message text only; comparators marked verify-text; every patch awaits named human sign-off; sign-off refused without measured evidence.",
    "mapping": {"y3172_nodes": ["Sandbox"], "readiness": ["D10 (d10_m01 Policy Sandbox, d10_m02 Policy Evaluation, d10_m03 Policy Extrapolation)"]},
    "evaluation": "docs/counterfactual_results.md", "data": "Synthetic only", "licence": "Apache-2.0", "added": TODAY})

out = Path("docs/agent_cards"); out.mkdir(parents=True, exist_ok=True)
# --- ITU-T Y.3176-style metadata for every card, and cards for the adviser, coordinator and wind tunnel ---
AUTHOR = "Team Sankalp (Eswar Panchakarla, P. Prudhvi Krishna)"
RUNTIME = "Python 3.10+, local Ollama (qwen2.5:14b, nomic-embed-text), fully offline; ITU AI Readiness reference ingest pipeline"
cards += [
 {"id": "hisn-policy-adviser", "name": "HISN Policy and Legal Adviser agent", "version": "1.0.0",
  "type": "policy and legal adviser agent (query, answer with citations)",
  "description": "Answers legal questions about the scenario from retrieved, verified evidence only, for the UAE, India or Singapore.",
  "models": ["qwen2.5:14b via Ollama", "nomic-embed-text (ITU reference ingest)"], "dataset": DATASET,
  "tools": ["retrieve (clause-first)", "answer", "link related gaps and verified global examples"],
  "guardrail": "Invented citations withheld; soft-law-only answers reported as no binding basis; never makes policy (Readiness Report 2.0 FAQ 7); every answer sealed in the audit chain.",
  "inputs": "natural-language question; country (UAE / IN / SG)",
  "outputs": "answer; status (binding basis / no binding basis / citation rejected); cited clause IDs with articles; related gaps; verified global examples with URLs",
  "mapping": {"y3172_nodes": ["M", "P"], "readiness": ["D10 (d10_m07 Explainability Metrics)"]},
  "evaluation": "tests/test_adviser.py; live answers for UAE and India logged in runs/adviser.jsonl",
  "data": "Synthetic scenario; public legal texts", "licence": "Apache-2.0", "added": TODAY},
 {"id": "hisn-coordinator", "name": "HISN Coordinator (MLFO, deterministic, no LLM)", "version": "1.0.0",
  "type": "machine learning function orchestrator (Y.3172 MLFO)",
  "description": "Advances the simulated clock, releases time-gated role-scoped events, routes escalations, routes referrals once between authorities (audited), enforces clinical-tier second review and emergency age.",
  "models": [], "dataset": "scenarios/crisis_exploit.yaml and scenarios/injects/",
  "tools": ["dispatch events", "route escalation", "route referral", "second review", "emergency state"],
  "guardrail": "Pre-agreed rules only; no re-referral; essential messages never silently dropped.",
  "inputs": "scenario events and injects; firewall, gateway and agent outputs",
  "outputs": "outcomes per event; holds with tier and limit; referral and escalation records in the audit chain",
  "mapping": {"y3172_nodes": ["MLFO"], "readiness": ["D7 (d7_m01 Coordination Level)"]},
  "evaluation": "tests/test_referrals.py, tests/test_tiers.py",
  "data": "Synthetic only", "licence": "Apache-2.0", "added": TODAY},
 {"id": "hisn-wind-tunnel", "name": "HISN Regulatory Wind Tunnel (policy sandbox)", "version": "1.0.0",
  "type": "regulatory sandbox (deterministic; a model only proposes the mechanism mapping, a human confirms)",
  "description": "Tests a draft rule before issuance against verified law (hierarchy of norms), eight public-interest invariants, measured effect and UAE-India interoperability; runs in CI on pull requests.",
  "models": ["qwen2.5:14b (mapping proposal only; skipped in CI where the human-confirmed mapping is in the draft file)"],
  "dataset": DATASET, "tools": ["compile draft", "conflict scan", "invariants I1-I8", "metrics", "interop", "impact card"],
  "guardrail": "Illustrative drafts only; no national recommendations; AI validates impact, humans decide (Report 2.0 FAQ 7); missing prerequisites refused.",
  "inputs": "draft text; instrument level; human-confirmed mechanisms",
  "outputs": "verdict; conflicts; invariants before and after; measured effect; interoperability; sealed impact card",
  "mapping": {"y3172_nodes": ["Sandbox", "P"], "readiness": ["D10 (d10_m01 Policy Sandbox, d10_m02 Policy Evaluation, d10_m03 Policy Extrapolation)"]},
  "evaluation": "tests/test_sunset.py, tests/test_confirmed.py; CI pull request #1 refused automatically",
  "data": "Synthetic only", "licence": "Apache-2.0", "added": TODAY},
]
_IO = {"hisn-policy-gateway": ("event (message metadata or data transfer)", "verdict and action with cited rule"),
       "hisn-gap-engine": ("abstract tactic battery; candidate patches", "loopholes, counterfactual metrics, load-bearing rules")}
from app.core.automation import load as _load_levels
_LEVELS = _load_levels()
for _c in cards:
    _c.setdefault("author", AUTHOR)
    _c.setdefault("runtime_environment", RUNTIME)
    _c.setdefault("inputs", _IO.get(_c["id"], ("event addressed to this institution; retrieved evidence",))[0])
    _c.setdefault("outputs", _IO.get(_c["id"], ("", "proposed action with cited clause IDs, or a logged gap"))[1])
    _comp = {"hisn-tdra": "institutional_agents", "hisn-health-authority": "institutional_agents", "hisn-ai-data-authority": "institutional_agents", "hisn-policy-gateway": "policy_gateway", "hisn-gap-engine": "gap_engine", "hisn-policy-adviser": "policy_adviser", "hisn-coordinator": "coordinator", "hisn-wind-tunnel": "wind_tunnel"}.get(_c["id"]); _c["automation_level"] = (_LEVELS[_comp]["label"] + " (ITU-T Y.3173; per-dimension levels in docs/automation_levels.md)") if _comp in _LEVELS else "not assessed"
    _c["metadata_standard"] = "Fields follow ITU-T Y.3176 ML model metadata (author, licence, name, version, description, inputs, outputs, runtime environment)"
Path("docs/agents.json").write_text(json.dumps(cards, indent=2, ensure_ascii=False), encoding="utf-8")
for c in cards:
    md = [f"# {c['name']}", "", f"**id** `{c['id']}` · **version** {c['version']} · **type** {c['type']} · **added** {c['added']}", "", c["description"], ""]
    for k in ("models", "dataset", "tools", "event_kinds", "actions", "decisive_actions", "competence_norms",
              "candidate_provisions", "guardrail", "mapping", "evaluation", "data", "licence"):
        if k in c and c[k] not in ([], None, ""): md.append(f"- **{k.replace('_', ' ')}**: {json.dumps(c[k], ensure_ascii=False) if not isinstance(c[k], str) else c[k]}")
    (out / f"{c['id']}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print(f"written docs/agents.json + {len(cards)} cards in docs/agent_cards/")
