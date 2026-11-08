"""Real Arabic message evaluation (added 8 Nov 2026). Counting rules fixed before the first run, below.

Data: Dataset of Arabic Spam and Ham Tweets (Kaddoura and Henno, Zayed University, Dubai; Mendeley Data 2024,
doi 10.17632/86x733xkb8.4, CC BY 4.0). ONLY the original file is used ("Dataset of Arabic Spam and Ham Tweets.xlsx",
13,241 real tweets: 1,924 spam, 11,299 ham). The augmented file contains generated text and is NOT used.
Download from https://data.mendeley.com/datasets/86x733xkb8/4 (not redistributed here).

    python tools/real_arabic_eval.py "path/to/Dataset of Arabic Spam and Ham Tweets.xlsx"

Measured: (1) how often HISN's Arabic filter keywords (kb/rulepacks/uae/senders.yaml) and (2) HISN's Arabic message
checks (app/agents/signals.py) fire on real Arabic spam and on real Arabic legitimate text, with Wilson 95% intervals.
These are tweets, not SMS: the test measures whether the Arabic checks over-fire on everyday real Arabic, which is the
risk that matters for "essential messages must not be lost". Reads .xlsx with the standard library only.
"""
import hashlib, math, re, sys, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core.audit import AuditLog
from app.core.firewall import SmsFirewall
from app.agents.signals import message_signals

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
RISK = ("untrusted_link", "offers_link", "asks_for_secret", "callback_number")

def wilson(k, n, z=1.96):
    if n == 0: return "n/a"
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return f"{100 * max(0, c - h):.1f}-{100 * min(1, c + h):.1f}%"

def read_xlsx(path):
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
            shared.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
    sheet = sorted(n for n in z.namelist() if n.startswith("xl/worksheets/sheet"))[0]
    rows = []
    for r in ET.fromstring(z.read(sheet)).iter("{%s}row" % NS["m"]):
        row = {}
        for c in r.findall("m:c", NS):
            col = re.sub(r"\d", "", c.get("r", ""))
            v = c.find("m:v", NS); is_ = c.find("m:is", NS)
            if c.get("t") == "s" and v is not None: val = shared[int(v.text)]
            elif is_ is not None: val = "".join(t.text or "" for t in is_.iter("{%s}t" % NS["m"]))
            else: val = v.text if v is not None else ""
            row[col] = val
        rows.append(row)
    return rows

def pick_columns(rows):
    header, body = rows[0], rows[1:]
    cols = sorted({k for r in body for k in r})
    txt = max(cols, key=lambda c: sum(len(str(r.get(c, ""))) for r in body))
    def score(c):    # the label column: few distinct, short values, ideally containing "spam"
        vals = {str(r.get(c, "")).strip().lower() for r in body if r.get(c)}
        short = all(len(v) <= 12 for v in vals)
        return (c != txt and short and 1 < len(vals) <= 3, any("spam" in v for v in vals))
    lab = max(cols, key=score)
    return header, body, lab, txt

def main(path, spam_value=None):
    raw = Path(path).read_bytes()
    header, body, lab, txt = pick_columns(read_xlsx(path))
    vals = {}
    for r in body: vals[str(r.get(lab, "")).strip().lower()] = vals.get(str(r.get(lab, "")).strip().lower(), 0) + 1
    sv = (spam_value or next((v for v in vals if "spam" in v), None))
    if sv is None:
        sys.exit(f"Label column {header.get(lab)} has values {vals}. Re-run with the spam value as a 2nd argument.")
    hv = next((v for v in vals if v != sv), None)
    spam = [r.get(txt, "") for r in body if str(r.get(lab, "")).strip().lower() == sv]
    ham = [r.get(txt, "") for r in body if str(r.get(lab, "")).strip().lower() == hv]
    fw = SmsFirewall("kb/rulepacks/uae/senders.yaml", AuditLog(Path("runs/real_arabic_audit.jsonl")), governed=False)
    kw = lambda t: any(k in str(t).lower() for k in fw.keywords)
    out = ["# Real Arabic message evaluation: 13,241 real Arabic tweets (original file only)", "",
           f"Input: Dataset of Arabic Spam and Ham Tweets (Kaddoura and Henno, Zayed University, CC BY 4.0), "
           f"{len(spam) + len(ham)} messages ({len(ham)} legitimate `{hv}`, {len(spam)} spam `{sv}`); text column "
           f"`{header.get(txt, txt)}`, label column `{header.get(lab, lab)}`; SHA-256 of input `{hashlib.sha256(raw).hexdigest()}`. "
           "Produced by `python tools/real_arabic_eval.py`. Counting rules were committed before the first run.", "",
           "| Class | Filter keyword hit (would be scored up) | Any message-check risk signal | Asks for a secret |", "|---|---|---|---|"]
    for name, ts in (("spam", spam), ("legitimate", ham)):
        s = [message_signals({"short_message": t}) for t in ts]; n = len(ts)
        k = sum(kw(t) for t in ts); a = sum(any(x[r] for r in RISK) for x in s); q = sum(x["asks_for_secret"] for x in s)
        out.append(f"| {name} | {k}/{n} = {100*k/max(n,1):.1f}% ({wilson(k, n)}) | {a}/{n} = {100*a/max(n,1):.1f}% ({wilson(a, n)}) | "
                   f"{q}/{n} = {100*q/max(n,1):.1f}% ({wilson(q, n)}) |")
    out += ["", "Reading: a keyword hit on legitimate Arabic means the filter would score it up. For an essential "
            "sender HISN then holds and routes it to a named officer instead of losing it; for others it is the "
            "operator's filter cost. The Arabic keywords and checks were written by the team and are pending native review.", "",
            "Limits: tweets (2023, Gulf Arabic and MSA), not SMS; no sender authentication."]
    Path("docs/real_arabic_eval.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))

if __name__ == "__main__":
    if len(sys.argv) not in (2, 3): sys.exit(__doc__)
    Path("runs").mkdir(exist_ok=True); main(sys.argv[1], sys.argv[2].lower() if len(sys.argv) == 3 else None)
