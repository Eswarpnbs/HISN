"""Deterministic message signals given to the institutional agents as FACTS (added 8 Nov 2026, after held-out v6).

Held-out v6 showed the model mixing two separate questions: WHO sent a message (identity) and WHAT the message asks
the citizen to do (content). Genuine, authenticated government messages that said "pay" or "verify" were held as if
they were scams. These signals separate the two. They are plain, auditable text patterns, not model judgement, and
they never decide anything themselves: the model still proposes and the fixed gates still decide.

Signals:
  authenticated               - sender proven by the network (from the payload, never from the text)
  untrusted_link              - the text contains a web address
  offers_link                 - the text offers to send a link ("get the link", "payment link")
  asks_for_secret             - asks the citizen to send an ID, card, PIN, code, password, date of birth or account no.
  asks_reply                  - asks the citizen to reply (a "no reply needed" note does not count)
  callback_number             - gives a phone number to call
  points_to_official_channel  - sends the citizen only to the official app, website, number or service centre
  mentions_payment            - mentions paying, a fine, a fee or a balance
"""
import re, unicodedata

_SECRET = re.compile(r"\b(id(?: card)? number|emirates id number|card number|card details|cvv|pin|otp|one[- ]time code|"
                     r"verification code|password|date of birth|passport number|account number|iban)\b")
_SECRET_ASK = re.compile(r"\b(reply|send|text|share|provide|confirm|enter|needs? your|with your|give)\b")
_NO_REPLY = re.compile(r"\b(no reply (?:is )?needed|do not reply|don't reply|no need to reply)\b")
_REPLY = re.compile(r"\breply\b")
_URL = re.compile(r"(https?://|www\.)\S+")
_LINK_OFFER = re.compile(r"\b(get|receive|send you|click|open|tap)\b[^.]{0,30}\blink\b|\b(payment|secure|new) link\b")
_PHONE = re.compile(r"(?:\+?\d[\d\s-]{6,}\d)")
_OFFICIAL = re.compile(r"\bofficial (app|website|site|number|channel|portal)\b|\bservice centre\b|\bservice center\b")
_PAY = re.compile(r"\b(pay|paid|payment|unpaid|fine|fee|balance|settle)\b")


# Arabic (added 8 Nov 2026). Matched on normalised text: diacritics and tatweel removed, alef/ya/ta-marbuta unified.
_AR_SECRET = re.compile(r"(رقم الهويه|رقم هويتك|رقم البطاقه|رقم بطاقتك|بيانات البطاقه|تاريخ الميلاد|تاريخ ميلادك|رمز التحقق|"
                        r"الرمز السري|كلمه المرور|رقم الحساب|الايبان)")
_AR_SECRET_ASK = re.compile(r"(ارسل|ارسال|رد |بالرد|ردا|الرد|زودنا|شارك|اكد|ادخل|يحتاج|يتطلب)")
_AR_NO_REPLY = re.compile(r"(لا داعي للرد|لا حاجه للرد|لا ترد|دون الحاجه للرد)")
_AR_REPLY = re.compile(r"(^|\s)(رد|ردا|بالرد|الرد)(\s|$|[.,،])")
_AR_LINK = re.compile(r"رابط")
_AR_OFFICIAL = re.compile(r"(التطبيق الرسمي|الموقع الرسمي|الرقم الرسمي|مركز الخدمه|مراكز الخدمه|القناه الرسميه)")
_AR_PAY = re.compile(r"(ادفع|دفع|سداد|سدد|غرامه|رسوم|رصيد|مخالفه)")
_AR_CALL = re.compile(r"(اتصل|اتصال|الاتصال)")
_AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def _norm(s):
    s = unicodedata.normalize("NFKC", s).translate(_AR_DIGITS).lower()
    s = re.sub("[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]", "", s).replace("\u0640", "")
    s = re.sub("[\u0622\u0623\u0625\u0671]", "\u0627", s).replace("\u0649", "\u064a").replace("\u0629", "\u0647")
    return re.sub(r"\s+", " ", s)


def message_signals(payload):
    text = _norm(str((payload or {}).get("short_message", "")))
    no_reply = bool(_NO_REPLY.search(text) or _AR_NO_REPLY.search(text))
    secret = (bool(_SECRET.search(text)) and bool(_SECRET_ASK.search(text))) or \
             (bool(_AR_SECRET.search(text)) and bool(_AR_SECRET_ASK.search(text)))
    phone = bool(_PHONE.search(text))
    calls = "call" in text or bool(_AR_CALL.search(text))
    return {
        "authenticated": bool((payload or {}).get("authenticated", False)),
        "untrusted_link": bool(_URL.search(text)),
        "offers_link": bool(_LINK_OFFER.search(text) or _AR_LINK.search(text)),
        "asks_for_secret": secret,
        "asks_reply": bool(_REPLY.search(text) or _AR_REPLY.search(text)) and not no_reply,
        "callback_number": phone and calls,
        "points_to_official_channel": bool(_OFFICIAL.search(text) or _AR_OFFICIAL.search(text)),
        "mentions_payment": bool(_PAY.search(text) or _AR_PAY.search(text)),
    }
