import importlib.util, tempfile, yaml
from pathlib import Path
from app.receipts import render

spec = importlib.util.spec_from_file_location("arabic", "kb/arabic.py")
AR = importlib.util.module_from_spec(spec); spec.loader.exec_module(AR)

# Synthetic test text written for the test (not legal text).
SAMPLE = ("مقدمة\nالمادة (٣)\nنص تجريبي أول للاختبار فقط.\n"
          "المادة (4)\nنصٌّ تَجْرِيبِيّ ثانٍ ـــ للاختبار فقط، مع إشارة إلى الأنظمة.\nالمادة (5)\nنص ثالث.")

def test_normalise_removes_presentation_only():
    assert AR.normalise("نصٌّ تَجْرِيبِيّ ـــ") == "نص تجريبي"
    assert AR.normalise("أإآ ى ٤٢") == "ااا ي 42"

def test_find_article_handles_both_digit_styles_and_stops_at_next_article():
    a3 = AR.find_article(SAMPLE, 3)
    assert a3.startswith("المادة (3)") and "أول" not in a3 and "اول" in a3 and "المادة (4)" not in a3
    a4 = AR.find_article(SAMPLE, "4")
    assert "ثان" in a4 and "المادة (5)" not in a4
    assert AR.find_article(SAMPLE, 9) is None

def test_contains_ignores_diacritics_but_not_wording():
    assert AR.contains(SAMPLE, "نص تجريبي ثان")
    assert not AR.contains(SAMPLE, "نص تجريبي رابع")

def test_hash_is_stable_under_presentation_changes():
    assert AR.sha("نصٌّ تَجْرِيبِيّ") == AR.sha("نص تجريبي")
    assert AR.sha("نص تجريبي") != AR.sha("نص تجريبي آخر")

def test_arabic_clause_file_holds_no_unverified_text():
    data = yaml.safe_load(Path("kb/clauses/clauses_ar.yaml").read_text(encoding="utf-8"))
    for c in data["clauses"]:
        assert c["sha256"] == AR.sha(c["text_ar"]) and c["status"] and (c.get("source_pdf") or c.get("source_url"))

RECEIPT = {"receipted_message_id": "Q1", "reason": "HELD tier T1 -> health_authority",
           "review_by_minutes": "5", "call_patient_after_minutes": "15", "audit_hash": "ab12cd34ef56aa77"}

def test_receipt_numbers_come_from_code_in_both_languages():
    en, ar = render(RECEIPT, "en"), render(RECEIPT, "ar")
    for r in (en, ar):
        assert "Q1" in r["text"] and "5" in r["text"] and "15" in r["text"] and "ab12cd34ef56" in r["text"]
    assert "Health Authority" in en["text"] and "الجهة الصحية" in ar["text"]
    assert ar["direction"] == "rtl" and "pending" in ar["review_status"]

def test_unknown_language_falls_back_to_english():
    assert render(RECEIPT, "xx")["lang"] == "en"

def test_find_article_with_mirrored_brackets_from_pdf_extraction():
    text = "المادة )12(\nنص أ.\nالمادة )13(\nنص ب للاختبار.\nالمادة )14(\nنص ج."
    a = AR.find_article(text, 13)
    assert a and "نص ب" in a and "نص ج" not in a
