"""HISN selftest: re-derives every headline number in the report from code and logs.
Deterministic results are recomputed now; LLM results are read from logs with provenance.
Usage: python selftest.py            (fast)
       python selftest.py --full     (also re-runs LLM evaluations with qwen2.5:14b, ~40 min)"""
import argparse, csv, datetime, subprocess, sys, tempfile, yaml
from pathlib import Path
from app.core.audit import AuditLog
from app.core.firewall import SmsFirewall
from app.core.gateway import PolicyGateway
from app.core.coordinator import Coordinator
from app.core.injects import load_injects, available
from app.gapengine.engine import run_battery, metrics

ap = argparse.ArgumentParser(); ap.add_argument("--full", action="store_true"); args = ap.parse_args()
SC, REG, PACK = "scenarios/crisis_exploit.yaml", "kb/rulepacks/uae/senders.yaml", "kb/rulepacks/uae/rules.yaml"
rows = []
def rec(name, value, source):
    rows.append((name, value, source)); print(f"{name:<52} {str(value):<34} <- {source}")
def tmp_audit(): return AuditLog(Path(tempfile.mkdtemp()) / "a.jsonl")

if args.full:
    for cmd in (["run_agents.py", "--model", "qwen2.5:14b"], ["run_baselines.py", "--model", "qwen2.5:14b"]):
        print(f"[--full] running {' '.join(cmd)} ..."); subprocess.run([sys.executable, *cmd], check=False)

r = subprocess.run([sys.executable, "-m", "pytest", "-q"], capture_output=True, text=True)
rec("Unit tests", r.stdout.strip().splitlines()[-1].split(" in ")[0], "python -m pytest -q")
r = subprocess.run([sys.executable, "kb/verify.py"], capture_output=True, text=True)
rec("Knowledge-base sources match manifest hashes", "yes" if r.returncode == 0 else "NO (see kb/verify.py)", "python kb/verify.py")
man = list(csv.DictReader(open("kb/manifest.csv", encoding="utf-8")))
cl = yaml.safe_load(open("kb/clauses/clauses.yaml", encoding="utf-8"))
rec("Hash-pinned records / verbatim clauses", f"{len(man)} / {len(cl)}", "kb/manifest.csv, kb/clauses/clauses.yaml")

GT = yaml.safe_load(open("scenarios/ground_truth.yaml", encoding="utf-8"))
def twin(gov):
    a = tmp_audit()
    out = Coordinator(SC, a, SmsFirewall(REG, a, governed=gov), PolicyGateway(PACK, a) if gov else None,
                      extra_events=load_injects(available()), sla_minutes=15 if gov else None).run()
    return {o["event_id"]: o for o in out}, a.verify()
g, gv = twin(True); u, uv = twin(False)
lost = lambda d: sum(1 for k, v in GT.items() if v == "legit" and k in d and (d[k].get("silent_drop") or d[k]["action"].startswith("BLOCK")))
off = lambda d: sum(1 for o in d.values() if o.get("kind") == "data_transfer" and not o["action"].startswith("BLOCK"))
rec("Legitimate essential messages silently lost", f"ungoverned {lost(u)} -> HISN {lost(g)}", "twin run (all injects, 15-min limit)")
rec("Offshore health-data transfers not blocked", f"ungoverned {off(u)} -> HISN {off(g)}", "twin run (all injects)")
rec("Audit chains verify (governed / ungoverned)", f"{gv} / {uv}", "AuditLog.verify()")

b = metrics(run_battery({}, tmp_audit()))
best = metrics(run_battery({"require_auth": True, "authenticated_bypass": True}, tmp_audit()))
fraud = metrics(run_battery({"fraud_duty": True}, tmp_audit()))
rec("Gap engine baseline (protection/access/MIZAN)", f"{b['protection']}/{b['access']}/{b['mizan']}", "app/gapengine (deterministic)")
rec("P-AUTH+P-VERIFIED (protection/access/MIZAN)", f"{best['protection']}/{best['access']}/{best['mizan']}", "app/gapengine (deterministic)")
rec("P-FRAUD alone MIZAN change", f"{fraud['mizan'] - b['mizan']:+.1f}", "app/gapengine (deterministic)")
pack = yaml.safe_load(open(PACK, encoding="utf-8"))
reduced = Path(tempfile.mkdtemp()) / "pack.yaml"
reduced.write_text(yaml.safe_dump(dict(pack, rules=[x for x in pack["rules"] if x["id"] != "HEALTH_LOCALISATION_01"])), encoding="utf-8")
a = tmp_audit()
out = Coordinator(SC, a, SmsFirewall(REG, a), PolicyGateway(str(reduced), a), extra_events=load_injects(["emergency"])).run()
rec("Art.13 rule load-bearing (transfers not blocked when removed)", sum(1 for o in out if o["kind"] == "data_transfer" and not o["action"].startswith("BLOCK")), "rule-removal re-run")

try:
    r = subprocess.run([sys.executable, "kb/eval_retrieval.py"], capture_output=True, text=True, timeout=600)
    line = next(l for l in r.stdout.splitlines() if l.startswith("HISN clause-first"))
    rec("Retrieval (HISN clause-first)", line.split("|")[0].replace("HISN clause-first", "").strip() + " | " + line.split("|")[2].strip(), "python kb/eval_retrieval.py")
except Exception as ex:
    rec("Retrieval", f"not run ({type(ex).__name__}: is Ollama running?)", "python kb/eval_retrieval.py")

ev = [l for l in Path("docs/eval_log_v3.md").read_text(encoding="utf-8").splitlines() if "qwen2.5:14b" in l] if Path("docs/eval_log_v3.md").exists() else []
for label in ("dev", "heldout_v2"):
    last = [l for l in ev if f"| {label} |" in l]
    if last:
        c = [x.strip() for x in last[-1].strip("|").split("|")]
        rec(f"Agents qwen2.5:14b {label} (accuracy / harmful)", f"{c[3]} / {c[4]}", f"docs/eval_log_v3.md ({c[0]})")
bl = [l for l in Path("docs/baselines.md").read_text(encoding="utf-8").splitlines() if l.startswith("| B")] if Path("docs/baselines.md").exists() else []
for l in bl:
    c = [x.strip() for x in l.strip("|").split("|")]
    rec(f"Baseline {c[0][:30]}", f"acc {c[1]} | harmful {c[3]} | unsupported {c[5]}", "docs/baselines.md")

with open("docs/headline_numbers.md", "w", encoding="utf-8") as f:
    f.write(f"# Headline numbers (selftest, {datetime.datetime.now():%Y-%m-%d %H:%M})\n\nEvery figure in the report traces to a row here.\n\n| figure | value | produced by |\n|---|---|---|\n")
    for n, v, s in rows: f.write(f"| {n} | {v} | `{s}` |\n")
print("\nwritten docs/headline_numbers.md")
