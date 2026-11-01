"""Cross-border essential message (gap G7): does essential-sender recognition survive a border?
Origin (India): legal status from the verified TRAI Government Message clause (a legal finding, not a simulation).
Destination (UAE): the same message run through HISN's UAE firewall, against a registered domestic sender, under
three conditions. Models a person on a UAE number reached via an international A2P route (roaming not modelled).
Synthetic, fictional senders."""
import copy, csv, sys, yaml
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core.audit import AuditLog
from app.core.firewall import SmsFirewall
from app.core.packs import pack

FOREIGN = "IN-HLTHGV-G"   # fictional Indian government health sender with the -G suffix

def run(log=Path("runs/cross_border.jsonl")):
    from app.core.injects import load_injects, available
    g = lambda e, k: e.get(k) if isinstance(e, dict) else getattr(e, k, None)
    ev = next(e for e in load_injects(available()) if g(e, "id") == "INJ-CRITLAB")
    base = {"id": g(ev, "id"), "payload": g(ev, "payload")}
    domestic = copy.deepcopy(base["payload"])
    foreign = copy.deepcopy(base["payload"]); foreign.update({"source_addr": FOREIGN, "route": "foreign_aggregator"})
    if "authenticated" in foreign: foreign["authenticated"] = False
    log.parent.mkdir(exist_ok=True); log.unlink(missing_ok=True); a = AuditLog(log)
    p = pack("UAE")
    adopted = yaml.safe_load(open("kb/rulepacks/uae/adopted.yaml", encoding="utf-8"))["flags"]
    rows = []
    for label, flags, thr in [("Current rules, normal day", p["firewall_flags"], None),
                              ("Current rules, after the panic threshold (0.20)", p["firewall_flags"], 0.2),
                              ("Tested rule set, after the panic threshold (0.20)", adopted, 0.2)]:
        res = {}
        for who, m in (("domestic", domestic), ("foreign", foreign)):
            fw = SmsFirewall(p["senders"], a, policy=flags)
            if thr is not None: fw.set_threshold(thr, "cross-border what-if")
            o = fw.process(copy.deepcopy(m), now=0) or {}
            res[who] = o.get("action", "?")
        rows.append({"condition": label, **res})
    gap = any(r["domestic"] == "ALLOW" and r["foreign"] != "ALLOW" for r in rows)
    a.write({"kind": "cross_border_finding", "gap": "G7", "foreign_sender": FOREIGN, "rows": rows, "gap_shown": gap})
    return {"rows": rows, "gap_shown": gap, "audit_ok": a.verify(), "base_event": base["id"]}

def main():
    r = run()
    CL = {c["clause_id"]: c for c in yaml.safe_load(open("kb/clauses/clauses.yaml", encoding="utf-8"))}
    URL = {m["record_id"]: m["url"] for m in csv.DictReader(open("kb/manifest.csv", encoding="utf-8"))}
    def cite(cid):
        c = CL[cid]; return f"**{cid}** ({c.get('article', '')}), [official source]({URL.get(c['record_id'], '')})"
    L = ["# Cross-border essential message (gap G7)", "",
         "_Does essential-sender recognition survive a border? Realistic senders: a home-country public-health authority or an embassy reaching its nationals on local numbers (how often this happens is not documented). Synthetic, fictional senders; a person on a UAE number reached through an "
         "international A2P route (roaming not modelled). Domain-level finding, not a national recommendation._", "",
         "## At the origin (India): a legal finding",
         f"A government message is sent only via DLT and is identifiable by its -G header suffix: {cite('IN-TRAI-GOVMSG')}. "
         "This protects it from customer opt-outs (the Preference Register); protection from operator AI filtering is not addressed.", "",
         "## At the destination (UAE): measured in HISN's UAE firewall",
         f"The only sender-identity rule is the marketing label: {cite('UAE-TDRA-UEC-8.8')}. The same critical message ({r['base_event']}) "
         f"was run from the registered domestic hospital and from the Indian essential sender `{FOREIGN}`. Note that a genuine foreign "
         "essential sender arrives the same way as a spoofed one (foreign route, unauthenticated, unknown to the registry):", "",
         "| Condition | Domestic registered hospital | Indian essential sender |", "|---|---|---|"]
    L += [f"| {x['condition']} | {x['domestic']} | **{x['foreign']}** |" for x in r["rows"]]
    L += ["", "## Finding",
          ("Recognition stops at the border: under conditions where the domestic essential sender is delivered, the foreign essential sender is not. "
           "Sender authentication fixes this only for senders the destination country knows; essential messages need recognition across borders."
           if r["gap_shown"] else "In this run the foreign and domestic senders were treated alike; no cross-border gap was shown."),
          *(["After the panic threshold, the foreign message is blocked outright while the domestic one is held for a human to review."]
            if any(x["domestic"] == "QUARANTINE" and str(x["foreign"]).startswith("BLOCK") for x in r["rows"]) else []),
          "", "Global example (partial): Singapore's Sender ID Registry admits overseas senders only through a Singapore-registered entity, and its "
          "operator states the protection applies to Singapore mobile numbers only ([IMDA](https://www.imda.gov.sg/How-We-Can-Help/Anti-Scam-Measures), "
          "[SGNIC FAQ](https://www.sgnic.sg/faq/sms-sender-id-registry)). Protection is national by design; no mutual recognition was found.",
          "", f"_Audit chain verified: {r['audit_ok']}. Generated by tools/cross_border.py._"]
    Path("docs/cross_border.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L)); print("\nwritten docs/cross_border.md")

if __name__ == "__main__":
    main()
