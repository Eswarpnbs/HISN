"""Run HISN as an SMPP 3.4 server.  Usage: python run_smpp.py [--port 2775] [--policy adopted|none]"""
import argparse, asyncio, yaml
from pathlib import Path
from app.core.audit import AuditLog
from app.core.firewall import SmsFirewall
from app.smpp.server import HisnSmppServer

ap = argparse.ArgumentParser(); ap.add_argument("--port", type=int, default=2775); ap.add_argument("--policy", default="adopted"); ap.add_argument("--panic", action="store_true", help="apply the Act 3 post-panic filter threshold")
a = ap.parse_args()
flags = yaml.safe_load(open("kb/rulepacks/uae/adopted.yaml"))["flags"] if a.policy == "adopted" and Path("kb/rulepacks/uae/adopted.yaml").exists() else {}
audit = AuditLog(Path("runs/smpp.jsonl"))
fw = SmsFirewall("kb/rulepacks/uae/senders.yaml", audit, governed=True, policy=flags)
if ap.parse_args().panic:
    import yaml
    _thr = next(e for e in yaml.safe_load(open("scenarios/crisis_exploit.yaml", encoding="utf-8"))["events"]
                if e["id"] == "A3-E1")["payload"]["threshold"]
    fw.set_threshold(_thr, "demo: operator tightens the filter after the scam wave (Act 3)")
    print(f"PANIC MODE: filter threshold tightened to {_thr}")
srv = HisnSmppServer(fw, yaml.safe_load(open("kb/rulepacks/uae/esme_accounts.yaml")), audit)

async def main():
    server = await asyncio.start_server(srv.handle, "127.0.0.1", a.port)
    print(f"HISN SMPP 3.4 listening on 127.0.0.1:{a.port} | firewall policy: {flags or 'UAE pack as-is'} | Ctrl+C to stop")
    async with server: await server.serve_forever()
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nHISN SMPP server stopped.")
