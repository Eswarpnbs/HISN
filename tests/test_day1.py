from app.core.audit import AuditLog
from app.core.gateway import PolicyGateway

PACK = "kb/rulepacks/uae/rules.yaml"

def test_unverified_citation_does_not_block(tmp_path):
    log = AuditLog(tmp_path / "a.jsonl")
    gw = PolicyGateway(PACK, log)
    d = gw.evaluate({"type": "message_log_transfer", "data_class": "health",
                     "destination_country": "XX"})
    assert d["action"].value == "QUARANTINE"
    assert log.verify()

def test_uncovered_event_becomes_gap(tmp_path):
    log = AuditLog(tmp_path / "a.jsonl")
    gw = PolicyGateway(PACK, log)
    d = gw.evaluate({"type": "sender_id_spoof", "sender_class": "government"})
    assert d["verdict"].value == "POTENTIAL_GAP"
    assert log.verify()
