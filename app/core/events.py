from dataclasses import dataclass, field

@dataclass
class Event:
    id: str
    t: int                      # simulated minute
    kind: str
    audience: tuple             # roles allowed to see this event
    payload: dict = field(default_factory=dict)
    act: int = 0

class EventBus:
    """Releases events over simulated time. An agent sees only events addressed to its
    role AND already released - never the future (information asymmetry by design)."""
    def __init__(self, audit):
        self.audit = audit
        self._events, self._released = [], set()

    def load(self, events):
        self._events = sorted(events, key=lambda e: (e.t, e.id))

    def release_until(self, now):
        newly = []
        for e in self._events:
            if e.t <= now and e.id not in self._released:
                self._released.add(e.id)
                newly.append(e)
                self.audit.write({"kind": "event_released", "event_id": e.id, "t": e.t,
                                  "audience": list(e.audience)})
        return newly

    def view(self, role, now):
        return [e for e in self._events
                if e.id in self._released and e.t <= now
                and (role in e.audience or "all" in e.audience)]
