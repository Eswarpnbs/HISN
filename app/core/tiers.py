import yaml

FHIR_PRIORITIES = {"routine", "urgent", "asap", "stat"}

class Tiers:
    """Clinical tiers. The tier comes from the sender's declared priority, never from message
    content (metadata-first, see gap G3). Only authenticated senders may declare a priority."""
    def __init__(self, path="kb/rulepacks/uae/health_tiers.yaml"):
        d = yaml.safe_load(open(path, encoding="utf-8"))
        self.status, self.default, self.tiers = d["status"], d["default_tier"], d["tiers"]
        self._by_fhir = {p: t for t, spec in self.tiers.items() for p in spec["fhir_priority"]}
        missing = FHIR_PRIORITIES - set(self._by_fhir)
        if missing:
            raise ValueError(f"FHIR priorities not mapped to a tier: {sorted(missing)}")

    def classify(self, payload):
        claimed = payload.get("priority")
        if claimed is None:
            return self.default, "no_priority_declared"
        if claimed not in self._by_fhir:
            return self.default, "unknown_priority_ignored"
        if not payload.get("authenticated", False):
            return self.default, "unauthenticated_priority_ignored"
        return self._by_fhir[claimed], "declared_by_authenticated_sender"

    def max_hold(self, tier):
        return self.tiers[tier]["max_hold_minutes"]

    def receipt_after(self, tier):
        return self.tiers[tier]["receipt_after_minutes"]