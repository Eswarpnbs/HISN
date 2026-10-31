import importlib.util
from pathlib import Path

def test_what_if_rows_have_targets_and_gaps():
    spec = importlib.util.spec_from_file_location("wi", Path("tools/what_if.py"))
    wi = importlib.util.module_from_spec(spec); spec.loader.exec_module(wi)
    r = wi.run(0.20, {})
    assert {"delivered", "held", "lost", "scams_stopped", "t1_ok", "parity", "gaps", "held_by_act"} <= set(r)
    assert r["audit_ok"] is True
