"""HISN demo: same scenario, ungoverned vs governed twin. Synthetic data only."""
from pathlib import Path
from app.core.audit import AuditLog
from app.core.gateway import PolicyGateway
from app.core.firewall import SmsFirewall
from app.core.coordinator import Coordinator

SC, REG, PACK = "scenarios/crisis_exploit.yaml", "kb/rulepacks/uae/senders.yaml", "kb/rulepacks/uae/rules.yaml"

def run(governed):
    p = Path(f"runs/{'governed' if governed else 'ungoverned'}.jsonl")
    if p.exists(): p.unlink()
    audit = AuditLog(p)
    gw = PolicyGateway(PACK, audit) if governed else None
    return Coordinator(SC, audit, SmsFirewall(REG, audit, governed=governed), gw).run(), audit

def fmt(o):
    s = o["action"]
    if o.get("silent_drop"): s += " (silent drop)"
    if o.get("escalate_to"): s += f" -> {o['escalate_to']}"
    if o.get("rule_id"): s += f" [{o['rule_id']}]"
    return s

g, ga = run(True); u, ua = run(False)
print(f"{'t':>3}  {'event':6} {'kind':15} {'UNGOVERNED':32} GOVERNED (HISN)")
print("-" * 100)
for a, b in zip(u, g):
    print(f"{b['t']:>3}  {b['event_id']:6} {b['kind']:15} {fmt(a):32} {fmt(b)}")
print("-" * 100)
print("audit chains verified:", ga.verify(), ua.verify())
