"""Download the records added on 8 Nov 2026 into kb/sources/<record_id>.pdf, then run kb/register.py.

    python kb/fetch_more.py

Some official sites refuse scripted downloads or serve a web page first. For those, the script prints the page to
open; download the PDF in your browser and save it as kb/sources/<record_id>.pdf. Nothing else is needed:
kb/register.py pins each file's SHA-256 and kb/verify.py checks it.
"""
import pathlib, urllib.request

DIRECT = {
    "UAE-CABRES-56-2024": "https://uaelegislation.gov.ae/en/legislations/2519/download",
    "UAE-FDL-46-2021": "https://uaelegislation.gov.ae/en/legislations/1539/download",
    "EU-REG-2021-1232": "https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32021R1232",
    "AU-SPF-ACT-2025": "https://www.ato.gov.au/law/view/pdf/acts/20250015.pdf",
}
MANUAL = {
    "UAE-CONSUMER-15-2020": "https://uaelegislation.gov.ae/en/legislations/1455/download",
    "UAE-DHA-AI-2022": "https://www.dha.gov.ae/uploads/082022/Artificial%20Intelligence%20Policy20228457.pdf",
    "UAE-FL-2-2019-AR": "https://uaelegislation.gov.ae/ar/legislations/1209 (Arabic page: click the download button)",
    "UAE-CABRES-32-2020-AR": "https://uaelegislation.gov.ae/ar/legislations/1444",
    "UAE-TELECOM-2003-AR": "https://uaelegislation.gov.ae/ar/legislations/1132",
    "UAE-CYBERCRIME-2021-AR": "https://uaelegislation.gov.ae/ar/legislations/1526",
    "UAE-PDPL-2021-AR": "https://uaelegislation.gov.ae/ar/legislations/1972",
    "UAE-CABRES-56-2024-AR": "https://uaelegislation.gov.ae/ar/legislations/2519",
    "UAE-FDL-46-2021-AR": "https://uaelegislation.gov.ae/ar/legislations/1539",
    "UAE-CONSUMER-15-2020-AR": "https://uaelegislation.gov.ae/ar/legislations/1455",
    "AU-SPF-ACT-2025": "https://www.legislation.gov.au/C2025A00015/asmade/downloads (PDF of the Act as made)",
    "AU-C661-2022": "https://commsalliance.com.au/Documents/all/codes/c661 (download the C661:2022 PDF)",
    "EU-EDPB-GL-2-2018": "https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-22018-derogations-article-49-under-regulation_en (English PDF)",
    "UAE-CABRES-56-2024": "https://uaelegislation.gov.ae/en/legislations/2519 (Download, English)",
    "UAE-FDL-46-2021": "https://uaelegislation.gov.ae/en/legislations/1539 (Download, English)",
    "EU-REG-2021-1232": "https://eur-lex.europa.eu/eli/reg/2021/1232/oj (PDF, English)",
}
src = pathlib.Path("kb/sources"); src.mkdir(parents=True, exist_ok=True)
todo = []
for rid in sorted(set(DIRECT) | set(MANUAL)):
    path = src / f"{rid}.pdf"
    if path.exists() and path.read_bytes()[:4] == b"%PDF":
        print(f"HAVE {rid}"); continue
    url = DIRECT.get(rid)
    if url:
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
            if data[:4] == b"%PDF":
                path.write_bytes(data); print(f"OK   {rid}  {len(data)//1024} KB"); continue
            print(f"NOT A PDF {rid} (site served a web page)")
        except Exception as e:
            print(f"FAIL {rid}: {e}")
    todo.append(rid)
if todo:
    print("\nDownload these in your browser and save each as kb/sources/<record_id>.pdf:")
    for rid in todo:
        print(f"  {rid}.pdf  <-  {MANUAL.get(rid, DIRECT.get(rid))}")
print("\nThen: python kb/register.py && python kb/verify.py && python kb/ingest_uae.py")
