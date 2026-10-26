from app.core.audit import AuditLog
from app.core.firewall import SmsFirewall
from app.core.gateway import PolicyGateway
from app.core.coordinator import Coordinator
from app.core.injects import load_injects

SC, REG, PACK = "scenarios/crisis_exploit.yaml", "kb/rulepacks/uae/senders.yaml", "kb/rulepacks/uae/rules.yaml"

def run(tmp_path, governed, injects):
    a = AuditLog(tmp_path / f"{governed}-{'-'.join(injects) or 'base'}.jsonl")
    c = Coordinator(SC, a, SmsFirewall(REG, a, governed=governed),
                    PolicyGateway(PACK, a) if governed else None, extra_events=load_injects(injects))
    return {o["event_id"]: o for o in c.run()}, a

def test_drift_holds_government_message(tmp_path):
    g, _ = run(tmp_path, True, []); u, _ = run(tmp_path, False, [])
    assert g["A4-E2"]["action"] == "QUARANTINE" and g["A4-E2"]["escalate_to"] == "ai_data_authority"
    assert u["A4-E2"]["silent_drop"] is True

def test_forged_exact_sender_is_escalated_not_released(tmp_path):
    g, _ = run(tmp_path, True, ["forged_sender"])
    assert g["INJ-FORGED"]["action"] == "QUARANTINE"
    assert "untrusted_url:hospital-a-billing.example" in g["INJ-FORGED"]["reasons"]

def test_emergency_has_no_fast_path(tmp_path):
    g, a = run(tmp_path, True, ["emergency"])
    assert g["INJ-EMERG-XFER"]["action"] == "BLOCK_PROHIBITED" and a.verify()
