from app.core.audit import AuditLog
from app.core.firewall import SmsFirewall
from app.core.gateway import PolicyGateway
from app.core.coordinator import Coordinator
from app.core.injects import load_injects
from app.core.packs import pack

def run(tmp_path, c):
    p = pack(c); a = AuditLog(tmp_path / f"{c}.jsonl")
    out = Coordinator("scenarios/crisis_exploit.yaml", a, SmsFirewall(p["senders"], a, policy=p["firewall_flags"]),
                      PolicyGateway(p["rules"], a), extra_events=load_injects(["gov_forged"])).run()
    return {o["event_id"]: o for o in out}

def test_three_transfer_models(tmp_path):
    u, i, s = run(tmp_path, "UAE"), run(tmp_path, "IN"), run(tmp_path, "SG")
    assert (u["A3-E3"]["action"], i["A3-E3"]["action"], s["A3-E3"]["action"]) == ("BLOCK_PROHIBITED", "ALLOW", "QUARANTINE")

def test_singapore_route_rule_and_url_blocklist_with_lag(tmp_path):
    s = run(tmp_path, "SG")
    assert s["INJ-GOVFORGED"]["forced_by_policy"] == "sender_id_from_unauthorised_aggregator"
    fw = SmsFirewall(pack("SG")["senders"], AuditLog(tmp_path / "f.jsonl"), policy=pack("SG")["firewall_flags"])
    known = fw.process({"source_addr": "RANDOM-CO", "route": "local", "short_message": "Pay at http://pay-portal.example"})
    new = fw.process({"source_addr": "RANDOM-CO", "route": "local", "short_message": "Pay at http://brand-new-scam.example"})
    assert known.get("forced_by_policy") == "known_malicious_url" and new.get("forced_by_policy") is None
