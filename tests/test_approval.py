import tempfile, json
from pathlib import Path
from app.core import approval as A
from app.core.audit import AuditLog
from app.core.coordinator import Coordinator

def good(**kw):
    a = A.make_approval("F1", "filter_policy", 0.2, "tdra-duty-officer", "vendor-ops", issued_at=0, valid_minutes=60)
    a.update(kw)
    return a

def test_valid_signed_approval_passes():
    assert A.verify(good(), "F1", "filter_policy", 0.2, now=10) == (True, "approved")

def test_name_string_is_not_an_approval():
    assert A.verify("Duty Officer 1", "F1", "filter_policy", 0.2, now=10) == (False, "no_signed_approval_record")

def test_forged_or_edited_record_fails_signature():
    a = good(); a["value"] = 0.05          # edited after signing
    assert A.verify(a, "F1", "filter_policy", 0.05, now=10) == (False, "signature_invalid")
    b = good(); b["signature"] = "0" * 64
    assert A.verify(b, "F1", "filter_policy", 0.2, now=10) == (False, "signature_invalid")

def test_approval_cannot_be_reused_for_another_change_or_value():
    assert A.verify(good(), "F2", "filter_policy", 0.2, now=10) == (False, "approval_bound_to_another_change")
    assert A.verify(good(), "F1", "filter_policy", 0.15, now=10) == (False, "approved_value_differs_from_change")

def test_role_must_be_competent():
    a = A.make_approval("F1", "filter_policy", 0.2, "health-duty-officer", "vendor-ops", issued_at=0)
    assert A.verify(a, "F1", "filter_policy", 0.2, now=10) == (False, "role_not_competent_for_change")
    v = A.make_approval("F1", "filter_policy", 0.2, "vendor-ops", "operator-change-board", issued_at=0)
    assert A.verify(v, "F1", "filter_policy", 0.2, now=10) == (False, "role_not_competent_for_change")

def test_unknown_approver_rejected():
    a = A.sign({"change_id": "F1", "kind": "filter_policy", "value": 0.2, "approver_id": "someone",
                "role": "x", "requested_by": "vendor-ops", "issued_at": 0, "expires_at": 60})
    assert A.verify(a, "F1", "filter_policy", 0.2, now=10) == (False, "approver_not_in_roster")

def test_maker_cannot_be_checker():
    a = A.make_approval("F1", "filter_policy", 0.2, "operator-change-board", "operator-change-board", issued_at=0)
    assert A.verify(a, "F1", "filter_policy", 0.2, now=10) == (False, "maker_and_checker_are_the_same")

def test_expiry():
    assert A.verify(good(), "F1", "filter_policy", 0.2, now=61) == (False, "approval_expired_or_not_yet_valid")

class FW:
    def __init__(self): self.t = None
    def set_threshold(self, t, reason=""): self.t = t

def _run(tmp, payload):
    sc = Path(tmp) / "s.yaml"
    sc.write_text("events:\n  - {id: F1, t: 0, kind: filter_policy, audience: [filter_ai], payload: %s}\n"
                  % json.dumps(payload), encoding="utf-8")
    fw, log = FW(), Path(tmp) / "a.jsonl"
    out = Coordinator(str(sc), AuditLog(log), fw, enforce_levels=True, approval_mode="signed").run(until=0)
    return fw, out[0], log.read_text()

def test_coordinator_signed_mode_holds_name_only_and_applies_signed():
    with tempfile.TemporaryDirectory() as tmp:
        fw, o, log = _run(tmp, {"threshold": 0.2, "approved_by": "Duty Officer 1"})
        assert fw.t is None and o["action"] == "HELD_FOR_APPROVAL" and "no_signed_approval_record" in log
    with tempfile.TemporaryDirectory() as tmp:
        fw, o, log = _run(tmp, {"threshold": 0.2, "approval": good()})
        assert fw.t == 0.2 and o["action"] == "APPLIED" and '"result": "APPROVED"' in log

def test_default_mode_unchanged():
    with tempfile.TemporaryDirectory() as tmp:
        sc = Path(tmp) / "s.yaml"
        sc.write_text("events:\n  - {id: F1, t: 0, kind: filter_policy, audience: [filter_ai], payload: {threshold: 0.2, approved_by: X}}\n", encoding="utf-8")
        fw = FW()
        out = Coordinator(str(sc), AuditLog(Path(tmp) / "a.jsonl"), fw, enforce_levels=True).run(until=0)
        assert fw.t == 0.2 and out[0]["action"] == "APPLIED"

def test_verifier_needs_only_the_public_key_and_rejects_a_key_it_does_not_know():
    roster = A.load_roster()
    assert all(len(a["public_key"]) == 64 for a in roster.values())
    a = good()
    swapped = {k: dict(v) for k, v in roster.items()}
    swapped["tdra-duty-officer"]["public_key"] = roster["operator-change-board"]["public_key"]
    assert A.verify(a, "F1", "filter_policy", 0.2, now=10, roster=swapped) == (False, "signature_invalid")
    nokey = {k: dict(v) for k, v in roster.items()}; nokey["tdra-duty-officer"].pop("public_key")
    assert A.verify(a, "F1", "filter_policy", 0.2, now=10, roster=nokey) == (False, "approver_has_no_registered_key")

def test_a_real_private_key_from_the_environment_is_used(monkeypatch):
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization as S
    k = ed25519.Ed25519PrivateKey.generate()
    monkeypatch.setenv("HISN_PRIV_TDRA_DUTY_OFFICER", k.private_bytes(S.Encoding.Raw, S.PrivateFormat.Raw, S.NoEncryption()).hex())
    roster = A.load_roster(); roster["tdra-duty-officer"]["public_key"] = k.public_key().public_bytes(S.Encoding.Raw, S.PublicFormat.Raw).hex()
    a = A.make_approval("F1", "filter_policy", 0.2, "tdra-duty-officer", "vendor-ops", issued_at=0, roster=roster)
    assert A.verify(a, "F1", "filter_policy", 0.2, now=10, roster=roster) == (True, "approved")
    assert A.verify(a, "F1", "filter_policy", 0.2, now=10) == (False, "signature_invalid")   # demo public key no longer matches
