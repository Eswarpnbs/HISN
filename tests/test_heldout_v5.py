import yaml
from app.core.audit import AuditLog
from app.core.gateway import PolicyGateway
from app.core.firewall import SmsFirewall
from app.core.coordinator import Coordinator
from app.core.injects import load_injects

def test_every_v5_gold_event_reaches_its_agent(tmp_path):
    a = AuditLog(tmp_path / "a.jsonl")
    out = Coordinator("scenarios/crisis_exploit.yaml", a, SmsFirewall("kb/rulepacks/uae/senders.yaml", a, governed=True),
                      PolicyGateway("kb/rulepacks/uae/rules.yaml", a), extra_events=load_injects(["heldout_v5"])).run()
    routed = {o["event_id"] + "-ESC": o.get("escalate_to") for o in out if o.get("escalate_to")}
    gold = yaml.safe_load(open("scenarios/gold_heldout_v5.yaml", encoding="utf-8"))
    assert len(gold) == 8
    for g in gold:
        assert routed.get(g["event"]) == g["role"], g["event"]

def test_v5_balances_spoofs_and_genuine():
    gold = yaml.safe_load(open("scenarios/gold_heldout_v5.yaml", encoding="utf-8"))
    keep = sum(g["acceptable"] == ["KEEP_QUARANTINED"] for g in gold)
    assert keep == 4 and len(gold) - keep == 4
