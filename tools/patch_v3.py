from pathlib import Path

def patch(path, edits):
    p = Path(path); s = p.read_text(encoding="utf-8")
    for old, new in edits:
        assert s.count(old) == 1, f"{path}: expected exactly one match for {old[:70]!r}"
        s = s.replace(old, new)
    return p, s

V2, V3 = '"scenarios/gold_heldout_v2.yaml"', '"scenarios/gold_heldout_v3.yaml"'
files = [
  patch("run_baselines.py", [
    (f'"scenarios/gold_dev_b.yaml", {V2}])\n', f'"scenarios/gold_dev_b.yaml", {V2}, {V3}])\n'),
    (f'HELD = load_gold([{V2}])\n', f'HELD = load_gold([{V2}])\nHELD3 = load_gold([{V3}])\n'),
    ("    a, h = score(c.agent_outputs, ALL), score(c.agent_outputs, HELD)\n    rows.append((label, a, h, round(time.time() - t0)))\n",
     "    a, h, h3 = score(c.agent_outputs, ALL), score(c.agent_outputs, HELD), score(c.agent_outputs, HELD3)\n"
     "    rows.append((label, a, h, h3, round(time.time() - t0)))\n"),
    ("| decisive w/o binding basis {a['decisive_without_binding_basis']} | {rows[-1][3]}s\")",
     "| decisive w/o binding basis {a['decisive_without_binding_basis']} | held-out v3 {h3['acc']} | {rows[-1][4]}s\")"),
    ('"(dev + held-out v2). Synthetic data.', '"(dev + held-out v2 + held-out v3). Synthetic data.'),
    ("| decisive w/o binding basis |\\n|---|---|---|---|---|---|---|\\n", "| decisive w/o binding basis | held-out v3 |\\n|---|---|---|---|---|---|---|---|\\n"),
    ("    for label, a, h, _ in rows:\n", "    for label, a, h, h3, _ in rows:\n"),
    ("{a['decisive_without_binding_basis']} |\\n\")", "{a['decisive_without_binding_basis']} | {h3['acc']} |\\n\")"),
  ]),
  patch("kb/rulepacks/uae/mechanisms.yaml", [
    ('description: "Authenticated essential senders bypass content-based scoring."',
     'description: "Authenticated essential senders bypass content-based scoring entirely, so their messages are never held by the filter. Use only when the draft says such senders skip or bypass filtering."'),
    ('description: "Essential messages held by a filter must reach a second human reviewer within a time limit."',
     'description: "One fixed time limit, the same for every held essential message, after which it must reach a second human reviewer. Use when the draft states a single number of minutes for all messages."'),
    ('description: "Essential health messages held by a filter must reach a second human reviewer within the time limit of their clinical tier, as declared by the authenticated sender (FHIR priority)."',
     'description: "Different time limits by clinical urgency (life-critical, time-sensitive, routine): a held health message must reach a second human reviewer within the limit of its clinical tier, as declared by the authenticated sender (FHIR priority). Use when the draft mentions clinical tiers, life-critical messages, urgency or priority."'),
  ]),
  patch("app/windtunnel/engine.py", [
    ('    verdict = ("DO NOT ISSUE AS DRAFTED" if (unresolved or regress) else "READY FOR NAMED HUMAN REVIEW")\n',
     '    missing = compiled.get("warnings", [])  # a mechanism presupposes another the draft does not include\n'
     '    verdict = ("DO NOT ISSUE AS DRAFTED" if (unresolved or regress or missing) else "READY FOR NAMED HUMAN REVIEW")\n'),
    ('"invariants_broken": regress,', '"invariants_broken": regress, "missing_prerequisites": missing,'),
  ]),
]
for p, s in files:
    p.write_text(s, encoding="utf-8"); print("patched", p)