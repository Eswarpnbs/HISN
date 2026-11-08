"""OCR every Arabic (-AR) record so the knowledge base holds READABLE Arabic text (added 8 Nov 2026).

The official Arabic PDFs extract with broken letters (font mapping), so their text layer is unusable. This runs
Tesseract (Arabic, 300 dpi, cached in runs/ocr/) on each -AR source and writes kb/sources/ocr/<record_id>.txt.
kb/ingest_uae.py then ingests that text instead of the broken text layer, marked text_source=ocr_tesseract.
The PDF itself stays hash-pinned; the OCR text is a derived, unreviewed reading of it.

    python kb/ocr_arabic_all.py          (about 2-5 seconds per page; run once, results are cached)
"""
import csv, importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("arabic_ocr", Path(__file__).with_name("arabic_ocr.py"))
O = importlib.util.module_from_spec(spec); spec.loader.exec_module(O)
out = Path("kb/sources/ocr"); out.mkdir(parents=True, exist_ok=True)
for r in csv.DictReader(open("kb/manifest.csv", encoding="utf-8")):
    rid = r["record_id"]
    if not rid.endswith("-AR") or not r["sha256"]: continue
    dst = out / f"{rid}.txt"
    if dst.exists() and dst.stat().st_size > 1000:
        print(f"HAVE {rid}"); continue
    text = O.ocr_pdf(f"kb/sources/{rid}.pdf")
    dst.write_text(text, encoding="utf-8")
    print(f"OCR  {rid}: {len(text)} characters")
print("Then: python kb/ingest_uae.py")
