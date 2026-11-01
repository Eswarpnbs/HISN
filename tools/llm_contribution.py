"""What the language model adds, and what deterministic code guarantees, measured from the run logs and baseline results."""
import json, re
from pathlib import Path

recs = []
for line in Path("runs/governed_agents.jsonl").read_text(encoding="utf-8").splitlines():
    try: d = json.loads(line)
    except ValueError: continue
    r = d.get("record") or d.get("payload") or d
    if r.get("role") and r.get("event_id"): recs.append(r)
gaps = [r for r in recs if r.get("status") == "POTENTIAL_GAP" and (r.get("missing_provision") or "").strip()]
conflicts = [r for r in recs if r.get("status") == "CONFLICT"]
nonsms = [r for r in recs if not str(r["event_id"]).endswith("-ESC")]
bl = Path("docs/baselines.md").read_text(encoding="utf-8") if Path("docs/baselines.md").exists() else ""
def grab(label, field):
    m = re.search(rf"{re.escape(label)}.*?{field} (\d+)", bl)
    return m.group(1) if m else "?"
L = ["# What the language model adds, and what code guarantees", "",
     f"_From runs/governed_agents.jsonl ({len(recs)} agent decisions) and docs/baselines.md._", "",
     "| The language model contributes | Deterministic code guarantees |", "|---|---|",
     f"| Reads unstructured events that fixed rules cannot parse: {len(nonsms)} decisions on complaints, disputes, referrals and emergencies | "
     f"No decisive action without a binding, competent source: HISN {grab('B3', 'decisive w/o binding basis')} vs fixed rules {grab('B0', 'decisive w/o binding basis')} |",
     f"| Finds gaps and states the missing provision in words: {len(gaps)} gap logs | "
     f"No invented citations: HISN {grab('B3', 'unsupported citations')} vs LLM alone {grab('B1', 'unsupported citations')} |",
     f"| Proposes referrals and actions with reasons a human can review | "
     f"Contradictions caught and sent to a named human: {len(conflicts)} (model fooled, decision not acted on) |",
     f"| | Harmful decisions: HISN {grab('B3', 'harmful')} vs fixed rules {grab('B0', 'harmful')} vs LLM alone {grab('B1', 'harmful')} |",
     "", "## Gaps the model found, in its own words", ""]
seen = set()
for r in gaps:
    t = r["missing_provision"].strip()
    if t not in seen:
        seen.add(t); L.append(f"- **{r['role']}** on `{r['event_id']}`: {t}")
Path("docs/llm_contribution.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L[:12])); print(f"... written docs/llm_contribution.md ({len(seen)} distinct gaps)")
