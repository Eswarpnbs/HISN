"""Country rule packs: gateway rules, sender registry and built-in firewall mechanisms."""
import yaml
from pathlib import Path

PACKS = {"UAE": Path("kb/rulepacks/uae"), "IN": Path("kb/rulepacks/india")}

def pack(country):
    d = PACKS[country]
    pol = yaml.safe_load(open(d / "firewall_policy.yaml", encoding="utf-8"))
    return {"country": country, "rules": str(d / "rules.yaml"), "senders": str(d / "senders.yaml"),
            "firewall_flags": pol.get("flags", {}), "firewall_basis": pol.get("basis", [])}
