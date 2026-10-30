"""Build a self-contained offline dashboard (docs/dashboard.html) from HISN runs. No server, no internet."""
import csv, json, html, datetime, tempfile, yaml
from pathlib import Path
from app.core.audit import AuditLog
from app.core.firewall import SmsFirewall
from app.core.gateway import PolicyGateway
from app.core.coordinator import Coordinator
from app.core.injects import load_injects, available
from app.gapengine.engine import run_battery, metrics

SC, REG, PACK = "scenarios/crisis_exploit.yaml", "kb/rulepacks/uae/senders.yaml", "kb/rulepacks/uae/rules.yaml"
E = lambda x: html.escape(str(x))

def jl(path, kind=None):
    p = Path(path)
    if not p.exists(): return []
    rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    return [r for r in rows if kind is None or r.get("kind") == kind]

def twin():
    out = {}
    for gov in (True, False):
        p = Path(f"runs/dash_{'gov' if gov else 'ungov'}.jsonl")
        if p.exists(): p.unlink()
        a = AuditLog(p)
        rows = Coordinator(SC, a, SmsFirewall(REG, a, governed=gov), PolicyGateway(PACK, a) if gov else None,
                           extra_events=load_injects(available()), sla_minutes=15 if gov else None).run()
        out[gov] = ({r["event_id"]: r for r in rows}, a.verify(), rows)
    return out

def fmt(o):
    if not o: return "—"
    s = o["action"]
    if o.get("silent_drop"): s += " · silent drop"
    if o.get("escalate_to"): s += f" → {o['escalate_to']}"
    if o.get("rule_id"): s += f" [{o['rule_id']}]"
    return s

GT = yaml.safe_load(open("scenarios/ground_truth.yaml", encoding="utf-8"))

def cls(o):
    if not o: return ""
    a, gt = o["action"], GT.get(o["event_id"])
    if o.get("kind") == "data_transfer":
        return "good" if a.startswith("BLOCK") else "bad"
    if gt == "legit":
        if o.get("silent_drop") or a.startswith("BLOCK"): return "bad"
        if a in ("QUARANTINE", "SECOND_REVIEW"): return "warn"
        if a == "ALLOW": return "good"
    if gt == "malicious":
        if a == "ALLOW": return "bad"
        if o.get("silent_drop"): return "muted"
        if a.startswith("BLOCK"): return "good"
        if a == "QUARANTINE": return "warn"
    if a == "SECOND_REVIEW": return "warn"
    return ""

def harms(rows):
    lost = sum(1 for k, v in GT.items() if v == "legit" and k in rows and (rows[k].get("silent_drop") or rows[k]["action"].startswith("BLOCK")))
    held = sum(1 for k, v in GT.items() if v == "legit" and k in rows and rows[k]["action"] == "QUARANTINE")
    scams = sum(1 for k, v in GT.items() if v == "malicious" and k in rows and rows[k]["action"] == "ALLOW")
    offshore = sum(1 for r in rows.values() if r.get("kind") == "data_transfer" and not r["action"].startswith("BLOCK"))
    unaudited = sum(1 for r in rows.values() if r.get("silent_drop"))
    return lost, held, scams, offshore, unaudited

def bar(label, v, c):
    return (f"<div class='bar'><span>{label}</span><div class='track'><div class='fill {c}' style='width:{v}%'></div>"
            f"</div><b>{v}</b></div>")

T = twin(); g, gv, grows = T[True]; u, uv, _ = T[False]
gh, uh = harms(g), harms(u)
twin_rows = "".join(
    f"<tr><td>{r['t']}</td><td>{E(r['event_id'])}</td><td>{E(r['kind'])}</td>"
    f"<td class='{cls(u.get(r['event_id']))}'>{E(fmt(u.get(r['event_id'])))}</td><td class='{cls(r)}'>{E(fmt(r))}</td></tr>"
    for r in grows)

rat = jl("runs/governed_agents.jsonl", "agent_rationale")
agent_rows = "".join(
    f"<tr><td>{r['t']}</td><td>{E(r['role'])}</td><td>{E(r['event_id'])}</td><td>{E(r['status'])}</td>"
    f"<td><b>{E(r['proposed_action'])}</b></td><td><code>{E(', '.join(r.get('cited_ids', [])) or '—')}</code></td>"
    f"<td>{E(r.get('reason') or '')} {E((r.get('assessment') or '')[:180])}</td></tr>" for r in rat)

base = metrics(run_battery({}, AuditLog(Path(tempfile.mkdtemp()) / "b.jsonl")))
cfs = jl("runs/gap_engine.jsonl", "counterfactual_test")
cards = [("UAE pack as-is (baseline)", base)] + [(r["patch"], r) for r in cfs]
gap_cards = "".join(
    f"<div class='card'><h4>{E(n)}</h4>{bar('protection', m['protection'], 'p')}{bar('access', m['access'], 'a')}"
    f"{bar('MIZAN', m['mizan'], 'm')}<small>officer reviews: {m['officer_reviews']}"
    f"{' · closes ' + E(', '.join(m['loopholes_closed'])) if m.get('loopholes_closed') else ''}</small></div>"
    for n, m in cards)
loops = "".join(f"<li><b>{E(r['tactic'])}</b> → gap {E(r['gap'])} ({r['cases']} cases)</li>" for r in jl("runs/gap_engine.jsonl", "loophole_found"))
lbs = "".join(f"<li><b>{E(r['rule'])}</b>: not blocked {r['allowed_with']} → {r['allowed_without']} when removed "
              f"⇒ {'LOAD-BEARING' if r['load_bearing'] else 'not load-bearing'}</li>" for r in jl("runs/gap_engine.jsonl", "load_bearing"))

ev_lines = [l for l in Path("docs/eval_log_v3.md").read_text(encoding="utf-8").splitlines() if l.startswith("|") and "---" not in l] \
    if Path("docs/eval_log_v3.md").exists() else []
ev_rows = "".join("<tr>" + "".join(f"<{'th' if i == 0 else 'td'}>{E(c.strip())}</{'th' if i == 0 else 'td'}>"
                  for c in l.strip("|").split("|")) + "</tr>" for i, l in enumerate(ev_lines))

man = list(csv.DictReader(open("kb/manifest.csv", encoding="utf-8")))
n_clauses = len(yaml.safe_load(open("kb/clauses/clauses.yaml", encoding="utf-8")))
kb_rows = "".join(f"<tr><td>{E(m['record_id'])}</td><td>{E(m['title'])}</td><td>{E(m['issuer'])}</td><td>{E(m['basis'])}</td>"
                  f"<td>{E(m['verification'])}</td><td><code>{E(m['sha256'][:12])}…</code></td></tr>" for m in man)
gaps = yaml.safe_load(open("docs/gap_register.yaml", encoding="utf-8"))
gap_html = "".join(f"<div class='card'><h4>{E(x['id'])} · {E(x['title'])}</h4><small>type: {E(x['type'])} · status: <b>{E(x['status'])}</b>"
                   f"<br>evidence: {E(', '.join(x.get('evidence', [])) or x.get('discovered_by', ''))}</small></div>" for x in gaps)
so_rows = "".join(f"<tr><td>{E(r['at'])}</td><td>{E('+'.join(r['patches']))}</td><td>{E(r['decision'])}</td>"
                  f"<td>{E(r['officer'])} ({E(r['officer_role'])})</td><td>MIZAN {r['evidence']['d_mizan']:+}</td></tr>"
                  for r in jl("runs/signoffs.jsonl", "human_signoff"))


def md_rows(path, prefix):
    if not Path(path).exists(): return ""
    rows = [l for l in Path(path).read_text(encoding="utf-8").splitlines() if l.startswith(prefix)]
    return "".join("<tr>" + "".join(f"<td>{E(c.strip())}</td>" for c in l.strip("|").split("|")) + "</tr>" for l in rows)
bl_rows = md_rows("docs/baselines_14b.md" if Path("docs/baselines_14b.md").exists() else "docs/baselines.md", "| B")
io_rows = md_rows("docs/interoperability.md", "| G")
nprof = yaml.safe_load(open("kb/rulepacks/network_profile.yaml", encoding="utf-8")) if Path("kb/rulepacks/network_profile.yaml").exists() else {}


import json as _json
_cards = sorted(Path("docs/impact_cards").glob("*.json"))[-6:] if Path("docs/impact_cards").exists() else []
wt_rows = ""
for _p in _cards:
    _r = _json.loads(_p.read_text(encoding="utf-8")); _c = _r.get("compiled", {})
    _cls = "good" if _r.get("verdict", "").startswith("READY") else "bad"
    _con = "; ".join(f"{'resolved' if x['resolved_by_level'] else 'UNRESOLVED'} {x['clause']}" for x in _r.get("conflicts", [])) or "none"
    _mb, _ma = _r.get("metrics_before", {}), _r.get("metrics_after", {})
    wt_rows += (f"<tr><td>{E(_c.get('draft', '')[:110])}</td><td>{E(_c.get('instrument_level', ''))}</td><td class='{_cls}'>{E(_r.get('verdict', ''))}</td>"
                f"<td>{E(_con)}</td><td>fixed {E(_r.get('invariants_fixed', []))} broken {E(_r.get('invariants_broken', []))}</td>"
                f"<td>{_mb.get('mizan', '')} &rarr; {_ma.get('mizan', '')}</td><td>{_r.get('interop_before', '')}% &rarr; {_r.get('interop_after', '')}%</td></tr>")

CSS = """:root{--g:#00732F;--r:#C8102E;--k:#1a1a1a;--gold:#B68A35;--sand:#F7F5F0;--ink:#1f2933;--mut:#5b6476}
*{box-sizing:border-box}body{margin:0;font-family:"Segoe UI",-apple-system,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--sand)}
.wrap{max-width:1280px;margin:0 auto;padding:0 28px 48px}
.top{height:6px;background:linear-gradient(90deg,var(--r) 0 25%,var(--g) 25% 50%,#fff 50% 75%,var(--k) 75% 100%)}
.hero{background:linear-gradient(135deg,#0b3d24 0%,var(--g) 55%,#0f5132 100%);color:#fff;padding:34px 28px 28px;border-bottom:4px solid var(--gold)}
.hero .in{max-width:1280px;margin:0 auto}.hero h1{margin:0;font-size:32px}.hero .ar{font-size:28px;color:#f3e3c3;margin-left:12px}
.hero p{margin:8px 0 0;color:#e7f2ea;font-size:15px}.tag{display:inline-block;margin:12px 6px 0 0;padding:4px 11px;border:1px solid rgba(255,255,255,.45);border-radius:20px;font-size:12px;color:#fff}
.disc{background:#fff8e6;border-left:4px solid var(--gold);padding:8px 28px;font-size:12px;color:#5a4a1f}
nav{position:sticky;top:0;z-index:5;background:#fff;border-bottom:1px solid #e6e1d6;box-shadow:0 2px 6px rgba(0,0,0,.05)}
nav .in{max-width:1280px;margin:0 auto;padding:8px 28px;display:flex;flex-wrap:wrap;gap:6px}
nav a{font-size:12.5px;text-decoration:none;color:var(--g);padding:5px 11px;border-radius:16px;background:#eef6f1}nav a:hover{background:var(--g);color:#fff}
.kpis{display:grid;grid-template-columns:repeat(auto-fill,minmax(215px,1fr));gap:14px;margin:24px 0}
.kpi{background:#fff;border-radius:12px;padding:16px;border-top:4px solid var(--g);box-shadow:0 2px 10px rgba(0,0,0,.06)}
.kpi.r{border-top-color:var(--r)}.kpi.gold{border-top-color:var(--gold)}.kpi.k{border-top-color:var(--k)}
.kpi .v{font-size:28px;font-weight:700;color:var(--k)}.kpi .l{font-size:12.5px;color:var(--mut);margin-top:4px}.kpi .s{font-size:12px;color:var(--g);margin-top:6px;font-weight:600}
.charts{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:14px;margin-bottom:8px}
.panel{background:#fff;border-radius:12px;padding:16px;box-shadow:0 2px 10px rgba(0,0,0,.06)}.panel h3{margin:0 0 10px;font-size:15px;color:var(--g)}
h2{margin:36px 0 12px;font-size:20px;color:var(--k);padding-left:12px;border-left:5px solid var(--g)}
.sub{color:var(--mut)}.note{font-size:12.5px;color:var(--mut)}
table{border-collapse:separate;border-spacing:0;width:100%;background:#fff;font-size:13px;border-radius:10px;overflow:hidden;box-shadow:0 1px 6px rgba(0,0,0,.05)}
td,th{padding:8px 10px;text-align:left;vertical-align:top;border-bottom:1px solid #efeae0}th{background:var(--g);color:#fff;font-weight:600}
tr:nth-child(even) td{background:#fbfaf6}
.bad{background:#fde4e6!important;color:#8a0f22}.warn{background:#fff3d6!important;color:#6b4e00}.good{background:#e1f3e8!important;color:#0b5a2a}.muted{background:#f0f0f0!important;color:#6b7280}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}
.card{background:#fff;border-radius:12px;padding:14px;box-shadow:0 2px 10px rgba(0,0,0,.06);border-top:3px solid var(--gold)}.card h4{margin:0 0 8px;color:var(--k)}
.bar{display:flex;align-items:center;gap:8px;font-size:12px;margin:4px 0}.bar span{width:72px;color:var(--mut)}
.track{flex:1;background:#efeae0;height:10px;border-radius:6px}.fill{height:10px;border-radius:6px}
.p{background:var(--g)}.a{background:var(--gold)}.m{background:var(--r)}
code{font-size:12px;background:#f3f0e8;padding:1px 4px;border-radius:4px}
footer{margin-top:40px;padding:18px 28px;background:var(--k);color:#cfcfcf;font-size:12px}"""

doc = f"""<!doctype html><html><head><meta charset='utf-8'><title>HISN dashboard</title><style>{CSS}</style></head><body>
<h1>HISN — governance for the telecom AI that decides what reaches citizens</h1>
<p class='sub'>Team Sankalp · ITU AI for Good Lab Hackathon UAE · <b>synthetic data only</b> · generated {datetime.datetime.now():%Y-%m-%d %H:%M}
 · audit chains verified: governed {gv}, ungoverned {uv}</p>
<table style='width:auto;margin-top:12px'><tr><th>Outcome (ground truth hidden from agents)</th><th>UNGOVERNED</th><th>GOVERNED (HISN)</th></tr><tr><td>Legitimate essential messages silently lost</td><td class='bad'>{uh[0]}</td><td class='good'>{gh[0]}</td></tr><tr><td>Legitimate messages held for a named human (not lost)</td><td>{uh[1]}</td><td class='warn'>{gh[1]}</td></tr><tr><td>Scams delivered</td><td>{uh[2]}</td><td>{gh[2]}</td></tr><tr><td>Health data transfers offshore not blocked</td><td class='bad'>{uh[3]}</td><td class='good'>{gh[3]}</td></tr><tr><td>Decisions with no audit trail (silent drops)</td><td class='bad'>{uh[4]}</td><td class='good'>{gh[4]}</td></tr></table>
<h2>1. Same events, two twins</h2><p class='note'>Red = real harm (legitimate message lost, scam delivered, health data offshore) · green = correct outcome · amber = held for a named human · grey = scam dropped silently, without audit.</p>
<table><tr><th>t</th><th>event</th><th>kind</th><th>UNGOVERNED</th><th>GOVERNED (HISN)</th></tr>{twin_rows}</table>
<h2>2. Institutional agents (last run)</h2><p class='note'>Agents propose; deterministic code checks evidence, mandate, binding basis, competence and consistency.</p>
<table><tr><th>t</th><th>role</th><th>event</th><th>status</th><th>proposed</th><th>cited</th><th>reason / assessment</th></tr>{agent_rows or '<tr><td colspan=7>run run_agents.py first</td></tr>'}</table>
<h2>3. Gap engine — loopholes, counterfactuals, load-bearing</h2>
<p class='note'>MIZAN = average of protection (% malicious stopped) and access (% legitimate delivered immediately). Synthetic battery; shows direction, not real-world magnitude.</p>
<ul>{loops}</ul><div class='cards'>{gap_cards}</div><ul>{lbs}</ul>
<h2>3b. Regulatory wind tunnel - test-driven regulation</h2><p class='note'>Each draft rule is tested before issuance: conflicts with verified law (hierarchy of norms), eight public-interest invariants, measured effect and UAE-India interoperability. A named human must sign off.</p><table><tr><th>draft</th><th>instrument</th><th>verdict</th><th>conflicts</th><th>invariants</th><th>MIZAN</th><th>UAE-India</th></tr>{wt_rows or '<tr><td colspan=7>run wind_tunnel.py first</td></tr>'}</table>
<h2>4a. Baselines (qwen2.5:14b, same events, pre-registered gold)</h2><table><tr><th>system</th><th>accuracy</th><th>held-out v2</th><th>harmful</th><th>out-of-mandate</th><th>unsupported citations</th><th>decisive w/o binding basis</th><th>held-out v3</th></tr>{bl_rows}</table><h2>4b. UAE-India gap coverage</h2><table><tr><th>gap</th><th>UAE</th><th>India</th><th>India clauses</th><th>note</th></tr>{io_rows}</table><h2>4c. Network evidence (Turkcell ITU challenge data, proxy)</h2><p>Relative risk of link failure: heat {nprof.get('relative_risk_hot')}, rain {nprof.get('relative_risk_rain')} ({nprof.get('n_link_days')} link-days). Heat did not raise failures; rain did.</p>
<h2>4. Evaluation (pre-registered gold)</h2><table>{ev_rows}</table>
<h2>5. Knowledge base ({len(man)} hash-pinned records · {n_clauses} verbatim clauses · ITU reference ingest pipeline)</h2>
<table><tr><th>record</th><th>title</th><th>issuer</th><th>basis</th><th>verification</th><th>sha256</th></tr>{kb_rows}</table>
<h2>6. Gap register</h2><div class='cards'>{gap_html}</div>
<h2>7. Named human sign-offs</h2><table><tr><th>at</th><th>patches</th><th>decision</th><th>officer</th><th>evidence</th></tr>{so_rows or '<tr><td colspan=5>none yet</td></tr>'}</table>
<p class='note'>Comparators are marked 'verify text' until checked against official sources. Candidate provisions are mechanisms tested in simulation, not legal drafting.</p>
</body></html>"""

import re as _re, datetime as _dt
def _hbars(rows, maxv, unit="", w=380):
    h = 28 * len(rows) + 6; o = [f"<svg viewBox='0 0 {w} {h}' width='100%' role='img'>"]
    for i, (lab, val, col) in enumerate(rows):
        y = 4 + i * 28; bw = 0 if not maxv else (w - 200) * float(val) / maxv
        o.append(f"<text x='0' y='{y+14}' font-size='11.5' fill='#5b6476'>{E(lab)}</text><rect x='160' y='{y+2}' width='{bw:.1f}' height='16' rx='5' fill='{col}'/>"
                 f"<text x='{166+bw:.1f}' y='{y+15}' font-size='11.5' font-weight='600' fill='#1a1a1a'>{val}{unit}</text>")
    o.append("</svg>"); return "".join(o)
_blf = Path("docs/baselines_14b.md") if Path("docs/baselines_14b.md").exists() else Path("docs/baselines.md")
_bl = [[c.strip() for c in l.strip("|").split("|")] for l in _blf.read_text(encoding="utf-8").splitlines() if l.startswith("| B")] if _blf.exists() else []
_acc = lambda c: round(100 * int(c[1].split("/")[0]) / int(c[1].split("/")[1]))
_col = {"B0": "#9aa3ad", "B1": "#C8102E", "B2": "#B68A35", "B3": "#00732F"}
ch_acc = _hbars([(c[0][:30], _acc(c), _col.get(c[0][:2], "#999")) for c in _bl], 100, "%")
ch_harm = _hbars([(c[0][:30], int(c[3]), _col.get(c[0][:2], "#999")) for c in _bl], max([int(c[3]) for c in _bl] + [1]))
ch_uns = _hbars([(c[0][:30], int(c[5]), _col.get(c[0][:2], "#999")) for c in _bl], max([int(c[5]) for c in _bl] + [1]))
_best = next((r for r in cfs if r["patch"] == "P-AUTH+P-VERIFIED"), None)
ch_miz = _hbars([("Protection - as-is", base["protection"], "#9aa3ad"), ("Protection - AUTH+LANE", _best["protection"] if _best else 0, "#00732F"),
                 ("Access - as-is", base["access"], "#9aa3ad"), ("Access - AUTH+LANE", _best["access"] if _best else 0, "#B68A35"),
                 ("MIZAN - as-is", base["mizan"], "#9aa3ad"), ("MIZAN - AUTH+LANE", _best["mizan"] if _best else 0, "#C8102E")], 100)
ch_twin = _hbars([("Lost - without HISN", uh[0], "#C8102E"), ("Lost - with HISN", gh[0], "#00732F"),
                  ("Offshore - without", uh[3], "#C8102E"), ("Offshore - with HISN", gh[3], "#00732F"),
                  ("Unaudited - without", uh[4], "#C8102E"), ("Unaudited - with HISN", gh[4], "#00732F")], max(uh[0], uh[3], uh[4], 1))
_io = Path("docs/interoperability.md").read_text(encoding="utf-8") if Path("docs/interoperability.md").exists() else ""
_m = _re.search(r"\*\*(\d+)%\*\*", _io); _agree = (_m.group(1) + "%") if _m else "-"
_b1 = next((c for c in _bl if c[0].startswith("B1")), None); _b3 = next((c for c in _bl if c[0].startswith("B3")), None)
def _k(v, l, sub="", c=""):
    return f"<div class='kpi {c}'><div class='v'>{v}</div><div class='l'>{l}</div>" + (f"<div class='s'>{sub}</div>" if sub else "") + "</div>"
kpis = "".join([
    _k(f"{uh[0]} &rarr; {gh[0]}", "Essential health &amp; government messages silently lost", "without &rarr; with HISN", "r"),
    _k(f"{uh[3]} &rarr; {gh[3]}", "Health-data transfers offshore not blocked", "Federal Law 2/2019 Art. 13", "r"),
    _k(f"{_b1[3] if _b1 else '-'} &rarr; {_b3[3] if _b3 else '-'}", "Harmful AI decisions (ITU reference model)", "ungoverned LLM &rarr; HISN"),
    _k(f"{_b1[5] if _b1 else '-'} &rarr; {_b3[5] if _b3 else '-'}", "Unsupported legal citations", "LLM only &rarr; HISN", "k"),
    _k(f"{base['mizan']} &rarr; {_best['mizan'] if _best else '-'}", "MIZAN balance (protection + access)", "authentication + verified lane", "gold"),
    _k(f"{n_clauses}", "Verbatim legal clauses", f"{len(man)} hash-pinned records &middot; UAE, India, Singapore"),
    _k(f"{len(gaps)}", "Policy gaps identified", "1 discovered by the agents", "gold"),
    _k(_agree, "UAE&ndash;India decision agreement", "4 of 5 gaps shared", "k"),
    _k(f"{len(_cards)}", "Regulatory impact cards", "test-driven regulation", "r"),
    _k(f"{nprof.get('relative_risk_rain', '-')}&times;", "Rain-driven link-failure risk", f"heat {nprof.get('relative_risk_hot', '-')}&times; &middot; real operator data")])
charts = (f"<div class='charts'><div class='panel'><h3>Harm prevented - same events, two twins</h3>{ch_twin}</div>"
          f"<div class='panel'><h3>Accuracy vs pre-registered gold (qwen2.5:14b)</h3>{ch_acc}</div>"
          f"<div class='panel'><h3>Harmful decisions</h3>{ch_harm}</div>"
          f"<div class='panel'><h3>Unsupported legal citations</h3>{ch_uns}</div>"
          f"<div class='panel'><h3>Gap engine - measured policy effect</h3>{ch_miz}</div></div>")
_h2 = _re.findall(r"<h2>(.*?)</h2>", doc)
for i, t in enumerate(_h2): doc = doc.replace(f"<h2>{t}</h2>", f"<h2 id='s{i}'>{t}</h2>", 1)
nav = "".join(f"<a href='#s{i}'>{_re.sub('<[^>]+>', '', t)[:34]}</a>" for i, t in enumerate(_h2))
hero = ("<div class='top'></div><header class='hero'><div class='in'><h1>HISN <span class='ar'>\u062d\u0635\u0646</span></h1>"
        "<p>Governance for the telecom AI that decides which health and government messages reach citizens - with test-driven regulation.</p>"
        f"<span class='tag'>ITU AI for Good Lab Hackathon &middot; UAE 2026</span><span class='tag'>Team Sankalp</span>"
        f"<span class='tag'>Synthetic data only</span><span class='tag'>Audit chains verified: {gv and uv}</span>"
        f"<span class='tag'>Generated {_dt.datetime.now():%d %b %Y %H:%M}</span></div></header>"
        "<div class='disc'>Independent hackathon prototype. Not an official government website; not affiliated with or endorsed by any UAE or Indian government entity. All senders and data are synthetic.</div>"
        f"<nav><div class='in'>{nav}</div></nav><div class='wrap'><div class='kpis'>{kpis}</div>{charts}")
doc = _re.sub(r"<h1>.*?</p>", lambda _x: hero, doc, count=1, flags=_re.S)
doc = doc.replace("</body>", "</div><footer>HISN &middot; Team Sankalp &middot; Every figure traces to docs/headline_numbers.md &middot; Comparators marked verify-text until checked against official sources.</footer></body>")

Path("docs").mkdir(exist_ok=True)
Path("docs/dashboard.html").write_text(doc, encoding="utf-8")
print(f"written docs/dashboard.html | twin rows {len(grows)} | agent decisions {len(rat)} | patches {len(cfs)} | records {len(man)}")
