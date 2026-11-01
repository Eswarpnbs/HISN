import importlib.util
from pathlib import Path

def test_language_scam_check_runs_and_is_audited(tmp_path):
    spec = importlib.util.spec_from_file_location("ls", Path("tools/language_scam_check.py"))
    ls = importlib.util.module_from_spec(spec); spec.loader.exec_module(ls)
    r = ls.run(log=tmp_path / "ls.jsonl")
    assert len(r["rows"]) == 12 and r["audit_ok"] is True
