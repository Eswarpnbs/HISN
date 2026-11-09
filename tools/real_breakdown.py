"""Breakdown of the held-out real run from the sealed audit log: what happened to scams and to legitimate texts."""
import json, collections, yaml
from pathlib import Path
gold = {(g["role"], g["event"]): g for g in yaml.safe_load(open("scenarios/gold_heldout_real.yaml", encoding="utf-8"))}
c = collections.Counter()
for l in Path("runs/governed_agents.jsonl").read_text(encoding="utf-8").splitlines():
    o = json.loads(l)
    if o.get("kind") != "agent_rationale": continue
    g = gold.get((o.get("role"), o.get("event_id")))
    if not g: continue
    kind = "scam" if g["acceptable"] == ["KEEP_QUARANTINED"] else "legitimate"
    c[(kind, o["status"], o.get("proposed_action"))] += 1
for k, v in sorted(c.items()): print(v, *k)
