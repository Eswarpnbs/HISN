from app.core.audit import AuditLog
from app.core.events import Event
from app.core.firewall import SmsFirewall
from app.core.gateway import PolicyGateway
from app.core.coordinator import Coordinator
from app.agents.institution import InstitutionalAgent

SC, REG, PACK = "scenarios/crisis_exploit.yaml", "kb/rulepacks/uae/senders.yaml", "kb/rulepacks/uae/rules.yaml"
EV = Event(id="X", t=50, kind="escalation", audience=("health_authority",), payload={"source_addr": "HOSPITAL-A"})

class StubRetriever:
    def __init__(self, sim=0.6): self.sim = sim
    def __call__(self, q):
        return [{"id": "UAE-FL-2-2019-ART16", "text": "Article 16 text", "similarity": self.sim,
                 "record_id": "UAE-FL-2-2019", "article": "Article (16)", "basis": "FEDERAL_LAW"}]

class StubLLM:
    def __init__(self, out): self.out, self.calls = out, 0
    def __call__(self, s, u): self.calls += 1; return self.out

def agent(tmp_path, llm, sim=0.6):
    a = AuditLog(tmp_path / "a.jsonl")
    return InstitutionalAgent("health_authority", StubRetriever(sim), llm, a), a

def test_low_confidence_refuses_without_calling_llm(tmp_path):
    llm = StubLLM({}); ag, _ = agent(tmp_path, llm, sim=0.1)
    r = ag.handle(EV, {}, 50)
    assert r["status"] == "INSUFFICIENT_EVIDENCE" and llm.calls == 0

def test_invented_citation_is_rejected(tmp_path):
    ag, _ = agent(tmp_path, StubLLM({"proposed_action": "KEEP_QUARANTINED", "cited_ids": ["FAKE-LAW-9"]}))
    r = ag.handle(EV, {}, 50)
    assert r["reason"] == "citation_not_in_evidence" and r["rejected_citations"] == ["FAKE-LAW-9"]

def test_action_outside_mandate_is_rejected(tmp_path):
    ag, _ = agent(tmp_path, StubLLM({"proposed_action": "DELETE_ALL_MESSAGES", "cited_ids": ["UAE-FL-2-2019-ART16"]}))
    assert ag.handle(EV, {}, 50)["reason"].startswith("action_not_allowed")

def test_valid_proposal_requires_named_human(tmp_path):
    ag, a = agent(tmp_path, StubLLM({"proposed_action": "RECOMMEND_RELEASE_BY_NAMED_OFFICER",
                                     "cited_ids": ["UAE-FL-2-2019-ART16"], "assessment": "ok"}))
    r = ag.handle(EV, {}, 50)
    assert r["status"] == "PROPOSED" and r["requires_human"] is True and a.verify()

def test_escalation_reaches_health_authority_only_when_governed(tmp_path):
    def run(governed):
        a = AuditLog(tmp_path / f"{governed}.jsonl")
        ha = InstitutionalAgent("health_authority", StubRetriever(), StubLLM(
            {"proposed_action": "KEEP_QUARANTINED", "cited_ids": ["UAE-FL-2-2019-ART16"]}), a)
        c = Coordinator(SC, a, SmsFirewall(REG, a, governed=governed),
                        PolicyGateway(PACK, a) if governed else None, agents={"health_authority": ha})
        c.run(); return [o["event_id"] for o in c.agent_outputs], a
    g, ga = run(True); u, ua = run(False)
    assert "A3-E2-ESC" in g and "A3-E2-ESC" not in u
    assert "A2-E3" in g and "A2-E3" in u          # the complaint reaches it in both twins
    assert ga.verify() and ua.verify()

def test_action_must_fit_event_kind(tmp_path):
    ag, _ = agent(tmp_path, StubLLM({"proposed_action": "RECOMMEND_RELEASE_BY_NAMED_OFFICER",
                                     "cited_ids": ["UAE-FL-2-2019-ART16"]}))
    complaint = Event(id="C", t=40, kind="complaint", audience=("health_authority",), payload={})
    assert ag.handle(complaint, {}, 40)["reason"].startswith("action_not_allowed_for_event")
