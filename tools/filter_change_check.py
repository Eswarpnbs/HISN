"""Pre-deployment check for an operator's SMS-filter change: would the new threshold treat the same genuine
hospital message differently by language? Prints DEPLOY / DO NOT DEPLOY; exit code 1 on DO NOT DEPLOY."""
import argparse, sys, yaml
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core.fairness import check_change, LANGS

ap = argparse.ArgumentParser(); ap.add_argument("--threshold", type=float, required=True)
ap.add_argument("--policy", default="none", choices=["none", "adopted"]); a = ap.parse_args()
flags = yaml.safe_load(open("kb/rulepacks/uae/adopted.yaml", encoding="utf-8"))["flags"] if a.policy == "adopted" else {}
r = check_change(flags, a.threshold)
word = {"ALLOW": "delivered", "QUARANTINE": "held"}
print(f"Proposed filter threshold {a.threshold} under {'current rules' if a.policy == 'none' else 'the tested rule set (authentication + verified lane)'}: {r['verdict']}")
for mid, acts in r["results"].items():
    print(f"  {mid:<14} " + "  ".join(f"{l}:{word.get(acts[l], acts[l].lower())}" for l in LANGS)
          + f"  [{'UNEQUAL' if mid in r['unequal'] else 'equal'}]")
if r["unequal"]:
    print("Reason: identical genuine messages would be treated differently by language. "
          "Review before deployment (gap G5: no instrument assigns authority to approve this change).")
for name, v in r["scam_results"].items():
    print(f"  scam: {name:<62} en:{v['en']:<18} ar:{v['ar']:<18} {'[LANGUAGE GAP]' if v['gap'] else '[equal]'}")
if r["scam_gaps"]:
    print("Reason: the same scam would be stopped in one language and delivered in another (wind-tunnel invariant I9).")

sys.exit(1 if r["unequal"] else 0)
