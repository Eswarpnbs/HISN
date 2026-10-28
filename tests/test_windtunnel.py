from app.windtunnel.compiler import compile_draft
from app.windtunnel.engine import wind_tunnel

class L:
    def __init__(self, out): self.out = out
    def __call__(self, s, u): return self.out

EMERG = {"mechanisms": [{"id": "emergency_offshore_exception", "params": {"hours": 72}}], "instrument_level": "regulation"}
def inv(r, i): return next(x for x in r["invariants_after"] if x["id"] == i)

def test_emergency_exception_as_regulation_conflicts_with_art13():
    r = wind_tunnel(compile_draft("emergency offshore", L(EMERG)))
    assert r["verdict"] == "DO NOT ISSUE AS DRAFTED" and r["unresolved_conflicts"] == 1 and not inv(r, "I2")["pass"]

def test_same_exception_as_health_authority_resolution_is_compatible():
    r = wind_tunnel(compile_draft("emergency offshore", L(EMERG), level_override="health_authority_resolution"))
    assert r["unresolved_conflicts"] == 0 and inv(r, "I2")["pass"]

def test_authentication_and_lane_fix_spoofing_without_regression():
    r = wind_tunnel(compile_draft("auth", L({"mechanisms": [{"id": "sender_authentication"}, {"id": "verified_sender_lane"}]})))
    assert "I3" in r["invariants_fixed"] and not r["invariants_broken"] and r["verdict"] == "READY FOR NAMED HUMAN REVIEW"

def test_invented_ids_rejected_and_dependency_warned():
    c = compile_draft("x", L({"mechanisms": [{"id": "ban_all_sms"}, {"id": "verified_sender_lane"}]}))
    assert c["rejected_ids"] == ["ban_all_sms"] and c["warnings"] == ["verified_sender_lane presupposes sender_authentication"]

def test_content_scanning_flags_article_16():
    r = wind_tunnel(compile_draft("scan", L({"mechanisms": [{"id": "content_scanning_health"}]})))
    assert any(x["clause"] == "UAE-FL-2-2019-ART16" and not x["resolved_by_level"] for x in r["conflicts"])
