from pathlib import Path

def patch(path, edits):
    p = Path(path); s = p.read_text(encoding="utf-8")
    for old, new in edits:
        assert s.count(old) == 1, f"{path}: expected exactly one match for {old[:70]!r}"
        s = s.replace(old, new)
    return p, s

files = [
  patch("app/core/gateway.py", [
    ("            elif event.get(k) != v:\n",
     "            elif k.endswith(\"_max\"):\n"
     "                val = event.get(k[:-4])\n"
     "                if val is None or val > v:\n"
     "                    return False\n"
     "            elif event.get(k) != v:\n"),
  ]),
  patch("app/core/coordinator.py", [
    ("            self.emergency = True\n", "            self.emergency, self.emergency_since = True, now\n"),
    ('                d = self.gateway.evaluate({"type": "message_log_transfer", **e.payload, "emergency": getattr(self, "emergency", False)})\n',
     '                em = getattr(self, "emergency", False)\n'
     '                d = self.gateway.evaluate({"type": "message_log_transfer", **e.payload, "emergency": em,\n'
     '                                           "emergency_minutes": (now - self.emergency_since) if em else None})\n'),
  ]),
  patch("app/windtunnel/compiler.py", [
    ("def _coerce(v, default):\n    try: return type(default)(v)\n    except (TypeError, ValueError): return default\n",
     "def _coerce(v, default):\n"
     "    \"\"\"A parameter the draft does not state keeps its default; a null default means 'not stated' (e.g. no time limit).\"\"\"\n"
     "    if v is None: return default\n"
     "    try: return type(default)(v) if default is not None else int(v)\n"
     "    except (TypeError, ValueError): return default\n"),
  ]),
  patch("kb/rulepacks/uae/mechanisms.yaml", [
    ("    params: {hours: 72}\n", "    params: {hours: null}\n"),
    ("for a limited period.\"", "for a limited period. Set hours only if the draft states a time limit; otherwise leave it null.\""),
  ]),
  patch("app/windtunnel/engine.py", [
    ("from app.core.coordinator import Coordinator, load_scenario\n",
     "from app.core.coordinator import Coordinator, load_scenario\nfrom app.core.events import Event\n"),
    ("def pack_with_overlay(",
     "HORIZON_HOURS = 72  # a draft with no stated limit is probed here: an exception still open then has no working sunset\n\n"
     "def _overlay_hours(overlay):\n"
     "    return ((overlay or {}).get(\"params\") or {}).get(\"hours\")\n\n"
     "def _overlay_condition(overlay):\n"
     "    cond = {\"data_class\": \"health\", \"emergency\": True}\n"
     "    if _overlay_hours(overlay): cond[\"emergency_minutes_max\"] = int(_overlay_hours(overlay)) * 60\n"
     "    return cond\n\n"
     "def _probe(overlay):\n"
     "    _, evs = load_scenario(SC)\n"
     "    t_em = min(e.t for e in list(evs) + list(load_injects(available())) if e.kind == \"emergency_declared\")\n"
     "    h = _overlay_hours(overlay) or HORIZON_HOURS\n"
     "    return Event(id=\"PROBE-SUNSET\", t=t_em + int(h) * 60 + 10, kind=\"data_transfer\", audience=(\"ai_data_authority\",),\n"
     "                 payload={\"data_class\": \"health\", \"destination_country\": \"XX\",\n"
     "                          \"reason\": \"probe: transfer after the emergency window\"}, act=3)\n\n"
     "def pack_with_overlay("),
    ('"condition": {"data_class": "health", "emergency": True}, "verdict": "COMPLIANT"',
     '"condition": _overlay_condition(overlay), "verdict": "COMPLIANT"'),
    ("def run_uae(flags, sla, pack_path, tiers=None):\n", "def run_uae(flags, sla, pack_path, tiers=None, probe=None):\n"),
    ("extra_events=load_injects(available()), sla_minutes=sla, tiers=tiers).run()",
     "extra_events=list(load_injects(available())) + ([probe] if probe else []), sla_minutes=sla,\n"
     "                      tiers=tiers).run(until=(probe.t + 5) if probe else None)"),
    ('    U0, v0 = run_uae({}, 15, "kb/rulepacks/uae/rules.yaml")\n',
     '    probe = _probe(overlay)\n    U0, v0 = run_uae({}, 15, "kb/rulepacks/uae/rules.yaml", probe=probe)\n'),
    ("                     TIERS if tiered else None)\n", "                     TIERS if tiered else None, probe=probe)\n"),
    ('    slow = [k for k in t1_ids() if (h := U.get(f"{k}-SLA")) and h["held_minutes"] > lim]\n',
     '    slow = [k for k in t1_ids() if (h := U.get(f"{k}-SLA")) and h["held_minutes"] > lim]\n'
     '    pr = U.get("PROBE-SUNSET")\n'),
    ('"detail": f"{len(slow)} T1 message(s) waited longer than {lim} min"}]',
     '"detail": f"{len(slow)} T1 message(s) waited longer than {lim} min"},\n'
     '        {"id": "I8", "text": "Emergency exceptions expire (sunset)", "pass": pr is None or pr["action"] != "ALLOW",\n'
     '         "detail": "no probe" if pr is None else f"transfer after the emergency window: {pr[\'action\']}"}]'),
  ]),
]
for p, s in files:
    p.write_text(s, encoding="utf-8"); print("patched", p)