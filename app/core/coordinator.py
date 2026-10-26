import yaml
from .events import Event, EventBus

def load_scenario(path):
    data = yaml.safe_load(open(path, encoding="utf-8"))
    evs = [Event(id=e["id"], t=int(e["t"]), kind=e["kind"], audience=tuple(e["audience"]),
                 payload=e.get("payload", {}), act=int(e.get("act", 0))) for e in data["events"]]
    return data, evs

class Coordinator:
    """Deterministic MLFO: advances the simulated clock and dispatches released events.
    gateway=None means the ungoverned twin (no policy node)."""
    def __init__(self, scenario_path, audit, firewall, gateway=None, step=5):
        self.meta, events = load_scenario(scenario_path)
        self.bus = EventBus(audit); self.bus.load(events)
        self.audit, self.firewall, self.gateway, self.step = audit, firewall, gateway, step
        self.outcomes = []

    def run(self, until=None):
        end, now = (until if until is not None else self.meta.get("duration", 70)), 0
        while now <= end:
            for e in self.bus.release_until(now):
                self._dispatch(e, now)
            now += self.step
        return self.outcomes

    def _dispatch(self, e, now):
        if e.kind == "sms_submit":
            r = self.firewall.process(e.payload, now=now)
        elif e.kind == "filter_policy":
            self.firewall.set_threshold(e.payload["threshold"], e.payload.get("reason", ""))
            r = {"action": "APPLIED"}
        elif e.kind == "data_transfer":
            if self.gateway is None:
                r = {"action": "ALLOW", "note": "no policy node"}
            else:
                d = self.gateway.evaluate({"type": "message_log_transfer", **e.payload})
                r = {"action": d["action"].value, "verdict": d["verdict"].value,
                     "rule_id": d.get("rule_id")}
        else:
            r = {"action": "OBSERVED"}
        self.outcomes.append({"t": now, "event_id": e.id, "kind": e.kind, "act": e.act, **r})
