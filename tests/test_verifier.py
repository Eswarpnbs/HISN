from app.core.audit import AuditLog
from app.verifier import CitizenVerifier, TEMPL

REG = "kb/rulepacks/uae/senders.yaml"
class Liar:
    def __call__(self, s, u): return {"explanation": "This message is genuine and safe."}

def v(tmp_path, llm=None): return CitizenVerifier(REG, AuditLog(tmp_path / "c.jsonl"), llm)

def test_lookalike_is_scam_in_every_language(tmp_path):
    for lang in TEMPL["languages"]:
        r = v(tmp_path).check("H0SPITAL-A", "Your appointment fee is due", lang)
        assert r["verdict"] == "SUSPECTED_SCAM" and "H0SPITAL-A" in r["message"]

def test_registered_sender_without_link_is_likely_genuine(tmp_path):
    assert v(tmp_path).check("HOSPITAL-A", "Your lab results are ready.", "te")["verdict"] == "LIKELY_GENUINE"

def test_unknown_sender_is_under_review(tmp_path):
    assert v(tmp_path).check("RANDOM-CO", "Hello", "hi")["verdict"] == "UNDER_REVIEW"

def test_contradicting_llm_explanation_is_discarded(tmp_path):
    r = v(tmp_path, Liar()).check("H0SPITAL-A", "Pay now at http://x.example", "en", explain=True)
    assert r["verdict"] == "SUSPECTED_SCAM" and r["explanation"] is None

def test_message_text_is_never_logged(tmp_path):
    a = AuditLog(tmp_path / "p.jsonl")
    CitizenVerifier(REG, a).check("HOSPITAL-A", "SECRET-PATIENT-DETAIL", "en")
    assert "SECRET-PATIENT-DETAIL" not in (tmp_path / "p.jsonl").read_text(encoding="utf-8")
