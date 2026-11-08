"""Arabic articles by OCR, for official Arabic PDFs whose fonts extract with wrong letters.

Some official UAE Arabic PDFs map their glyphs to the wrong Unicode letters, so copying or extracting their text gives
corrupted words. OCR reads the page as an image instead, so it sees the letters a reader sees. OCR is not
guaranteed verbatim, so every OCR clause is stored with status "ocr_unreviewed" until a native reader checks it
against the PDF and sets "reviewed_by_<name>_<date>".

Needs Tesseract with Arabic (macOS: brew install tesseract tesseract-lang).

    python kb/arabic_ocr.py --record UAE-FL-2-2019 --article 13 --pdf kb/sources/UAE-FL-2-2019-AR.pdf
    python kb/arabic_ocr.py --record UAE-FL-2-2019 --article 13 --pdf kb/sources/UAE-FL-2-2019-AR.pdf --show   # print, do not store

The OCR text of each PDF is cached in runs/ocr/<file>.txt (one run per PDF, about a minute).
"""
import argparse, importlib.util, shutil, subprocess, sys, tempfile
from pathlib import Path

spec = importlib.util.spec_from_file_location("arabic", Path(__file__).with_name("arabic.py"))
AR = importlib.util.module_from_spec(spec); spec.loader.exec_module(AR)

def render_pages(pdf, out_dir, dpi=300):
    try:
        import pymupdf
    except ImportError:
        pymupdf = None
    if pymupdf:
        doc = pymupdf.open(pdf)
        for i, page in enumerate(doc):
            page.get_pixmap(dpi=dpi).save(str(Path(out_dir) / f"p{i + 1:03d}.png"))
    else:
        subprocess.run(["pdftoppm", "-r", str(dpi), "-png", str(pdf), str(Path(out_dir) / "p")], check=True)
    return sorted(Path(out_dir).glob("p*.png"))

def ocr_pdf(pdf):
    cache = Path("runs/ocr") / (Path(pdf).stem + ".txt")
    if cache.exists():
        return cache.read_text(encoding="utf-8")
    if not shutil.which("tesseract"):
        sys.exit("Tesseract not found. On macOS: brew install tesseract tesseract-lang")
    langs = subprocess.run(["tesseract", "--list-langs"], capture_output=True, text=True).stdout.split()
    if "ara" not in langs:
        sys.exit("Tesseract has no Arabic model. On macOS: brew install tesseract-lang")
    with tempfile.TemporaryDirectory() as tmp:
        texts = []
        for img in render_pages(pdf, tmp):
            r = subprocess.run(["tesseract", str(img), "-", "-l", "ara", "--psm", "6"], capture_output=True, text=True)
            texts.append(r.stdout)
    text = "\n".join(texts)
    cache.parent.mkdir(parents=True, exist_ok=True); cache.write_text(text, encoding="utf-8")
    return text

def find_article_strict(text, number):
    """Like arabic.find_article, but an article heading must be its own short line, so cross-references inside the text
    (for example 'in violation of Article (13)') do not cut the article short."""
    lines = [AR.normalise(l) for l in text.splitlines()]
    # a heading line is short; a cross-reference sits inside a longer sentence
    starts = [(i, int(m.group(1))) for i, l in enumerate(lines) if len(l) <= 30 for m in [AR.HEAD.search(l)] if m]
    for k, (i, n) in enumerate(starts):
        if n == int(number):
            # the article ends at the next heading with a HIGHER number; earlier numbers are cross-references
            end = next((j for j, m in starts[k + 1:] if j > i and m > n), len(lines))
            return AR.normalise(" ".join(lines[i:end]))
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", required=True); ap.add_argument("--article", required=True); ap.add_argument("--pdf", required=True)
    ap.add_argument("--show", action="store_true", help="print the OCR article without storing it")
    a = ap.parse_args()
    art = find_article_strict(ocr_pdf(a.pdf), a.article)
    if not art:
        sys.exit(f"Article {a.article} not found in the OCR text; see runs/ocr/{Path(a.pdf).stem}.txt")
    if a.show:
        print(art); return
    AR._store(a.record, a.article, art, a.pdf, "ocr_unreviewed")
    print("Read it against the PDF before calling it reviewed:\n" + art[:400])

if __name__ == "__main__":
    main()
