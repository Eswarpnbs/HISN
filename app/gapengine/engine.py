from collections import defaultdict
from app.core.firewall import SmsFirewall
from .tactics import battery

REG = "kb/rulepacks/uae/senders.yaml"

def run_battery(policy, audit):
    fw = SmsFirewall(REG, audit, governed=True, policy=policy)
    out = []
    for c in battery():
        fw.threshold = c.threshold
        out.append((c, fw.process(c.msg)))
    return out

def metrics(res):
    mal = [r for c, r in res if c.malicious]
    leg = [r for c, r in res if not c.malicious]
    prot = sum(r["action"] != "ALLOW" for r in mal) / len(mal)
    acc = sum(r["action"] == "ALLOW" for r in leg) / len(leg)
    return {"protection": round(100 * prot, 1), "access": round(100 * acc, 1),
            "mizan": round(50 * (prot + acc), 1),
            "officer_reviews": sum(r["action"] == "QUARANTINE" for c, r in res),
            "n_malicious": len(mal), "n_legit": len(leg)}

def loopholes(res):
    out = defaultdict(list)
    for c, r in res:
        if c.malicious and r["action"] == "ALLOW":
            out[(c.tactic, c.gap)].append(c.id)
    return dict(out)

def access_harms(res):
    return [c.id for c, r in res if not c.malicious and r["action"] != "ALLOW"]
