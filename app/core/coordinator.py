import yaml
from .events import Event, EventBus

def load_scenario(path):
    data = yaml.safe_load(open(path, encoding="utf-8"))
    evs = [Event(id=e["id"], t=int(e["t"]), kind=e["kind"], audience=tuple(e["audience"]),
                 payload=e.get("payload", {}), act=int(e.get("act", 0))) for e in data["events"]]
    return data, evs

class Coordinator:
    """Deterministic MLFO: advances the simulated clock, dispatches released events, delivers each
    event only to the agents in its audience, and routes escalations. gateway=None = ungoverned twin."""
    def __init__(self, scenario_path, audit, firewall, gateway=None, step=5, agents=None, extra_events=None, sla_minutes=None):
        self.meta, events = load_scenario(scenario_path)
        self.bus = EventBus(audit); self.bus.load(list(events) + list(extra_events or []))
        self.audit, self.firewall, self.gateway, self.step = audit, firewall, gateway, step
        self.agents = agents or {}
        self.outcomes, self.agent_outputs = [], []
        self.sla, self.holds = sla_minutes, []

    def run(self, until=None):
        end, now = (until if until is not None else self.meta.get("duration", 70)), 0
        while now <= end:
            for e in self.bus.release_until(now):
                self._dispatch(e, now)
            self._check_sla(now)
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
                d = self.gateway.evaluate({"type": "message_log_transfer", **e.payload, "emergency": getattr(self, "emergency", False)})
                r = {"action": d["action"].value, "verdict": d["verdict"].value, "rule_id": d.get("rule_id")}
        elif e.kind == "emergency_declared":
            self.emergency = True
            r = {"action": "OBSERVED"}
        else:
            r = {"action": "OBSERVED"}
        self.outcomes.append({"t": now, "event_id": e.id, "kind": e.kind, "act": e.act, **r})
        self._deliver(e, r, now)
        if r.get("escalate_to"):
            esc = Event(id=f"{e.id}-ESC", t=now, kind="escalation", audience=(r["escalate_to"],),
                        payload={"original_event": e.id, **e.payload}, act=e.act)
            self.bus.inject(esc)
            n_before = len(self.agent_outputs)
            self._deliver(esc, {"action": "ESCALATED", "firewall": r}, now)
            recs = [o.get("proposed_action") for o in self.agent_outputs[n_before:]]
            if self.sla is not None:
                self.holds.append({"event_id": e.id, "t_held": now, "escalated_to": r["escalate_to"],
                                   "resolved": "release_recommended" if "RECOMMEND_RELEASE_BY_NAMED_OFFICER" in recs else None})

    def _deliver(self, e, r, now):
        for role in e.audience:
            agent = self.agents.get(role)
            if agent:
                self.agent_outputs.append(agent.handle(e, r, now))

    def _check_sla(self, now):
        """Essential messages held beyond the time limit go to a second human, whatever the agent proposed."""
        for h in self.holds:
            if h["resolved"] is None and now - h["t_held"] >= self.sla:
                h["resolved"] = "sla_second_review"
                o = {"t": now, "event_id": f"{h['event_id']}-SLA", "kind": "sla_escalation", "act": 0,
                     "action": "SECOND_REVIEW", "escalate_to": "duty_supervisor", "held_minutes": now - h["t_held"]}
                self.audit.write({"kind": "sla_escalation", **o})
                self.outcomes.append(o)
