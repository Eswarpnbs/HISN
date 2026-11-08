"""kb/batch_add.py identifies PDFs from their own first page. Page text is stubbed: no PDF or OCR needed here.
The sample page texts are written for the test (not legal text)."""
import importlib.util
spec = importlib.util.spec_from_file_location("batch_add", "kb/batch_add.py")
B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)

def ident(monkeypatch, page, ocr="", name="x.pdf"):
    monkeypatch.setattr(B, "_page_text", lambda pdf, pages=2: page)
    monkeypatch.setattr(B, "_ocr_first_page", lambda pdf: ocr)
    return B.identify(name)

def test_english_federal_law_with_page_id(monkeypatch):
    r = ident(monkeypatch, "Federal Law No. (13) of 2020\nConcerning Public Health\n\nWe, Khalifa ...")
    assert r["record_id"] == "UAE-FL-13-2020" and r["basis"] == "FEDERAL_LAW"
    assert r["url"] == "https://uaelegislation.gov.ae/en/legislations/1456" and "Public Health" in r["title"]

def test_decree_law_and_earliest_mention_wins(monkeypatch):
    r = ident(monkeypatch, "Federal Decree-Law No. 31 of 2021 Promulgating the Crimes and Penalties Law. "
                           "Having reviewed Federal Law No. (3) of 1987 ...")
    assert r["record_id"] == "UAE-FDL-31-2021"

def test_cabinet_resolution_and_existing_alias(monkeypatch):
    r = ident(monkeypatch, "Cabinet Resolution No. (32) of 2020 on the Executive Regulation of Federal Law No. (2) of 2019")
    assert r["record_id"] == "UAE-CABRES-32-2020" and r["basis"] == "CABINET_RESOLUTION"
    assert ident(monkeypatch, "Federal Decree-Law No. (45) of 2021 Concerning the Protection of Personal Data")["record_id"] == "UAE-PDPL-2021"

def test_arabic_from_text_layer_and_from_ocr(monkeypatch):
    r = ident(monkeypatch, "قانون اتحادي رقم (١٣) لسنة ٢٠٢٠ في شأن الصحة العامة")
    assert r["record_id"] == "UAE-FL-13-2020-AR" and r["url"].startswith("https://uaelegislation.gov.ae/ar/legislations/1456")
    broken = "ﺍﻟﻮﺣﺮﺍﺍ ﻢﻠﻗ ﺱﺱﺱ ﺏﺏ ﺕﺕ ﺙﺙ ﺝﺝ"   # garbled text layer: Arabic glyphs, no readable number
    r = ident(monkeypatch, broken, ocr="مرسوم بقانون اتحادي رقم (26) لسنة 2025 بشأن السلامة الرقمية للطفل")
    assert r["record_id"] == "UAE-FDL-26-2025-AR" and r["how_obtained"] == "official_arabic_authoritative"

def test_itu_recommendation(monkeypatch):
    r = ident(monkeypatch, "INTERNATIONAL TELECOMMUNICATION UNION\nITU-T X.1242\n(02/2009)\nSERIES X ...")
    assert r["record_id"] == "ITU-T-X1242-2009" and r["basis"] == "SOFT_LAW" and "SMS" in r["title"]

def test_a_cv_that_mentions_an_itu_recommendation_is_not_taken_for_it(monkeypatch):
    assert ident(monkeypatch, "Curriculum vitae. Skills: network slicing, ITU-T Y.3061 study, Python") is None

def test_unknown_document_is_not_guessed(monkeypatch):
    assert ident(monkeypatch, "Quarterly newsletter, nothing official here") is None

def test_file_name_chooses_among_laws_the_text_names(monkeypatch):
    page = ("Having reviewed Federal Law No. (1) of 1972 concerning the Ministries ... "
            "Federal Law by Decree No. (31) of 2021 Promulgating the Crimes and Penalties Law")
    r = ident(monkeypatch, page, name="Federal Law by Decree No. (31) of 2021 Promulgating the Crimes and Penalties Law.pdf")
    assert r["record_id"] == "UAE-FDL-31-2021"
    page2 = "Federal Decree-Law No. (46) of 2021 ... Cabinet Resolution No. (52) of 2024 Concerning the Administrative Penalties"
    assert ident(monkeypatch, page2, name="Cabinet Resolution No. (52) of 2024 Concerning the Administrative Penalties.pdf")["record_id"] == "UAE-CABRES-52-2024"

def test_a_file_name_the_text_does_not_support_is_ignored(monkeypatch):
    r = ident(monkeypatch, "Federal Law No. (13) of 2020 on the Public Health", name="Federal Law No. (99) of 2099 Fake.pdf")
    assert r["record_id"] == "UAE-FL-13-2020"

def test_arabic_file_name_chooses_cabinet_resolution_over_the_law_it_implements(monkeypatch):
    page = "المرسوم بقانون اتحادي رقم (46) لسنة 2021 ... قرار مجلس الوزراء رقم (28) لسنة 2023 بشأن اللائحة التنفيذية"
    r = ident(monkeypatch, page, name="قرار مجلس الوزراء رقم (28 ) لسنة 2023 بشأن اللائحة التنفيذية.pdf")
    assert r["record_id"] == "UAE-CABRES-28-2023-AR"
