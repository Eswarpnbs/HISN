from app.windtunnel.confirmed import compile_confirmed

def test_unknown_mechanism_rejected_and_prerequisite_flagged():
    c = compile_confirmed({"draft": "x", "mechanisms": [{"id": "no_such"}, {"id": "verified_sender_lane"}]})
    assert c["rejected_ids"] == ["no_such"]
    assert c["warnings"] == ["verified_sender_lane presupposes sender_authentication"]

def test_unstated_time_limit_stays_unstated():
    c = compile_confirmed({"draft": "x", "mechanisms": [{"id": "emergency_offshore_exception"}]})
    assert c["mechanisms"][0]["params"]["hours"] is None
