import importlib, json

def test_console_run_shows_chain_receipts_and_signed_enforcement():
    c = importlib.import_module("console")
    d = c.run({"injects": ["critical_lab"]})
    assert d["silently_lost"]["hisn"] == 0 and d["silently_lost"]["ungoverned"] > 0 and all(d["verified"])
    rec = [r["receipt"] for r in d["rows"] if r["receipt"]]
    assert rec and "Health Authority" in rec[0]["en"] and "الجهة الصحية" in rec[0]["ar"]
    e = c.run({"enforce": True})
    assert {a["reason"] for a in e["approvals"]} == {"no_signed_approval_record"}
    held = [r for r in e["rows"] if r["kind"] == "filter_policy"]
    assert all("HELD_FOR_APPROVAL" in r["hisn"]["filter"] for r in held)
