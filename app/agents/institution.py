"""Institutional agents: the LLM proposes; deterministic code validates evidence, mandate and event fit."""
import json
from app.core.enums import Verdict

ROLE_SPECS = {
    "health_authority": {
        "name": "Health Authority (DoH / DHA)",
        "mandate": "Protects patients and governs health information under Federal Law No. 2 of 2019. "
                   "Weighs patient harm from undelivered genuine health messages against scam risk. "
                   "Quarantined essential health messages may only be released by a named human officer.",
        "actions_by_kind": {
            "escalation": ["RECOMMEND_RELEASE_BY_NAMED_OFFICER", "KEEP_QUARANTINED", "REQUEST_INFO", "LOG_GAP"],
            "complaint": ["REFER_TO_TDRA", "REQUEST_INFO", "LOG_GAP"]}},
    "tdra": {
        "name": "TDRA (telecommunications regulator)",
        "mandate": "Regulates telecom licensees, including their obligations on unsolicited electronic "
                   "communications and network operations.",
        "actions_by_kind": {
            "network_summary": ["MONITOR", "REQUEST_INFO", "LOG_GAP"],
            "complaint": ["DIRECT_OPERATOR", "REQUEST_INFO", "LOG_GAP"]}},
    "ai_data_authority": {
        "name": "Federal Authority for AI and Data",
        "mandate": "Oversees AI and data governance, digital government and cross-border data questions. "
                   "Its mandates are transitional since June 2026.",
        "actions_by_kind": {"data_transfer": ["UPHOLD_BLOCK", "REQUEST_INFO", "LOG_GAP"]}},
}
DEFAULT_ACTIONS = ["REQUEST_INFO", "LOG_GAP"]

SYSTEM = """You are the {name} in a governance simulation (synthetic data only).
Mandate: {mandate}
Rules:
1. Use ONLY the EVIDENCE provided. Cite evidence by its exact id in "cited_ids". Cite only evidence that is directly relevant to THIS situation. Never invent laws, articles or ids.
2. Read the FACTS carefully. If the evidence does not cover the situation, choose "LOG_GAP" and describe the missing provision in one sentence.
3. Your assessment must be consistent with your proposed_action.
4. You only PROPOSE. Allowed proposed_action values for this event: {actions}.
5. Reply with JSON only:
{{"assessment": "...", "proposed_action": "...", "cited_ids": ["..."], "missing_provision": null, "uncertainty": "low|medium|high"}}"""

class InstitutionalAgent:
    def __init__(self, role, retriever, llm, audit, threshold=0.25):
        self.role, self.spec = role, ROLE_SPECS[role]
        self.retriever, self.llm, self.audit, self.threshold = retriever, llm, audit, threshold

    def allowed_actions(self, kind):
        return self.spec["actions_by_kind"].get(kind, DEFAULT_ACTIONS)

    def handle(self, event, outcome, now):
        facts = {"event_kind": event.kind, "payload": event.payload, "system_outcome": outcome}
        q = f"{event.kind}: {json.dumps(event.payload, ensure_ascii=False)}"
        evidence = self.retriever(q)
        best = max((e["similarity"] for e in evidence), default=0.0)
        actions = self.allowed_actions(event.kind)
        rec = {"role": self.role, "event_id": event.id, "t": now, "best_similarity": best,
               "evidence_ids": [e["id"] for e in evidence], "allowed_actions": actions}
        if best < self.threshold:
            rec.update(status=Verdict.INSUFFICIENT_EVIDENCE.value,
                       reason="retrieval_below_threshold", proposed_action="LOG_GAP")
            return self._log(rec)
        ev_text = "\n".join(f"[{e['id']}] ({e['basis']} {e['article']}) {e['text'][:600]}" for e in evidence)
        system = SYSTEM.format(name=self.spec["name"], mandate=self.spec["mandate"], actions=actions)
        user = f"SITUATION at t={now} min.\nFACTS:\n{json.dumps(facts, ensure_ascii=False, indent=1)}\n\nEVIDENCE:\n{ev_text}"
        try:
            out = self.llm(system, user)
        except Exception as ex:
            rec.update(status=Verdict.INSUFFICIENT_EVIDENCE.value, reason=f"llm_error:{ex}", proposed_action="LOG_GAP")
            return self._log(rec)
        action = out.get("proposed_action")
        cited = [c for c in out.get("cited_ids", []) if isinstance(c, str)]
        allowed_ids = set(rec["evidence_ids"])
        if action not in actions:
            rec.update(status=Verdict.INSUFFICIENT_EVIDENCE.value,
                       reason=f"action_not_allowed_for_event:{action}", proposed_action="LOG_GAP")
        elif action != "LOG_GAP" and (not cited or not set(cited) <= allowed_ids):
            rec.update(status=Verdict.INSUFFICIENT_EVIDENCE.value, reason="citation_not_in_evidence",
                       proposed_action="LOG_GAP", rejected_citations=sorted(set(cited) - allowed_ids))
        else:
            rec.update(status="PROPOSED" if action != "LOG_GAP" else Verdict.POTENTIAL_GAP.value,
                       proposed_action=action, cited_ids=cited)
        mp = out.get("missing_provision")
        rec.update(assessment=str(out.get("assessment", ""))[:600],
                   missing_provision=None if (not mp or str(mp).upper() in {a.upper() for a in actions}) else mp,
                   uncertainty=out.get("uncertainty"),
                   requires_human=(rec["proposed_action"] == "RECOMMEND_RELEASE_BY_NAMED_OFFICER"))
        return self._log(rec)

    def _log(self, rec):
        self.audit.write({"kind": "agent_rationale", **rec})
        return rec
