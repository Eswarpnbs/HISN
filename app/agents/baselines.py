"""Baselines for comparison: B0 fixed rules, B1 LLM-only (no KB, no gate), B2 LLM+KB (RAG, no gate)."""
import json
from app.agents.institution import ROLE_SPECS, DEFAULT_ACTIONS, SYSTEM, QUERY_INTENTS

RULES = {"escalation": "KEEP_QUARANTINED", "complaint": "REQUEST_INFO", "data_transfer": "UPHOLD_BLOCK",
         "network_summary": "MONITOR", "override_dispute": "REQUEST_INFO"}

SYSTEM_NOKB = """You are the {name} in a governance simulation (synthetic data only).
Mandate: {mandate}
Use your own knowledge of UAE law and policy. Cite the instruments you rely on in "cited_ids".
Allowed proposed_action values for this event: {actions}.
Reply with JSON only:
{{"assessment": "...", "proposed_action": "...", "cited_ids": ["..."], "missing_provision": null, "scam_likelihood": "low|medium|high"}}"""

class RuleAgent:
    def __init__(self, role, audit):
        self.role, self.audit = role, audit
    def handle(self, event, outcome, now):
        rec = {"role": self.role, "event_id": event.id, "t": now, "status": "PROPOSED",
               "proposed_action": RULES.get(event.kind, "REQUEST_INFO"), "cited_ids": [], "baseline": "B0_rules"}
        self.audit.write({"kind": "baseline_decision", **rec})
        return rec

class UngatedLLMAgent:
    def __init__(self, role, retriever, llm, audit, use_kb=True):
        self.role, self.retriever, self.llm, self.audit, self.use_kb = role, retriever, llm, audit, use_kb
    def handle(self, event, outcome, now):
        spec = ROLE_SPECS[self.role]
        actions = spec["actions_by_kind"].get(event.kind, DEFAULT_ACTIONS)
        facts = {"event_kind": event.kind, "payload": event.payload, "system_outcome": outcome}
        evidence = []
        if self.use_kb:
            q = f"{QUERY_INTENTS.get((self.role, event.kind), QUERY_INTENTS.get(event.kind, event.kind))} | {json.dumps(event.payload, ensure_ascii=False)}"
            evidence = self.retriever(q)
            ev_text = "\n".join(f"[{e['id']}] ({e['basis']} {e['article']}) {e['text'][:600]}" for e in evidence)
            system = SYSTEM.format(name=spec["name"], mandate=spec["mandate"], actions=actions)
            user = f"SITUATION at t={now} min.\nFACTS:\n{json.dumps(facts, ensure_ascii=False, indent=1)}\n\nEVIDENCE:\n{ev_text}"
        else:
            system = SYSTEM_NOKB.format(name=spec["name"], mandate=spec["mandate"], actions=actions)
            user = f"SITUATION at t={now} min.\nFACTS:\n{json.dumps(facts, ensure_ascii=False, indent=1)}"
        try:
            out = self.llm(system, user)
        except Exception as ex:
            out = {"proposed_action": "ERROR", "cited_ids": [], "assessment": str(ex)}
        cited = [c for c in out.get("cited_ids", []) if isinstance(c, str)]
        ev_ids = {e["id"] for e in evidence}
        rec = {"role": self.role, "event_id": event.id, "t": now, "status": "PROPOSED",
               "proposed_action": out.get("proposed_action"), "cited_ids": cited,
               "unsupported_citations": [c for c in cited if c not in ev_ids],
               "out_of_mandate": out.get("proposed_action") not in actions,
               "baseline": "B2_rag_nogate" if self.use_kb else "B1_llm_only",
               "assessment": str(out.get("assessment", ""))[:400]}
        self.audit.write({"kind": "baseline_decision", **rec})
        return rec
