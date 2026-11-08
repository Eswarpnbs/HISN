import yaml
from app.core.audit import AuditLog
from app.core.gateway import PolicyGateway
from app.core.firewall import SmsFirewall
from app.core.coordinator import Coordinator
from app.core.injects import load_injects
from app.agents.signals import message_signals
from app.agents.llm import VotingLLM

def test_every_v8_gold_event_reaches_its_agent(tmp_path):
    a = AuditLog(tmp_path / "a.jsonl")
    out = Coordinator("scenarios/crisis_exploit.yaml", a, SmsFirewall("kb/rulepacks/uae/senders.yaml", a, governed=True),
                      PolicyGateway("kb/rulepacks/uae/rules.yaml", a), extra_events=load_injects(["heldout_v8"])).run()
    routed = {o["event_id"] + "-ESC": o.get("escalate_to") for o in out if o.get("escalate_to")}
    gold = yaml.safe_load(open("scenarios/gold_heldout_v8.yaml", encoding="utf-8"))
    assert len(gold) == 10 and sum(g["acceptable"] == ["KEEP_QUARANTINED"] for g in gold) == 5
    for g in gold:
        assert routed.get(g["event"]) == g["role"], g["event"]

def test_v8_gold_matches_the_stated_rule_table_in_both_languages():
    gold = {g["event"]: g["acceptable"] for g in yaml.safe_load(open("scenarios/gold_heldout_v8.yaml", encoding="utf-8"))}
    for e in load_injects(["heldout_v8"]):
        s = message_signals(e.payload)
        keep = (not s["authenticated"]) or s["untrusted_link"] or s["offers_link"] or s["asks_for_secret"]
        assert ("KEEP_QUARANTINED" in gold[e.id + "-ESC"]) == keep, e.id

def test_majority_vote_keeps_the_winning_answer_and_records_votes():
    a = lambda s, u: {"proposed_action": "KEEP_QUARANTINED", "cited_ids": ["x"]}
    b = lambda s, u: {"proposed_action": "RECOMMEND_RELEASE_BY_NAMED_OFFICER", "cited_ids": ["y"]}
    out = VotingLLM([a, b, b])("s", "u")
    assert out["proposed_action"] == "RECOMMEND_RELEASE_BY_NAMED_OFFICER" and out["cited_ids"] == ["y"]
    assert out["_votes"] == ["KEEP_QUARANTINED", "RECOMMEND_RELEASE_BY_NAMED_OFFICER", "RECOMMEND_RELEASE_BY_NAMED_OFFICER"]

def test_no_majority_falls_back_to_the_temperature_zero_answer_and_failures_do_not_sink_it():
    c = lambda s, u: {"proposed_action": "LOG_GAP"}
    def boom(s, u): raise ValueError("bad json")
    a = lambda s, u: {"proposed_action": "KEEP_QUARANTINED"}
    assert VotingLLM([a, c, boom])("s", "u")["proposed_action"] == "KEEP_QUARANTINED"
    assert VotingLLM([boom, c, c])("s", "u")["proposed_action"] == "LOG_GAP"
