"""HISN live chain console (judges' screen). Standard library only; runs offline.

    python console.py            # then open http://127.0.0.1:8765

Pick injects or type a custom SMS, choose whether Y.3173 levels are enforced (signed approvals), and run.
Each event is shown along the chain: sender/citizen -> operator AI filter -> institution -> law -> standards,
for the ungoverned twin and for HISN side by side. Held essential messages get a receipt in English and Arabic.
Deterministic layer only (no language model needed); agents are run with run_agents.py.
"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from app.core.audit import AuditLog
from app.core.gateway import PolicyGateway
from app.core.firewall import SmsFirewall
from app.core.coordinator import Coordinator, load_scenario
from app.core.events import Event
from app.core.injects import available, load_injects
from app.core.tiers import Tiers
from app.receipts import render

SC, REG, PACK = "scenarios/crisis_exploit.yaml", "kb/rulepacks/uae/senders.yaml", "kb/rulepacks/uae/rules.yaml"
TIERS = Tiers()
Path("runs").mkdir(exist_ok=True)

def run_once(governed, extra, enforce):
    p = Path(f"runs/console_web_{'gov' if governed else 'ungov'}.jsonl")
    if p.exists(): p.unlink()
    a = AuditLog(p)
    out = Coordinator(SC, a, SmsFirewall(REG, a, governed=governed), PolicyGateway(PACK, a) if governed else None,
                      extra_events=extra, enforce_levels=enforce and governed,
                      approval_mode="signed" if enforce else "name").run()
    return {o["event_id"]: o for o in out}, a.verify(), p

def chain(o, payload):
    act = o.get("action", "")
    stage = {"citizen": payload.get("source_addr") or payload.get("destination_country") or "", "filter": "",
             "institution": "", "law": "", "standards": ""}
    if o.get("kind") == "sms_submit":
        stage["filter"] = act + (" (silent drop)" if o.get("silent_drop") else "")
        if o.get("escalate_to"): stage["institution"] = "held for " + o["escalate_to"]
    elif o.get("kind") == "filter_policy":
        stage["filter"] = f"threshold change -> {act}"
        if o.get("automation_violation"): stage["standards"] = "Y.3173: demand mapping is Human; no valid approval"
        if act == "HELD_FOR_APPROVAL": stage["standards"] += " -> change held"
    elif o.get("kind") == "data_transfer":
        stage["law"] = act + (f" [{o['rule_id']}]" if o.get("rule_id") else " (no policy node)")
    else:
        stage["institution"] = act
    return stage

def receipt_for(o, payload, hashes):
    if o.get("action") != "QUARANTINE": return None
    tier, _ = TIERS.classify(payload)
    rec = {"receipted_message_id": o["event_id"], "reason": f"HELD tier {tier} -> {o.get('escalate_to') or 'reviewer'}",
           "review_by_minutes": TIERS.max_hold(tier), "call_patient_after_minutes": TIERS.receipt_after(tier),
           "audit_hash": hashes.get(o["event_id"], "")}
    return {"en": render(rec, "en")["text"], "ar": render(rec, "ar")["text"]}

def run(body):
    extra = load_injects(body.get("injects") or [])
    c = body.get("custom") or {}
    if c.get("sender") and c.get("text"):
        extra.append(Event(id="JUDGE-1", t=55, kind="sms_submit", audience=("filter_ai",), act=3,
                           payload={"source_addr": c["sender"], "short_message": c["text"],
                                    "route": c.get("route") or "local", "authenticated": bool(c.get("authenticated"))}))
    enforce = bool(body.get("enforce"))
    (g, gv, gp), (u, uv, _) = run_once(True, extra, enforce), run_once(False, extra, enforce)
    _, base = load_scenario(SC)
    payloads = {e.id: e.payload for e in list(base) + extra}
    hashes = {}
    for line in gp.read_text(encoding="utf-8").splitlines():
        rec = json.loads(line)
        if rec.get("event_id") or rec.get("id"): hashes[rec.get("event_id") or rec.get("id")] = rec.get("hash", "")
    rows = []
    for eid in sorted(g, key=lambda i: g[i]["t"]):
        pl = payloads.get(eid, {})
        rows.append({"t": g[eid]["t"], "id": eid, "kind": g[eid]["kind"], "injected": eid in {e.id for e in extra},
                     "ungoverned": chain(u[eid], pl), "hisn": chain(g[eid], pl), "receipt": receipt_for(g[eid], pl, hashes)})
    lost = lambda d: sum(1 for o in d.values() if o.get("silent_drop"))
    approvals = [json.loads(l) for l in gp.read_text(encoding="utf-8").splitlines() if '"approval_check"' in l]
    return {"rows": rows, "verified": [gv, uv], "silently_lost": {"ungoverned": lost(u), "hisn": lost(g)},
            "approvals": approvals, "enforce": enforce}

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HISN live chain</title><style>
:root{--bg:#f7f7f5;--fg:#1d1d1b;--mut:#6b6b66;--card:#fff;--line:#e2e2dc;--ok:#1d7a4a;--bad:#b3261e;--acc:#0b5e7a}
@media (prefers-color-scheme:dark){:root{--bg:#141413;--fg:#ecece8;--mut:#a3a39b;--card:#1e1e1c;--line:#33332f;--ok:#5cc28e;--bad:#f2867d;--acc:#6cc3e0}}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,sans-serif}
header{padding:16px 20px;border-bottom:1px solid var(--line)}h1{margin:0;font-size:20px}header p{margin:4px 0 0;color:var(--mut)}
main{padding:16px 20px;max-width:1300px}fieldset{border:1px solid var(--line);border-radius:8px;margin:0 0 12px;padding:10px 12px;background:var(--card)}
label{margin-right:12px;white-space:nowrap}input[type=text]{padding:5px;border:1px solid var(--line);border-radius:5px;background:var(--bg);color:var(--fg)}
button{background:var(--acc);color:#fff;border:0;border-radius:6px;padding:8px 16px;font-weight:600;cursor:pointer}
.kpi{display:flex;gap:12px;flex-wrap:wrap;margin:12px 0}.kpi div{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 14px}
.kpi b{font-size:20px;display:block}table{width:100%;border-collapse:collapse;background:var(--card);font-size:12.5px}
th,td{border-bottom:1px solid var(--line);padding:6px;text-align:left;vertical-align:top}th{position:sticky;top:0;background:var(--card)}
.inj{background:rgba(11,94,122,.08)}.bad{color:var(--bad);font-weight:600}.ok{color:var(--ok);font-weight:600}
.rc{font-size:12px;color:var(--mut);margin-top:4px}.ar{direction:rtl;text-align:right;font-family:'Noto Naskh Arabic',serif}
.wrap{overflow-x:auto}</style></head><body>
<header><h1>HISN: the law layer and last mile</h1><p>Same events, ungoverned twin vs HISN, along the chain citizen &rarr; operator AI &rarr; institution &rarr; law &rarr; standards. Synthetic data.</p></header>
<main><fieldset><legend>Inject events</legend><div id="inj"></div></fieldset>
<fieldset><legend>Or type your own SMS (arrives at minute 55, after the filter is tightened)</legend>
<label>Sender <input type="text" id="snd" value="H0SPITAL-A" size="14"></label>
<label>Text <input type="text" id="txt" size="50" value="Your bill is unpaid. Pay now at http://h0spital-pay.example"></label>
<label><input type="checkbox" id="auth"> authenticated sender</label></fieldset>
<fieldset><label><input type="checkbox" id="enf"> Enforce ITU-T Y.3173 levels (only signed approvals unlock filter changes)</label>
<button onclick="go()">Run</button></fieldset>
<div class="kpi" id="kpi"></div><div class="wrap"><table id="tb"></table></div></main>
<script>
const esc=s=>String(s??'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
fetch('/api/injects').then(r=>r.json()).then(l=>{document.getElementById('inj').innerHTML=l.map(n=>`<label><input type=checkbox value="${n}"> ${n}</label>`).join('')});
function cell(s){const c=['filter','institution','law','standards'].map(k=>s[k]).filter(Boolean).join(' · ');
 const cls=/silent drop|ALLOW \\(no policy|APPLIED/.test(c)&&!/HELD/.test(c)?'bad':/QUARANTINE|BLOCK_PROHIBITED|held/i.test(c)?'ok':'';return `<span class="${cls}">${esc(c)}</span>`}
async function go(){const inj=[...document.querySelectorAll('#inj input:checked')].map(i=>i.value);
 const body={injects:inj,enforce:document.getElementById('enf').checked,custom:{sender:document.getElementById('snd').value,text:document.getElementById('txt').value,authenticated:document.getElementById('auth').checked}};
 const d=await (await fetch('/api/run',{method:'POST',body:JSON.stringify(body)})).json();
 document.getElementById('kpi').innerHTML=`<div>Essential messages silently lost<b><span class="bad">${d.silently_lost.ungoverned}</span> &rarr; <span class="ok">${d.silently_lost.hisn}</span></b></div><div>Audit chains verified<b>${d.verified.join(' / ')}</b></div><div>Y.3173 enforcement<b>${d.enforce?'on (signed)':'off'}</b></div>`+(d.approvals.length?`<div>Approval checks<b>${d.approvals.map(a=>esc(a.result+': '+a.reason)).join('<br>')}</b></div>`:'');
 document.getElementById('tb').innerHTML='<tr><th>t</th><th>event</th><th>sender / data</th><th>Ungoverned</th><th>HISN</th></tr>'+d.rows.map(r=>`<tr class="${r.injected?'inj':''}"><td>${r.t}</td><td>${esc(r.id)}<br><small>${esc(r.kind)}</small></td><td>${esc(r.hisn.citizen)}</td><td>${cell(r.ungoverned)}</td><td>${cell(r.hisn)}${r.receipt?`<div class="rc">${esc(r.receipt.en)}</div><div class="rc ar" lang="ar">${esc(r.receipt.ar)}</div>`:''}</td></tr>`).join('')}
</script></body></html>"""

class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        b = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code); self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.path == "/": self._send(200, PAGE, "text/html")
        elif self.path == "/api/injects": self._send(200, json.dumps(available()))
        else: self._send(404, "{}")
    def do_POST(self):
        if self.path != "/api/run": return self._send(404, "{}")
        n = int(self.headers.get("Content-Length", 0))
        try:
            self._send(200, json.dumps(run(json.loads(self.rfile.read(n) or b"{}")), ensure_ascii=False, default=str))
        except Exception as ex:
            self._send(400, json.dumps({"error": str(ex)}))
    def log_message(self, *a): pass

if __name__ == "__main__":
    print("HISN live chain console: http://127.0.0.1:8765  (Ctrl+C to stop)")
    ThreadingHTTPServer(("127.0.0.1", 8765), H).serve_forever()
