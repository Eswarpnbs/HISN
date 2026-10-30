import tempfile
from pathlib import Path
from app.core.audit import AuditLog
from app.core.coordinator import Coordinator

class Fake:
    def __init__(self, role, action): self.role, self.action, self.seen = role, action, []
    def handle(self, e, r, now):
        self.seen.append(e.kind)
        return {"role": self.role, "event_id": e.id, "status": "PROPOSED", "proposed_action": self.action,
                "assessment": "synthetic", "cited_ids": []}

def _run(tmp, route):
    sc = Path(tmp) / "s.yaml"
    sc.write_text("events:\n  - {id: C1, t: 0, kind: complaint, audience: [health_authority], payload: {note: synthetic}}\n", encoding="utf-8")
    ha, td = Fake("health_authority", "REFER_TO_TDRA"), Fake("tdra", "REFER_TO_TDRA")
    log = Path(tmp) / "a.jsonl"
    Coordinator(str(sc), AuditLog(log), firewall=None, agents={"health_authority": ha, "tdra": td}, route_referrals=route).run(until=0)
    return td, log

def test_referral_routed_once_and_audited():
    with tempfile.TemporaryDirectory() as tmp:
        td, log = _run(tmp, True)
        assert td.seen == ["referral"]
        assert log.read_text().count("referral_routed") == 1

def test_no_routing_when_disabled():
    with tempfile.TemporaryDirectory() as tmp:
        td, _ = _run(tmp, False)
        assert td.seen == []
