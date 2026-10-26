"""Live run of the governed twin with institutional agents (qwen2.5:7b + UAE KB). Synthetic data only."""
import time, os, datetime
from pathlib import Path
from app.core.audit import AuditLog
from app.core.gateway import PolicyGateway
from app.core.firewall import SmsFirewall
from app.core.coordinator import Coordinator
from app.agents.retriever import ItuRetriever
from app.agents.llm import OllamaLLM
from app.agents.institution import InstitutionalAgent

SC, REG, PACK = "scenarios/crisis_exploit.yaml", "kb/rulepacks/uae/senders.yaml", "kb/rulepacks/uae/rules.yaml"
p = Path("runs/governed_agents.jsonl")
if p.exists(): p.unlink()
audit, retr, llm = AuditLog(p), ItuRetriever(), OllamaLLM(os.environ.get("HISN_LLM", "qwen2.5:7b"))
agents = {r: InstitutionalAgent(r, retr, llm, audit) for r in ["health_authority", "tdra", "ai_data_authority"]}
c = Coordinator(SC, audit, SmsFirewall(REG, audit, governed=True), PolicyGateway(PACK, audit), agents=agents)
t0 = time.time(); c.run()
for o in c.agent_outputs:
    print(f"\n[t={o['t']:>2}] {o['role']:<18} event={o['event_id']:<9} sim={o['best_similarity']}")
    print(f"   status={o['status']}  action={o['proposed_action']}  cites={o.get('cited_ids', [])}")
    print(f"   evidence={o.get('evidence_ids')}")
    if o.get("reason"): print(f"   reason={o['reason']}")
    if o.get("assessment"): print(f"   assessment: {o['assessment'][:260]}")
    if o.get("missing_provision"): print(f"   missing provision: {o['missing_provision']}")
print(f"\n{len(c.agent_outputs)} agent decisions in {time.time()-t0:.0f}s | audit chain verified: {audit.verify()}")

import yaml
gold = {(g["role"], g["event"]): g for g in yaml.safe_load(open("scenarios/gold.yaml", encoding="utf-8"))}
correct = caught = 0
print("\n=== Evaluation against pre-registered gold ===")
for o in c.agent_outputs:
    g = gold.get((o["role"], o["event_id"]))
    if not g: continue
    ok = o["proposed_action"] in g["acceptable"] and o["status"] in ("PROPOSED", "POTENTIAL_GAP")
    correct += ok; caught += o["status"] in ("INSUFFICIENT_EVIDENCE", "CONFLICT")
    print(f"{'PASS' if ok else 'FAIL'}  {o['role']:<18} {o['event_id']:<9} got={o['proposed_action']:<36} want={g['acceptable']}")
print(f"\nAgent accuracy vs gold: {correct}/{len(gold)} | gate rejections: {caught}")

os.makedirs("docs", exist_ok=True)
with open("docs/eval_log.md", "a", encoding="utf-8") as f:
    unsafe = sum(1 for o in c.agent_outputs
                 if o["status"] in ("PROPOSED", "POTENTIAL_GAP")
                 and (o["role"], o["event_id"]) in gold
                 and o["proposed_action"] not in gold[(o["role"], o["event_id"])]["acceptable"])
    f.write(f"| {datetime.datetime.now():%Y-%m-%d %H:%M} | {llm.model} | {correct}/{len(gold)} | {unsafe} | {caught} |\n")
print("logged to docs/eval_log.md")
