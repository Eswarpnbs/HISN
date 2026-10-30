import importlib.util
from pathlib import Path

def test_fairness_check_covers_all_languages_and_states():
    spec = importlib.util.spec_from_file_location("fc", Path("tools/fairness_check.py"))
    fc = importlib.util.module_from_spec(spec); spec.loader.exec_module(fc)
    res = fc.run()
    assert len(res) == 4 * 2 * 6
    assert {r["lang"] for r in res} == {"en", "ar", "hi", "te", "ur", "ml"}
