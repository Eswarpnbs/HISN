import asyncio
from app.core.audit import AuditLog
from app.core.firewall import SmsFirewall
from app.smpp.protocol import bind_pdu, submit_pdu, enquire_pdu, unbind_pdu, RSUBMITFAIL, RINVBNDSTS
from app.smpp.server import HisnSmppServer, send

REG = "kb/rulepacks/uae/senders.yaml"
ACC = {"hospital-a-gw": {"password": "p1", "route": "local", "authorised_headers": ["HOSPITAL-A"]},
       "intl-agg": {"password": "p4", "route": "foreign_aggregator", "authorised_headers": []}}

def run(tmp_path, scripts):
    async def go():
        a = AuditLog(tmp_path / "s.jsonl")
        fw = SmsFirewall(REG, a, governed=True, policy={"require_auth": True, "authenticated_bypass": True})
        server = await asyncio.start_server(HisnSmppServer(fw, ACC, a).handle, "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        out = [await send("127.0.0.1", port, s) for s in scripts]
        server.close(); await server.wait_closed()
        return out, a
    return asyncio.run(go())

def test_spoof_rejected_genuine_delivered_over_real_smpp(tmp_path):
    (spoof, genuine), a = run(tmp_path, [
        [bind_pdu(1, "intl-agg", "p4"), submit_pdu(2, "HOSPITAL-A", "TESTDEST", "Pay fee at http://x.example"), enquire_pdu(3), unbind_pdu(4)],
        [bind_pdu(1, "hospital-a-gw", "p1"), submit_pdu(2, "HOSPITAL-A", "TESTDEST", "Your appointment is rescheduled."), unbind_pdu(3)]])
    assert spoof[0][1] == 0 and spoof[1][1] == RSUBMITFAIL and spoof[2][1] == 0
    assert genuine[1][1] == 0 and genuine[1][3].startswith(b"H")
    assert a.verify() and "Pay fee" not in (tmp_path / "s.jsonl").read_text(encoding="utf-8")

def test_submit_without_bind_is_refused(tmp_path):
    (r,), _ = run(tmp_path, [[submit_pdu(1, "HOSPITAL-A", "TESTDEST", "hello")]])
    assert r[0][1] == RINVBNDSTS

def test_ucs2_arabic_is_decoded(tmp_path):
    (r,), _ = run(tmp_path, [[bind_pdu(1, "hospital-a-gw", "p1"), submit_pdu(2, "HOSPITAL-A", "TESTDEST", "موعدك غداً", ucs2=True), unbind_pdu(3)]])
    assert r[1][1] == 0
