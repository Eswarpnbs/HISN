"""Maker-checker demo: which approvals can unlock a filter-threshold change? Synthetic, fictional approvers.
A name string, a forged or edited record, the wrong role, the requester approving their own change,
a reused or expired approval: all are held. Only a valid signed record applies the change."""
import json, tempfile
from pathlib import Path
from app.core import approval as A
from app.core.audit import AuditLog
from app.core.coordinator import Coordinator

class FW:
    def __init__(self): self.t = None
    def set_threshold(self, t, reason=""): self.t = t

def case(payload, t=10):
    with tempfile.TemporaryDirectory() as tmp:
        sc = Path(tmp) / "s.yaml"
        sc.write_text("events:\n  - {id: A4-E1, t: %d, kind: filter_policy, audience: [filter_ai], payload: %s}\n"
                      % (t, json.dumps(payload)), encoding="utf-8")
        log = Path(tmp) / "a.jsonl"
        out = Coordinator(str(sc), AuditLog(log), FW(), enforce_levels=True, approval_mode="signed").run(until=t)
        why = [json.loads(l).get("reason") for l in log.read_text().splitlines() if '"approval_check"' in l]
        return out[0]["action"], (why or ["-"])[0]

ok = A.make_approval("A4-E1", "filter_policy", 0.15, "tdra-duty-officer", "vendor-ops", issued_at=0)
edited = dict(ok, value=0.05)
wrong_role = A.make_approval("A4-E1", "filter_policy", 0.15, "health-duty-officer", "vendor-ops", issued_at=0)
self_approved = A.make_approval("A4-E1", "filter_policy", 0.15, "operator-change-board", "operator-change-board", issued_at=0)
other_change = A.make_approval("A3-E1", "filter_policy", 0.15, "tdra-duty-officer", "vendor-ops", issued_at=0)
rows = [
    ("Vendor retunes with no approval", {"threshold": 0.15}, 10),
    ("Name typed in a field", {"threshold": 0.15, "approved_by": "Duty Officer 1"}, 10),
    ("Signed record, value edited afterwards", {"threshold": 0.05, "approval": edited}, 10),
    ("Signed by a role not competent for filters", {"threshold": 0.15, "approval": wrong_role}, 10),
    ("Requester approves own change", {"threshold": 0.15, "approval": self_approved}, 10),
    ("Approval copied from another change", {"threshold": 0.15, "approval": other_change}, 10),
    ("Valid record, used after it expired", {"threshold": 0.15, "approval": ok}, 75),
    ("Valid signed record from the TDRA duty officer", {"threshold": 0.15, "approval": ok}, 10),
]
print(f"{'case':48} {'result':18} reason")
print("-" * 100)
for name, payload, t in rows:
    act, why = case(payload, t)
    print(f"{name:48} {act:18} {why}")
