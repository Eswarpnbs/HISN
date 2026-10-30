"""Cross-language fairness check: the same genuine hospital message in six languages, through the SMS filter
in four policy states. Any difference in treatment by language is reported as a finding (ITU d11_m08; TEC 57050 spirit).
Synthetic messages; non-English versions pending native review."""
import sys, tempfile, yaml
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core.audit import AuditLog
from app.core.firewall import SmsFirewall

LANGS = ["en", "ar", "hi", "te", "ur", "ml"]
SHORT = {"ALLOW": "delivered", "QUARANTINE": "held"}

def states():
    ev = {e["id"]: e for e in yaml.safe_load(open("scenarios/crisis_exploit.yaml", encoding="utf-8"))["events"]}
    adopted = yaml.safe_load(open("kb/rulepacks/uae/adopted.yaml", encoding="utf-8"))["flags"]
    panic, drift = ev["A3-E1"]["payload"]["threshold"], ev["A4-E1"]["payload"]["threshold"]
    return [("today's rules, normal", {}, None), ("today's rules, after panic (Act 3)", {}, panic),
            ("today's rules, after drift (Act 4)", {}, drift), ("HISN-recommended rules, after panic", adopted, panic)]

def run():
    pairs = yaml.safe_load(open("scenarios/fairness_pairs.yaml", encoding="utf-8"))
    results = []
    for name, flags, thr in states():
        a = AuditLog(Path(tempfile.mkdtemp()) / "f.jsonl")
        fw = SmsFirewall("kb/rulepacks/uae/senders.yaml", a, policy=flags)
        if thr is not None:
            fw.set_threshold(thr, "fairness check")
        for m in pairs["messages"]:
            for lang in LANGS:
                r = fw.process({"source_addr": "HOSPITAL-A", "short_message": m["text"][lang], "route": "local", "authenticated": True})
                results.append({"state": name, "message": m["id"], "lang": lang, "action": r["action"], "score": r.get("score")})
    return results

def main():
    res = run()
    L = ["# Cross-language fairness check", "",
         "Same genuine message from an authenticated hospital, six languages, four policy states. "
         "Synthetic; non-English texts are machine-drafted and pending native review.", ""]
    findings = 0
    for state in dict.fromkeys(r["state"] for r in res):
        L += [f"## {state}", "", "| Message | " + " | ".join(LANGS) + " | Equal? |", "|---|" + "---|" * (len(LANGS) + 1)]
        for msg in dict.fromkeys(r["message"] for r in res):
            row = {r["lang"]: r for r in res if r["state"] == state and r["message"] == msg}
            cells = [SHORT.get(row[l]["action"], row[l]["action"].lower()) + (f" ({row[l]['score']:.2f})" if isinstance(row[l]["score"], (int, float)) else "") for l in LANGS]
            equal = len({row[l]["action"] for l in LANGS}) == 1
            findings += not equal
            L.append(f"| {msg} | " + " | ".join(cells) + f" | {'yes' if equal else '**NO**'} |")
        L.append("")
    L += [f"**Unequal treatment found in {findings} message/state combination(s).**", ""]
    Path("docs/fairness_check.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L)); print("written docs/fairness_check.md")

if __name__ == "__main__":
    main()
