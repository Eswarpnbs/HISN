import importlib.util
from pathlib import Path

def test_public_warnings_runs_and_is_audited(tmp_path):
    spec = importlib.util.spec_from_file_location("pw", Path("tools/public_warnings_check.py"))
    pw = importlib.util.module_from_spec(spec); spec.loader.exec_module(pw)
    r = pw.run(log=tmp_path / "pw.jsonl")
    assert len(r["rows"]) % 6 == 0 and len(r["rows"]) >= 42 and r["audit_ok"] is True
