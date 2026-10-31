"""ITU-T Y.3173 (02/2020) network intelligence levels, computed exactly as clause 7.2 specifies:
per-dimension level = highest L in Table 7-2 whose required capability matches; overall = minimum across dimensions."""
import yaml

DIMS = ["action_implementation", "data_collection", "analysis", "decision", "demand_mapping"]
H, HS, S = "Human", "Human and System", "System"
TABLE_7_2 = {0: (H, H, H, H, H), 1: (HS, HS, H, H, H), 2: (S, HS, HS, H, H),
             3: (S, S, HS, HS, H), 4: (S, S, S, S, HS), 5: (S, S, S, S, S)}
NAMES = {0: "Manual network operation", 1: "Assisted network operation", 2: "Preliminary intelligence",
         3: "Intermediate intelligence", 4: "Advanced intelligence", 5: "Full intelligence"}

def per_dimension(dim, cap):
    matches = [lvl for lvl, row in TABLE_7_2.items() if row[DIMS.index(dim)] == cap]
    if not matches:
        raise ValueError(f"{dim}: capability {cap!r} matches no level in Table 7-2")
    return max(matches)

def overall(caps):
    return min(per_dimension(d, caps[d]) for d in DIMS)

def load(path="kb/automation_levels.yaml"):
    out = {}
    for cid, c in yaml.safe_load(open(path, encoding="utf-8"))["components"].items():
        caps = {d: c[d]["level"] for d in DIMS}
        per = {d: per_dimension(d, caps[d]) for d in DIMS}
        lvl = min(per.values())
        out[cid] = {"name": c["name"], "caps": caps, "per_dimension": per, "overall": lvl,
                    "label": f"L{lvl} {NAMES[lvl]}", "why": {d: c[d]["why"] for d in DIMS}}
    return out
