import importlib.util
from pathlib import Path

def test_cross_border_runs_and_is_audited(tmp_path):
    spec = importlib.util.spec_from_file_location("cb", Path("tools/cross_border.py"))
    cb = importlib.util.module_from_spec(spec); spec.loader.exec_module(cb)
    r = cb.run(log=tmp_path / "cb.jsonl")
    assert len(r["rows"]) == 3 and r["audit_ok"] is True
    assert all({"domestic", "foreign"} <= set(row) for row in r["rows"])
