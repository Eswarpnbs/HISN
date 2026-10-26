from app.core.audit import AuditLog
from app.gapengine.engine import run_battery, metrics, loopholes

def test_baseline_has_spoof_and_fraud_loopholes(tmp_path):
    lh = loopholes(run_battery({}, AuditLog(tmp_path / "b.jsonl")))
    assert ("exact_spoof_essential", "G2") in lh and ("unregistered_payment_demand", "G1") in lh

def test_auth_patch_closes_spoofing_without_hurting_access(tmp_path):
    a = AuditLog(tmp_path / "p.jsonl")
    base = metrics(run_battery({}, a)); res = run_battery({"require_auth": True}, a)
    assert ("exact_spoof_essential", "G2") not in loopholes(res)
    assert metrics(res)["access"] == base["access"] and metrics(res)["protection"] > base["protection"]

def test_fraud_duty_has_an_access_cost(tmp_path):
    a = AuditLog(tmp_path / "f.jsonl")
    base = metrics(run_battery({}, a)); m = metrics(run_battery({"fraud_duty": True}, a))
    assert m["protection"] > base["protection"] and m["access"] < base["access"]
