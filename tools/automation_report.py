"""Writes docs/automation_levels.md: ITU-T Y.3173 levels for every HISN component, computed from Table 7-2."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core.automation import load, DIMS

L = ["# ITU-T Y.3173 network intelligence levels of HISN components", "",
     "_Capability per dimension declared from Table 7-1 (kb/automation_levels.yaml); per-dimension and overall levels computed "
     "by app/core/automation.py exactly as clause 7.2 specifies (highest matching level per dimension; overall = minimum)._", "",
     "| Component | Action impl. | Data collection | Analysis | Decision | Demand mapping | Overall |", "|---|---|---|---|---|---|---|"]
lv = load()
for c in lv.values():
    L.append(f"| {c['name']} | " + " | ".join(f"{c['caps'][d]} (L{c['per_dimension'][d]})" for d in DIMS) + f" | **{c['label']}** |")
L += ["", "**Reading:** the language-model components (agents, adviser) analyse at the System level but are L0 overall, because they never "
      "implement actions; the wind tunnel and gap engine are L0 because nothing is adopted without named sign-off. The network "
      "functions run at L2 under human-defined rules.", "",
      "**Table 7-2 Note 1 (human authority):** in every component, decisions and instructions by a human have the highest authority: "
      "held messages are released by a named human, a second human reviews within the clinical limit, and sign-off is refused without evidence.", "",
      "## Justifications (Table 7-1 conditions)", ""]
for c in lv.values():
    L.append(f"**{c['name']}**")
    L += [f"- {d.replace('_', ' ')}: {c['caps'][d]}. {c['why'][d]}" for d in DIMS]
    L.append("")
Path("docs/automation_levels.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L[:16])); print("written docs/automation_levels.md")
