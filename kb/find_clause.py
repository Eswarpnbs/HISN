"""Print passages around search terms in a PDF, so clauses can be copied verbatim.
Usage: python kb/find_clause.py kb/sources/FILE.pdf "term one" "term two" """
import sys, re
try:
    import pymupdf as fitz
except ImportError:
    import fitz
pdf, *terms = sys.argv[1:]
for pno, page in enumerate(fitz.open(pdf), 1):
    flat = re.sub(r"\s+", " ", page.get_text())
    for term in terms:
        for m in re.finditer(re.escape(term), flat, re.I):
            s, e = max(0, m.start() - 250), min(len(flat), m.end() + 450)
            print(f"\n--- page {pno} [{term}]\n...{flat[s:e]}...")
