"""Ask the policy and legal adviser a question (answers cite only retrieved, verified evidence).
Example: python ask_adviser.py "Can a telecom operator scan the content of health SMS to detect fraud?"
"""
import argparse
from pathlib import Path
from app.core.audit import AuditLog
from app.agents.retriever import ItuRetriever
from app.agents.llm import OllamaLLM
from app.agents.adviser import PolicyAdviser

COUNTRY = {"UAE": "United Arab Emirates", "IN": "India", "SG": "Singapore"}
ap = argparse.ArgumentParser(); ap.add_argument("question")
ap.add_argument("--country", default="UAE", choices=list(COUNTRY)); ap.add_argument("--model", default="qwen2.5:14b")
a = ap.parse_args()
r = PolicyAdviser(ItuRetriever(country=COUNTRY[a.country]), OllamaLLM(a.model), AuditLog(Path("runs/adviser.jsonl"))).answer(a.question)
ev = {e["id"]: e for e in r["evidence"]}
print(f"\nQuestion ({a.country}): {a.question}\nStatus: {r['status']}\n\n{r['answer']}\n")
if r["cited_ids"]:
    print("Cited (retrieved, verified):")
    for c in r["cited_ids"]:
        print(f"  [{c}] {ev[c]['article'] or 'document passage'} ({ev[c]['basis']}{', binding' if c in r['binding_ids'] else ', not binding'})")
if r["rejected_citations"]:
    print(f"Rejected citations (not retrieved): {r['rejected_citations']}")
if r["related_gaps"]:
    print(f"\nRelated policy gaps: {', '.join(r['related_gaps'])}")
for e in r["global_examples"]:
    print(f"  Global example ({e['gap']}, {e['jurisdiction']}): {e['instrument']}\n    {e['url']}")
print("\nLogged to the audit chain: runs/adviser.jsonl")
