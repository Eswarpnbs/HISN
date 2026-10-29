from pathlib import Path
p = Path("app/windtunnel/engine.py"); src = p.read_text(encoding="utf-8")

def rep(old, new):
    global src
    assert src.count(old) == 1, f"expected exactly one match for: {old[:70]!r}"
    src = src.replace(old, new)

rep("from app.core.coordinator import Coordinator\n",
    "from app.core.coordinator import Coordinator, load_scenario\nfrom app.core.tiers import Tiers\n")
rep('_tmp = lambda: AuditLog(Path(tempfile.mkdtemp()) / "a.jsonl")\n',
    '_tmp = lambda: AuditLog(Path(tempfile.mkdtemp()) / "a.jsonl")\nTIERS = Tiers()\n\n'
    'def t1_ids():\n'
    '    """Messages whose authenticated sender declared a life-critical (T1) priority."""\n'
    '    _, evs = load_scenario(SC)\n'
    '    return [e.id for e in list(evs) + list(load_injects(available()))\n'
    '            if e.kind == "sms_submit" and TIERS.classify(e.payload)[0] == "T1"]\n')
rep("    flags, sla, overlay = {}, 15, None\n", "    flags, sla, overlay, tiered = {}, 15, None, False\n")
rep('        if eff.get("gateway_overlay") == "emergency_offshore": overlay = m\n    return flags, sla, overlay\n',
    '        if eff.get("gateway_overlay") == "emergency_offshore": overlay = m\n'
    '        if eff.get("tiered_holds"): tiered = True\n    return flags, sla, overlay, tiered\n')
rep("def run_uae(flags, sla, pack_path):\n", "def run_uae(flags, sla, pack_path, tiers=None):\n")
rep("extra_events=load_injects(available()), sla_minutes=sla).run()",
    "extra_events=load_injects(available()), sla_minutes=sla, tiers=tiers).run()")
rep("    flags, sla, overlay = config(compiled)\n", "    flags, sla, overlay, tiered = config(compiled)\n")
rep('    U1, v1 = run_uae(flags, sla, pack_with_overlay(overlay, compiled["draft"], compiled["instrument_level"]))\n',
    '    U1, v1 = run_uae(flags, sla, pack_with_overlay(overlay, compiled["draft"], compiled["instrument_level"]),\n'
    '                     TIERS if tiered else None)\n')
rep('"emergency_overlay": bool(overlay)}', '"emergency_overlay": bool(overlay), "tiered_holds": tiered}')
rep('    a0, a1 = metrics(base_bat)["access"], metrics(bat)["access"]\n',
    '    a0, a1 = metrics(base_bat)["access"], metrics(bat)["access"]\n'
    '    lim = TIERS.max_hold("T1")\n'
    '    slow = [k for k in t1_ids() if (h := U.get(f"{k}-SLA")) and h["held_minutes"] > lim]\n')
rep('"detail": f"access {a0} -> {a1}"}]',
    '"detail": f"access {a0} -> {a1}"},\n'
    '        {"id": "I7", "text": "Life-critical health messages reach a human within their clinical limit",\n'
    '         "pass": not slow, "detail": f"{len(slow)} T1 message(s) waited longer than {lim} min"}]')

p.write_text(src, encoding="utf-8"); print("engine.py patched: 11 edits")