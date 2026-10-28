"""Regulatory wind tunnel. Usage:
  python wind_tunnel.py "Draft provision text" [--level health_authority_resolution] [--yes] [--model qwen2.5:7b]"""
import argparse, datetime, json, re
from pathlib import Path
from app.core.audit import AuditLog
from app.windtunnel.compiler import compile_draft, LEVELS
from app.windtunnel.engine import wind_tunnel

ap = argparse.ArgumentParser(); ap.add_argument("draft"); ap.add_argument("--level", choices=LEVELS)
ap.add_argument("--yes", action="store_true"); ap.add_argument("--model", default="qwen2.5:7b"); a = ap.parse_args()
from app.agents.llm import OllamaLLM
c = compile_draft(a.draft, OllamaLLM(a.model), a.level)
print(f"\nMapped to: {[m['id'] + str(m['params'] or '') for m in c['mechanisms']] or 'nothing'} | level: {c['instrument_level']}")
for w in c["warnings"]: print(f"  WARNING: {w}")
if c["untestable_parts"]: print(f"  Not testable here: {c['untestable_parts']}")
if not a.yes and input("Confirm this mapping? [y/N] ").strip().lower() != "y":
    print("Not confirmed - nothing tested."); raise SystemExit
r = wind_tunnel(c)
ok = lambda b: "PASS" if b else "FAIL"
L = [f"# Regulatory Impact Card", "", f"**Draft:** {a.draft}", f"**Instrument level:** {c['instrument_level']}",
     f"**Verdict:** **{r['verdict']}**", ""]
if r["verdict"] != "NOT TESTABLE":
    mb, ma = r["metrics_before"], r["metrics_after"]
    L += ["## Measured effect (synthetic battery + crisis scenario)",
          f"- Protection {mb['protection']}% -> {ma['protection']}% | Access {mb['access']}% -> {ma['access']}% | MIZAN {mb['mizan']} -> {ma['mizan']} | officer reviews {mb['officer_reviews']} -> {ma['officer_reviews']}",
          f"- Gaps addressed: {', '.join(r['closes_gaps']) or '-'} | UAE-India decision agreement {r['interop_before']}% -> {r['interop_after']}%", "",
          "## Conflicts with existing verified law"]
    L += [f"- {'RESOLVED by instrument level' if x['resolved_by_level'] else 'UNRESOLVED'}: {x['clause']} ({x['article']}) - {x['note']}\n  > {x['verbatim']}" for x in r["conflicts"]] or ["- none found in the verified corpus"]
    L += ["", "## Public-interest invariants (before -> after)"]
    L += [f"- {b['id']} {b['text']}: {ok(a_['pass'])} -> {ok(b['pass'])} {('(' + b['detail'] + ')') if b['detail'] else ''}"
          for a_, b in zip(r["invariants_before"], r["invariants_after"])]
    L += ["", f"Warnings: {'; '.join(c['warnings']) or 'none'} | Not testable here: {c['untestable_parts'] or 'none'}"]
L += ["", "_Simulation-based pre-issuance test. Conflict table hand-authored from verified clauses; requires legal review. A named human must sign off before any use._"]
slug = re.sub(r"[^a-z0-9]+", "-", a.draft.lower())[:40].strip("-")
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
md = Path(f"docs/impact_cards/{stamp}-{slug}.md"); md.write_text("\n".join(L) + "\n", encoding="utf-8")
md.with_suffix(".json").write_text(json.dumps(r, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
h = AuditLog(Path("runs/windtunnel.jsonl")).write({"kind": "impact_card", "draft": a.draft, "verdict": r["verdict"], "card": str(md)})
print("\n".join(L)); print(f"\nwritten {md} (+ .json) | sealed {h[:16]}...")
