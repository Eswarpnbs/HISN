"""Named human sign-off for candidate provisions. No sign-off without measured evidence from the gap engine."""
import datetime, json, os, sys, pathlib, yaml
from .patches import PATCHES

ITU = pathlib.Path(os.environ.get("ITU_DIR", pathlib.Path.home() / "ITUAIReadiness/simulation"))
EVIDENCE_LOG = pathlib.Path("runs/gap_engine.jsonl")
OVERLAY = pathlib.Path("kb/rulepacks/uae/adopted.yaml")

def tested_combos(log=None):
    log = log or EVIDENCE_LOG
    if not log.exists(): return {}
    out = {}
    for line in log.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if r.get("kind") == "counterfactual_test":
            out[r["patch"]] = r
    return out

def signoff(patch_ids, officer, role, decision, note, audit, record_in_itu_kb=True):
    key = "+".join(patch_ids)
    evidence = tested_combos().get(key)
    if evidence is None:
        raise ValueError(f"Refused: '{key}' was never tested by the gap engine. No sign-off without measured evidence.")
    rec = {"kind": "human_signoff", "patches": patch_ids, "officer": officer, "officer_role": role,
           "decision": decision, "note": note, "at": datetime.datetime.now().isoformat(timespec="seconds"),
           "evidence": {k: evidence[k] for k in ("protection", "access", "mizan", "d_mizan", "loopholes_closed")}}
    h = audit.write(rec)
    if decision == "APPROVE":
        flags = {}
        for pid in patch_ids:
            flags.update(next(p for p in PATCHES if p["id"] == pid)["flags"])
        OVERLAY.write_text(yaml.safe_dump({"note": "SIMULATION ONLY - adopted candidate provisions after named sign-off",
                                           "patches": patch_ids, "flags": flags, "signoff_hash": h}), encoding="utf-8")
        if record_in_itu_kb:
            sys.path.insert(0, str(ITU))
            from server.knowledge.kb import KnowledgeBase
            from server.knowledge.ingest import embed_texts
            text = (f"DECISION (named human sign-off) by {officer} ({role}): adopt candidate provision(s) {key} "
                    f"in the simulation rule pack. Mechanisms: " +
                    "; ".join(p["mechanism"] for p in PATCHES if p["id"] in patch_ids) +
                    f". Measured MIZAN change {evidence['d_mizan']:+}. Comparators pending verification.")
            KnowledgeBase().add_decision(decision_text=text, embedding=embed_texts([text])[0],
                                         metadata={"country": "United Arab Emirates", "source": "HISN gap engine",
                                                   "patches": key, "officer": officer, "audit_hash": h})
    return h
