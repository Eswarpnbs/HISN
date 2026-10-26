import json
import pytest
from app.core.audit import AuditLog
from app.core.firewall import SmsFirewall
from app.core.gateway import PolicyGateway
from app.core.coordinator import Coordinator
from app.core.events import Event
from app.agents.institution import InstitutionalAgent
from app.gapengine import signoff as so

SC, REG, PACK = "scenarios/crisis_exploit.yaml", "kb/rulepacks/uae/senders.yaml", "kb/rulepacks/uae/rules.yaml"

class R:
    def __call__(self, q):
        return [{"id": "UAE-FL-2-2019-ART4", "text": "x", "similarity": 0.7,
                 "record_id": "UAE-FL-2-2019", "article": "Article (4)", "basis": "FEDERAL_LAW"}]
class L:
    def __init__(self, action): self.action = action
    def __call__(self, s, u):
        return {"proposed_action": self.action, "cited_ids": ["UAE-FL-2-2019-ART4"], "scam_likelihood": "low"}

def run(tmp_path, sla, agent_action=None):
    a = AuditLog(tmp_path / f"r{sla}{agent_action}.jsonl")
    agents = {"health_authority": InstitutionalAgent("health_authority", R(), L(agent_action), a)} if agent_action else {}
    c = Coordinator(SC, a, SmsFirewall(REG, a), PolicyGateway(PACK, a), agents=agents, sla_minutes=sla)
    return {o["event_id"]: o for o in c.run()}, a

def test_held_essential_message_goes_to_second_human_after_time_limit(tmp_path):
    out, a = run(tmp_path, 15)
    assert out["A3-E2-SLA"]["t"] == 65 and out["A3-E2-SLA"]["escalate_to"] == "duty_supervisor" and a.verify()
    assert "A4-E2-SLA" in out

def test_no_time_limit_means_no_second_review(tmp_path):
    out, _ = run(tmp_path, None)
    assert not any(k.endswith("-SLA") for k in out)

def test_release_recommendation_resolves_the_hold(tmp_path):
    out, _ = run(tmp_path, 15, "RECOMMEND_RELEASE_BY_NAMED_OFFICER")
    assert "A3-E2-SLA" not in out

def test_signoff_refused_without_measured_evidence(tmp_path, monkeypatch):
    log = tmp_path / "ge.jsonl"
    log.write_text(json.dumps({"kind": "counterfactual_test", "patch": "P-AUTH", "protection": 1, "access": 1,
                               "mizan": 1, "d_mizan": 1, "loopholes_closed": []}) + "\n", encoding="utf-8")
    monkeypatch.setattr(so, "EVIDENCE_LOG", log)
    monkeypatch.setattr(so, "OVERLAY", tmp_path / "adopted.yaml")
    audit = AuditLog(tmp_path / "s.jsonl")
    with pytest.raises(ValueError):
        so.signoff(["P-ROUTE", "P-FRAUD"], "X", "Y", "APPROVE", "", audit, record_in_itu_kb=False)
    so.signoff(["P-AUTH"], "X", "Y", "APPROVE", "", audit, record_in_itu_kb=False)
    assert (tmp_path / "adopted.yaml").exists() and audit.verify()
