"""Language parity of the SMS filter, both ways: (1) does the same GENUINE message from an authenticated sender get the
same decision in every language, and (2) is the same SCAM stopped equally in English and Arabic? Used to gate operator
filter changes before deployment (gap G5) and by wind-tunnel invariant I9."""
import tempfile, yaml
from pathlib import Path
from .audit import AuditLog
from .firewall import SmsFirewall

LANGS = ["en", "ar", "hi", "te", "ur", "ml"]

def parity(flags, threshold=None, pairs_path="scenarios/fairness_pairs.yaml"):
    pairs = yaml.safe_load(open(pairs_path, encoding="utf-8"))
    fw = SmsFirewall("kb/rulepacks/uae/senders.yaml", AuditLog(Path(tempfile.mkdtemp()) / "p.jsonl"), policy=flags)
    if threshold is not None:
        fw.set_threshold(threshold, "pre-deployment language-parity check")
    return {m["id"]: {l: fw.process({"source_addr": "HOSPITAL-A", "short_message": m["text"][l], "route": "local",
                                     "authenticated": True})["action"] for l in LANGS} for m in pairs["messages"]}

# Synthetic scams (fictional senders, reserved .example domains): the same scam in English and Arabic.
SCAM_PAIRS = [
 ("No-link ID request claiming the hospital (local route)", {"source_addr": "HOSPITAL-A", "route": "local"},
  "Urgent: reply with your ID number to verify your hospital record.", "عاجل: أرسل رقم هويتك للتحقق من سجلك في المستشفى."),
 ("Payment link claiming the hospital (foreign route)", {"source_addr": "HOSPITAL-A", "route": "foreign_aggregator"},
  "Your lab fee is unpaid. Pay now at http://hospital-a-billing.example", "رسوم الفحص غير مدفوعة. ادفع الآن عبر http://hospital-a-billing.example"),
 ("Card-number request claiming the fines authority (local route)", {"source_addr": "GOV-FINES", "route": "local"},
  "Unpaid fine: reply with your card number to avoid penalties.", "مخالفة غير مدفوعة: أرسل رقم بطاقتك لتجنب الغرامات."),
]

def scam_parity(flags, threshold=None):
    """For each scam pair: (English action, Arabic action). A gap = stopped in one language, delivered in the other."""
    out = {}
    for name, base, en, ar in SCAM_PAIRS:
        acts = []
        for text in (en, ar):
            fw = SmsFirewall("kb/rulepacks/uae/senders.yaml", AuditLog(Path(tempfile.mkdtemp()) / "s.jsonl"), policy=flags)
            if threshold is not None:
                fw.set_threshold(threshold, "pre-deployment scam-parity check")
            acts.append(fw.process({**base, "short_message": text})["action"])
        out[name] = {"en": acts[0], "ar": acts[1], "gap": (acts[0] == "ALLOW") != (acts[1] == "ALLOW")}
    return out

def check_change(flags, threshold):
    res = parity(flags, threshold)
    unequal = {mid: acts for mid, acts in res.items() if len(set(acts.values())) > 1}
    scams = scam_parity(flags, threshold)
    scam_gaps = {k: v for k, v in scams.items() if v["gap"]}
    return {"verdict": "DO NOT DEPLOY" if (unequal or scam_gaps) else "DEPLOY", "unequal": unequal, "results": res,
            "scam_gaps": scam_gaps, "scam_results": scams}
