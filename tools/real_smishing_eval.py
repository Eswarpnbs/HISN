"""Real smishing evaluation (added 8 Nov 2026). Fixed before the first run: what is counted and how, below.

Data: SMS Phishing Dataset for Machine Learning and Pattern Recognition (Mishra and Soni, Mendeley Data, 2022,
doi 10.17632/f45bkkt8pr.1, CC BY 4.0): 5,971 real SMS labelled ham (4,844), smishing (638) and spam (489).
Download the CSV from https://data.mendeley.com/datasets/f45bkkt8pr/1 (not redistributed here).

    python tools/real_smishing_eval.py path/to/Dataset_5971.csv

Measured on every message, with Wilson 95% intervals:
  1. HISN's message checks (app/agents/signals.py): share with a RISK SIGNAL = web address, offer of a link, request
     for a secret (ID, card, PIN, code, password, date of birth, account) or a phone number to call. These are the
     facts the agents receive; this shows how often they fire on real smishing and, the cost, on real legitimate SMS.
  2. The prototype filter's score at the operator thresholds (0.5 / 0.2 / 0.15), as in docs/real_sms_eval.md.
Real messages carry no network authentication, so the essential-sender lane is not tested here.
"""
import csv, hashlib, io, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core.audit import AuditLog
from app.core.firewall import SmsFirewall
from app.agents.signals import message_signals

RISK = ("untrusted_link", "offers_link", "asks_for_secret", "callback_number")

def wilson(k, n, z=1.96):
    if n == 0: return "n/a"
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return f"{100 * max(0, c - h):.1f}-{100 * min(1, c + h):.1f}%"

def load(raw):
    text = raw.decode("utf-8-sig", errors="replace")
    rows = list(csv.DictReader(io.StringIO(text)))
    if not rows: sys.exit("empty file")
    cols = list(rows[0].keys())
    lab = next((c for c in cols if c and "label" in c.lower()), cols[0])
    txt = next((c for c in cols if c and "text" in c.lower()), cols[1])
    out = []
    for r in rows:
        l = (r.get(lab) or "").strip().lower()
        l = "smishing" if l.startswith("smish") else l
        if l in ("ham", "spam", "smishing"): out.append((l, r.get(txt) or ""))
    return out, lab, txt

def pct(k, n): return f"{k}/{n} = {100 * k / max(n, 1):.1f}% ({wilson(k, n)})"

def main(path):
    raw = Path(path).read_bytes()
    rows, lab, txt = load(raw)
    by = {c: [t for l, t in rows if l == c] for c in ("smishing", "spam", "ham")}
    fw = SmsFirewall("kb/rulepacks/uae/senders.yaml", AuditLog(Path("runs/real_smishing_audit.jsonl")), governed=False)
    score = lambda t: fw.score({"source_addr": "LOCAL-SENDER", "route": "local", "short_message": t})[0]
    sig = {c: [message_signals({"short_message": t}) for t in ts] for c, ts in by.items()}
    out = ["# Real smishing evaluation: 5,971 real SMS", "",
           f"Input: SMS Phishing Dataset (Mishra and Soni 2022, Mendeley Data, CC BY 4.0), {len(rows)} messages "
           f"({len(by['ham'])} legitimate, {len(by['smishing'])} smishing, {len(by['spam'])} spam); columns `{lab}`/`{txt}`; "
           f"SHA-256 of input `{hashlib.sha256(raw).hexdigest()}`. Produced by `python tools/real_smishing_eval.py`. "
           "Counting rules were committed before the first run.", "",
           "## 1. HISN message checks (facts given to the agents)", "",
           "| Class | Any risk signal | Asks for a secret | Web address | Offers a link | Number to call |", "|---|---|---|---|---|---|"]
    for c in ("smishing", "spam", "ham"):
        s, n = sig[c], len(sig[c])
        anyr = sum(any(x[k] for k in RISK) for x in s)
        out.append(f"| {c} | {pct(anyr, n)} | {pct(sum(x['asks_for_secret'] for x in s), n)} | "
                   f"{pct(sum(x['untrusted_link'] for x in s), n)} | {pct(sum(x['offers_link'] for x in s), n)} | "
                   f"{pct(sum(x['callback_number'] for x in s), n)} |")
    out += ["", "## 2. Prototype filter at the operator thresholds", "",
            "| Threshold | Legitimate blocked | Smishing caught | Spam caught |", "|---|---|---|---|"]
    sc = {c: [score(t) for t in ts] for c, ts in by.items()}
    for thr in (0.5, 0.2, 0.15):
        f = lambda c: sum(v >= thr for v in sc[c])
        out.append(f"| {thr} | {pct(f('ham'), len(by['ham']))} | {pct(f('smishing'), len(by['smishing']))} | {pct(f('spam'), len(by['spam']))} |")
    out += ["", "Reading: the message checks are what the agents are told; a high rate on smishing with a low rate on "
            "legitimate SMS means the facts are informative. They never block anything by themselves: an unauthenticated "
            "sender claiming a protected entity is held by the fixed gate, and a person decides.", "",
            "Limits: English SMS collected for research (mostly India and UK), not UAE traffic; no sender IDs or "
            "authentication, so the essential-sender lane is not tested."]
    Path("docs/real_smishing_eval.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))

if __name__ == "__main__":
    if len(sys.argv) != 2: sys.exit(__doc__)
    Path("runs").mkdir(exist_ok=True); main(sys.argv[1])
