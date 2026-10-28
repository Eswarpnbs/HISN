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

CSS = """body{font-family:-apple-system,Segoe UI,Arial,sans-serif;margin:24px;color:#1d2433;background:#f7f8fa}
h1{margin:0}h2{margin-top:36px;border-bottom:2px solid #d9dee7;padding-bottom:6px}.sub{color:#5b6476}
table{border-collapse:collapse;width:100%;background:#fff;font-size:13px}td,th{border:1px solid #e3e7ee;padding:6px;text-align:left;vertical-align:top}
th{background:#eef1f6}.bad{background:#fde2e1}.warn{background:#fff3cd}.good{background:#dff3e4}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}
.card{background:#fff;border:1px solid #e3e7ee;border-radius:8px;padding:12px}.card h4{margin:0 0 8px}
.bar{display:flex;align-items:center;gap:8px;font-size:12px;margin:3px 0}.bar span{width:72px}
.track{flex:1;background:#eef1f6;height:10px;border-radius:5px}.fill{height:10px;border-radius:5px}
.muted{background:#eceff3;color:#5b6476}.p{background:#3b6fd8}.a{background:#2e9e63}.m{background:#8a4fd8}code{font-size:12px}.note{font-size:12px;color:#5b6476}"""

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
<h2>4a. Baselines (qwen2.5:14b, same events, pre-registered gold)</h2><table><tr><th>system</th><th>accuracy</th><th>held-out v2</th><th>harmful</th><th>out-of-mandate</th><th>unsupported citations</th><th>decisive w/o binding basis</th></tr>{bl_rows}</table><h2>4b. UAE-India gap coverage</h2><table><tr><th>gap</th><th>UAE</th><th>India</th><th>India clauses</th><th>note</th></tr>{io_rows}</table><h2>4c. Network evidence (Turkcell ITU challenge data, proxy)</h2><p>Relative risk of link failure: heat {nprof.get('relative_risk_hot')}, rain {nprof.get('relative_risk_rain')} ({nprof.get('n_link_days')} link-days). Heat did not raise failures; rain did.</p>
<h2>4. Evaluation (pre-registered gold)</h2><table>{ev_rows}</table>
<h2>5. Knowledge base ({len(man)} hash-pinned records · {n_clauses} verbatim clauses · ITU reference ingest pipeline)</h2>
<table><tr><th>record</th><th>title</th><th>issuer</th><th>basis</th><th>verification</th><th>sha256</th></tr>{kb_rows}</table>
<h2>6. Gap register</h2><div class='cards'>{gap_html}</div>
<h2>7. Named human sign-offs</h2><table><tr><th>at</th><th>patches</th><th>decision</th><th>officer</th><th>evidence</th></tr>{so_rows or '<tr><td colspan=5>none yet</td></tr>'}</table>
<p class='note'>Comparators are marked 'verify text' until checked against official sources. Candidate provisions are mechanisms tested in simulation, not legal drafting.</p>
</body></html>"""
Path("docs").mkdir(exist_ok=True)
Path("docs/dashboard.html").write_text(doc, encoding="utf-8")
print(f"written docs/dashboard.html | twin rows {len(grows)} | agent decisions {len(rat)} | patches {len(cfs)} | records {len(man)}")
