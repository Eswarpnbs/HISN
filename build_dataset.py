"""Publish HISN's synthetic SMS dataset in ITU Sandbox catalogue style (datasets/hisn-synthetic-sms/)."""
import csv, datetime, hashlib, re, yaml
from pathlib import Path
from app.gapengine.tactics import battery

OUT = Path("datasets/hisn-synthetic-sms"); (OUT / "metadata").mkdir(parents=True, exist_ok=True)
rows = []
for c in battery():
    m = re.search(r"https?://([^/\s]+)", c.msg["short_message"])
    rows.append({"case_id": c.id, "source": "gap_engine_battery", "sender_id": c.msg["source_addr"],
                 "route": c.msg["route"], "has_url": bool(m), "url_domain": m.group(1) if m else "",
                 "payment_request": "[PAYMENT]" in c.msg["short_message"], "authenticated": c.msg.get("authenticated", False),
                 "filter_state": c.id.split("|")[-1], "threshold": c.threshold, "tactic": c.tactic,
                 "gap_tag": c.gap, "label": "malicious" if c.malicious else "legitimate",
                 "placeholder_text": c.msg["short_message"]})
gt = yaml.safe_load(open("scenarios/ground_truth.yaml", encoding="utf-8"))
events = yaml.safe_load(open("scenarios/crisis_exploit.yaml", encoding="utf-8"))["events"]
for inj in sorted(Path("scenarios/injects").glob("*.yaml")):
    events += yaml.safe_load(open(inj, encoding="utf-8"))["events"]
for e in events:
    if e["kind"] != "sms_submit" or e["id"] not in gt: continue
    p = e["payload"]; m = re.search(r"https?://([^/\s]+)", p["short_message"])
    rows.append({"case_id": e["id"], "source": "crisis_exploit_scenario", "sender_id": p["source_addr"], "route": p["route"],
                 "has_url": bool(m), "url_domain": m.group(1) if m else "", "payment_request": any(k in p["short_message"].lower() for k in ("pay", "fee", "fine")),
                 "authenticated": "", "filter_state": f"t={e['t']}", "threshold": "", "tactic": "scenario_event",
                 "gap_tag": "", "label": "malicious" if gt[e["id"]] == "malicious" else "legitimate",
                 "placeholder_text": p["short_message"]})
csv_path = OUT / "hisn_synthetic_sms.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
data = csv_path.read_bytes()
meta = {"name": "HISN Synthetic SMS Governance Dataset", "id": "hisn-synthetic-sms", "version": "1.0.0",
        "description": ("Synthetic SMS metadata for testing governance of AI message filters that affect essential health and "
                        "government messages: abstract tactic battery (exact spoof, lookalike, unregistered payment demand, "
                        "legitimate essential and business traffic) across normal/panic/drift filter states, plus labelled "
                        "scenario events. Fictional senders and example.* domains only; placeholder text, no persuasive content."),
        "rows": len(rows), "size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
        "files": [csv_path.name], "licence": "CC-BY-4.0", "task": ["binary-classification", "policy-evaluation"],
        "labels": {"malicious": sum(r["label"] == "malicious" for r in rows), "legitimate": sum(r["label"] == "legitimate" for r in rows)},
        "tags": ["telecom", "sms", "fraud", "policy", "governance", "synthetic", "agentic", "itu-ai4good"],
        "generator": "build_dataset.py from app/gapengine/tactics.py and scenarios/", "personal_data": "none",
        "added": datetime.date.today().isoformat(), "contact": "Team Sankalp (see README)"}
(OUT / "metadata" / "metadata.yaml").write_text(yaml.safe_dump(meta, sort_keys=False), encoding="utf-8")
(OUT / "README.md").write_text(f"# {meta['name']}\n\n{meta['description']}\n\n- rows: {meta['rows']} ({meta['labels']})\n"
                               f"- licence: {meta['licence']}\n- sha256: `{meta['sha256']}`\n- regenerate: `python build_dataset.py`\n",
                               encoding="utf-8")
print(f"written {csv_path} ({len(rows)} rows: {meta['labels']}) + metadata/metadata.yaml + README.md")
