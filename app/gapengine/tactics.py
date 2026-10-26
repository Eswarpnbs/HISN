"""Abstract tactic catalogue. Messages are neutral placeholders - no persuasive or real phishing text."""
from dataclasses import dataclass

THRESHOLDS = {"normal": 0.5, "panic": 0.2, "drift": 0.15}

@dataclass
class Case:
    id: str
    malicious: bool
    tactic: str
    gap: str
    msg: dict
    threshold: float

def battery():
    cases = []
    def add(tactic, malicious, gap, sender, route, url, pay, auth=False):
        for tname, th in THRESHOLDS.items():
            text = "[PAYMENT] please pay reference 001" if pay else "[NOTICE] reference 001"
            if url: text += f" http://{url}"
            cid = f"{tactic}|{route}|{url or 'nourl'}|{'pay' if pay else 'nopay'}|{tname}"
            cases.append(Case(cid, malicious, tactic, gap,
                              {"source_addr": sender, "route": route, "short_message": text, "authenticated": auth}, th))
    for pay in (False, True):                                    # legitimate traffic
        for url in (None, "hospital-a.example"):
            add("genuine_essential_health", False, "-", "HOSPITAL-A", "local", url, pay, auth=True)
        add("genuine_essential_gov", False, "-", "GOV-FINES", "local", None, pay, auth=True)
        add("legit_unregistered_business", False, "-", "SHOP-XYZ", "local", None, pay)
    for route in ("local", "foreign_aggregator"):                # malicious tactics (abstract)
        for url in (None, "pay-portal.example"):
            for pay in (False, True):
                add("exact_spoof_essential", True, "G2", "HOSPITAL-A", route, url, pay)
                add("lookalike_essential", True, "G1", "H0SPITAL-A", route, url, pay)
            add("unregistered_payment_demand", True, "G1", "BILLING-CTR", route, url, True)
    return cases
