import csv, hashlib, datetime, pathlib

# (record_id, title, issuer, jurisdiction, type, basis, official_url, how_obtained)
DOCS = [
  ("UAE-DOH-AI-2018", "Policy on Use of AI in the Healthcare Sector", "Department of Health Abu Dhabi", "AE-AZ", "policy", "REGULATOR_POLICY",
   "https://www.doh.gov.ae/-/media/E9C1470A575146B18015DEBE57E47F8D.ashx", "official"),
  ("UAE-DOH-RAI-2025", "Responsible AI Standard", "Department of Health Abu Dhabi", "AE-AZ", "standard", "REGULATOR_POLICY",
   "https://www.doh.gov.ae/-/media/B84FF5DD027846699C51F36C439A580F.ashx", "official"),
  ("UAE-AI-CHARTER-2024", "UAE Charter for the Development and Use of AI", "UAE AI Office", "AE", "charter", "SOFT_LAW",
   "https://ai.gov.ae/wp-content/uploads/2024/07/UAEAI-Methaq-EN2-3.pdf", "official_archived"),
  ("UAE-AI-STRATEGY-2031", "UAE National Strategy for AI 2031", "UAE Government", "AE", "strategy", "SOFT_LAW",
   "https://ai.gov.ae/wp-content/uploads/2021/07/UAE-National-Strategy-for-Artificial-Intelligence-2031.pdf", "official_archived"),
]

src = pathlib.Path("kb/sources")
today = datetime.date.today().isoformat()
rows = []
for rid, title, issuer, jur, itype, basis, url, how in DOCS:
    p = src / f"{rid}.pdf"
    if p.exists() and p.read_bytes()[:4] == b"%PDF":
        data = p.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        status = how
        print(f"OK   {rid}  {len(data)//1024} KB  {sha[:12]}...  ({how})")
    elif p.exists():
        sha, status = "", "check_file_not_pdf"
        print(f"WARN {rid}: file is not a PDF - re-download")
    else:
        sha, status = "", "missing"
        print(f"MISS {rid}: add later")
    rows.append([rid, title, issuer, jur, itype, basis, "in_force", url, sha, today, status])

with open("kb/manifest.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["record_id","title","issuer","jurisdiction","instrument_type","basis","status","url","sha256","retrieved_at","verification"])
    w.writerows(rows)
print("Wrote kb/manifest.csv")
