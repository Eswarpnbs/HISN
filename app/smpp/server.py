"""HISN SMPP 3.4 listener: real network server in front of the governed firewall. Message text is never logged.
Held messages produce an accountable delivery receipt (deliver_sm) when the sender requests one."""
import asyncio, itertools, struct
from app.core.tiers import Tiers
from .protocol import (BIND_IDS, SUBMIT_SM, ENQUIRE_LINK, UNBIND, GENERIC_NACK, DELIVER_SM, DELIVER_SM_RESP,
                       ROK, RINVCMDID, RINVBNDSTS, RBINDFAIL, RSUBMITFAIL, PRIORITY_TO_FHIR,
                       pdu, cstr, parse_submit, parse_receipt, receipt_pdu)

class HisnSmppServer:
    def __init__(self, firewall, accounts, audit, tiers=None):
        self.fw, self.accounts, self.audit, self.ids = firewall, accounts, audit, itertools.count(1)
        self.tiers, self.rseq = tiers or Tiers(), itertools.count(1)

    async def handle(self, reader, writer):
        bound, mode = None, None
        try:
            while True:
                length, cmd, _, seq = struct.unpack(">IIII", await reader.readexactly(16))
                body = await reader.readexactly(length - 16) if length > 16 else b""
                if cmd in BIND_IDS:
                    sid, i = cstr(body, 0); pw, _ = cstr(body, i)
                    acc = self.accounts.get(sid)
                    ok = acc is not None and acc.get("password") == pw
                    bound = (sid, acc) if ok else None
                    mode = BIND_IDS[cmd] if ok else None   # receiver | transmitter | transceiver
                    self.audit.write({"kind": "smpp_bind", "esme": sid, "ok": ok})
                    writer.write(pdu(cmd | 0x80000000, ROK if ok else RBINDFAIL, seq, b"HISN\x00" if ok else b"\x00"))
                elif cmd == SUBMIT_SM:
                    if not bound:
                        writer.write(pdu(SUBMIT_SM | 0x80000000, RINVBNDSTS, seq, b"\x00"))
                    else:
                        sid, acc = bound
                        m = parse_submit(body)
                        msg = {"source_addr": m["source_addr"], "short_message": m["text"], "route": acc["route"],
                               "authenticated": m["source_addr"] in acc.get("authorised_headers", []),
                               "priority": PRIORITY_TO_FHIR.get(m["priority_flag"])}
                        r = self.fw.process(msg)
                        if r["action"] == "ALLOW": mid, st = f"H{next(self.ids)}", ROK
                        elif r["action"] == "QUARANTINE": mid, st = f"Q{next(self.ids)}", ROK
                        else: mid, st = "", RSUBMITFAIL
                        tier, why = self.tiers.classify(msg) if r["action"] == "QUARANTINE" else (None, None)
                        h = self.audit.write({"kind": "smpp_submit", "esme": sid, "source_addr": m["source_addr"],
                                              "dest": m["destination_addr"], "data_coding": m["data_coding"],
                                              "action": r["action"], "command_status": st, "message_id": mid,
                                              "tier": tier, "tier_reason": why})
                        writer.write(pdu(SUBMIT_SM | 0x80000000, st, seq, mid.encode() + b"\x00"))
                        if r["action"] == "QUARANTINE" and m["registered_delivery"] & 0x01 and mode == "transmitter":
                            # SMPP 3.4: deliver_sm goes only to a receiver or transceiver session, never a transmitter.
                            # The receipt is still recorded, to be fetched by the sender's receiver bind.
                            self.audit.write({"kind": "smpp_receipt_pending", "message_id": mid,
                                              "reason": "transmitter_bind_cannot_receive_deliver_sm"})
                        elif r["action"] == "QUARANTINE" and m["registered_delivery"] & 0x01:
                            to = r.get("escalate_to") or "reviewer"
                            review, call = self.tiers.max_hold(tier), self.tiers.receipt_after(tier)
                            writer.write(receipt_pdu(next(self.rseq), mid, m["source_addr"], m["destination_addr"],
                                                     f"HELD tier {tier} -> {to}", review, call, h))
                            self.audit.write({"kind": "smpp_receipt", "message_id": mid, "tier": tier, "escalate_to": to,
                                              "review_by_minutes": review, "call_patient_after_minutes": call,
                                              "decision_hash": h})
                elif cmd == DELIVER_SM_RESP:
                    pass  # client acknowledged a receipt
                elif cmd == ENQUIRE_LINK:
                    writer.write(pdu(ENQUIRE_LINK | 0x80000000, ROK, seq))
                elif cmd == UNBIND:
                    writer.write(pdu(UNBIND | 0x80000000, ROK, seq)); await writer.drain(); break
                else:
                    writer.write(pdu(GENERIC_NACK, RINVCMDID, seq))
                await writer.drain()
        except (asyncio.IncompleteReadError, ConnectionError):
            pass
        finally:
            writer.close()

async def send_with_receipts(host, port, pdus):
    """SMPP client for demos/tests: send PDUs in order; acknowledge and collect any delivery receipts.
    Returns (responses, receipts). Put an enquire_link after a submit so its receipt is read before unbind."""
    reader, writer = await asyncio.open_connection(host, port)
    out, receipts = [], []
    for p in pdus:
        writer.write(p); await writer.drain()
        while True:
            length, cmd, st, seq = struct.unpack(">IIII", await reader.readexactly(16))
            body = await reader.readexactly(length - 16) if length > 16 else b""
            if cmd == DELIVER_SM:
                receipts.append(parse_receipt(body))
                try:
                    writer.write(pdu(DELIVER_SM_RESP, ROK, seq, b"\x00")); await writer.drain()
                except ConnectionError:
                    pass
                continue
            out.append((cmd, st, seq, body)); break
    writer.close()
    return out, receipts

async def send(host, port, pdus):
    """Tiny SMPP client for demos/tests: send PDUs in order, return (command_id, status, seq, body) per response."""
    return (await send_with_receipts(host, port, pdus))[0]