import yaml
from .enums import Verdict, Action, Basis, BLOCKING_BASES

def _plain(d):
    return {k: (v.value if hasattr(v, "value") else v) for k, v in d.items()}

class PolicyGateway:
    def __init__(self, pack_path, audit):
        with open(pack_path, encoding="utf-8") as f:
            self.pack = yaml.safe_load(f)
        self.audit = audit

    def _matches(self, cond, event):
        for k, v in cond.items():
            if k.endswith("_not"):
                if event.get(k[:-4]) == v:
                    return False
            elif k.endswith("_max"):
                val = event.get(k[:-4])
                if val is None or val > v:
                    return False
            elif event.get(k) != v:
                return False
        return True

    def evaluate(self, event: dict) -> dict:
        for rule in self.pack["rules"]:
            if event.get("type") not in rule["applies_to"]:
                continue
            if not self._matches(rule["condition"], event):
                continue
            basis = Basis(rule["basis"])
            unverified = "TODO" in rule["citation"]["quote"]
            if unverified or basis not in BLOCKING_BASES:
                decision = {"verdict": Verdict.INSUFFICIENT_EVIDENCE,
                            "action": Action.QUARANTINE,
                            "reason": "citation unverified or non-blocking basis"}
            else:
                decision = {"verdict": Verdict(rule["verdict"]),
                            "action": Action(rule["action"])}
            decision.update(rule_id=rule["id"], citation=rule["citation"],
                            pack=self.pack["pack_id"])
            self.audit.write({"kind": "gateway_decision", "event": event, **_plain(decision)})
            return decision
        decision = {"verdict": Verdict.POTENTIAL_GAP, "action": Action.FLAG,
                    "reason": "no rule covers this event", "pack": self.pack["pack_id"]}
        self.audit.write({"kind": "gap_candidate", "event": event, **_plain(decision)})
        return decision
