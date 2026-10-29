"""Regulatory wind tunnel: test a compiled draft against existing law, invariants, the gap battery and the India pack."""
import tempfile, yaml
from pathlib import Path
from app.core.audit import AuditLog
from app.core.firewall import SmsFirewall
from app.core.gateway import PolicyGateway
from app.core.coordinator import Coordinator, load_scenario
from app.core.events import Event
from app.core.tiers import Tiers
from app.core.injects import load_injects, available
from app.core.packs import pack
from app.gapengine.engine import run_battery, metrics, loopholes
from .compiler import VOC

SC = "scenarios/crisis_exploit.yaml"
CLAUSES = {c["clause_id"]: c for c in yaml.safe_load(open("kb/clauses/clauses.yaml", encoding="utf-8"))}
GT = yaml.safe_load(open("scenarios/ground_truth.yaml", encoding="utf-8"))
_tmp = lambda: AuditLog(Path(tempfile.mkdtemp()) / "a.jsonl")
TIERS = Tiers()

def t1_ids():
    """Messages whose authenticated sender declared a life-critical (T1) priority."""
    _, evs = load_scenario(SC)
    return [e.id for e in list(evs) + list(load_injects(available()))
            if e.kind == "sms_submit" and TIERS.classify(e.payload)[0] == "T1"]

def config(compiled):
    flags, sla, overlay, tiered = {}, 15, None, False
    for m in compiled["mechanisms"]:
        eff = VOC[m["id"]].get("effect", {})
        if "firewall_flag" in eff: flags[eff["firewall_flag"]] = True
        if "sla_minutes" in eff: sla = int(m["params"].get("minutes", 15))
        if eff.get("gateway_overlay") == "emergency_offshore": overlay = m
        if eff.get("tiered_holds"): tiered = True
    return flags, sla, overlay, tiered

HORIZON_HOURS = 72  # a draft with no stated limit is probed here: an exception still open then has no working sunset

def _overlay_hours(overlay):
    return ((overlay or {}).get("params") or {}).get("hours")

def _overlay_condition(overlay):
    cond = {"data_class": "health", "emergency": True}
    if _overlay_hours(overlay): cond["emergency_minutes_max"] = int(_overlay_hours(overlay)) * 60
    return cond

def _probe(overlay):
    _, evs = load_scenario(SC)
    t_em = min(e.t for e in list(evs) + list(load_injects(available())) if e.kind == "emergency_declared")
    h = _overlay_hours(overlay) or HORIZON_HOURS
    return Event(id="PROBE-SUNSET", t=t_em + int(h) * 60 + 10, kind="data_transfer", audience=("ai_data_authority",),
                 payload={"data_class": "health", "destination_country": "XX",
                          "reason": "probe: transfer after the emergency window"}, act=3)

def pack_with_overlay(overlay, draft, level):
    base = yaml.safe_load(open("kb/rulepacks/uae/rules.yaml", encoding="utf-8"))
    if overlay:
        rule = {"id": "DRAFT_EMERGENCY_OFFSHORE", "applies_to": ["message_log_transfer"],
                "condition": _overlay_condition(overlay), "verdict": "COMPLIANT", "action": "ALLOW",
                "basis": "REGULATOR_POLICY", "zone": "AUGMENTATION",
                "citation": {"record_id": "DRAFT", "article": f"Draft provision ({level})", "quote": draft}}
        base = dict(base, rules=[rule] + base["rules"])
    p = Path(tempfile.mkdtemp()) / "pack.yaml"; p.write_text(yaml.safe_dump(base), encoding="utf-8")
    return str(p)

def run_uae(flags, sla, pack_path, tiers=None, probe=None):
    a = _tmp()
    out = Coordinator(SC, a, SmsFirewall("kb/rulepacks/uae/senders.yaml", a, policy=flags), PolicyGateway(pack_path, a),
                      extra_events=list(load_injects(available())) + ([probe] if probe else []), sla_minutes=sla,
                      tiers=tiers).run(until=(probe.t + 5) if probe else None)
    return {o["event_id"]: o for o in out}, a.verify()

def run_india():
    p = pack("IN"); a = _tmp()
    out = Coordinator(SC, a, SmsFirewall(p["senders"], a, policy=p["firewall_flags"]), PolicyGateway(p["rules"], a),
                      extra_events=load_injects(available()), sla_minutes=15).run()
    return {o["event_id"]: o for o in out}

def agreement(U, I):
    shared = [k for k in U if k in I and U[k]["kind"] in ("sms_submit", "data_transfer")]
    return round(100 * sum(U[k]["action"] == I[k]["action"] for k in shared) / len(shared)) if shared else None

def conflicts(compiled):
    out = []
    for m in compiled["mechanisms"]:
        for c in VOC[m["id"]].get("conflicts", []):
            cl = CLAUSES.get(c["clause"], {})
            out.append({"mechanism": m["id"], "clause": c["clause"], "article": cl.get("article"), "type": c["type"],
                        "resolved_by_level": compiled["instrument_level"] in c.get("compatible_levels", []),
                        "note": c["note"], "verbatim": cl.get("text", "")[:280]})
    return out

def invariants(U, verified, bat, base_bat, level):
    lost = [k for k, v in GT.items() if v == "legit" and k in U and (U[k].get("silent_drop") or U[k]["action"].startswith("BLOCK"))]
    draft_offshore = [k for k, o in U.items() if o.get("rule_id") == "DRAFT_EMERGENCY_OFFSHORE"]
    rank_ok = not draft_offshore or level in ("health_authority_resolution", "federal_amendment")
    spoof = sum(len(v) for k, v in loopholes(bat).items() if k[0] == "exact_spoof_essential")
    blocks = [o for o in U.values() if o.get("kind") == "data_transfer" and o["action"].startswith("BLOCK")]
    a0, a1 = metrics(base_bat)["access"], metrics(bat)["access"]
    lim = TIERS.max_hold("T1")
    slow = [k for k in t1_ids() if (h := U.get(f"{k}-SLA")) and h["held_minutes"] > lim]
    pr = U.get("PROBE-SUNSET")
    return [
        {"id": "I1", "text": "No legitimate essential message silently lost or blocked", "pass": not lost, "detail": f"{len(lost)} lost"},
        {"id": "I2", "text": "No offshore health-data transfer without a legal basis of sufficient rank", "pass": rank_ok,
         "detail": f"{len(draft_offshore)} transfer(s) allowed by the draft; instrument level: {level}"},
        {"id": "I3", "text": "Spoofed protected sender IDs are never delivered", "pass": spoof == 0, "detail": f"{spoof} spoof case(s) delivered"},
        {"id": "I4", "text": "Every policy block cites a verified binding clause", "pass": all(o.get("rule_id") for o in blocks), "detail": f"{len(blocks)} block(s)"},
        {"id": "I5", "text": "All decisions sealed in a verifiable audit chain", "pass": verified, "detail": ""},
        {"id": "I6", "text": "Legitimate access does not regress", "pass": a1 >= a0, "detail": f"access {a0} -> {a1}"},
        {"id": "I7", "text": "Life-critical health messages reach a human within their clinical limit",
         "pass": not slow, "detail": f"{len(slow)} T1 message(s) waited longer than {lim} min"},
        {"id": "I8", "text": "Emergency exceptions expire (sunset)", "pass": pr is None or pr["action"] != "ALLOW",
         "detail": "no probe" if pr is None else f"transfer after the emergency window: {pr['action']}"}]

def wind_tunnel(compiled):
    if not compiled["mechanisms"]:
        return {"verdict": "NOT TESTABLE", "reason": "no mechanism in the vocabulary matches this draft", "compiled": compiled}
    flags, sla, overlay, tiered = config(compiled)
    probe = _probe(overlay)
    U0, v0 = run_uae({}, 15, "kb/rulepacks/uae/rules.yaml", probe=probe)
    U1, v1 = run_uae(flags, sla, pack_with_overlay(overlay, compiled["draft"], compiled["instrument_level"]),
                     TIERS if tiered else None, probe=probe)
    I = run_india()
    b0, b1 = run_battery({}, _tmp()), run_battery(flags, _tmp())
    inv0 = invariants(U0, v0, b0, b0, "unspecified"); inv1 = invariants(U1, v1, b1, b0, compiled["instrument_level"])
    con = conflicts(compiled)
    regress = [b["id"] for a, b in zip(inv0, inv1) if a["pass"] and not b["pass"]]
    fixed = [b["id"] for a, b in zip(inv0, inv1) if not a["pass"] and b["pass"]]
    unresolved = [c for c in con if not c["resolved_by_level"]]
    m0, m1 = metrics(b0), metrics(b1)
    missing = compiled.get("warnings", [])  # a mechanism presupposes another the draft does not include
    verdict = ("DO NOT ISSUE AS DRAFTED" if (unresolved or regress or missing) else "READY FOR NAMED HUMAN REVIEW")
    return {"verdict": verdict, "compiled": compiled, "conflicts": con, "unresolved_conflicts": len(unresolved),
            "invariants_before": inv0, "invariants_after": inv1, "invariants_fixed": fixed, "invariants_broken": regress, "missing_prerequisites": missing,
            "metrics_before": m0, "metrics_after": m1,
            "closes_gaps": sorted({g for m in compiled["mechanisms"] for g in VOC[m["id"]].get("closes", [])}),
            "interop_before": agreement(U0, I), "interop_after": agreement(U1, I),
            "settings": {"firewall_flags": flags, "sla_minutes": sla, "emergency_overlay": bool(overlay), "tiered_holds": tiered}}
