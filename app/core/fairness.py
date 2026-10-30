"""Language parity of the SMS filter: does the same genuine message from an authenticated sender get the same
decision in every language? Used to gate operator filter changes before deployment (gap G5)."""
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

def check_change(flags, threshold):
    res = parity(flags, threshold)
    unequal = {mid: acts for mid, acts in res.items() if len(set(acts.values())) > 1}
    return {"verdict": "DO NOT DEPLOY" if unequal else "DEPLOY", "unequal": unequal, "results": res}
