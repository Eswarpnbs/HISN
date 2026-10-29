import tempfile
from pathlib import Path
import pytest
from app.core.tiers import Tiers
from app.core.audit import AuditLog
from app.core.coordinator import Coordinator
from app.fhir import from_communication_request

T = Tiers()

def test_stat_from_authenticated_sender_is_T1():
    assert T.classify({"priority": "stat", "authenticated": True})[0] == "T1"
    assert T.max_hold("T1") == 5

def test_stat_from_unauthenticated_sender_is_ignored():
    tier, why = T.classify({"priority": "stat", "authenticated": False})
    assert tier == T.default and why == "unauthenticated_priority_ignored"

def test_missing_priority_defaults_to_T2():
    assert T.classify({"authenticated": True}) == ("T2", "no_priority_declared")

def test_T1_hold_escalates_at_5_minutes():
    with tempfile.TemporaryDirectory() as tmp:
        sc = Path(tmp) / "s.yaml"; sc.write_text("events: []\n", encoding="utf-8")
        c = Coordinator(str(sc), AuditLog(Path(tmp) / "a.jsonl"), firewall=None, tiers=T)
        c.holds.append({"event_id": "X", "t_held": 0, "escalated_to": "health_authority",
                        "resolved": None, "tier": "T1", "limit": 5})
        c._check_sla(0); assert c.holds[0]["resolved"] is None
        c._check_sla(5); assert c.holds[0]["resolved"] == "sla_second_review"
        assert c.outcomes[-1]["tier"] == "T1"

def test_fhir_reader_keeps_content_out_of_metadata():
    res = {"resourceType": "CommunicationRequest", "priority": "stat",
           "sender": {"reference": "Organization/HOSPITAL-A"},
           "payload": [{"contentString": "SYNTHETIC TEST CONTENT"}]}
    meta, text = from_communication_request(res, authenticated=True)
    assert "SYNTHETIC" not in str(meta) and text
    assert T.classify(meta)[0] == "T1"
    with pytest.raises(ValueError):
        from_communication_request({**res, "priority": "urgent-ish"}, authenticated=True)