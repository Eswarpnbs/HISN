"""Usage: python signoff.py --patches P-AUTH P-VERIFIED --officer "Name" --role "Role" --decision APPROVE --note "..." """
import argparse
from pathlib import Path
from app.core.audit import AuditLog
from app.gapengine.signoff import signoff

ap = argparse.ArgumentParser()
ap.add_argument("--patches", nargs="+", required=True)
ap.add_argument("--officer", required=True)
ap.add_argument("--role", required=True)
ap.add_argument("--decision", choices=["APPROVE", "REJECT", "DEFER"], required=True)
ap.add_argument("--note", default="")
a = ap.parse_args()
audit = AuditLog(Path("runs/signoffs.jsonl"))
try:
    h = signoff(a.patches, a.officer, a.role, a.decision, a.note, audit)
    print(f"{a.decision} recorded by {a.officer} | audit hash {h[:16]}... | chain verified: {audit.verify()}")
    if a.decision == "APPROVE":
        print("written kb/rulepacks/uae/adopted.yaml (simulation only) + recorded in ITU kb_decisions")
except ValueError as e:
    print(e)
