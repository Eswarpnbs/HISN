"""Build a wind-tunnel input from a draft file whose mechanism mapping a named human has already confirmed.
Used by CI ("law as a pull request"), where no language model is available."""
from .compiler import VOC, _coerce

def compile_confirmed(d):
    mechs, rejected = [], []
    for m in d.get("mechanisms") or []:
        mid = m.get("id")
        if mid not in VOC:
            rejected.append(mid); continue
        given = m.get("params") or {}
        mechs.append({"id": mid, "params": {k: _coerce(given.get(k, dv), dv) for k, dv in VOC[mid].get("params", {}).items()}})
    ids = {m["id"] for m in mechs}
    warnings = [f"{m['id']} presupposes {r}" for m in mechs for r in VOC[m["id"]].get("requires", []) if r not in ids]
    return {"draft": d["draft"], "mechanisms": mechs, "instrument_level": d.get("instrument_level", "unspecified"),
            "untestable_parts": d.get("untestable_parts", ""), "rationale": "mapping confirmed by a named human in the draft file",
            "rejected_ids": rejected, "warnings": warnings}
