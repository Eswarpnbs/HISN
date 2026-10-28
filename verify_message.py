"""Usage: python verify_message.py --sender H0SPITAL-A --text "Pay fee at http://x.example" --lang te [--explain]"""
import argparse
from pathlib import Path
from app.core.audit import AuditLog
from app.verifier import CitizenVerifier, TEMPL

ap = argparse.ArgumentParser()
ap.add_argument("--sender", required=True); ap.add_argument("--text", required=True)
ap.add_argument("--lang", default="en", choices=sorted(TEMPL["languages"])); ap.add_argument("--explain", action="store_true")
a = ap.parse_args()
llm = None
if a.explain:
    from app.agents.llm import OllamaLLM
    llm = OllamaLLM("qwen2.5:7b")
r = CitizenVerifier("kb/rulepacks/uae/senders.yaml", AuditLog(Path("runs/citizen_checks.jsonl")), llm).check(a.sender, a.text, a.lang, a.explain)
print(f"[{r['verdict']}] ({r['lang']}, {r['review_status']})\n{r['message']}")
if r["explanation"]: print(f"\nExplanation (AI-generated, English): {r['explanation']}")
