from app.core.audit import AuditLog
from app.core.firewall import SmsFirewall
from app.core.gateway import PolicyGateway
from app.core.coordinator import Coordinator, load_scenario
from app.core.events import EventBus

SC, REG, PACK = "scenarios/crisis_exploit.yaml", "kb/rulepacks/uae/senders.yaml", "kb/rulepacks/uae/rules.yaml"

def _bus(tmp_path):
    bus = EventBus(AuditLog(tmp_path / "b.jsonl")); bus.load(load_scenario(SC)[1]); return bus

def test_no_agent_sees_the_future(tmp_path):
    bus = _bus(tmp_path); bus.release_until(10)
    assert all(e.t <= 10 for e in bus.view("filter_ai", 10))
    assert bus.view("filter_ai", 10) == []          # scam SMS arrives at t=20

def test_role_scoping(tmp_path):
    bus = _bus(tmp_path); bus.release_until(70)
    assert all(e.kind != "sms_submit" for e in bus.view("health_authority", 70))
    assert [e.id for e in bus.view("tdra", 70)] == ["A1-E2"]

def test_lookalike_scam_blocked_real_hospital_allowed(tmp_path):
    fw = SmsFirewall(REG, AuditLog(tmp_path / "f.jsonl"))
    scam = fw.process({"source_addr": "H0SPITAL-A", "route": "foreign_aggregator",
                       "short_message": "Pay the fee at http://hosp1tal-a.pay.example"})
    real = fw.process({"source_addr": "HOSPITAL-A", "route": "local",
                       "short_message": "Your appointment is rescheduled to 10:00."})
    assert scam["action"] == "BLOCK_OVERRIDABLE" and "lookalike_of:HOSPITAL-A" in scam["reasons"]
    assert real["action"] == "ALLOW"

def test_twin_divergence_on_overblocking(tmp_path):
    def run(governed):
        a = AuditLog(tmp_path / f"{governed}.jsonl")
        gw = PolicyGateway(PACK, a) if governed else None
        out = Coordinator(SC, a, SmsFirewall(REG, a, governed=governed), gw).run()
        return {o["event_id"]: o for o in out}, a
    g, ga = run(True); u, ua = run(False)
    assert g["A3-E2"]["action"] == "QUARANTINE" and g["A3-E2"]["escalate_to"] == "health_authority"
    assert u["A3-E2"]["silent_drop"] is True
    assert g["A3-E3"]["action"] == "BLOCK_PROHIBITED"     # Article 13, verified quote
    assert u["A3-E3"]["action"] == "ALLOW"
    assert ga.verify() and ua.verify()
