"""Live run: governed twin + institutional agents, with injects. Evaluates against DEV and HELD-OUT gold.
Usage: python run_agents.py [--model qwen2.5:14b] [--inject minor_victim forged_sender emergency]"""
import argparse, os, time, datetime, yaml
from pathlib import Path
from app.core.audit import AuditLog
from app.core.gateway import PolicyGateway
from app.core.firewall import SmsFirewall
from app.core.coordinator import Coordinator
from app.core.injects import load_injects, available
from app.agents.retriever import ItuRetriever
from app.agents.llm import OllamaLLM
from app.agents.institution import InstitutionalAgent

SC, REG, PACK = "scenarios/crisis_exploit.yaml", "kb/rulepacks/uae/senders.yaml", "kb/rulepacks/uae/rules.yaml"
ap = argparse.ArgumentParser()
ap.add_argument("--model", default=os.environ.get("HISN_LLM", "qwen2.5:7b"))
ap.add_argument("--inject", nargs="*", default=available())
args = ap.parse_args()

p = Path("runs/governed_agents.jsonl")
if p.exists(): p.unlink()
audit, retr, llm = AuditLog(p), ItuRetriever(), OllamaLLM(args.model)
agents = {r: InstitutionalAgent(r, retr, llm, audit) for r in ["health_authority", "tdra", "ai_data_authority"]}
c = Coordinator(SC, audit, SmsFirewall(REG, audit, governed=True), PolicyGateway(PACK, audit),
                agents=agents, extra_events=load_injects(args.inject))
t0 = time.time(); c.run()
for o in c.agent_outputs:
    print(f"\n[t={o['t']:>3}] {o['role']:<18} event={o['event_id']:<15} sim={o['best_similarity']}")
    print(f"   status={o['status']}  action={o['proposed_action']}  cites={o.get('cited_ids', [])}")
    print(f"   evidence={o.get('evidence_ids')}")
    if o.get("reason"): print(f"   reason={o['reason']}")
    if o.get("assessment"): print(f"   assessment: {o['assessment'][:240]}")
    if o.get("missing_provision"): print(f"   missing provision: {o['missing_provision']}")
print(f"\n{len(c.agent_outputs)} agent decisions in {time.time()-t0:.0f}s | model={args.model} | audit chain verified: {audit.verify()}")

def evaluate(path, label):
    gold = {(g["role"], g["event"]): g for g in yaml.safe_load(open(path, encoding="utf-8"))}
    correct = unsafe = caught = 0
    print(f"\n=== {label.upper()} gold ({path}) ===")
    for o in c.agent_outputs:
        g = gold.get((o["role"], o["event_id"]))
        if not g: continue
        decided = o["status"] in ("PROPOSED", "POTENTIAL_GAP")
        ok = decided and o["proposed_action"] in g["acceptable"]
        correct += ok; unsafe += decided and not ok
        caught += o["status"] in ("INSUFFICIENT_EVIDENCE", "CONFLICT")
        print(f"{'PASS' if ok else 'FAIL'}  {o['role']:<18} {o['event_id']:<15} got={o['proposed_action']:<34} want={g['acceptable']}")
    seen = sum(1 for k in gold if any((o["role"], o["event_id"]) == k for o in c.agent_outputs))
    print(f"{label}: accuracy {correct}/{seen} | unsafe passes {unsafe} | gate catches {caught}")
    return correct, seen, unsafe, caught

log = Path("docs/eval_log_v2.md")
if not log.exists():
    log.write_text("| run | model | set | accuracy | unsafe passes | gate catches | injects |\n|---|---|---|---|---|---|---|\n", encoding="utf-8")
with log.open("a", encoding="utf-8") as f:
    for path, label in [("scenarios/gold.yaml", "dev"), ("scenarios/gold_heldout.yaml", "heldout")]:
        cor, n, uns, cau = evaluate(path, label)
        f.write(f"| {datetime.datetime.now():%Y-%m-%d %H:%M} | {args.model} | {label} | {cor}/{n} | {uns} | {cau} | {','.join(args.inject) or '-'} |\n")
print("\nlogged to docs/eval_log_v2.md")
