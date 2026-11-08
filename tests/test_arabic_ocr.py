import importlib.util
spec = importlib.util.spec_from_file_location("arabic_ocr", "kb/arabic_ocr.py")
OCR = importlib.util.module_from_spec(spec); spec.loader.exec_module(OCR)

# Synthetic OCR output written for the test (not legal text).
TEXT = "المادة (12)\nنص أول.\nالمادة (13)\nلا يجوز نقل البيانات التجريبية\nوفق المادة (12)\nمن هذا النص.\nالمادة (14)\nنص ثالث."

def test_cross_reference_to_an_earlier_article_does_not_cut_the_article():
    a = OCR.find_article_strict(TEXT, 13)
    assert a.startswith("المادة (13)") and "من هذا النص" in a and "نص ثالث" not in a

def test_missing_article():
    assert OCR.find_article_strict(TEXT, 99) is None
