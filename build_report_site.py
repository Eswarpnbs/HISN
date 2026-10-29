"""Formal report-style site (docs/index.html): executive summary first, details collapsed, print-friendly."""
import csv, datetime, html, json, re, subprocess, tempfile, yaml
from pathlib import Path
from app.core.audit import AuditLog
from app.core.firewall import SmsFirewall
from app.core.gateway import PolicyGateway
from app.core.coordinator import Coordinator
from app.core.injects import load_injects, available
from app.gapengine.engine import run_battery, metrics

E = lambda x: html.escape(str(x))
SC, REG, PACK = "scenarios/crisis_exploit.yaml", "kb/rulepacks/uae/senders.yaml", "kb/rulepacks/uae/rules.yaml"
ex = lambda p: Path(p).exists()
def jl(p, kind=None):
    if not ex(p): return []
    rows = [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]
    return [r for r in rows if kind is None or r.get("kind") == kind]
tmp = lambda: AuditLog(Path(tempfile.mkdtemp()) / "a.jsonl")
GT = yaml.safe_load(open("scenarios/ground_truth.yaml", encoding="utf-8"))

def twin(gov):
    a = tmp()
    rows = Coordinator(SC, a, SmsFirewall(REG, a, governed=gov), PolicyGateway(PACK, a) if gov else None,
                       extra_events=load_injects(available()), sla_minutes=15 if gov else None).run()
    return {r["event_id"]: r for r in rows}, rows, a.verify()
G, GROWS, GV = twin(True); U, _, UV = twin(False)
def harms(d):
    return {"lost": sum(1 for k, v in GT.items() if v == "legit" and k in d and (d[k].get("silent_drop") or d[k]["action"].startswith("BLOCK"))),
            "held": sum(1 for k, v in GT.items() if v == "legit" and k in d and d[k]["action"] == "QUARANTINE"),
            "off": sum(1 for r in d.values() if r.get("kind") == "data_transfer" and not r["action"].startswith("BLOCK")),
            "unaud": sum(1 for r in d.values() if r.get("silent_drop"))}
HG, HU = harms(G), harms(U)

blf = Path("docs/baselines_14b.md") if ex("docs/baselines_14b.md") else Path("docs/baselines.md")
BL = [[c.strip() for c in l.strip("|").split("|")] for l in blf.read_text(encoding="utf-8").splitlines() if l.startswith("| B")] if blf.exists() else []
B = {c[0][:2]: c for c in BL}
BASE = metrics(run_battery({}, tmp())); BEST = metrics(run_battery({"require_auth": True, "authenticated_bypass": True}, tmp()))
FRAUD = metrics(run_battery({"fraud_duty": True}, tmp()))
_cards = {}
for p in sorted(Path("docs/impact_cards").glob("*.json")) if ex("docs/impact_cards") else []:
    r = json.loads(p.read_text(encoding="utf-8")); c = r.get("compiled", {})
    _cards[(c.get("draft"), c.get("instrument_level"))] = r
CARDS = list(_cards.values())
GAPS = yaml.safe_load(open("docs/gap_register.yaml", encoding="utf-8"))
GM = yaml.safe_load(open("kb/rulepacks/gap_mechanisms.yaml", encoding="utf-8")) if ex("kb/rulepacks/gap_mechanisms.yaml") else {}
MAN = list(csv.DictReader(open("kb/manifest.csv", encoding="utf-8")))
NCL = len(yaml.safe_load(open("kb/clauses/clauses.yaml", encoding="utf-8")))
_ret = Path("docs/retrieval_eval.md").read_text(encoding="utf-8") if ex("docs/retrieval_eval.md") else ""
_m = re.search(r"HISN clause-first\s+Recall@1 (\S+) \| Recall@3 (\S+) \| Recall@5 (\S+) \| MRR ([\d.]+)", _ret)
RET = _m.groups() if _m else ("-", "-", "-", "-")
NP = yaml.safe_load(open("kb/rulepacks/network_profile.yaml", encoding="utf-8")) if ex("kb/rulepacks/network_profile.yaml") else {}
_io = Path("docs/interoperability.md").read_text(encoding="utf-8") if ex("docs/interoperability.md") else ""
_mi = re.search(r"\*\*(\d+)%\*\*", _io); AGREE = (_mi.group(1) + "%") if _mi else "-"
SIGN = jl("runs/signoffs.jsonl", "human_signoff"); AGENTS = jl("runs/governed_agents.jsonl", "agent_rationale")
COMMIT = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip() or "-"
_v = re.findall(r"## (v[\d.]+)", Path("changelog/CHANGELOG.md").read_text(encoding="utf-8")) if ex("changelog/CHANGELOG.md") else []
VERSION = _v[-1] if _v else "v-"
NOW = datetime.datetime.now()

def pair_chart(rows, maxv, w=600):
    h = 48 * len(rows) + 8; sc = (w - 270) / maxv if maxv else 0
    o = [f"<svg viewBox='0 0 {w} {h}' width='100%' role='img' class='chart'>"]
    for i, (lab, b, a) in enumerate(rows):
        y = 6 + i * 48
        o.append(f"<text x='0' y='{y+14}' class='cl'>{E(lab)}</text>"
                 f"<rect x='230' y='{y}' width='{b*sc:.1f}' height='14' fill='#b8bec6'/><text x='{236+b*sc:.1f}' y='{y+11}' class='cv'>{b}</text>"
                 f"<rect x='230' y='{y+18}' width='{a*sc:.1f}' height='14' fill='#00732F'/><text x='{236+a*sc:.1f}' y='{y+29}' class='cv'>{a}</text>")
    return "".join(o) + "</svg>"

def bars(rows, maxv, unit="", w=600):
    h = 30 * len(rows) + 6; sc = (w - 270) / maxv if maxv else 0
    o = [f"<svg viewBox='0 0 {w} {h}' width='100%' role='img' class='chart'>"]
    for i, (lab, v, hi) in enumerate(rows):
        y = 4 + i * 30
        o.append(f"<text x='0' y='{y+14}' class='cl'>{E(lab)}</text><rect x='230' y='{y+2}' width='{v*sc:.1f}' height='16' "
                 f"fill='{'#00732F' if hi else '#b8bec6'}'/><text x='{236+v*sc:.1f}' y='{y+15}' class='cv'>{v}{unit}</text>")
    return "".join(o) + "</svg>"

legend = lambda a, b: f"<div class='legend'><span class='sw g0'></span>{a}<span class='sw g1'></span>{b}</div>"
details = lambda s, inner: f"<details><summary>{E(s)}</summary>{inner}</details>"
badge = lambda t, k: f"<span class='badge {k}'>{E(t)}</span>"
def table(head, rows):
    return ("<table><thead><tr>" + "".join(f"<th>{E(h)}</th>" for h in head) + "</tr></thead><tbody>"
            + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table>")
def section(n, sid, title, body):
    return f"<section id='{sid}'><h2><span class='num'>{n}</span>{E(title)}</h2>{body}</section>"
def outcome(o):
    if not o: return badge("-", "info")
    a = o["action"]
    if o.get("silent_drop"): return badge("Silently dropped", "no")
    if a == "QUARANTINE": return badge(f"Held - {o.get('escalate_to', 'reviewer')}", "hold")
    if a == "BLOCK_PROHIBITED": return badge("Blocked - Art. 13", "ok")
    if a == "SECOND_REVIEW": return badge("Second human review", "hold")
    if a == "ALLOW" and o.get("kind") == "data_transfer": return badge("Allowed offshore", "no")
    if a.startswith("BLOCK"): return badge("Blocked - logged", "ok")
    if a == "ALLOW": return badge("Delivered", "info")
    return badge(a.title(), "info")
acc = lambda c: round(100 * int(c[1].split("/")[0]) / int(c[1].split("/")[1]))

b1, b3, b0 = B.get("B1"), B.get("B3"), B.get("B0")
findings = [
    f"Without governance, <b>{HU['lost']}</b> genuine health and government messages were silently lost and <b>{HU['off']}</b> health-data transfers left the country. With HISN: <b>{HG['lost']}</b> and <b>{HG['off']}</b>; held messages reach a named human, then a second reviewer within 15 minutes.",
    f"On ITU's reference model, an ungoverned LLM scored <b>{b1[1] if b1 else '-'}</b> with <b>{b1[5] if b1 else '-'}</b> unsupported legal citations, below fixed rules ({b0[1] if b0 else '-'}). HISN scored <b>{b3[1] if b3 else '-'}</b> (held-out {b3[2] if b3 else '-'}) with <b>zero</b> harmful decisions.",
    f"Testing candidate rules: sender authentication with a verified-sender lane raised the MIZAN balance from <b>{BASE['mizan']}</b> to <b>{BEST['mizan']}</b>; a blunt fraud duty lowered it ({FRAUD['mizan']}), over-blocking legitimate businesses.",
    "The regulatory wind tunnel tests draft rules before issuance: the same emergency-offshore provision is <b>rejected as a regulation</b> (conflicts with Federal Law No. 2 of 2019, Art. 13) and <b>compatible as a Health Authority resolution</b>, the route Article 13 itself provides.",
    f"<b>{len(GAPS)}</b> domain-level policy gaps were identified, one discovered by the agents; four are shared or only partly addressed in India (UAE-India decision agreement {AGREE})."]
tiles = [(f"{HU['lost']} &rarr; {HG['lost']}", "Essential messages silently lost"), (f"{b1[3] if b1 else '-'} &rarr; {b3[3] if b3 else '-'}", "Harmful AI decisions (ITU reference model)"),
         (f"{BASE['mizan']} &rarr; {BEST['mizan']}", "MIZAN balance under tested rule"), (f"{NCL} / {len(MAN)}", "Verbatim clauses / hash-pinned records")]
S = []
S.append(section("1", "summary", "Executive summary", "<ol class='findings'>" + "".join(f"<li>{f}</li>" for f in findings) + "</ol>"))
S.append(section("2", "indicators", "Key indicators", "<div class='tiles'>" + "".join(f"<div class='tile'><div class='v'>{v}</div><div class='l'>{l}</div></div>" for v, l in tiles) + "</div>"))
key = [r for r in GROWS if r["kind"] in ("sms_submit", "data_transfer", "sla_escalation")]
S.append(section("3", "twin", "Policy-ON versus Policy-OFF: same events, two systems",
    "<p>The same crisis scenario and injected events were run through an ungoverned system and through HISN. Ground-truth labels are used only for this evaluation and are never visible to agents or the filter.</p>"
    + legend("Without governance", "With HISN") + pair_chart([("Essential messages silently lost", HU["lost"], HG["lost"]), ("Offshore health-data transfers", HU["off"], HG["off"]),
                                                              ("Decisions without audit trail", HU["unaud"], HG["unaud"])], max(HU["lost"], HU["off"], HU["unaud"], 1))
    + details("Show event-level outcomes", table(["Time", "Event", "Type", "Without governance", "With HISN"],
              [[r["t"], E(r["event_id"]), E(r["kind"]), outcome(U.get(r["event_id"])), outcome(r)] for r in key]))))
S.append(section("4", "agents", "Governed institutional agents",
    "<p>TDRA, the Health Authority and the Federal AI &amp; Data Authority propose actions; fixed code accepts a proposal only with retrieved evidence, within mandate, fitted to the event, on a binding and competent legal basis, and consistent with the agent's own risk rating.</p>"
    + "<h3>Accuracy against pre-registered expectations (qwen2.5:14b)</h3>" + bars([(c[0][:34], acc(c), c[0].startswith("B3")) for c in BL], 100, "%")
    + "<h3>Harmful decisions</h3>" + bars([(c[0][:34], int(c[3]), c[0].startswith("B3")) for c in BL], max([int(c[3]) for c in BL] + [1]))
    + details("Show baseline comparison", table(["System", "Accuracy", "Held-out", "Harmful", "Out of mandate", "Unsupported citations", "Decisive w/o binding basis"], [[E(x) for x in c] for c in BL]))
    + details("Show agent decisions (latest run)", table(["Time", "Authority", "Event", "Status", "Proposed", "Cited"],
              [[r["t"], E(r["role"]), E(r["event_id"]), E(r["status"]), E(r["proposed_action"]), f"<span class='small'>{E(', '.join(r.get('cited_ids', [])))}</span>"] for r in AGENTS]))))
LEVEL_NAMES = {"regulation": "Regulation", "health_authority_resolution": "Health Authority resolution",
               "federal_amendment": "Federal law amendment", "unspecified": "Unspecified"}
def inv_text(r, ids):
    names = {x["id"]: x["text"] for x in r.get("invariants_after", [])}
    return "; ".join(f"{i}: {names.get(i, '')}" for i in ids) or "none"
def card(r):
    c = r.get("compiled", {}); ok = r.get("verdict", "").startswith("READY")
    con = "".join(f"<li>{badge('Resolved' if x['resolved_by_level'] else 'Unresolved', 'ok' if x['resolved_by_level'] else 'no')} {E(x['clause'])} ({E(x['article'])}) - {E(x['note'])}</li>" for x in r.get("conflicts", [])) or "<li>None found in the verified corpus</li>"
    mb, ma = r.get("metrics_before", {}), r.get("metrics_after", {})
    return (f"<div class='card'><q>{E(c.get('draft', ''))}</q>{badge(r.get('verdict', ''), 'ok' if ok else 'no')} <span class='small'>Instrument: {E(LEVEL_NAMES.get(c.get('instrument_level', ''), c.get('instrument_level', '')))}</span>"
            f"<ul class='small'>{con}</ul><div class='small'>Fixes: {E(inv_text(r, r.get('invariants_fixed', [])))}<br>Breaks: {E(inv_text(r, r.get('invariants_broken', [])))}<br>{('Missing prerequisite: ' + E('; '.join(r['missing_prerequisites'])) + '<br>') if r.get('missing_prerequisites') else ''}"
            f"MIZAN {mb.get('mizan', '')} &rarr; {ma.get('mizan', '')} &middot; UAE-India agreement {r.get('interop_before', '')}% &rarr; {r.get('interop_after', '')}%</div></div>")
S.append(section("5", "windtunnel", "Test-driven regulation: the regulatory wind tunnel",
    "<p>A draft provision in plain language is mapped onto testable mechanisms (proposed by a model, validated by code, confirmed by a human), checked against verified law including the hierarchy of norms, regression-tested against eight public-interest invariants, and measured. Each result is sealed in the audit chain.</p>"
    + "".join(card(r) for r in CARDS)))
S.append(section("6", "gaps", "Policy gaps (domain level)",
    table(["Gap", "Description", "Type", "Status", "Evidence"], [[f"<b>{E(g['id'])}</b>", E(g["title"]), E(g["type"]), badge(g["status"].replace("_", " "), "ok" if g["status"] == "confirmed" else "info"),
           f"<span class='small'>{E(', '.join(g.get('evidence', [])) or g.get('discovered_by', ''))}</span>"] for g in GAPS])
    + details("Show UAE-India-Singapore comparison", table(["Gap", "UAE", "India", "Singapore", "Singapore clauses", "Notes"], [[E(k), E(v["UAE"]["status"]), E(v["IN"]["status"]), E(v.get("SG", {}).get("status", "-")), E(", ".join(v.get("SG", {}).get("clauses", []))), E(v.get("SG", {}).get("note", "") or v["IN"].get("note", ""))] for k, v in GM.items()]))))
S.append(section("7", "evidence", "Evidence base",
    f"<p>{len(MAN)} records (official instruments from the UAE, India and Singapore, plus one Saudi historical draft) pinned by SHA-256 and {NCL} verbatim clauses, ingested through the ITU AI Readiness reference pipeline. Retrieval on 24 policy questions: Recall@5 {RET[2]}, Recall@1 {RET[0]}, MRR {RET[3]}. "
    f"Network evidence ({NP.get('n_link_days', '-')} real operator link-days, used as proxy): rain raised link-failure risk {NP.get('relative_risk_rain', '-')}x; heat did not ({NP.get('relative_risk_hot', '-')}x).</p>"
    + details("Show knowledge-base records", table(["Record", "Title", "Issuer", "Basis", "Verification", "SHA-256"],
              [[E(m["record_id"]), E(m["title"]), E(m["issuer"]), E(m["basis"]), E(m["verification"]), f"<code>{E(m['sha256'][:12])}</code>"] for m in MAN]))))
S.append(section("8", "limits", "Method and limitations",
    "<ul><li>Synthetic data and scoring weights: results show direction, not real-world magnitudes.</li><li>Pre-registered expectations committed to version control before each held-out run; a smaller model overfitted the development set, the reference model did not.</li>"
    "<li>A similarity threshold copied from the ITU reference agent did not transfer to this embedding model and is not claimed as a safeguard.</li><li>Comparator texts and the wind tunnel's conflict table require legal review; India institutional agents are future work.</li>"
    "<li>This is a sandbox prototype for pre-issuance testing, not a production system.</li></ul>"))
S.append(section("A", "annex", "Annex: sign-off record and document control",
    table(["Signed at", "Provisions", "Decision", "Officer", "Measured effect"], [[E(r["at"]), E("+".join(r["patches"])), E(r["decision"]), E(r["officer"]), f"MIZAN {r['evidence']['d_mizan']:+}"] for r in SIGN] or [["-", "-", "-", "-", "-"]])
    + table(["Field", "Value"], [["Reference", "HISN-UAE-2026-001"], ["Version", E(VERSION)], ["Generated", NOW.strftime("%d %B %Y, %H:%M")], ["Source commit", f"<code>{E(COMMIT)}</code>"],
                                 ["Figures provenance", "docs/headline_numbers.md (python selftest.py)"], ["Audit chains", f"governed {GV}, ungoverned {UV}"]])))

CSS = """:root{--g:#00732F;--gold:#9A7B3C;--ink:#1d2329;--mut:#5f6b76;--line:#e3e6ea;--soft:#f6f7f8}
*{box-sizing:border-box}body{margin:0;font-family:"Segoe UI","Helvetica Neue",Arial,sans-serif;color:var(--ink);background:#fff;line-height:1.55}
.mast{border-top:4px solid var(--g);border-bottom:1px solid var(--line)}.mast .in{max-width:1180px;margin:0 auto;padding:14px 28px;display:flex;justify-content:space-between;align-items:center}
.brand{font-weight:700;font-size:19px;letter-spacing:.6px;color:var(--g)}.brand small{display:block;font-weight:400;font-size:12px;color:var(--mut);letter-spacing:0}
.meta{font-size:12px;color:var(--mut);text-align:right}.rule{height:2px;background:var(--gold);opacity:.55}
.crumb{max-width:1180px;margin:0 auto;padding:10px 28px;font-size:12px;color:var(--mut)}
.layout{max-width:1180px;margin:0 auto;padding:0 28px 40px;display:grid;grid-template-columns:220px 1fr;gap:40px}
aside{position:sticky;top:16px;align-self:start;font-size:13px}aside .t{font-size:11px;text-transform:uppercase;letter-spacing:.8px;color:var(--mut);margin:6px 0}
aside a{display:block;color:var(--ink);text-decoration:none;padding:6px 10px;border-left:2px solid var(--line)}aside a:hover{border-left-color:var(--g);color:var(--g)}
h1{font-size:27px;line-height:1.28;margin:10px 0 6px;font-weight:600}.lead{color:var(--mut);font-size:15px;margin:0 0 12px}
.chips span{display:inline-block;font-size:11.5px;border:1px solid var(--line);border-radius:3px;padding:2px 8px;margin:0 6px 6px 0;color:var(--mut)}
.notice{background:var(--soft);border-left:3px solid var(--gold);padding:10px 14px;font-size:12.5px;color:var(--mut);margin:14px 0 6px}
section{border-top:1px solid var(--line);margin-top:30px}h2{font-size:20px;font-weight:600;margin:16px 0 10px}h2 .num{display:inline-block;min-width:34px;color:var(--g)}
h3{font-size:14px;margin:18px 0 6px;color:var(--mut);font-weight:600}.findings li{margin:9px 0}.findings b{color:var(--g)}
.tiles{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid var(--line);border-radius:4px}.tile{padding:16px;border-right:1px solid var(--line)}.tile:last-child{border-right:none}
.tile .v{font-size:23px;font-weight:600}.tile .l{font-size:12px;color:var(--mut);margin-top:4px}
.chart .cl{font-size:12px;fill:#5f6b76}.chart .cv{font-size:12px;font-weight:600;fill:#1d2329}
.legend{font-size:12px;color:var(--mut);margin:6px 0 8px}.sw{display:inline-block;width:12px;height:10px;margin:0 6px 0 14px;vertical-align:middle}.sw:first-child{margin-left:0}.g0{background:#b8bec6}.g1{background:#00732F}
table{width:100%;border-collapse:collapse;font-size:12.5px;margin:8px 0}th{text-align:left;font-weight:600;border-bottom:2px solid var(--ink);padding:7px 8px}td{border-bottom:1px solid var(--line);padding:7px 8px;vertical-align:top}
details{margin:10px 0;border:1px solid var(--line);border-radius:4px;padding:0 12px}summary{cursor:pointer;padding:9px 0;font-size:13px;color:var(--g);font-weight:600}
.badge{display:inline-block;font-size:11px;font-weight:600;padding:2px 8px;border-radius:3px;letter-spacing:.2px}.ok{background:#e6f2ea;color:#0b5a2a}.no{background:#fbe9ea;color:#8a1020}.hold{background:#fdf3dc;color:#6b4e00}.info{background:#eef0f3;color:#3d4852}
.card{border:1px solid var(--line);border-radius:4px;padding:14px 16px;margin:10px 0}.card q{display:block;font-style:italic;margin-bottom:8px}.small{font-size:12px;color:var(--mut)}
footer{border-top:1px solid var(--line);margin-top:30px}footer .in{max-width:1180px;margin:0 auto;padding:16px 28px;font-size:11.5px;color:var(--mut)}
@media print{aside,.crumb{display:none}.layout{display:block}details{border:none}}@media (max-width:900px){.layout{grid-template-columns:1fr}aside{display:none}.tiles{grid-template-columns:repeat(2,1fr)}}"""
toc = "".join(f"<a href='#{sid}'>{t}</a>" for sid, t in [("summary", "1. Executive summary"), ("indicators", "2. Key indicators"), ("twin", "3. Policy-ON vs OFF"), ("agents", "4. Governed agents"),
              ("windtunnel", "5. Regulatory wind tunnel"), ("gaps", "6. Policy gaps"), ("evidence", "7. Evidence base"), ("limits", "8. Method and limitations"), ("annex", "Annex")])
page = (f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>HISN Regulatory Assurance Report</title><style>{CSS}</style></head><body>"
        f"<div class='mast'><div class='in'><div class='brand'>HISN <span style='font-weight:400;color:#9A7B3C'>\u062d\u0635\u0646</span><small>Regulatory Assurance Report</small></div>"
        f"<div class='meta'>Ref. HISN-UAE-2026-001 &middot; {E(VERSION)}<br>{NOW:%d %B %Y}</div></div></div><div class='rule'></div>"
        f"<div class='crumb'>Reports &rsaquo; Telecommunications, Health &amp; Public Services &rsaquo; HISN-UAE-2026-001</div>"
        f"<div class='layout'><aside><div class='t'>Contents</div>{toc}</aside><main>"
        f"<h1>Governing the telecom AI that decides which health and government messages reach citizens</h1>"
        f"<p class='lead'>Assurance report on a working prototype, with pre-issuance testing of draft rules against verified UAE law.</p>"
        f"<div class='chips'><span>ITU AI for Good Lab Hackathon, UAE 2026</span><span>Team Sankalp</span><span>Synthetic data</span><span>Audit chains verified</span></div>"
        f"<div class='notice'>Independent hackathon prototype. This is not an official government publication and is not affiliated with or endorsed by any UAE or Indian government entity. All senders and data are synthetic.</div>"
        + "".join(S) + "</main></div>"
        f"<footer><div class='in'>HISN &middot; Team Sankalp &middot; Every figure is reproducible with <code>python selftest.py</code> &middot; Source commit {E(COMMIT)}</div></footer></body></html>")
Path("docs/index.html").write_text(page, encoding="utf-8")
print(f"written docs/index.html | cards {len(CARDS)} | baselines {len(BL)} | records {len(MAN)}")
