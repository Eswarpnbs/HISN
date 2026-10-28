"""Send demo traffic to a running HISN SMPP server (python run_smpp.py in another tab)."""
import asyncio
from app.smpp.protocol import bind_pdu, submit_pdu, unbind_pdu
from app.smpp.server import send

CASES = [("hospital-a-gw", "demo1", "HOSPITAL-A", "Your appointment is rescheduled to 10:00.", False, "genuine, hospital's own gateway"),
         ("intl-agg", "demo4", "HOSPITAL-A", "Pay your lab fee at http://hospital-a-billing.example", False, "exact spoof via international aggregator"),
         ("local-agg", "demo3", "H0SPITAL-A", "Pay the fee at http://x.example", False, "lookalike via local aggregator"),
         ("gov-gw", "demo2", "GOV-FINES", "تم استلام دفعتك. المرجع 7781", True, "genuine government receipt in Arabic (UCS-2)")]
STATUS = {0x00: "OK", 0x45: "REJECTED (0x45 submit failed)", 0x0D: "BIND FAILED"}

async def main():
    for sid, pw, src, text, ucs2, label in CASES:
        r = await send("127.0.0.1", 2775, [bind_pdu(1, sid, pw), submit_pdu(2, src, "TESTDEST", text, ucs2), unbind_pdu(3)])
        st, mid = r[1][1], r[1][3].rstrip(b"\x00").decode()
        kind = "delivered" if mid.startswith("H") else "held for a human" if mid.startswith("Q") else "not delivered"
        print(f"{label:<46} -> {STATUS.get(st, hex(st)):<28} message_id={mid or '-':<5} ({kind})")
asyncio.run(main())
