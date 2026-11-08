"""Arabic clause support: the Arabic text of UAE law is authoritative, so key clauses are stored in Arabic too.

Nothing here writes legal text. Arabic clauses are copied from the official Arabic PDF on your own machine:

    python kb/arabic.py extract --record UAE-FL-2-2019 --article 13 --pdf kb/sources/<arabic file>.pdf
    python kb/arabic.py verify                       # re-checks every stored Arabic clause against its PDF

`extract` finds the article heading (المادة plus the number, in Western or Arabic-Indic digits), cuts the text up
to the next article, stores it in kb/clauses/clauses_ar.yaml with its SHA-256 and status
"extracted_unreviewed". A native reader then reads it against the PDF and sets status "reviewed_by_<name>_<date>".
Matching normalises only presentation: diacritics (tashkeel), tatweel, alef and ya variants, and whitespace.
"""
import argparse, hashlib, re, sys, unicodedata
from pathlib import Path
import yaml

AR_PATH = Path("kb/clauses/clauses_ar.yaml")
TASHKEEL = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭ]")
AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")

def normalise(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = TASHKEEL.sub("", s).replace("ـ", "")                      # diacritics, tatweel
    s = re.sub("[إأآٱ]", "ا", s).replace("ى", "ي")                       # alef and ya variants
    s = s.translate(AR_DIGITS)
    return re.sub(r"\s+", " ", s).strip()

def sha(s):
    return hashlib.sha256(normalise(s).encode("utf-8")).hexdigest()

HEAD = re.compile(r"(?:ال)?مادة\s*[\(\)\[\]]?\s*(\d+)\s*[\(\)\[\]]?")  # PDFs may extract brackets mirrored

def find_article(text, number):
    """Return the normalised text of article `number`, from its heading up to the next article heading."""
    t = normalise(text)
    heads = [(m.start(), int(m.group(1))) for m in HEAD.finditer(t)]
    for i, (pos, n) in enumerate(heads):
        if n == int(number):
            end = next((p for p, _ in heads[i + 1:] if p > pos), len(t))
            return t[pos:end].strip()
    return None

def contains(page_text, quote):
    return normalise(quote) in normalise(page_text)

def load():
    return yaml.safe_load(AR_PATH.read_text(encoding="utf-8")) if AR_PATH.exists() else {"clauses": []}

def save(data):
    AR_PATH.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000), encoding="utf-8")

def _pdf_text(pdf):
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz
    return "\n".join(p.get_text() for p in fitz.open(pdf))

def cmd_extract(a):
    art = find_article(_pdf_text(a.pdf), a.article)
    if not art:
        sys.exit(f"Article {a.article} not found. Open the PDF and check the heading; some PDFs extract Arabic "
                 "in visual order, in which case copy the clause by hand and use `add`.")
    _store(a.record, a.article, art, a.pdf, "extracted_unreviewed")

def cmd_add(a):
    text = Path(a.text_file).read_text(encoding="utf-8")
    if a.pdf and not contains(_pdf_text(a.pdf), text):
        sys.exit("The text is not found in the PDF after normalisation; not stored.")
    _store(a.record, a.article, text, a.pdf, "copied_unreviewed", a.source_url)

def _store(record, article, text, pdf, status, source_url=None):
    data = load()
    data["clauses"] = [c for c in data["clauses"] if not (c["record_id"] == record and str(c["article"]) == str(article))]
    data["clauses"].append({"record_id": record, "article": str(article), "text_ar": normalise(text),
                            "sha256": sha(text), "source_pdf": Path(pdf).name if pdf else None,
                            "source_url": source_url, "status": status, "language": "ar (authoritative)"})
    save(data)
    print(f"stored {record} Art. {article} ({len(normalise(text))} chars), status {status}")

def cmd_verify(_a):
    bad = 0
    for c in load()["clauses"]:
        ok = sha(c["text_ar"]) == c["sha256"]
        src = Path("kb/sources") / (c.get("source_pdf") or "")
        if ok and c.get("source_pdf") and src.exists() and not str(c["status"]).startswith(("ocr", "copied")):
            # text-layer check only for extracted text; OCR/copied text is checked by hash and its stated method
            ok = contains(_pdf_text(src), c["text_ar"])
        print(("OK  " if ok else "FAIL"), c["record_id"], "Art.", c["article"], c["status"])
        bad += not ok
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    e = sp.add_parser("extract"); e.add_argument("--record", required=True); e.add_argument("--article", required=True); e.add_argument("--pdf", required=True)
    d = sp.add_parser("add"); d.add_argument("--record", required=True); d.add_argument("--article", required=True); d.add_argument("--text-file", required=True); d.add_argument("--pdf")
    d.add_argument("--source-url", help="official page the text was copied from (when the PDF's fonts extract wrongly)")
    sp.add_parser("verify")
    a = ap.parse_args()
    {"extract": cmd_extract, "add": cmd_add, "verify": cmd_verify}[a.cmd](a)
