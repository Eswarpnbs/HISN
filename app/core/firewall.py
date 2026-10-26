"""SMS firewall accepting SMPP submit_sm-shaped messages (stub).
Governed mode: essential senders are never silently dropped - quarantine + escalate to a named role.
Ungoverned mode: whatever scores as spam is dropped silently."""
import re, difflib, yaml
from .enums import Action

_MAP = str.maketrans({"0": "o", "1": "i", "3": "e", "5": "s"})
def _norm(s): return re.sub(r"[^a-z]", "", (s or "").lower().translate(_MAP))
def _lookalike(a, b): return a != b and difflib.SequenceMatcher(None, _norm(a), _norm(b)).ratio() >= 0.8

class SmsFirewall:
    def __init__(self, registry_path, audit, governed=True, threshold=0.5, policy=None):
        reg = yaml.safe_load(open(registry_path, encoding="utf-8"))
        self.essential = {s["sender_id"]: s for s in reg["essential_senders"]}
        self.trusted = set(reg["trusted_domains"])
        self.keywords = reg["suspicious_keywords"]
        self.audit, self.governed, self.threshold = audit, governed, threshold
        self.policy = policy or {}

    def set_threshold(self, value, reason=""):
        old, self.threshold = self.threshold, value
        self.audit.write({"kind": "filter_threshold_changed", "old": old, "new": value, "reason": reason})

    def score(self, msg):
        s, reasons = 0.0, []
        sender, text = msg.get("source_addr", ""), msg.get("short_message", "")
        if sender not in self.essential:
            hit = next((sid for sid in self.essential if _lookalike(sender, sid)), None)
            if hit: s += 0.6; reasons.append(f"lookalike_of:{hit}")
        m = re.search(r"https?://([^/\s]+)", text)
        if m and m.group(1).lower() not in self.trusted:
            s += 0.3; reasons.append(f"untrusted_url:{m.group(1).lower()}")
        if msg.get("route") == "foreign_aggregator":
            s += 0.2; reasons.append("foreign_aggregator_route")
        if any(k in text.lower() for k in self.keywords):
            s += 0.25; reasons.append("suspicious_keyword")
        if self.policy.get("fraud_duty") and sender not in self.essential and any(k in text.lower() for k in ("pay", "unpaid", "fine")):
            s += 0.3; reasons.append("fraud_duty:payment_demand_unregistered_sender")
        return round(min(s, 1.0), 2), reasons

    def process(self, msg, now=0):
        score, reasons = self.score(msg)
        sender = msg.get("source_addr", "")
        essential = sender in self.essential
        forced = None
        if essential and self.policy.get("require_auth") and not msg.get("authenticated"):
            forced = "unauthenticated_protected_sender"
        elif essential and self.policy.get("protected_routes_only") and msg.get("route") == "foreign_aggregator":
            forced = "protected_id_on_unregistered_route"
        if forced:
            rec = {"action": Action.BLOCK_OVERRIDABLE.value, "score": 1.0, "threshold": self.threshold,
                   "reasons": reasons + [forced], "essential_sender": essential, "silent_drop": False,
                   "escalate_to": None, "forced_by_policy": forced}
            self.audit.write({"kind": "firewall_decision", "t": now, "source_addr": sender,
                              "governed": self.governed, **rec})
            return rec
        spam = score >= self.threshold
        silent_drop, escalate_to = False, None
        if not spam:
            action = Action.ALLOW
        elif essential and self.governed:
            action, escalate_to = Action.QUARANTINE, self.essential[sender]["escalation_role"]
        else:
            action, silent_drop = Action.BLOCK_OVERRIDABLE, not self.governed
        rec = {"action": action.value, "score": score, "threshold": self.threshold,
               "reasons": reasons, "essential_sender": essential,
               "silent_drop": silent_drop, "escalate_to": escalate_to}
        self.audit.write({"kind": "firewall_decision", "t": now, "source_addr": sender,
                          "governed": self.governed, **rec})
        return rec
