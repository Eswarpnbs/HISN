"""Run HISN as an SMPP 3.4 server.  Usage: python run_smpp.py [--port 2775] [--policy adopted|none]"""
import argparse, asyncio, yaml
from pathlib import Path
from app.core.audit import AuditLog
from app.core.firewall import SmsFirewall
from app.smpp.server import HisnSmppServer

ap = argparse.ArgumentParser(); ap.add_argument("--port", type=int, default=2775); ap.add_argument("--policy", default="adopted")
a = ap.parse_args()
flags = yaml.safe_load(open("kb/rulepacks/uae/adopted.yaml"))["flags"] if a.policy == "adopted" and Path("kb/rulepacks/uae/adopted.yaml").exists() else {}
audit = AuditLog(Path("runs/smpp.jsonl"))
fw = SmsFirewall("kb/rulepacks/uae/senders.yaml", audit, governed=True, policy=flags)
srv = HisnSmppServer(fw, yaml.safe_load(open("kb/rulepacks/uae/esme_accounts.yaml")), audit)

async def main():
    server = await asyncio.start_server(srv.handle, "127.0.0.1", a.port)
    print(f"HISN SMPP 3.4 listening on 127.0.0.1:{a.port} | firewall policy: {flags or 'UAE pack as-is'} | Ctrl+C to stop")
    async with server: await server.serve_forever()
asyncio.run(main())
