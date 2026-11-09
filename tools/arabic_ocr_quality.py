"""Automatic quality check of the Arabic OCR texts (added 9 Nov 2026). Not a substitute for native review.

For every Arabic record with OCR text (kb/sources/ocr/<id>-AR.txt) and its English twin (kb/sources/<id>.pdf):
  - article headings found in the Arabic OCR (a short line: "المادة" + number) vs in the official English text
    ("Article (N)"): how many of the English article numbers the OCR also found;
  - share of Arabic letters in the OCR text (low = noise).
A high article match means the OCR kept the law's structure; it does not prove every word is right.

    python tools/arabic_ocr_quality.py          -> docs/arabic_ocr_quality.md
"""
import csv, importlib.util, re, sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("arabic", "kb/arabic.py")
AR = importlib.util.module_from_spec(spec); spec.loader.exec_module(AR)
EN_ART = re.compile(r"^\s*Article\s*\(?\s*(\d{1,3})\s*\)?", re.M | re.I)

def ar_articles(text):
    out = set()
    for line in text.splitlines():
        n = AR.normalise(line)
        if len(n) <= 30:
            m = AR.HEAD.search(n)
            if m: out.add(int(m.group(1)))
    return out

def en_articles(pdf):
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz
    return {int(x) for x in EN_ART.findall("\n".join(p.get_text() for p in fitz.open(pdf)))}

def arabic_share(t):
    a = sum(c.isalpha() and "\u0600" <= c <= "\u06ff" for c in t); l = sum(c.isalpha() for c in t)
    return a / max(l, 1)

def main():
    rows, tot_en, tot_hit = [], 0, 0
    for r in csv.DictReader(open("kb/manifest.csv", encoding="utf-8")):
        rid = r["record_id"]
        if not rid.endswith("-AR"): continue
        ocr = Path("kb/sources/ocr") / f"{rid}.txt"
        en = Path("kb/sources") / f"{rid[:-3]}.pdf"
        if not ocr.exists(): rows.append((rid, "no OCR text", "", "", "")); continue
        t = ocr.read_text(encoding="utf-8"); a = ar_articles(t)
        e = en_articles(en) if en.exists() else set()
        hit = len(a & e)
        if e: tot_en += len(e); tot_hit += hit
        rows.append((rid, len(a), len(e) if e else "no English twin", f"{100 * hit / len(e):.0f}%" if e else "", f"{100 * arabic_share(t):.0f}%"))
    out = ["# Arabic OCR quality check (automatic)", "",
           "Article headings found in each Arabic OCR text compared with the official English text of the same law. "
           "Produced by `python tools/arabic_ocr_quality.py`. Structure check only: native review is still needed for wording.", "",
           f"Overall: the OCR found {tot_hit} of {tot_en} English article numbers ({100 * tot_hit / max(tot_en, 1):.0f}%).", "",
           "| Arabic record | Articles found (Arabic OCR) | Articles in English text | English articles also found in Arabic | Arabic letters |",
           "|---|---|---|---|---|"] + [f"| {a} | {b} | {c} | {d} | {e} |" for a, b, c, d, e in rows]
    Path("docs/arabic_ocr_quality.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out[4:]))

if __name__ == "__main__":
    main()
