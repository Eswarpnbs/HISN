import tempfile
from pathlib import Path
from app.core.automation import TABLE_7_2, DIMS, overall, load
from app.core.audit import AuditLog
from app.core.coordinator import Coordinator

def test_algorithm_reproduces_every_row_of_table_7_2():
    for lvl, row in TABLE_7_2.items():
        assert overall(dict(zip(DIMS, row))) == lvl

def test_declared_components():
    lv = load()
    assert lv["filter_ai"]["overall"] == 2
    assert lv["institutional_agents"]["overall"] == 0 and lv["policy_adviser"]["overall"] == 0

class FW:
    def __init__(self): self.t = None
    def set_threshold(self, t, reason=""): self.t = t

def _run(tmp, payload, enforce):
    sc = Path(tmp) / "s.yaml"
    sc.write_text("events:\n  - {id: F1, t: 0, kind: filter_policy, audience: [filter_ai], payload: %s}\n" % payload, encoding="utf-8")
    fw, log = FW(), Path(tmp) / "a.jsonl"
    out = Coordinator(str(sc), AuditLog(log), fw, enforce_levels=enforce).run(until=0)
    return fw, out[0], log.read_text()

def test_unapproved_change_is_flagged_but_applied_by_default():
    with tempfile.TemporaryDirectory() as tmp:
        fw, o, log = _run(tmp, "{threshold: 0.2}", False)
        assert fw.t == 0.2 and o["automation_violation"] and "automation_level_violation" in log

def test_enforcement_holds_unapproved_change_and_applies_approved_one():
    with tempfile.TemporaryDirectory() as tmp:
        fw, o, _ = _run(tmp, "{threshold: 0.2}", True)
        assert fw.t is None and o["action"] == "HELD_FOR_APPROVAL"
    with tempfile.TemporaryDirectory() as tmp:
        fw, o, _ = _run(tmp, "{threshold: 0.2, approved_by: Duty Officer 1}", True)
        assert fw.t == 0.2 and o["action"] == "APPLIED"
