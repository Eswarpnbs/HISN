import yaml
from app.core.fairness import check_change

def test_panic_threshold_flagged_under_todays_rules():
    assert check_change({}, 0.2)["verdict"] == "DO NOT DEPLOY"

def test_normal_threshold_and_recommended_rules_pass():
    assert check_change({}, None)["verdict"] == "DEPLOY"
    adopted = yaml.safe_load(open("kb/rulepacks/uae/adopted.yaml", encoding="utf-8"))["flags"]
    assert check_change(adopted, 0.2)["verdict"] == "DEPLOY"
