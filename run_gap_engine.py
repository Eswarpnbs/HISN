"""HISN gap engine: loophole hunt -> counterfactual policy tests -> load-bearing analysis. Deterministic, no LLM."""
import json, yaml
from pathlib import Path
from app.core.audit import AuditLog
from app.core.firewall import SmsFirewall
from app.core.gateway import PolicyGateway
from app.core.coordinator import Coordinator
from app.core.injects import load_injects
from app.gapengine.engine import run_battery, metrics, loopholes, access_harms
from app.gapengine.patches import PATCHES, COMBOS

p = Path("runs/gap_engine.jsonl")
if p.exists(): p.unlink()
audit = AuditLog(p)

base_res = run_battery({}, audit)
base = metrics(base_res)
print("=== 1. LOOPHOLE HUNT (UAE pack as-is) ===")
print(f"battery: {base['n_malicious']} malicious + {base['n_legit']} legitimate cases across normal/panic/drift filter states")
print(f"baseline: protection {base['protection']}% | access {base['access']}% | MIZAN {base['mizan']} | officer reviews {base['officer_reviews']}")
lh = loopholes(base_res)
for (tactic, gap), ids in lh.items():
    print(f"  LOOPHOLE  {tactic:<30} -> gap {gap}  ({len(ids)} cases, e.g. {ids[0]})")
    audit.write({"kind": "loophole_found", "tactic": tactic, "gap": gap, "cases": len(ids), "example": ids[0]})
harms = access_harms(base_res)
print(f"  ACCESS HARMS: {len(harms)} legitimate cases not delivered immediately (e.g. {harms[0] if harms else '-'})")

print("\n=== 2. COUNTERFACTUAL POLICY TESTS (each awaits named human sign-off) ===")
rows = []
def test(ids):
    flags = {}
    for pid in ids:
        flags.update(next(x for x in PATCHES if x["id"] == pid)["flags"])
    res = run_battery(flags, audit)
    m = metrics(res)
    closed = [k for k in lh if k not in loopholes(res)]
    row = {"patch": "+".join(ids), **m, "d_protection": round(m["protection"] - base["protection"], 1),
           "d_access": round(m["access"] - base["access"], 1), "d_mizan": round(m["mizan"] - base["mizan"], 1),
           "loopholes_closed": [f"{t}/{g}" for t, g in closed], "status": "awaiting_named_human_signoff"}
    audit.write({"kind": "counterfactual_test", **row})
    rows.append(row)
    print(f"  {row['patch']:<22} protection {m['protection']:>5}% ({row['d_protection']:+}) | access {m['access']:>5}% ({row['d_access']:+}) "
          f"| MIZAN {m['mizan']:>5} ({row['d_mizan']:+}) | reviews {m['officer_reviews']:>2} | closes {row['loopholes_closed'] or '-'}")
for pt in PATCHES: test([pt["id"]])
for combo in COMBOS: test(combo)

print("\n=== 3. LOAD-BEARING ANALYSIS (remove one existing rule, re-run the crisis + emergency inject) ===")
SC, REG, PACK = "scenarios/crisis_exploit.yaml", "kb/rulepacks/uae/senders.yaml", "kb/rulepacks/uae/rules.yaml"
def offshore_allowed(pack_path):
    a = AuditLog(Path("runs/loadbearing_tmp.jsonl"))
    out = Coordinator(SC, a, SmsFirewall(REG, a), PolicyGateway(pack_path, a), extra_events=load_injects(["emergency"])).run()
    return sum(1 for o in out if o["kind"] == "data_transfer" and not o["action"].startswith("BLOCK"))
pack = yaml.safe_load(open(PACK, encoding="utf-8"))
with_rule = offshore_allowed(PACK)
for rule in pack["rules"]:
    reduced = dict(pack, rules=[r for r in pack["rules"] if r["id"] != rule["id"]])
    tmp = Path(f"runs/pack_minus_{rule['id']}.yaml"); tmp.write_text(yaml.safe_dump(reduced), encoding="utf-8")
    without = offshore_allowed(tmp)
    lb = without > with_rule
    print(f"  {rule['id']:<26} ({rule['citation']['article']}): offshore transfers NOT blocked {with_rule} -> {without} when removed "
          f"=> {'LOAD-BEARING' if lb else 'not load-bearing in this scenario'}")
    audit.write({"kind": "load_bearing", "rule": rule["id"], "allowed_with": with_rule, "allowed_without": without, "load_bearing": lb})

print("  note: without the rule the gateway does not silently allow - it FLAGs the transfer as POTENTIAL_GAP (fail-visible)")
Path("docs").mkdir(exist_ok=True)
with open("docs/counterfactual_results.md", "w", encoding="utf-8") as f:
    f.write(f"# Counterfactual policy tests (deterministic, synthetic)\n\nBaseline: protection {base['protection']}%, access {base['access']}%, "
            f"MIZAN {base['mizan']}, officer reviews {base['officer_reviews']}\n\n"
            "| patch | protection | access | MIZAN | Δ MIZAN | reviews | loopholes closed | status |\n|---|---|---|---|---|---|---|---|\n")
    for r in rows:
        f.write(f"| {r['patch']} | {r['protection']}% | {r['access']}% | {r['mizan']} | {r['d_mizan']:+} | {r['officer_reviews']} | "
                f"{', '.join(r['loopholes_closed']) or '-'} | {r['status']} |\n")
    f.write("\nComparators are marked 'verify text' until checked against official sources. Patches are candidate mechanisms, not legal drafting.\n")
print(f"\nwritten docs/counterfactual_results.md | audit chain verified: {audit.verify()}")
