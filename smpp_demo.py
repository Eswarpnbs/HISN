"""Send demo traffic to a running HISN SMPP server (python run_smpp.py in another tab)."""
import asyncio
from app.smpp.protocol import bind_pdu, submit_pdu, enquire_pdu, unbind_pdu
from app.smpp.server import send_with_receipts

# (account, password, sender ID, text, UCS-2, priority_flag, request receipt, label)
CASES = [("hospital-a-gw", "demo1", "HOSPITAL-A", "Your appointment is rescheduled to 10:00.", False, 0, False, "genuine, hospital's own gateway"),
         ("intl-agg", "demo4", "HOSPITAL-A", "Pay your lab fee at http://hospital-a-billing.example", False, 0, False, "exact spoof via international aggregator"),
         ("local-agg", "demo3", "H0SPITAL-A", "Pay the fee at http://x.example", False, 0, False, "lookalike via local aggregator"),
         ("gov-gw", "demo2", "GOV-FINES", "تم استلام دفعتك. المرجع 7781", True, 0, False, "genuine government receipt in Arabic (UCS-2)"),
         ("hospital-a-gw", "demo1", "HOSPITAL-A", "Urgent: a critical test result needs your attention. Please call your clinic today.",
          False, 3, True, "critical lab result, priority stat, receipt requested")]
STATUS = {0x00: "OK", 0x45: "REJECTED (0x45 submit failed)", 0x0D: "BIND FAILED"}

async def main():
    for sid, pw, src, text, ucs2, prio, rcpt, label in CASES:
        out, receipts = await send_with_receipts("127.0.0.1", 2775, [
            bind_pdu(1, sid, pw),
            submit_pdu(2, src, "TESTDEST", text, ucs2, priority_flag=prio, registered_delivery=1 if rcpt else 0),
            enquire_pdu(3), unbind_pdu(4)])
        st, mid = out[1][1], out[1][3].rstrip(b"\x00").decode()
        kind = "delivered" if mid.startswith("H") else "held for a human" if mid.startswith("Q") else "not delivered"
        print(f"{label:<54} -> {STATUS.get(st, hex(st)):<28} message_id={mid or '-':<5} ({kind})")
        for r in receipts:
            print(f"{'':<8}RECEIPT to sender: {r['reason']} | review within {r['review_by_minutes']} min"
                  f" | call the patient after {r['call_patient_after_minutes']} min | audit {r['audit_hash'][:12]}...")
asyncio.run(main())