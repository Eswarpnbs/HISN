import importlib.util
spec = importlib.util.spec_from_file_location("q", "tools/arabic_ocr_quality.py")
Q = importlib.util.module_from_spec(spec); spec.loader.exec_module(Q)

def test_article_headings_are_short_lines_only():
    # synthetic test text, not legal text
    t = "المادة (1)\nنص.\nالمادة ٢\nنص يشير إلى المادة (9) من قانون آخر في سطر طويل جدا جدا جدا\nالمادة (3)"
    assert Q.ar_articles(t) == {1, 2, 3}

def test_arabic_share():
    assert Q.arabic_share("نص عربي") == 1.0 and Q.arabic_share("abc") == 0.0
