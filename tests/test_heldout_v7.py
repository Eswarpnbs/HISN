import yaml
from app.core.audit import AuditLog
from app.core.gateway import PolicyGateway
from app.core.firewall import SmsFirewall
from app.core.coordinator import Coordinator
from app.core.injects import load_injects
from app.agents.institution import SYSTEM

def test_every_v7_gold_event_reaches_its_agent(tmp_path):
    a = AuditLog(tmp_path / "a.jsonl")
    out = Coordinator("scenarios/crisis_exploit.yaml", a, SmsFirewall("kb/rulepacks/uae/senders.yaml", a, governed=True),
                      PolicyGateway("kb/rulepacks/uae/rules.yaml", a), extra_events=load_injects(["heldout_v7"])).run()
    routed = {o["event_id"] + "-ESC": o.get("escalate_to") for o in out if o.get("escalate_to")}
    gold = yaml.safe_load(open("scenarios/gold_heldout_v7.yaml", encoding="utf-8"))
    assert len(gold) == 8 and sum(g["acceptable"] == ["KEEP_QUARANTINED"] for g in gold) == 4
    for g in gold:
        assert routed.get(g["event"]) == g["role"], g["event"]

def test_identity_rule_is_in_the_prompt():
    assert "a sender ID shown in a message is a claim, not proof" in SYSTEM

def test_rule6_separates_identity_from_content():
    assert "Identity and content are two separate questions" in SYSTEM and "message_signals" in SYSTEM

def test_v7_gold_matches_the_stated_rule_table():
    from app.agents.signals import message_signals
    from app.core.injects import load_injects
    gold = {g["event"]: g["acceptable"] for g in yaml.safe_load(open("scenarios/gold_heldout_v7.yaml", encoding="utf-8"))}
    for e in load_injects(["heldout_v7"]):
        s = message_signals(e.payload)
        keep = (not s["authenticated"]) or s["untrusted_link"] or s["offers_link"] or s["asks_for_secret"]
        assert ("KEEP_QUARANTINED" in gold[e.id + "-ESC"]) == keep, e.id
