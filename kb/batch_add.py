"""Add many official PDFs to the knowledge base at once (added 8 Nov 2026).

You download PDFs in your browser (kb/download_list.html has the links). Then:

    python kb/batch_add.py ~/Downloads            # shows what each PDF is; changes nothing
    python kb/batch_add.py ~/Downloads --apply    # files them and records them in kb/register_extra.csv
    python kb/register.py && python kb/verify.py && python kb/ingest_uae.py

Each PDF is identified from its OWN first page, never from its file name:
  - English UAE legislation: "Federal Law / Federal Decree-Law / Cabinet Resolution No. (N) of YYYY"
  - Arabic UAE legislation:  "رقم (N) لسنة YYYY" (Arabic PDFs often extract with broken letters, so page 1 is OCR'd
                              with Tesseract when the text layer fails)
  - ITU-T Recommendations:   "ITU-T X.1242" and the edition date "(02/2009)"
Already-registered laws and duplicate files are skipped. Anything it cannot identify is listed and left untouched.
Records are pinned by SHA-256 exactly like the original 32 (kb/register.py writes the manifest).
"""
import argparse, csv, hashlib, re, shutil, subprocess, tempfile, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXTRA = ROOT / "register_extra.csv"
SRC = ROOT / "sources"
FIELDS = ["record_id", "title", "issuer", "jurisdiction", "instrument_type", "basis", "url", "how_obtained"]

# Laws already in kb/register.py under older record ids: (kind, number, year) -> record id stem
ALIASES = {("FDL", 45, 2021): "UAE-PDPL-2021", ("FDL", 34, 2021): "UAE-CYBERCRIME-2021", ("FDL", 3, 2003): "UAE-TELECOM-2003",
           ("FL", 2, 2019): "UAE-FL-2-2019", ("CABRES", 32, 2020): "UAE-CABRES-32-2020", ("CABRES", 56, 2024): "UAE-CABRES-56-2024",
           ("FDL", 46, 2021): "UAE-FDL-46-2021", ("FL", 15, 2020): "UAE-CONSUMER-15-2020"}

# uaelegislation.gov.ae page ids for the laws in kb/download_list.html (same id serves /en and /ar). Used only for the
# record's URL, and only when the PDF's own first page names the same law.
PAGE_IDS = {("FDL", 4, 2016): 1192, ("FL", 13, 2020): 1456, ("FL", 14, 2014): 1197, ("FL", 3, 2016): 1176,
            ("FDL", 31, 2021): 1529, ("FL", 8, 2019): 1426, ("FL", 4, 2015): 1204, ("FDL", 26, 2025): 3912}

ITU_TITLES = {
    "X.1231": "Technical strategies for countering spam",
    "X.1240": "Technologies involved in countering e-mail spam",
    "X.1241": "Technical framework for countering email spam",
    "X.1242": "Short message service (SMS) spam filtering system based on user-specified rules",
    "X.1243": "Interactive gateway system for countering spam",
    "X.1244": "Overall aspects of countering spam in IP-based multimedia applications",
    "X.1245": "Framework for countering spam in IP-based multimedia applications",
    "X.1246": "Technologies involved in countering voice spam in telecommunication organizations",
    "X.1247": "Technical framework for countering mobile messaging spam",
    "Y.3172": "Architectural framework for machine learning in future networks including IMT-2020",
    "Y.3173": "Framework for evaluating intelligence levels of future networks including IMT-2020",
    "Y.3174": "Framework for data handling to enable machine learning in future networks including IMT-2020",
}

EN_KIND = re.compile(r"(federal\s+decree[\s-]*(?:by[\s-]*)?law|federal\s+law|cabinet\s+(?:resolution|decision))\s*"
                     r"(?:no\.?|number)\s*\(?\s*(\d+)\s*\)?\s*(?:of|for)\s*(?:the\s+year\s*)?(\d{4})", re.I)
AR_NUM = re.compile(r"رقم\s*[\(\)]?\s*(\d+)\s*[\(\)]?\s*لسنة\s*(\d{4})")
ITU_REC = re.compile(r"ITU-T\s+(?:Recommendation\s+)?([XY])\.\s?(\d{3,4})|Recommendation\s+ITU-T\s+([XY])\.\s?(\d{3,4})")
ITU_DATE = re.compile(r"\((\d{2})/(\d{4})\)")
AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")


def _norm_ar(s):
    s = unicodedata.normalize("NFKC", s or "").translate(AR_DIGITS)
    s = re.sub("[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]", "", s).replace("\u0640", "")
    s = re.sub("[إأآٱ]", "ا", s).replace("ى", "ي")
    return re.sub(r"\s+", " ", s)


def _page_text(pdf, pages=2):
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz
    doc = fitz.open(pdf)
    return "\n".join(doc[i].get_text() for i in range(min(pages, len(doc))))


def _ocr_first_page(pdf):
    if not shutil.which("tesseract"):
        return ""
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz
    with tempfile.TemporaryDirectory() as d:
        img = Path(d) / "p1.png"
        fitz.open(pdf)[0].get_pixmap(dpi=300).save(img)
        r = subprocess.run(["tesseract", str(img), "-", "-l", "ara+eng", "--psm", "6"], capture_output=True, text=True)
        return r.stdout


def _arabic_share(text):
    ar = sum("\u0600" <= ch <= "\u06ff" or "\ufb50" <= ch <= "\ufdff" or "\ufe70" <= ch <= "\ufeff" for ch in text)
    lat = sum("a" <= ch.lower() <= "z" for ch in text)
    return ar / max(1, ar + lat)


def _kind(word):
    w = word.lower()
    if "cabinet" in w or "مجلس الوزراء" in w: return "CABRES"
    if "decree" in w or "مرسوم" in w: return "FDL"
    return "FL"


def identify(pdf):
    """Return a dict describing the PDF, or None if it cannot be identified from its own pages."""
    text = _page_text(pdf)
    first = _page_text(pdf, pages=1)
    # Only a real ITU-T Recommendation: its cover page carries the ITU name. A CV or paper that merely MENTIONS
    # "ITU-T Y.3061" must not be taken for the standard itself.
    itu_cover = re.search(r"INTERNATIONAL\s+TELECOMMUNICATION\s+UNION|TELECOMMUNICATION\s+STANDARDIZATION\s+SECTOR", first, re.I)
    m = ITU_REC.search(first) if itu_cover else None
    if m:
        series, num = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(4))
        rec = f"{series}.{num}"
        d = ITU_DATE.search(text)
        year = d.group(2) if d else ""
        return {"record_id": f"ITU-T-{series}{num}" + (f"-{year}" if year else ""),
                "title": f"Recommendation ITU-T {rec}" + (f" ({d.group(1)}/{year})" if d else "") +
                         (f": {ITU_TITLES[rec]}" if rec in ITU_TITLES else ""),
                "issuer": "ITU-T", "jurisdiction": "INT", "instrument_type": "itu_recommendation", "basis": "SOFT_LAW",
                "url": f"https://www.itu.int/rec/T-REC-{rec}/en", "how_obtained": "official", "lang": "en"}
    arabic = _arabic_share(text) > 0.5
    if not arabic:
        hits = sorted(EN_KIND.finditer(text), key=lambda x: x.start())
        if not hits:
            return None
        h = hits[0]
        kind, n, y = _kind(h.group(1)), int(h.group(2)), int(h.group(3))
        rest = re.sub(r"\s+", " ", text[h.start(): h.start() + 260])
        title = re.split(r"\s(?:We,|We |The President|In the name|Having reviewed|After perusal)", rest)[0].strip(" ,.")[:200]
        lang = "en"
    else:
        t = _norm_ar(text)
        m = AR_NUM.search(t)
        if not m:
            t = _norm_ar(_ocr_first_page(pdf))
            m = AR_NUM.search(t)
        if not m:
            return None
        n, y = int(m.group(1)), int(m.group(2))
        before = t[max(0, m.start() - 40): m.start()]
        kind = "CABRES" if "مجلس الوزراء" in before else ("FDL" if "مرسوم" in before else "FL")
        title = None
        lang = "ar"
    stem = ALIASES.get((kind, n, y), f"UAE-{kind}-{n}-{y}")
    label = {"FL": "Federal Law", "FDL": "Federal Decree-Law", "CABRES": "Cabinet Resolution"}[kind]
    if lang == "ar":
        title = f"النص العربي: {label} No. ({n}) of {y}"
    return {"record_id": stem + ("-AR" if lang == "ar" else ""), "title": title,
            "issuer": "UAE Cabinet" if kind == "CABRES" else "UAE Federal Government", "jurisdiction": "AE",
            "instrument_type": "cabinet_resolution" if kind == "CABRES" else "federal_law",
            "basis": "CABINET_RESOLUTION" if kind == "CABRES" else "FEDERAL_LAW",
            "url": (f"https://uaelegislation.gov.ae/{lang}/legislations/{PAGE_IDS[(kind, n, y)]}" if (kind, n, y) in PAGE_IDS
                    else f"https://uaelegislation.gov.ae/{lang}/legislations (search: {label} No. {n} of {y})"),
            "how_obtained": "official_arabic_authoritative" if lang == "ar" else "official", "lang": lang}


def known_ids():
    ids = set()
    reg = (ROOT / "register.py").read_text(encoding="utf-8")
    ids |= set(re.findall(r'\(\s*"([A-Z][A-Z0-9-]+)"', reg))
    if EXTRA.exists():
        ids |= {r["record_id"] for r in csv.DictReader(open(EXTRA, encoding="utf-8"))}
    return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", nargs="+", help="folder(s) or PDF files to look at, e.g. ~/Downloads")
    ap.add_argument("--apply", action="store_true", help="copy into kb/sources and record them (default: dry run)")
    ap.add_argument("--skip", nargs="*", default=[], help="record ids NOT to add (e.g. off-topic laws)")
    ap.add_argument("--since", help="only look at PDFs saved after this time today, HH:MM (keeps your other files out)")
    a = ap.parse_args()
    pdfs = []
    for f in a.folder:
        p = Path(f).expanduser()
        pdfs += sorted(p.glob("*.pdf")) if p.is_dir() else [p]
    if a.since:
        import datetime
        h, mnt = map(int, a.since.split(":"))
        cut = datetime.datetime.now().replace(hour=h, minute=mnt, second=0, microsecond=0).timestamp()
        pdfs = [p for p in pdfs if p.stat().st_mtime >= cut]
        print(f"looking only at {len(pdfs)} PDF(s) saved after {a.since} today")
    have = {hashlib.sha256(p.read_bytes()).hexdigest() for p in SRC.glob("*.pdf")}
    ids, new_rows, seen = known_ids(), [], set()
    for pdf in pdfs:
        data = pdf.read_bytes()
        if data[:4] != b"%PDF":
            print(f"SKIP not a PDF        {pdf.name}"); continue
        if hashlib.sha256(data).hexdigest() in have:
            print(f"SKIP already in KB    {pdf.name}"); continue
        try:
            info = identify(pdf)
        except Exception as ex:
            info = None; print(f"     (could not read {pdf.name}: {ex})")
        if not info:
            print(f"???  not identified   {pdf.name}"); continue
        rid = info["record_id"]
        if rid in a.skip:
            print(f"SKIP you asked        {rid:26s} {pdf.name}"); continue
        if rid in ids or rid in seen:
            print(f"SKIP already recorded {rid:26s} {pdf.name}"); continue
        seen.add(rid)
        print(f"NEW  {rid:26s} {info['title'][:70]}   <- {pdf.name}")
        if a.apply:
            shutil.copyfile(pdf, SRC / f"{rid}.pdf")
            new_rows.append({k: info[k] for k in FIELDS})
    if a.apply and new_rows:
        first = not EXTRA.exists()
        with open(EXTRA, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            if first: w.writeheader()
            w.writerows(new_rows)
        print(f"\nadded {len(new_rows)} records to {EXTRA.name}. Next: python kb/register.py && python kb/verify.py")
    elif not a.apply:
        print(f"\n{len(seen)} new. Nothing changed (dry run). Re-run with --apply to add them.")


if __name__ == "__main__":
    main()
