"""Institutional agents: the LLM proposes; deterministic code validates evidence, mandate and event fit."""
import json
from app.core.enums import Verdict
from app.agents.signals import message_signals

ROLE_SPECS = {
    "health_authority": {
        "name": "Health Authority (DoH / DHA)",
        "mandate": "Protects patients and governs health information under Federal Law No. 2 of 2019. "
                   "Weighs patient harm from undelivered genuine health messages against scam risk. "
                   "Quarantined essential health messages may only be released by a named human officer.",
        "actions_by_kind": {
            "escalation": ["RECOMMEND_RELEASE_BY_NAMED_OFFICER", "KEEP_QUARANTINED", "REQUEST_INFO", "LOG_GAP"],
            "complaint": ["REFER_TO_TDRA", "REQUEST_INFO", "LOG_GAP"],
            "override_dispute": ["ORDER_OPERATOR_WHITELIST", "REQUEST_INFO", "LOG_GAP"]}},
    "tdra": {
        "name": "TDRA (telecommunications regulator)",
        "mandate": "Regulates telecom licensees, including their obligations on unsolicited electronic "
                   "communications and network operations.",
        "actions_by_kind": {
            "network_summary": ["MONITOR", "REQUEST_INFO", "LOG_GAP"],
            "complaint": ["DIRECT_OPERATOR", "REQUEST_INFO", "LOG_GAP"],
            "referral": ["DIRECT_OPERATOR", "REQUEST_INFO", "LOG_GAP"],
            "override_dispute": ["DIRECT_OPERATOR", "ASSIGN_OVERRIDE_AUTHORITY", "REQUEST_INFO", "LOG_GAP"]}},
    "ai_data_authority": {
        "name": "Federal Authority for AI and Data",
        "mandate": "Oversees AI and data governance, digital government and cross-border data questions. "
                   "Its mandates are transitional since June 2026.",
        "actions_by_kind": {"data_transfer": ["UPHOLD_BLOCK", "REQUEST_INFO", "LOG_GAP"],
            "escalation": ["RECOMMEND_RELEASE_BY_NAMED_OFFICER", "KEEP_QUARANTINED", "REQUEST_INFO", "LOG_GAP"],
            "override_dispute": ["ASSIGN_OVERRIDE_AUTHORITY", "REQUEST_INFO", "LOG_GAP"]}},
}
DEFAULT_ACTIONS = ["REQUEST_INFO", "LOG_GAP"]
# Decisive actions change what happens to a person's message or data: they REQUIRE cited evidence.
CITATION_REQUIRED = {"RECOMMEND_RELEASE_BY_NAMED_OFFICER", "KEEP_QUARANTINED", "UPHOLD_BLOCK", "DIRECT_OPERATOR",
                     "ASSIGN_OVERRIDE_AUTHORITY", "ORDER_OPERATOR_WHITELIST"}
# Soft law can inform, never compel: decisive actions need at least one binding source.
BINDING = {"FEDERAL_LAW", "NATIONAL_LAW", "REGULATOR_POLICY", "CABINET_RESOLUTION"}
# Competence needs a competence norm: which instruments can ground each decisive action.
# None = any binding source; () = no competence norm exists in this rule pack -> always a logged gap.
COMPETENT_SOURCES = {
    "DIRECT_OPERATOR": ("UAE-TDRA-",),
    "ORDER_OPERATOR_WHITELIST": ("UAE-TDRA-",),
    "ASSIGN_OVERRIDE_AUTHORITY": (),
    "UPHOLD_BLOCK": ("UAE-FL-", "UAE-PDPL-", "UAE-TDRA-"),
}
# Deterministic retrieval intents per event kind (what the institution needs to look up).
QUERY_INTENTS = {
    "escalation": "availability of health information to the authorised; release of a quarantined essential health message; human oversight of AI decisions",
    "complaint": "spam reporting facilities and protections for mobile customers; impersonation scam affecting patients",
    "network_summary": "licensee obligations on network operations and monitoring",
    "referral": "licensee obligations to protect customers from spam and impersonation scams; directions to telecom operators",
    "data_transfer": "storing or processing health data and information outside the State",
    "override_dispute": "authority to approve or override changes to operator AI filtering; notification duties for filter changes",
    "emergency_declared": "emergency declaration powers; exceptions for health data and telecommunications during emergencies",
    ("ai_data_authority", "escalation"): "messages from government entities; government data; human oversight of AI decisions",
}

SYSTEM = """You are the {name} in a governance simulation (synthetic data only).
Mandate: {mandate}
Rules:
1. Use ONLY the EVIDENCE provided. Cite evidence by its exact id in "cited_ids". Cite only evidence that is directly relevant to THIS situation. Never invent laws, articles or ids.
2. Read the FACTS carefully. If the evidence does not cover the situation, choose "LOG_GAP" and describe the missing provision in one sentence.
3. Your assessment must be consistent with your proposed_action. Rate scam_likelihood honestly from the FACTS (sender verification, route, URLs, firewall score and threshold).
4. Decisive actions (RECOMMEND_RELEASE_BY_NAMED_OFFICER, KEEP_QUARANTINED, UPHOLD_BLOCK, DIRECT_OPERATOR, ASSIGN_OVERRIDE_AUTHORITY, ORDER_OPERATOR_WHITELIST) REQUIRE at least one EVIDENCE id in cited_ids, and at least one cited source must be binding (FEDERAL_LAW or REGULATOR_POLICY) and within your competence. SOFT_LAW can inform but never alone justify a decisive action.
5. You only PROPOSE. Allowed proposed_action values for this event: {actions}.
6. Identity and content are two separate questions. WHO sent it: a sender ID shown in a message is a claim, not proof; only "authenticated": true proves it. WHAT it asks: read "message_signals" in the FACTS (fixed text checks). Decide in this order:
 a) NOT authenticated and the sender claims a government or health entity: never release. KEEP_QUARANTINED if it asks for a secret, a reply, a payment or a call-back, or offers a link.
 b) Authenticated, but it has an untrusted link, offers a link, or asks for a secret (ID, card, PIN, code, date of birth): KEEP_QUARANTINED; a proven sender does not ask for secrets by SMS.
 c) Authenticated, no link, no request for a secret: this is normal public service even if it says urgent, pay, fine, fee, verify, renew or call, and even if it points to the official app, website, number or service centre. The firewall held it only for a keyword. Rate scam_likelihood low and RECOMMEND_RELEASE_BY_NAMED_OFFICER, citing binding evidence; if no binding evidence covers it, LOG_GAP. Do not keep it quarantined and do not ask for more information.
7. Reply with JSON only:
{{"assessment": "...", "proposed_action": "...", "cited_ids": ["..."], "missing_provision": null, "uncertainty": "low|medium|high", "scam_likelihood": "low|medium|high"}}"""

class InstitutionalAgent:
    def __init__(self, role, retriever, llm, audit, threshold=0.25):
        self.role, self.spec = role, ROLE_SPECS[role]
        self.retriever, self.llm, self.audit, self.threshold = retriever, llm, audit, threshold

    def allowed_actions(self, kind):
        return self.spec["actions_by_kind"].get(kind, DEFAULT_ACTIONS)

    def handle(self, event, outcome, now):
        facts = {"event_kind": event.kind, "payload": event.payload, "system_outcome": outcome}
        if "short_message" in (event.payload or {}):
            facts["message_signals"] = message_signals(event.payload)
        q = f"{QUERY_INTENTS.get((self.role, event.kind), QUERY_INTENTS.get(event.kind, event.kind))} | {json.dumps(event.payload, ensure_ascii=False)}"
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
        elif (cited and not set(cited) <= allowed_ids) or (action in CITATION_REQUIRED and not cited):
            rec.update(status=Verdict.INSUFFICIENT_EVIDENCE.value, reason="citation_not_in_evidence",
                       proposed_action="LOG_GAP", rejected_citations=sorted(set(cited) - allowed_ids))
        else:
            rec.update(status="PROPOSED" if action != "LOG_GAP" else Verdict.POTENTIAL_GAP.value,
                       proposed_action=action, cited_ids=cited)
        if rec.get("status") == "PROPOSED" and action in CITATION_REQUIRED:
            prefixes = COMPETENT_SOURCES.get(action)
            grounded = [e for e in evidence if e["id"] in cited and e.get("basis") in BINDING
                        and (prefixes is None or str(e.get("record_id") or "").startswith(prefixes))]
            if not grounded:
                rec.update(status=Verdict.POTENTIAL_GAP.value, reason="no_competent_binding_basis",
                           rejected_action=action, proposed_action="LOG_GAP")
        # Gate 6 (applicability): a cited binding source must apply to THIS action on THESE facts. Releasing a held
        # message presupposes that the claimed essential sender is the real one, so release requires an
        # authenticated sender (fixed precondition, not model judgement). Added 7 Nov 2026 after held-out v4.
        if rec.get("status") == "PROPOSED" and action == "RECOMMEND_RELEASE_BY_NAMED_OFFICER" \
                and not event.payload.get("authenticated", False):
            rec.update(status="PRECONDITION_FAILED", reason="release_requires_authenticated_sender",
                       rejected_action=action, proposed_action="KEEP_QUARANTINED")
        sl = str(out.get("scam_likelihood", "")).lower() or None
        if rec.get("status") == "PROPOSED" and (
                (action == "KEEP_QUARANTINED" and sl == "low") or
                (action == "RECOMMEND_RELEASE_BY_NAMED_OFFICER" and sl == "high")):
            rec.update(status=Verdict.CONFLICT.value, reason="action_inconsistent_with_own_risk_rating")
        rec["scam_likelihood"] = sl
        mp = out.get("missing_provision")
        rec.update(assessment=str(out.get("assessment", ""))[:600],
                   missing_provision=None if (not mp or str(mp).upper() in {a.upper() for a in actions}) else mp,
                   uncertainty=out.get("uncertainty"),
                   requires_human=(rec["proposed_action"] == "RECOMMEND_RELEASE_BY_NAMED_OFFICER" or rec["status"] in ("CONFLICT", "PRECONDITION_FAILED")),
                   procedural=(rec["proposed_action"] not in CITATION_REQUIRED and rec["proposed_action"] != "LOG_GAP"))
        return self._log(rec)

    def _log(self, rec):
        self.audit.write({"kind": "agent_rationale", **rec})
        return rec
