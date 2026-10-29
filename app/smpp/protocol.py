"""Minimal SMPP 3.4 PDU encode/decode (bind, submit_sm, deliver_sm receipts, enquire_link, unbind)."""
import struct, time

BIND_IDS = {0x00000001: "receiver", 0x00000002: "transmitter", 0x00000009: "transceiver"}
SUBMIT_SM, ENQUIRE_LINK, UNBIND, GENERIC_NACK = 0x00000004, 0x00000015, 0x00000006, 0x80000000
DELIVER_SM, DELIVER_SM_RESP = 0x00000005, 0x80000005
ROK, RINVCMDID, RINVBNDSTS, RBINDFAIL, RSUBMITFAIL = 0x00, 0x03, 0x04, 0x0D, 0x45

# Standard TLVs and SMPP message_state values
TLV_RECEIPTED_ID, TLV_MESSAGE_STATE, ENROUTE = 0x001E, 0x0427, 1
# HISN fields, in SMPP 3.4's vendor-specific TLV range (0x1400-0x3FFF)
TLV_HISN_REASON, TLV_HISN_REVIEW_BY, TLV_HISN_CALL_AFTER, TLV_HISN_AUDIT = 0x1401, 0x1402, 0x1403, 0x1404
# HISN convention: SMPP priority_flag -> FHIR priority. 0 = not declared (tier default applies).
PRIORITY_TO_FHIR = {1: "urgent", 2: "asap", 3: "stat"}

def pdu(cmd, status, seq, body=b""):
    return struct.pack(">IIII", 16 + len(body), cmd, status, seq) + body

def cstr(b, i):
    j = b.index(b"\x00", i)
    return b[i:j].decode("latin-1"), j + 1

def tlv(tag, value):
    return struct.pack(">HH", tag, len(value)) + value

def tlv_str(tag, s):
    return tlv(tag, s.encode("ascii") + b"\x00")

def parse_tlvs(b, i):
    out = {}
    while i + 4 <= len(b):
        tag, n = struct.unpack(">HH", b[i:i + 4]); out[tag] = b[i + 4:i + 4 + n]; i += 4 + n
    return out

def _parse_sm(b):
    """submit_sm and deliver_sm share this body layout."""
    i = 0
    _, i = cstr(b, i); i += 2
    src, i = cstr(b, i); i += 2
    dst, i = cstr(b, i)
    esm, pf = b[i], b[i + 2]; i += 3
    _, i = cstr(b, i); _, i = cstr(b, i)
    rd = b[i]; i += 2
    dc = b[i]; i += 2
    n = b[i]; i += 1
    raw = b[i:i + n]; i += n
    text = raw.decode("utf-16-be", errors="replace") if dc == 8 else raw.decode("latin-1")
    return {"source_addr": src, "destination_addr": dst, "data_coding": dc, "text": text,
            "esm_class": esm, "priority_flag": pf, "registered_delivery": rd}, i

def parse_submit(b):
    return _parse_sm(b)[0]

def parse_receipt(b):
    m, i = _parse_sm(b)
    t = parse_tlvs(b, i)
    s = lambda tag: t.get(tag, b"").rstrip(b"\x00").decode("ascii")
    return {"receipted_message_id": s(TLV_RECEIPTED_ID), "message_state": t.get(TLV_MESSAGE_STATE, b"\x00")[0],
            "reason": s(TLV_HISN_REASON), "review_by_minutes": s(TLV_HISN_REVIEW_BY),
            "call_patient_after_minutes": s(TLV_HISN_CALL_AFTER), "audit_hash": s(TLV_HISN_AUDIT),
            "receipt_text": m["text"]}

def bind_pdu(seq, system_id, password, cmd=0x00000009):
    body = system_id.encode() + b"\x00" + password.encode() + b"\x00" + b"\x00" + bytes([0x34, 0, 0]) + b"\x00"
    return pdu(cmd, 0, seq, body)

def submit_pdu(seq, src, dst, text, ucs2=False, priority_flag=0, registered_delivery=0):
    raw = text.encode("utf-16-be") if ucs2 else text.encode("latin-1")
    body = (b"\x00" + bytes([5, 0]) + src.encode() + b"\x00" + bytes([1, 1]) + dst.encode() + b"\x00"
            + bytes([0, 0, priority_flag]) + b"\x00" + b"\x00" + bytes([registered_delivery, 0])
            + bytes([8 if ucs2 else 0, 0]) + bytes([len(raw)]) + raw)
    return pdu(SUBMIT_SM, 0, seq, body)

def receipt_pdu(seq, msg_id, orig_src, orig_dst, reason, review_by, call_after, audit_hash):
    """Delivery receipt for a HELD message. Never echoes message text."""
    ts = time.strftime("%y%m%d%H%M")
    txt = f"id:{msg_id} sub:001 dlvrd:000 submit date:{ts} done date:{ts} stat:ENROUTE err:000 text:".encode("ascii")
    body = (b"\x00" + bytes([1, 1]) + orig_dst.encode() + b"\x00" + bytes([5, 0]) + orig_src.encode() + b"\x00"
            + bytes([0x04, 0, 0]) + b"\x00" + b"\x00" + bytes([0, 0]) + bytes([0, 0]) + bytes([len(txt)]) + txt
            + tlv_str(TLV_RECEIPTED_ID, msg_id) + tlv(TLV_MESSAGE_STATE, bytes([ENROUTE]))
            + tlv_str(TLV_HISN_REASON, reason) + tlv_str(TLV_HISN_REVIEW_BY, str(review_by))
            + tlv_str(TLV_HISN_CALL_AFTER, str(call_after)) + tlv_str(TLV_HISN_AUDIT, audit_hash))
    return pdu(DELIVER_SM, 0, seq, body)

def enquire_pdu(seq): return pdu(ENQUIRE_LINK, 0, seq)
def unbind_pdu(seq): return pdu(UNBIND, 0, seq)