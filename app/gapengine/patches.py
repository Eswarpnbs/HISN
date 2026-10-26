"""Candidate provisions as machine-readable patches. Comparators are UNVERIFIED until checked against official text."""
PATCHES = [
    {"id": "P-AUTH", "flags": {"require_auth": True}, "closes": ["G2"],
     "mechanism": "Protected (essential) sender IDs accepted only when authenticated by the registered sender",
     "comparator": "Inspired by Singapore SMS Sender ID Registry (verify text)", "verification": "pending"},
    {"id": "P-ROUTE", "flags": {"protected_routes_only": True}, "closes": ["G2"],
     "mechanism": "Protected sender IDs rejected when arriving via unregistered / foreign aggregator routes",
     "comparator": "Inspired by Singapore SSIR / India TRAI DLT header registration (verify text)", "verification": "pending"},
    {"id": "P-FRAUD", "flags": {"fraud_duty": True}, "closes": ["G1"],
     "mechanism": "Operator filtering duty extended from marketing spam to fraud: payment demands from unregistered senders blocked",
     "comparator": "Inspired by Singapore Shared Responsibility Framework telco duties (verify text)", "verification": "pending"},
]
COMBOS = [["P-AUTH", "P-FRAUD"], ["P-AUTH", "P-ROUTE", "P-FRAUD"]]
