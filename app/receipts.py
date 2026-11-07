"""Plain-language receipts for a held essential message, in English and Arabic.

The SMPP receipt (app/smpp/protocol.py) carries machine fields: reason, review deadline, when to call the
patient, audit hash. This module turns those fields into text a sending institution can show or forward
to the person concerned. The decision and the numbers come from code; the template only phrases them.
Arabic templates were drafted by the team and are pending native review (status below).
"""
REVIEW = {"en": "reviewed_by_team", "ar": "team_drafted_native_review_pending"}

INSTITUTION_AR = {"health_authority": "الجهة الصحية المختصة", "tdra": "هيئة تنظيم الاتصالات والحكومة الرقمية",
                  "ai_data_authority": "الجهة الاتحادية المختصة بالذكاء الاصطناعي والبيانات", "reviewer": "مسؤول المراجعة"}
INSTITUTION_EN = {"health_authority": "the Health Authority", "tdra": "TDRA",
                  "ai_data_authority": "the Federal AI and Data Authority", "reviewer": "a named reviewer"}

TEMPLATES = {
    "en": ("Your message {mid} was not delivered yet. It was held by the operator's automated filter, not lost. "
           "It has been sent to {inst}, where a named officer must decide within {review} minutes. "
           "If there is no decision within {call} minutes, contact the recipient by phone. "
           "Record reference: {ref}."),
    "ar": ("لم تُسلَّم رسالتكم {mid} بعد. احتجزها المرشّح الآلي لدى المشغّل ولم تُفقد. "
           "أُحيلت إلى {inst}، ويجب أن يتخذ موظف مسمّى قراراً بشأنها خلال {review} دقيقة. "
           "إذا لم يصدر قرار خلال {call} دقيقة، يُرجى التواصل مع المستلم هاتفياً. "
           "رقم المرجع: {ref}."),
}

def render(receipt, lang="en"):
    """receipt: dict from protocol.parse_receipt or the smpp_receipt audit record."""
    lang = lang if lang in TEMPLATES else "en"
    reason = receipt.get("reason", "")
    inst_key = reason.split("->")[-1].strip() if "->" in reason else receipt.get("escalate_to", "reviewer")
    names = INSTITUTION_AR if lang == "ar" else INSTITUTION_EN
    ref = str(receipt.get("audit_hash") or receipt.get("decision_hash") or "")[:12]
    text = TEMPLATES[lang].format(
        mid=receipt.get("receipted_message_id") or receipt.get("message_id", ""),
        inst=names.get(inst_key, names["reviewer"]),
        review=receipt.get("review_by_minutes", "?"), call=receipt.get("call_patient_after_minutes", "?"), ref=ref)
    return {"lang": lang, "text": text, "review_status": REVIEW[lang], "direction": "rtl" if lang == "ar" else "ltr"}
