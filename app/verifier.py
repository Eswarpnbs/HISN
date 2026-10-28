"""Citizen verifier (D11 Inclusion): 'Is this message genuine?' in 6 languages.
Verdict decided by deterministic code; templates phrase it; optional English LLM explanation is
discarded if it contradicts the verdict. Message text is never logged (data minimisation)."""
import re, yaml
from app.core.firewall import SmsFirewall, _lookalike

TEMPL = yaml.safe_load(open("kb/verifier_templates.yaml", encoding="utf-8"))
PAY = ("pay", "unpaid", "fine", "fee")
CONTRA = {"SUSPECTED_SCAM": ["genuine", "legitimate", "safe", "authentic", "trustworthy"],
          "LIKELY_GENUINE": ["scam", "fraud", "fake"],
          "UNDER_REVIEW": ["genuine", "safe", "scam", "fraud"]}

class CitizenVerifier:
    def __init__(self, registry, audit, llm=None):
        self.fw, self.audit, self.llm = SmsFirewall(registry, audit, governed=True), audit, llm

    def verdict(self, sender, text):
        ess = self.fw.essential
        m = re.search(r"https?://([^/\s]+)", text or "")
        dom = m.group(1).lower() if m else None
        pay = any(k in (text or "").lower() for k in PAY)
        if sender not in ess and any(_lookalike(sender, s) for s in ess):
            return "SUSPECTED_SCAM", ["lookalike_of_registered_sender"]
        if dom and dom not in self.fw.trusted and pay:
            return "SUSPECTED_SCAM", ["payment_request_with_unrecognised_link"]
        if sender in ess and (not dom or dom in self.fw.trusted):
            return "LIKELY_GENUINE", ["registered_sender", "no_unrecognised_link"]
        return "UNDER_REVIEW", ["could_not_confirm"]

    def check(self, sender, text, lang="en", explain=False):
        v, reasons = self.verdict(sender, text)
        if lang not in TEMPL["languages"]: lang = "en"
        t = TEMPL["languages"][lang]
        message = t[v].format(sender=sender) + " " + t["FOOTER"]
        explanation = None
        if explain and self.llm:
            try:
                out = self.llm("You explain an automated SMS check to a citizen in plain English, in two sentences. "
                               "Never change or soften the verdict. Reply JSON: {\"explanation\": \"...\"}",
                               f"Verdict: {v}. Reasons: {reasons}. Sender shown: {sender}.")
                cand = str(out.get("explanation", ""))
                if cand and not any(w in cand.lower() for w in CONTRA[v]):
                    explanation = cand
            except Exception:
                explanation = None
        self.audit.write({"kind": "citizen_verification", "sender": sender, "verdict": v, "reasons": reasons,
                          "lang": lang, "review_status": TEMPL["review"][lang], "llm_explanation_used": explanation is not None})
        return {"verdict": v, "reasons": reasons, "message": message, "explanation": explanation,
                "lang": lang, "review_status": TEMPL["review"][lang]}
