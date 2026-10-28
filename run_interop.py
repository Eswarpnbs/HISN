"""Interoperability: same events under the UAE and India packs (deterministic layers). Agreement, divergences, gap coverage."""
import datetime, yaml
from pathlib import Path
from app.core.audit import AuditLog
from app.core.firewall import SmsFirewall
from app.core.gateway import PolicyGateway
from app.core.coordinator import Coordinator
from app.core.injects import load_injects, available
from app.core.packs import pack
from app.gapengine.engine import run_battery, metrics

SC = "scenarios/crisis_exploit.yaml"
def run(country):
    p = pack(country); log = Path(f"runs/interop_{country}.jsonl")
    if log.exists(): log.unlink()
    a = AuditLog(log)
    out = Coordinator(SC, a, SmsFirewall(p["senders"], a, policy=p["firewall_flags"]), PolicyGateway(p["rules"], a),
                      extra_events=load_injects(available()), sla_minutes=15).run()
    return {o["event_id"]: o for o in out}, a.verify(), p

U, uv, up = run("UAE"); I, iv, ip = run("IN")
shared = [k for k in U if k in I and U[k]["kind"] in ("sms_submit", "data_transfer")]
div = [k for k in shared if U[k]["action"] != I[k]["action"]]
agree = 100 * (len(shared) - len(div)) / len(shared)
print(f"=== Decision agreement on {len(shared)} decisive events: {agree:.0f}% ===")
for k in div:
    print(f"  DIVERGENCE {k:<16} UAE {U[k]['action']:<18} IN {I[k]['action']:<18} "
          f"({U[k].get('rule_id') or ','.join(U[k].get('reasons', []))} | {I[k].get('rule_id') or I[k].get('forced_by_policy') or ''})")
mu, mi = metrics(run_battery(up["firewall_flags"], AuditLog(Path("runs/interop_bat.jsonl")))), metrics(run_battery(ip["firewall_flags"], AuditLog(Path("runs/interop_bat.jsonl"))))
print(f"\nGap-engine baseline  UAE: protection {mu['protection']} access {mu['access']} MIZAN {mu['mizan']} | "
      f"IN: protection {mi['protection']} access {mi['access']} MIZAN {mi['mizan']}")
gm = yaml.safe_load(open("kb/rulepacks/gap_mechanisms.yaml", encoding="utf-8"))
print("\nGap coverage (verified clauses):")
for g, v in gm.items():
    print(f"  {g}: UAE {v['UAE']['status']:<8} IN {v['IN']['status']:<8} {v['IN'].get('note', '')}")
shared_gaps = [g for g, v in gm.items() if v["UAE"]["status"] == "none" and v["IN"]["status"] in ("none", "partial")]
print(f"\nShared or partly shared gaps (candidate multi-country standards work): {shared_gaps}")
with open("docs/interoperability.md", "w", encoding="utf-8") as f:
    f.write(f"# UAE-India interoperability ({datetime.datetime.now():%Y-%m-%d %H:%M}, deterministic layers)\n\n"
            f"Decision agreement on {len(shared)} decisive events: **{agree:.0f}%**\n\n| event | UAE | India |\n|---|---|---|\n")
    for k in div: f.write(f"| {k} | {U[k]['action']} | {I[k]['action']} |\n")
    f.write(f"\nGap-engine baseline MIZAN: UAE {mu['mizan']}, India {mi['mizan']}\n\n| gap | UAE | India | India clauses | note |\n|---|---|---|---|---|\n")
    for g, v in gm.items(): f.write(f"| {g} | {v['UAE']['status']} | {v['IN']['status']} | {', '.join(v['IN']['clauses'])} | {v['IN'].get('note', '')} |\n")
    f.write("\nScope: gateway, firewall and gap engine only; India institutional agents are future work. Comparator status as tagged in kb/manifest.csv.\n")
print(f"\naudit chains verified: UAE {uv}, IN {iv} | written docs/interoperability.md")
