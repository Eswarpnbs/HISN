"""Essential Message Assurance Report: the one page a regulator would read each morning.
Runs the governed system (UAE pack as-is, clinical tiers on) over the scenario and summarises it.
Synthetic data: shows the format and the direction, not real-world volumes."""
import json, tempfile, datetime, yaml
from pathlib import Path
from app.core.audit import AuditLog
from app.core.firewall import SmsFirewall
from app.core.gateway import PolicyGateway
from app.core.coordinator import Coordinator
from app.core.injects import load_injects, available
from app.core.tiers import Tiers
from app.core.fairness import check_change

import argparse
ap = argparse.ArgumentParser(); ap.add_argument("--policy", default="none", choices=["none", "adopted"])
POLICY = ap.parse_args().policy
FLAGS = yaml.safe_load(open("kb/rulepacks/uae/adopted.yaml", encoding="utf-8"))["flags"] if POLICY == "adopted" else {}
SC = "scenarios/crisis_exploit.yaml"
GT = yaml.safe_load(open("scenarios/ground_truth.yaml", encoding="utf-8"))
T = Tiers()

a = AuditLog(Path(tempfile.mkdtemp()) / "daily.jsonl")
c = Coordinator(SC, a, SmsFirewall("kb/rulepacks/uae/senders.yaml", a, policy=FLAGS), PolicyGateway("kb/rulepacks/uae/rules.yaml", a),
                extra_events=load_injects(available()), sla_minutes=15, tiers=T)
out = c.run()
by_id = {o["event_id"]: o for o in out}
sms = [o for o in out if o["kind"] == "sms_submit"]

legit = [o for o in sms if GT.get(o["event_id"]) == "legit"]
bad = [o for o in sms if GT.get(o["event_id"]) == "malicious"]
delivered = [o for o in legit if o["action"] == "ALLOW"]
held = [o for o in legit if o["action"] == "QUARANTINE"]
lost = [o for o in legit if o["action"].startswith("BLOCK") or o.get("silent_drop")]
spoofs_stopped = [o for o in bad if o["action"] != "ALLOW"]
spoofs_delivered = [o for o in bad if o["action"] == "ALLOW"]

holds = []
for h in c.holds:
    sla = by_id.get(f"{h['event_id']}-SLA")
    waited = sla["held_minutes"] if sla else None
    holds.append({"event": h["event_id"], "tier": h.get("tier") or "-", "authority": h["escalated_to"],
                  "limit": h["limit"], "second_review_after": waited,
                  "met": waited is None or waited <= h["limit"], "legit": GT.get(h["event_id"]) == "legit"})

transfers = [o for o in out if o["kind"] == "data_transfer"]
filter_changes = [o for o in out if o["kind"] == "filter_policy"]
cards = []
for p in sorted(Path("docs/impact_cards").glob("*.json")):
    r = json.loads(p.read_text(encoding="utf-8"))
    cards.append((r.get("compiled", {}).get("draft", "")[:90], r.get("compiled", {}).get("instrument_level", ""), r.get("verdict", "")))
verified = a.verify()

L = [f"# Essential Message Assurance Report",
     f"_Synthetic scenario day · generated {datetime.datetime.now():%Y-%m-%d %H:%M} · UAE rules {'as-is' if POLICY == 'none' else 'with the tested rule set (sender authentication + verified lane)'}, clinical tiers on (provisional)_", "",
     "## Headline", "",
     "| Indicator | Value | Target |", "|---|---|---|",
     f"| Genuine essential messages | {len(legit)} | |",
     f"| Delivered immediately | {len(delivered)} | |",
     f"| Held for a named human | {len(held)} | |",
     f"| **Silently lost** | **{len(lost)}** | **0** |",
     f"| Held messages that reached second review within their clinical limit | {sum(h['met'] for h in holds)}/{len(holds)} | all |",
     f"| Scam / spoof messages stopped | {len(spoofs_stopped)}/{len(bad)} | all |",
     f"| Offshore health-data transfers blocked | {sum(o['action'].startswith('BLOCK') for o in transfers)}/{len(transfers)} | all, unless a valid resolution applies |",
     f"| Operator filter changes with a pre-deployment test on record | 0/{len(filter_changes)} | all |",
     f"| Filter changes violating declared Y.3173 automation levels (no named approval) | {sum(1 for o in filter_changes if o.get('automation_violation'))}/{len(filter_changes)} | 0 |",
     f"| Audit chain verified | {'yes' if verified else '**NO**'} | yes |", "",
     "## Held messages", "",
     "| Message | Genuine? | Tier | Held for | Limit (min) | Second review after (min) | Within limit |", "|---|---|---|---|---|---|---|"]
L += [f"| {h['event']} | {'yes' if h['legit'] else 'no'} | {h['tier']} | {h['authority']} | {h['limit']} | {h['second_review_after'] if h['second_review_after'] is not None else '-'} | {'yes' if h['met'] else '**no**'} |" for h in holds]
L += ["", "## Offshore transfers", "", "| Event | Decision | Legal basis |", "|---|---|---|"]
L += [f"| {o['event_id']} | {o['action']} | {o.get('rule_id') or '-'} |" for o in transfers]
L += ["", "## Operator filter changes", "",
      "Every change below was applied without any record that it was tested before deployment, and no instrument assigns authority to approve it (gap G5). The last column shows what HISN's pre-deployment check would have said.", "",
      "| Event | New threshold | Effect | HISN pre-deployment check (language parity) |", "|---|---|---|---|"]
EVS = {e["id"]: e for e in yaml.safe_load(open(SC, encoding="utf-8"))["events"]}
L += [f"| {o['event_id']} | {EVS[o['event_id']]['payload']['threshold']} | {o['action']} | "
      f"{check_change(FLAGS, EVS[o['event_id']]['payload']['threshold'])['verdict']} |" for o in filter_changes]
L += ["", "## Draft rules tested before issuance (wind tunnel)", "", "| Draft | Instrument | Verdict |", "|---|---|---|"]
L += [f"| {d} | {lvl} | {v} |" for d, lvl, v in cards]
if spoofs_delivered:
    L += ["", f"**Attention:** {len(spoofs_delivered)} malicious message(s) delivered: " + ", ".join(o['event_id'] for o in spoofs_delivered)]
L += ["", "_Synthetic data; tier limits are provisional pending clinician review. Reproduce with `python daily_report.py`._"]

Path(f"docs/daily_report_{POLICY}.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L[:16]))
print(f"\nwritten docs/daily_report_{POLICY}.md")