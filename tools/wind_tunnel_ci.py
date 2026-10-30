"""'Law as a pull request': run the regulatory wind tunnel on draft-rule files (human-confirmed mapping, no LLM).
Writes a markdown impact card per draft; exits 1 if any draft is not ready, so the pull request check fails."""
import argparse, os, sys, yaml
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.windtunnel.confirmed import compile_confirmed
from app.windtunnel.engine import wind_tunnel

def card(path, d, r):
    v = r["verdict"]; ok = v.startswith("READY")
    L = [f"### [{'READY' if ok else 'NOT READY'}] `{path}`: **{v}**", "", f"> {d['draft']}", "",
         f"Instrument: `{d.get('instrument_level', 'unspecified')}` | Mapping confirmed by: {d.get('confirmed_by', '(not stated)')}", ""]
    if r.get("reason"): L += [f"Reason: {r['reason']}", ""]
    for c in r.get("conflicts", []):
        L.append(f"- Conflict with **{c['clause']}** ({c.get('article') or ''}): {'resolved' if c['resolved_by_level'] else '**unresolved**'}. {c['note']}")
    for w in r.get("missing_prerequisites", []):
        L.append(f"- **Missing prerequisite:** {w}")
    inv0 = {i["id"]: i for i in r.get("invariants_before", [])}
    rows = [f"| {i['id']} | {i['text']} | {'PASS' if inv0[i['id']]['pass'] else 'FAIL'} | {'PASS' if i['pass'] else '**FAIL**'} | {i['detail']} |"
            for i in r.get("invariants_after", [])]
    if rows:
        L += ["", "| Invariant | | Before | After | Detail |", "|---|---|---|---|---|"] + rows
        L += ["", "_Only a change from PASS to FAIL counts against the draft. FAIL to FAIL rows are existing gaps under current rules, not caused by this draft._"]
    if "metrics_before" in r:
        m0, m1 = r["metrics_before"], r["metrics_after"]
        L += ["", "Measured effect: " + " | ".join(f"{k} {m0[k]} -> {m1[k]}" for k in ("protection", "access", "mizan", "officer_reviews") if k in m0 and k in m1),
              f"UAE-India decision agreement: {r.get('interop_before')}% -> {r.get('interop_after')}%"]
    return ok, L

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("files", nargs="*"); ap.add_argument("--out", default="wt_report.md")
    a = ap.parse_args()
    files = [f for f in a.files if f.endswith(".yaml") and Path(f).exists()]
    out, all_ok = ["## Regulatory wind tunnel: pre-issuance test", ""], True
    if not files:
        out.append("No draft rule files changed in this pull request.")
    for f in files:
        d = yaml.safe_load(open(f, encoding="utf-8"))
        comp = compile_confirmed(d)
        if comp["rejected_ids"]:
            ok, L = False, [f"### [NOT READY] `{f}`: unknown mechanism(s) {comp['rejected_ids']}"]
        else:
            ok, L = card(f, d, wind_tunnel(comp))
        all_ok = all_ok and ok; out += L + [""]
    out.append("_Simulation-based pre-issuance test on synthetic data. Conflict table hand-authored; requires legal review. A named human must sign off before any use._")
    text = "\n".join(out); Path(a.out).write_text(text, encoding="utf-8"); print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh: fh.write(text + "\n")
    sys.exit(0 if all_ok else 1)

if __name__ == "__main__":
    main()
