"""What-if simulated timeline (ITU AI Readiness Report 2.0, Dimension 10 "AI for Policies", FAQ 6).
Replays the crisis timeline once per candidate filter threshold, as if the operator had chosen that value at each
filter change, and compares outcomes with fixed targets. Synthetic data: shows direction, not real-world magnitude."""
import argparse, sys, tempfile, yaml
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core.audit import AuditLog
from app.core.firewall import SmsFirewall
from app.core.gateway import PolicyGateway
from app.core.coordinator import Coordinator
from app.core.injects import load_injects, available
from app.core.tiers import Tiers
from app.core.fairness import check_change

SC = "scenarios/crisis_exploit.yaml"
TARGETS = "0 genuine essential messages lost; 0 scams delivered; T1 within clinical limit; equal treatment in 6 languages"

def run(threshold, flags):
    data = yaml.safe_load(open(SC, encoding="utf-8"))
    for e in data["events"]:
        if e["kind"] == "filter_policy":
            e["payload"]["threshold"] = threshold
    sc = Path(tempfile.mkdtemp()) / "sc.yaml"; sc.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    gt = yaml.safe_load(open("scenarios/ground_truth.yaml", encoding="utf-8"))
    a = AuditLog(Path(tempfile.mkdtemp()) / "w.jsonl")
    c = Coordinator(str(sc), a, SmsFirewall("kb/rulepacks/uae/senders.yaml", a, policy=flags),
                    PolicyGateway("kb/rulepacks/uae/rules.yaml", a), extra_events=load_injects(available()),
                    sla_minutes=15, tiers=Tiers())
    out = c.run(); by = {o["event_id"]: o for o in out}
    sms = [o for o in out if o["kind"] == "sms_submit"]
    legit = [o for o in sms if gt.get(o["event_id"]) == "legit"]
    bad = [o for o in sms if gt.get(o["event_id"]) == "malicious"]
    lost = [o for o in legit if o["action"].startswith("BLOCK") or o.get("silent_drop")]
    held = [o for o in legit if o["action"] == "QUARANTINE"]
    t1_ok = all((by.get(f"{h['event_id']}-SLA") or {}).get("held_minutes", 0) <= h["limit"] for h in c.holds if h.get("tier") == "T1")
    parity = check_change(flags, threshold)["verdict"] == "DEPLOY"
    by_act = {}
    for o in held:
        by_act[o["act"]] = by_act.get(o["act"], 0) + 1
    gaps = [g for g, ok in (("messages lost", not lost), ("scams delivered", all(o["action"] != "ALLOW" for o in bad)),
                            ("T1 over limit", t1_ok), ("unequal by language", parity)) if not ok]
    return {"threshold": threshold, "legit": len(legit), "delivered": sum(o["action"] == "ALLOW" for o in legit),
            "held": len(held), "lost": len(lost), "scams_stopped": sum(o["action"] != "ALLOW" for o in bad), "scams": len(bad),
            "t1_ok": t1_ok, "parity": parity, "held_by_act": by_act, "gaps": gaps, "audit_ok": a.verify()}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--values", default="0.10,0.15,0.20,0.25,0.30,0.40")
    ap.add_argument("--policy", default="none", choices=["none", "adopted"])
    a = ap.parse_args()
    flags = yaml.safe_load(open("kb/rulepacks/uae/adopted.yaml", encoding="utf-8"))["flags"] if a.policy == "adopted" else {}
    label = "current rules" if a.policy == "none" else "tested rule set (sender authentication + verified lane)"
    rows = [run(float(v), flags) for v in a.values.split(",")]
    ok = [r["threshold"] for r in rows if not r["gaps"]]
    L = [f"# What-if: filter threshold under {label}", "",
         "_Each row replays the full crisis timeline as if the operator had set the filter to that threshold at every filter change. "
         "Synthetic data; Readiness Report 2.0 Dimension 10 (simulated timeline, target vs achievement)._", "",
         f"**Targets:** {TARGETS}", "",
         "| Threshold | Genuine delivered | Held for a human | Lost | Scams stopped | T1 within limit | Languages equal | Gap to target |",
         "|---|---|---|---|---|---|---|---|"]
    L += [f"| {r['threshold']:.2f} | {r['delivered']}/{r['legit']} | {r['held']} | **{r['lost']}** | {r['scams_stopped']}/{r['scams']} | "
          f"{'yes' if r['t1_ok'] else '**no**'} | {'yes' if r['parity'] else '**no**'} | {', '.join(r['gaps']) or 'none'} |" for r in rows]
    acts = sorted({k for r in rows for k in r["held_by_act"]})
    L += ["", "## Simulated timeline: genuine messages held, by act", ""]
    if acts:
        L += ["| Threshold | " + " | ".join(f"Act {k}" for k in acts) + " |", "|---|" + "---|" * len(acts)]
        L += [f"| {r['threshold']:.2f} | " + " | ".join(str(r["held_by_act"].get(k, 0)) for k in acts) + " |" for r in rows]
    else:
        L += ["No genuine message was held at any threshold."]
    L += ["", "**Conclusion:** " + (f"thresholds meeting every target: {', '.join(f'{t:.2f}' for t in ok)}." if ok
          else "no threshold meets every target under these rules; the gap is structural, not a tuning problem."),
          "", f"_Audit chains verified for all runs: {all(r['audit_ok'] for r in rows)}._"]
    out = Path(f"docs/what_if_{a.policy}.md"); out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L)); print(f"\nwritten {out}")

if __name__ == "__main__":
    main()
