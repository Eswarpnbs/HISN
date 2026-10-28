from app.core.audit import AuditLog
from app.core.firewall import SmsFirewall
from app.core.gateway import PolicyGateway
from app.core.coordinator import Coordinator
from app.core.injects import load_injects
from app.core.packs import pack

def run(tmp_path, country):
    p = pack(country); a = AuditLog(tmp_path / f"{country}.jsonl")
    out = Coordinator("scenarios/crisis_exploit.yaml", a, SmsFirewall(p["senders"], a, policy=p["firewall_flags"]),
                      PolicyGateway(p["rules"], a), extra_events=load_injects(["gov_forged"])).run()
    return {o["event_id"]: o for o in out}, a

def test_offshore_health_data_diverges_between_packs(tmp_path):
    u, _ = run(tmp_path, "UAE"); i, a = run(tmp_path, "IN")
    assert u["A3-E3"]["action"] == "BLOCK_PROHIBITED" and i["A3-E3"]["action"] == "ALLOW"
    assert i["A3-E3"]["rule_id"] == "HEALTH_XFER_IN_01" and a.verify()

def test_india_route_binding_rejects_foreign_route_protected_id(tmp_path):
    u, _ = run(tmp_path, "UAE"); i, _ = run(tmp_path, "IN")
    assert u["INJ-GOVFORGED"]["action"] == "QUARANTINE"
    assert i["INJ-GOVFORGED"]["forced_by_policy"] == "protected_id_on_unregistered_route"
