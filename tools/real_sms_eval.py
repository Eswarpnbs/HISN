"""Real-message evaluation: how does threshold drift affect REAL text messages?

Data: the SMS Spam Collection (Almeida, Gomez Hidalgo and Yamakami, 2011), 5,574 real English SMS labelled ham
or spam, published by the UCI Machine Learning Repository under CC BY 4.0:
https://archive.ics.uci.edu/dataset/228/sms+spam+collection
Download the zip from that page and unzip it; the data file is called SMSSpamCollection (label<TAB>text).
The data is not redistributed here; only aggregate counts are written, with the SHA-256 of the input file.

    python tools/real_sms_eval.py path/to/SMSSpamCollection

What it measures: HISN's filter scores each real message on its text (keywords, untrusted links). Real messages
have no sender ID, so every message is treated as an ordinary local sender: this measures the filter, not HISN's
essential lane. For each threshold the operator might set (0.5 default, 0.2 after the scam wave, 0.15 after the
silent vendor retune) it counts legitimate messages blocked and spam caught, with Wilson 95% intervals.
"""
import hashlib, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core.audit import AuditLog
from app.core.firewall import SmsFirewall

def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return f"{100 * max(0, c - h):.1f}-{100 * min(1, c + h):.1f}%"

def main(path):
    raw = Path(path).read_bytes()
    rows = [l.split("\t", 1) for l in raw.decode("utf-8", errors="replace").splitlines() if "\t" in l]
    rows = [(lab.strip(), txt) for lab, txt in rows if lab.strip() in ("ham", "spam")]
    ham = [t for l, t in rows if l == "ham"]; spam = [t for l, t in rows if l == "spam"]
    fw = SmsFirewall("kb/rulepacks/uae/senders.yaml", AuditLog(Path("runs/real_sms_eval_audit.jsonl")), governed=False)
    score = lambda t: fw.score({"source_addr": "LOCAL-SENDER", "route": "local", "short_message": t})[0]
    sh, ss = [score(t) for t in ham], [score(t) for t in spam]
    out = ["# Real-message evaluation: threshold drift on 5,574 real SMS", "",
           f"Input: SMS Spam Collection (UCI, CC BY 4.0), {len(rows)} messages ({len(ham)} legitimate, {len(spam)} spam); "
           f"SHA-256 of input file `{hashlib.sha256(raw).hexdigest()}`. Produced by `python tools/real_sms_eval.py`.", "",
           "Every message is scored as an ordinary local sender (real messages carry no sender ID), so this measures the "
           "filter alone, not HISN's essential lane.", "",
           "| Threshold (event) | Legitimate messages blocked | Spam caught |", "|---|---|---|"]
    for thr, why in ((0.5, "default"), (0.2, "after the scam wave, A3-E1"), (0.15, "after the silent vendor retune, A4-E1")):
        fb = sum(s >= thr for s in sh); tp = sum(s >= thr for s in ss)
        out.append(f"| {thr} ({why}) | {fb}/{len(ham)} = {100 * fb / len(ham):.1f}% ({wilson(fb, len(ham))}) | "
                   f"{tp}/{len(spam)} = {100 * tp / len(spam):.1f}% ({wilson(tp, len(spam))}) |")
    fb2 = sum(s >= 0.2 for s in sh); tp2 = sum(s >= 0.2 for s in ss)
    out += ["", f"Reading: at 0.2 the filter blocks {fb2} real legitimate messages while catching {tp2} spam messages. "
            "The prototype's scores are discrete (0, 0.25, 0.3, 0.55 and up), so 0.15 and 0.2 behave the same on this data. "
            "The prototype filter is a deliberately simple stand-in and catches little real spam; HISN governs whatever "
            "filter an operator runs. In an ungoverned filter those blocks are silent. HISN does not make the filter more accurate; "
            "it makes sure blocked essential messages are held, routed to a named officer and receipted, and that the "
            "threshold change itself needs a signed approval.", "",
            "Limits: 2011 English SMS from the UK and Singapore, not UAE traffic; no sender IDs, so essential senders "
            "cannot be identified in this data."]
    Path("docs/real_sms_eval.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out[7:11]))

if __name__ == "__main__":
    if len(sys.argv) != 2: sys.exit(__doc__)
    Path("runs").mkdir(exist_ok=True); main(sys.argv[1])
