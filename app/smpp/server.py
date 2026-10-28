"""HISN SMPP 3.4 listener: real network server in front of the governed firewall. Message text is never logged."""
import asyncio, itertools, struct
from .protocol import (BIND_IDS, SUBMIT_SM, ENQUIRE_LINK, UNBIND, GENERIC_NACK,
                       ROK, RINVCMDID, RINVBNDSTS, RBINDFAIL, RSUBMITFAIL, pdu, cstr, parse_submit)

class HisnSmppServer:
    def __init__(self, firewall, accounts, audit):
        self.fw, self.accounts, self.audit, self.ids = firewall, accounts, audit, itertools.count(1)

    async def handle(self, reader, writer):
        bound = None
        try:
            while True:
                length, cmd, _, seq = struct.unpack(">IIII", await reader.readexactly(16))
                body = await reader.readexactly(length - 16) if length > 16 else b""
                if cmd in BIND_IDS:
                    sid, i = cstr(body, 0); pw, _ = cstr(body, i)
                    acc = self.accounts.get(sid)
                    ok = acc is not None and acc.get("password") == pw
                    bound = (sid, acc) if ok else None
                    self.audit.write({"kind": "smpp_bind", "esme": sid, "ok": ok})
                    writer.write(pdu(cmd | 0x80000000, ROK if ok else RBINDFAIL, seq, b"HISN\x00" if ok else b"\x00"))
                elif cmd == SUBMIT_SM:
                    if not bound:
                        writer.write(pdu(SUBMIT_SM | 0x80000000, RINVBNDSTS, seq, b"\x00"))
                    else:
                        sid, acc = bound
                        m = parse_submit(body)
                        msg = {"source_addr": m["source_addr"], "short_message": m["text"], "route": acc["route"],
                               "authenticated": m["source_addr"] in acc.get("authorised_headers", [])}
                        r = self.fw.process(msg)
                        if r["action"] == "ALLOW": mid, st = f"H{next(self.ids)}", ROK
                        elif r["action"] == "QUARANTINE": mid, st = f"Q{next(self.ids)}", ROK
                        else: mid, st = "", RSUBMITFAIL
                        self.audit.write({"kind": "smpp_submit", "esme": sid, "source_addr": m["source_addr"],
                                          "dest": m["destination_addr"], "data_coding": m["data_coding"],
                                          "action": r["action"], "command_status": st, "message_id": mid})
                        writer.write(pdu(SUBMIT_SM | 0x80000000, st, seq, mid.encode() + b"\x00"))
                elif cmd == ENQUIRE_LINK:
                    writer.write(pdu(ENQUIRE_LINK | 0x80000000, ROK, seq))
                elif cmd == UNBIND:
                    writer.write(pdu(UNBIND | 0x80000000, ROK, seq)); await writer.drain(); break
                else:
                    writer.write(pdu(GENERIC_NACK, RINVCMDID, seq))
                await writer.drain()
        except asyncio.IncompleteReadError:
            pass
        finally:
            writer.close()

async def send(host, port, pdus):
    """Tiny SMPP client for demos/tests: send PDUs in order, return (command_id, status, seq, body) per response."""
    reader, writer = await asyncio.open_connection(host, port)
    out = []
    for p in pdus:
        writer.write(p); await writer.drain()
        length, cmd, st, seq = struct.unpack(">IIII", await reader.readexactly(16))
        out.append((cmd, st, seq, await reader.readexactly(length - 16) if length > 16 else b""))
    writer.close()
    return out
