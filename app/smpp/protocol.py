"""Minimal SMPP 3.4 PDU encode/decode (bind, submit_sm, enquire_link, unbind)."""
import struct

BIND_IDS = {0x00000001: "receiver", 0x00000002: "transmitter", 0x00000009: "transceiver"}
SUBMIT_SM, ENQUIRE_LINK, UNBIND, GENERIC_NACK = 0x00000004, 0x00000015, 0x00000006, 0x80000000
ROK, RINVCMDID, RINVBNDSTS, RBINDFAIL, RSUBMITFAIL = 0x00, 0x03, 0x04, 0x0D, 0x45

def pdu(cmd, status, seq, body=b""):
    return struct.pack(">IIII", 16 + len(body), cmd, status, seq) + body

def cstr(b, i):
    j = b.index(b"\x00", i)
    return b[i:j].decode("latin-1"), j + 1

def parse_submit(b):
    i = 0
    _, i = cstr(b, i); i += 2
    src, i = cstr(b, i); i += 2
    dst, i = cstr(b, i); i += 3
    _, i = cstr(b, i); _, i = cstr(b, i); i += 2
    dc = b[i]; i += 2
    n = b[i]; i += 1
    raw = b[i:i + n]
    text = raw.decode("utf-16-be", errors="replace") if dc == 8 else raw.decode("latin-1")
    return {"source_addr": src, "destination_addr": dst, "data_coding": dc, "text": text}

def bind_pdu(seq, system_id, password, cmd=0x00000009):
    body = system_id.encode() + b"\x00" + password.encode() + b"\x00" + b"\x00" + bytes([0x34, 0, 0]) + b"\x00"
    return pdu(cmd, 0, seq, body)

def submit_pdu(seq, src, dst, text, ucs2=False):
    raw = text.encode("utf-16-be") if ucs2 else text.encode("latin-1")
    body = (b"\x00" + bytes([5, 0]) + src.encode() + b"\x00" + bytes([1, 1]) + dst.encode() + b"\x00"
            + bytes([0, 0, 0]) + b"\x00" + b"\x00" + bytes([0, 0]) + bytes([8 if ucs2 else 0, 0])
            + bytes([len(raw)]) + raw)
    return pdu(SUBMIT_SM, 0, seq, body)

def enquire_pdu(seq): return pdu(ENQUIRE_LINK, 0, seq)
def unbind_pdu(seq): return pdu(UNBIND, 0, seq)
