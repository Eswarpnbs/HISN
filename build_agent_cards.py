"""Generate agent cards (ITU Sandbox catalogue style) from the code, so cards never drift from behaviour."""
import datetime, json
from pathlib import Path
from app.agents.institution import ROLE_SPECS, CITATION_REQUIRED, COMPETENT_SOURCES, BINDING
from app.gapengine.patches import PATCHES

TODAY = datetime.date.today().isoformat()
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
        "dataset": "UAE knowledge base: 13 hash-pinned records (UAE, India, Singapore; 1 Saudi historical draft), 32 verbatim clauses (kb/manifest.csv)",
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
Path("docs/agents.json").write_text(json.dumps(cards, indent=2, ensure_ascii=False), encoding="utf-8")
for c in cards:
    md = [f"# {c['name']}", "", f"**id** `{c['id']}` · **version** {c['version']} · **type** {c['type']} · **added** {c['added']}", "", c["description"], ""]
    for k in ("models", "dataset", "tools", "event_kinds", "actions", "decisive_actions", "competence_norms",
              "candidate_provisions", "guardrail", "mapping", "evaluation", "data", "licence"):
        if k in c and c[k] not in ([], None, ""): md.append(f"- **{k.replace('_', ' ')}**: {json.dumps(c[k], ensure_ascii=False) if not isinstance(c[k], str) else c[k]}")
    (out / f"{c['id']}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print(f"written docs/agents.json + {len(cards)} cards in docs/agent_cards/")
