"""SMPP interoperability check with an INDEPENDENT client library (added 9 Nov 2026).

HISN's own tests talk to its SMPP server with HISN's own client code, which could share its mistakes. This check
uses smpplib (an open-source Python SMPP 3.4 client, https://github.com/python-smpplib/python-smpplib), written by
other people, to bind, submit and receive delivery receipts. It also shows that in the SMPP path a sender is
"authenticated" only because the bound account is authorised for that sender ID, not because a field says so.

    pip install smpplib
    python tools/smpp_interop_check.py          -> docs/smpp_interop.md
"""
import asyncio, socket, sys, threading, time, yaml
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core.audit import AuditLog
from app.core.firewall import SmsFirewall
from app.smpp.server import HisnSmppServer

def start_server():
    audit = AuditLog(Path("runs/smpp_interop.jsonl"))
    fw = SmsFirewall("kb/rulepacks/uae/senders.yaml", audit, governed=True)
    fw.set_threshold(0.2, "interop check: post-panic threshold (Act 3)")
    srv = HisnSmppServer(fw, yaml.safe_load(open("kb/rulepacks/uae/esme_accounts.yaml", encoding="utf-8")), audit)
    s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
    loop = asyncio.new_event_loop()
    def run():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(asyncio.start_server(srv.handle, "127.0.0.1", port))
        loop.run_forever()
    threading.Thread(target=run, daemon=True).start(); time.sleep(0.3)
    return port, audit

CASES = [  # (case, account, password, sender ID, text, expected outcome, bind mode)
    ("Genuine hospital message, authorised account", "hospital-a-gw", "demo1", "HOSPITAL-A",
     "Your appointment is rescheduled to 10:00 tomorrow.", "held + receipt (authenticated)", "transceiver"),
    ("Same sender ID from an unauthorised account", "local-agg", "demo3", "HOSPITAL-A",
     "Urgent: verify your hospital record. Reply with your ID number.", "held + receipt (NOT authenticated)", "transceiver"),
    ("Held message, sender bound as transmitter only", "hospital-a-gw", "demo1", "HOSPITAL-A",
     "Your scan is rescheduled to Monday 09:00.", "held (receipt not pushed: SMPP 3.4)", "transmitter"),
    ("Ordinary message, no risk words", "local-agg", "demo3", "SHOP-1",
     "Your order has been dispatched.", "delivered", "transceiver"),
    ("Wrong password", "gov-gw", "wrong", "GOV-FINES", "Fine reference 1 is due.", "bind refused", "transceiver"),
]

def main():
    try:
        import smpplib.client, smpplib.consts
    except ImportError:
        sys.exit("pip install smpplib")
    port, audit = start_server()
    rows = []
    for case, acc, pw, sender, text, expected, bmode in CASES:
        got = {"sent": None, "receipt": None}
        c = smpplib.client.Client("127.0.0.1", port, allow_unknown_opt_params=True)
        c.set_message_sent_handler(lambda pdu: got.__setitem__("sent", (pdu.status, getattr(pdu, "message_id", b""))))
        c.set_message_received_handler(lambda pdu: got.__setitem__("receipt", getattr(pdu, "short_message", b"")))
        c.connect()
        try:
            (c.bind_transceiver if bmode == "transceiver" else c.bind_transmitter)(system_id=acc, password=pw)
        except Exception as ex:
            rows.append((case, expected, f"bind refused ({type(ex).__name__})", "")); c.disconnect(); continue
        c.send_message(source_addr=sender, destination_addr="971500000000", short_message=text.encode(),
                       registered_delivery=1)
        c.read_once()                       # submit_sm_resp
        if got["sent"] and got["sent"][1][:1] == b"Q" and bmode == "transceiver":
            c.read_once()                   # deliver_sm receipt for a held message
        try: c.unbind()
        except Exception: pass
        c.disconnect()
        st, mid = got["sent"] or (None, b"")
        outcome = ("held" if mid[:1] == b"Q" else "delivered" if mid[:1] == b"H" else f"refused (status {st})")
        if got["receipt"]: outcome += " + receipt"
        rows.append((case, expected, outcome, (got["receipt"] or b"").decode(errors="replace")[:70]))
    ok = all(r[2].split(" (")[0].startswith(r[1].split(" (")[0]) for r in rows)
    out = ["# SMPP interoperability check (independent client library)", "",
           f"Client: smpplib (open source, not HISN code). Server: HISN SMPP 3.4 listener. Audit chain verified: {audit.verify()}. "
           f"All outcomes as expected: {ok}. Produced by `python tools/smpp_interop_check.py`. HISN's receipt carries vendor-specific "
           "optional parameters (tags 0x1401-0x1404, inside the range SMPP 3.4 reserves for vendors), which smpplib skips as unknown.", "",
           "| Case | Expected | Outcome via smpplib | Receipt text (start) |", "|---|---|---|---|"] + \
          [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows]
    Path("docs/smpp_interop.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))

if __name__ == "__main__":
    main()
