"""Run-to-run stability of agent decisions: run the governed agents N times and report, for every (agent, event),
whether the decision was identical in every run. --include-current counts the existing runs/governed_agents.jsonl as run 1."""
import argparse, json, shutil, subprocess, sys
from collections import defaultdict
from pathlib import Path

SRC = Path("runs/governed_agents.jsonl")
def decisions(path):
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        try: d = json.loads(line)
        except ValueError: continue
        r = d.get("record") or d.get("payload") or d
        role, ev = r.get("role"), r.get("event_id") or r.get("event")
        act = r.get("proposed_action") or r.get("final_action") or r.get("action")
        if role and ev and act: out[(role, ev)] = act
    return out

ap = argparse.ArgumentParser(); ap.add_argument("--runs", type=int, default=3); ap.add_argument("--include-current", action="store_true")
ap.add_argument("--model", default="qwen2.5:14b"); a = ap.parse_args()
runs = []
if a.include_current and SRC.exists():
    dst = Path("runs/stability_run1.jsonl"); shutil.copy(SRC, dst); runs.append(dst)
while len(runs) < a.runs:
    i = len(runs) + 1; print(f"--- stability run {i}/{a.runs} ---", flush=True)
    subprocess.run([sys.executable, "run_agents.py", "--model", a.model], check=True, stdout=subprocess.DEVNULL)
    dst = Path(f"runs/stability_run{i}.jsonl"); shutil.copy(SRC, dst); runs.append(dst)
D = [decisions(p) for p in runs]
if not D[0]:
    sys.exit("no decisions parsed: record keys were " + str(list(json.loads(SRC.read_text().splitlines()[0]).keys())))
keys = sorted(set().union(*D))
same = [k for k in keys if len({d.get(k) for d in D}) == 1]
diff = [k for k in keys if k not in same]
L = [f"# Run-to-run stability of agent decisions ({len(runs)} runs, {a.model})", "",
     f"**{len(same)}/{len(keys)} agent decisions identical in every run** ({100*len(same)/len(keys):.0f}%).", "",
     "Safeguards are deterministic; this measures the language model's proposals before any human decision.", ""]
if diff:
    L += ["| Agent | Event | " + " | ".join(f"Run {i+1}" for i in range(len(runs))) + " |", "|---|---|" + "---|" * len(runs)]
    L += [f"| {r} | {e} | " + " | ".join(str(d.get((r, e), "-")) for d in D) + " |" for r, e in diff]
Path("docs/stability.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L)); print("written docs/stability.md")
