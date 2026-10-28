"""Interoperability across country packs (deterministic layers): pairwise agreement, divergences, gap coverage."""
import datetime, itertools, yaml
from pathlib import Path
from app.core.audit import AuditLog
from app.core.firewall import SmsFirewall
from app.core.gateway import PolicyGateway
from app.core.coordinator import Coordinator
from app.core.injects import load_injects, available
from app.core.packs import pack, PACKS
from app.gapengine.engine import run_battery, metrics

SC = "scenarios/crisis_exploit.yaml"; C = list(PACKS)
def run(country):
    p = pack(country); log = Path(f"runs/interop_{country}.jsonl")
    if log.exists(): log.unlink()
    a = AuditLog(log)
    out = Coordinator(SC, a, SmsFirewall(p["senders"], a, policy=p["firewall_flags"]), PolicyGateway(p["rules"], a),
                      extra_events=load_injects(available()), sla_minutes=15).run()
    return {o["event_id"]: o for o in out}, a.verify(), p
R = {c: run(c) for c in C}
decisive = [k for k in R[C[0]][0] if R[C[0]][0][k]["kind"] in ("sms_submit", "data_transfer") and all(k in R[c][0] for c in C)]
def agree(a, b): return round(100 * sum(R[a][0][k]["action"] == R[b][0][k]["action"] for k in decisive) / len(decisive))
pairs = {f"{a}-{b}": agree(a, b) for a, b in itertools.combinations(C, 2)}
print(f"=== Pairwise decision agreement on {len(decisive)} decisive events ===")
for k, v in pairs.items(): print(f"  {k:<8} {v}%")
print("\n=== Events where the countries differ ===")
div = [k for k in decisive if len({R[c][0][k]["action"] for c in C}) > 1]
for k in div: print(f"  {k:<16} " + " | ".join(f"{c} {R[c][0][k]['action']}" for c in C))
M = {c: metrics(run_battery(R[c][2]["firewall_flags"], AuditLog(Path("runs/interop_bat.jsonl")))) for c in C}
print("\nGap-engine baseline MIZAN: " + " | ".join(f"{c} {M[c]['mizan']} (prot {M[c]['protection']}, access {M[c]['access']})" for c in C))
gm = yaml.safe_load(open("kb/rulepacks/gap_mechanisms.yaml", encoding="utf-8"))
print("\nGap coverage:"); [print(f"  {g}: " + "  ".join(f"{c} {v.get(c, {}).get('status', '-'):<8}" for c in C)) for g, v in gm.items()]
shared = [g for g, v in gm.items() if all(v.get(c, {}).get("status") in ("none", "partial") for c in C)]
print(f"\nGaps not fully addressed by any pack: {shared}")
with open("docs/interoperability.md", "w", encoding="utf-8") as f:
    f.write(f"# Interoperability across {', '.join(C)} ({datetime.datetime.now():%Y-%m-%d %H:%M}, deterministic layers)\n\n"
            f"UAE-India decision agreement: **{pairs.get('UAE-IN', '-')}%**\n\n| pair | agreement |\n|---|---|\n" + "".join(f"| {k} | {v}% |\n" for k, v in pairs.items()))
    f.write("\n| event | " + " | ".join(C) + " |\n|" + "---|" * (len(C) + 1) + "\n" + "".join(f"| {k} | " + " | ".join(R[c][0][k]["action"] for c in C) + " |\n" for k in div))
    f.write("\n| gap | " + " | ".join(C) + " | notes |\n|" + "---|" * (len(C) + 2) + "\n")
    for g, v in gm.items():
        f.write(f"| {g} | " + " | ".join(v.get(c, {}).get("status", "-") for c in C) + " | " + "; ".join(f"{c}: {v[c]['note']}" for c in C if v.get(c, {}).get("note")) + " |\n")
    f.write("\nScope: gateway, firewall and gap engine only; institutional agents for India and Singapore are future work.\n")
print("\naudit chains verified: " + ", ".join(f"{c} {R[c][1]}" for c in C) + " | written docs/interoperability.md")
