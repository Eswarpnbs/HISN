"""Map a plain-language draft provision onto the fixed mechanism vocabulary. LLM proposes; code validates."""
import yaml

VOC = yaml.safe_load(open("kb/rulepacks/uae/mechanisms.yaml", encoding="utf-8"))["mechanisms"]
LEVELS = ["regulation", "health_authority_resolution", "federal_amendment", "unspecified"]
SYSTEM = """You map a draft regulatory provision onto a FIXED vocabulary of testable mechanisms.
Use ONLY these mechanism ids: {ids}
{desc}
If part of the draft cannot be expressed with these mechanisms, describe it in "untestable_parts". Never invent ids.
Classify instrument_level as one of {levels} from the wording (use "unspecified" if unclear).
Reply JSON only: {{"mechanisms": [{{"id": "...", "params": {{}}}}], "instrument_level": "...", "untestable_parts": "...", "rationale": "..."}}"""

def _coerce(v, default):
    """A parameter the draft does not state keeps its default; a null default means 'not stated' (e.g. no time limit)."""
    if v is None: return default
    try: return type(default)(v) if default is not None else int(v)
    except (TypeError, ValueError): return default

def _show_params(p):
    """Prompt view of parameters; a null default is shown as 'only if stated' so the model does not invent one."""
    return "{" + ", ".join(f"{k}: {d if d is not None else '<number, only if the draft states it>'}" for k, d in p.items()) + "}"

def compile_draft(text, llm, level_override=None):
    desc = "\n".join(f"- {k}: {v['description']} params: {_show_params(v.get('params', {}))}" for k, v in VOC.items())
    out = llm(SYSTEM.format(ids=list(VOC), desc=desc, levels=LEVELS), f"DRAFT PROVISION:\n{text}")
    mechs, rejected = [], []
    for m in out.get("mechanisms", []):
        mid = m.get("id")
        if mid not in VOC: rejected.append(mid); continue
        given = m.get("params") or {}
        mechs.append({"id": mid, "params": {k: _coerce(given.get(k, d), d) for k, d in VOC[mid].get("params", {}).items()}})
    level = level_override or (out.get("instrument_level") if out.get("instrument_level") in LEVELS else "unspecified")
    ids = {m["id"] for m in mechs}
    warnings = [f"{m['id']} presupposes {r}" for m in mechs for r in VOC[m["id"]].get("requires", []) if r not in ids]
    return {"draft": text, "mechanisms": mechs, "instrument_level": level,
            "untestable_parts": out.get("untestable_parts") or "", "rationale": str(out.get("rationale", ""))[:400],
            "rejected_ids": rejected, "warnings": warnings}
