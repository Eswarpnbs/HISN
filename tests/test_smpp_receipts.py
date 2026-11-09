import asyncio, json, yaml
from app.core.audit import AuditLog
from app.core.firewall import SmsFirewall
from app.smpp.server import HisnSmppServer, send_with_receipts
from app.smpp.protocol import bind_pdu, submit_pdu, enquire_pdu, unbind_pdu, ROK, ENROUTE

ACC = {"hospital-a-gw": {"password": "p1", "route": "local", "authorised_headers": ["HOSPITAL-A"]}}
TEXT = "Urgent: a critical test result needs your attention. Please call your clinic today."

def tightened():
    evs = yaml.safe_load(open("scenarios/crisis_exploit.yaml", encoding="utf-8"))["events"]
    return next(e for e in evs if e["id"] == "A3-E1")["payload"]["threshold"]

def session(tmp_path, pdus):
    async def go():
        audit = AuditLog(tmp_path / "a.jsonl")
        fw = SmsFirewall("kb/rulepacks/uae/senders.yaml", audit)
        fw.set_threshold(tightened(), "test: post-panic threshold")
        srv = await asyncio.start_server(HisnSmppServer(fw, ACC, audit).handle, "127.0.0.1", 0)
        port = srv.sockets[0].getsockname()[1]
        try:
            out, receipts = await send_with_receipts("127.0.0.1", port, pdus)
        finally:
            srv.close(); await srv.wait_closed()
        return out, receipts, tmp_path / "a.jsonl"
    return asyncio.run(go())

def script(priority_flag, registered_delivery):
    return [bind_pdu(1, "hospital-a-gw", "p1"),
            submit_pdu(2, "HOSPITAL-A", "TESTDEST", TEXT, priority_flag=priority_flag, registered_delivery=registered_delivery),
            enquire_pdu(3), unbind_pdu(4)]

def test_held_stat_message_gets_accountable_receipt(tmp_path):
    out, receipts, log = session(tmp_path, script(3, 1))
    sub = out[1]
    assert sub[1] == ROK and sub[3].startswith(b"Q"), "critical message should be held (QUARANTINE)"
    assert len(receipts) == 1
    r = receipts[0]
    assert r["message_state"] == ENROUTE and r["reason"].startswith("HELD tier T1")
    assert r["review_by_minutes"] == "5" and r["call_patient_after_minutes"] == "10"
    hashes = {json.loads(l)["hash"] for l in log.read_text().splitlines()}
    assert r["audit_hash"] in hashes

def test_no_receipt_unless_requested(tmp_path):
    _, receipts, _ = session(tmp_path, script(3, 0))
    assert receipts == []

def test_receipt_and_audit_never_contain_message_text(tmp_path):
    _, receipts, log = session(tmp_path, script(3, 1))
    assert "critical test result" not in str(receipts)
    assert "critical test result" not in log.read_text()
def test_no_receipt_is_pushed_to_a_transmitter_only_bind(tmp_path):
    """SMPP 3.4: deliver_sm goes only to receiver/transceiver sessions (found by the independent smpplib check)."""
    import asyncio, yaml
    from pathlib import Path
    from app.core.audit import AuditLog
    from app.core.firewall import SmsFirewall
    from app.smpp.server import HisnSmppServer, send_with_receipts
    a = AuditLog(tmp_path / "a.jsonl"); fw = SmsFirewall("kb/rulepacks/uae/senders.yaml", a, governed=True); fw.set_threshold(0.2, "t")
    accounts = {"hospital-a-gw": {"password": "p1", "route": "local", "authorised_headers": ["HOSPITAL-A"]}}
    srv = HisnSmppServer(fw, accounts, a)
    async def go():
        server = await asyncio.start_server(srv.handle, "127.0.0.1", 0); port = server.sockets[0].getsockname()[1]
        async with server:
            return await send_with_receipts("127.0.0.1", port, [bind_pdu(1, "hospital-a-gw", "p1", cmd=0x00000002),
                submit_pdu(2, "HOSPITAL-A", "TESTDEST", "Your appointment is rescheduled.", registered_delivery=1), enquire_pdu(3), unbind_pdu(4)])
    out, receipts = asyncio.run(go())
    assert receipts == [] and any('"smpp_receipt_pending"' in l for l in (tmp_path / "a.jsonl").read_text().splitlines())
