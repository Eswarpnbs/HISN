"""Judge inject console: pick injects or type a custom SMS; both twins replay instantly.
(For agent reasoning on the same injects: python run_agents.py --inject <names>)"""
from pathlib import Path
from app.core.audit import AuditLog
from app.core.events import Event
from app.core.gateway import PolicyGateway
from app.core.firewall import SmsFirewall
from app.core.coordinator import Coordinator
from app.core.injects import load_injects, available

SC, REG, PACK = "scenarios/crisis_exploit.yaml", "kb/rulepacks/uae/senders.yaml", "kb/rulepacks/uae/rules.yaml"

def run(governed, extra):
    p = Path(f"runs/console_{'gov' if governed else 'ungov'}.jsonl")
    if p.exists(): p.unlink()
    a = AuditLog(p)
    out = Coordinator(SC, a, SmsFirewall(REG, a, governed=governed),
                      PolicyGateway(PACK, a) if governed else None, extra_events=extra).run()
    return {o["event_id"]: o for o in out}, a.verify()

def fmt(o):
    s = o["action"] + (" (silent drop)" if o.get("silent_drop") else "")
    s += f" -> {o['escalate_to']}" if o.get("escalate_to") else ""
    return s + (f" [{o['rule_id']}]" if o.get("rule_id") else "")

while True:
    print("\nInjects:", ", ".join(available()), "| custom = type your own SMS | q = quit")
    choice = input("inject> ").strip()
    if choice == "q": break
    if choice == "custom":
        sender = input("  sender ID: ").strip()
        text = input("  message text: ").strip()
        route = input("  route [local/foreign_aggregator]: ").strip() or "local"
        extra = [Event(id="JUDGE-1", t=55, kind="sms_submit", audience=("filter_ai",), act=3,
                       payload={"source_addr": sender, "short_message": text, "route": route})]
    else:
        try:
            extra = load_injects([n.strip() for n in choice.split(",") if n.strip()])
        except FileNotFoundError:
            print("  unknown inject"); continue
    ids = {e.id for e in extra}
    (g, gv), (u, uv) = run(True, extra), run(False, extra)
    print(f"\n{'event':<16}{'UNGOVERNED':<36}GOVERNED (HISN)")
    for eid in sorted(ids, key=lambda i: g[i]["t"]):
        print(f"{eid:<16}{fmt(u[eid]):<36}{fmt(g[eid])}")
    print(f"audit chains verified: {gv} {uv}")
