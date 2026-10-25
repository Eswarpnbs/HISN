import csv, hashlib, urllib.request, datetime, pathlib

DOCS = [
  ("UAE-DOH-AI-2018", "Policy on Use of AI in the Healthcare Sector", "Department of Health Abu Dhabi", "AE-AZ", "policy", "REGULATOR_POLICY",
   "https://www.doh.gov.ae/-/media/E9C1470A575146B18015DEBE57E47F8D.ashx"),
  ("UAE-DOH-RAI-2025", "Responsible AI Standard", "Department of Health Abu Dhabi", "AE-AZ", "standard", "REGULATOR_POLICY",
   "https://www.doh.gov.ae/-/media/B84FF5DD027846699C51F36C439A580F.ashx"),
  ("UAE-AI-CHARTER-2024", "UAE Charter for the Development and Use of AI", "UAE AI Office", "AE", "charter", "SOFT_LAW",
   "https://ai.gov.ae/wp-content/uploads/2024/07/UAEAI-Methaq-EN2-3.pdf"),
  ("UAE-AI-STRATEGY-2031", "UAE National Strategy for AI 2031", "UAE Government", "AE", "strategy", "SOFT_LAW",
   "https://u.ae/-/media/AI-publications/UAE-National-Strategy-for-Artificial-Intelligence-2031.pdf"),
]

src = pathlib.Path("kb/sources"); src.mkdir(parents=True, exist_ok=True)
today = datetime.date.today().isoformat()
rows = []
for rid, title, issuer, jur, itype, basis, url in DOCS:
    path = src / f"{rid}.pdf"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=60).read()
        path.write_bytes(data)
        sha = hashlib.sha256(data).hexdigest()
        status = "official"
        print(f"OK   {rid}  {len(data)//1024} KB  {sha[:12]}...")
    except Exception as e:
        sha, status = "", "download_failed"
        print(f"FAIL {rid}: {e}")
    rows.append([rid, title, issuer, jur, itype, basis, "in_force", url, sha, today, status])

with open("kb/manifest.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["record_id","title","issuer","jurisdiction","instrument_type","basis","status","url","sha256","retrieved_at","verification"])
    w.writerows(rows)
print("Wrote kb/manifest.csv")
