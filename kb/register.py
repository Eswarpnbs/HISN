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
  ("UAE-FL-2-2019", "Federal Law No. (2) of 2019 Concerning the Use of ICT in Health Fields", "UAE Federal Government", "AE", "federal_law", "FEDERAL_LAW",
   "https://uaelegislation.gov.ae/en/legislations/1209", "official"),
  ("UAE-TELECOM-2003", "Federal Decree-Law No. (3) of 2003 Regulating Telecommunications (as amended)", "UAE Federal Government", "AE", "federal_law", "FEDERAL_LAW",
   "https://uaelegislation.gov.ae/en/legislations/1132", "official"),
  ("UAE-CYBERCRIME-2021", "Federal Decree-Law No. (34) of 2021 on Countering Rumors and Cybercrimes (as amended)", "UAE Federal Government", "AE", "federal_law", "FEDERAL_LAW",
   "https://uaelegislation.gov.ae/en/legislations/1526", "official"),
  ("UAE-TDRA-UEC-2022", "Regulatory Policy: Unsolicited Electronic Communications v1.1", "TDRA", "AE", "regulatory_policy", "REGULATOR_POLICY",
   "https://tdra.gov.ae/-/media/About/regulations-and-ruling/EN/cellular-phone-spam-regulatory-policy-English.ashx", "official"),
  ("UAE-PDPL-2021", "Federal Decree-Law No. (45) of 2021 Concerning the Protection of Personal Data", "UAE Federal Government", "AE", "federal_law", "FEDERAL_LAW",
   "https://uaelegislation.gov.ae/en/legislations/1972/download", "official"),
  ("IN-DPDP-2023", "Digital Personal Data Protection Act, 2023 (No. 22 of 2023)", "Ministry of Electronics and IT, Government of India", "IN", "national_law", "NATIONAL_LAW",
   "https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf", "official"),
  ("IN-TELECOM-ACT-2023", "Telecommunications Act, 2023 (No. 44 of 2023)", "Government of India (Gazette)", "IN", "national_law", "NATIONAL_LAW",
   "https://egazette.gov.in/WriteReadData/2023/250880.pdf", "official_s20_s28_in_force_26jun2024_SO2408E"),
  ("IN-TRAI-TCCCPR-CONS", "Telecom Commercial Communications Customer Preference Regulations, 2018 - TRAI consolidated text (reference; gazetted text prevails)", "Telecom Regulatory Authority of India", "IN", "regulation", "REGULATOR_POLICY",
   "https://www.trai.gov.in/sites/default/files/2026-05/CA_21052026.pdf", "official_consolidated_reference_gazetted_text_prevails"),
  ("SG-SRF-2024", "Guidelines on Shared Responsibility Framework", "Monetary Authority of Singapore and Infocomm Media Development Authority", "SG", "guidelines", "REGULATOR_POLICY",
   "https://www.mas.gov.sg/regulation/guidelines/guidelines-on-shared-responsibility-framework", "official"),
  ("SG-PDPA-2012", "Personal Data Protection Act 2012 (current version as at 29 Oct 2026)", "Republic of Singapore (Singapore Statutes Online)", "SG", "national_law", "NATIONAL_LAW",
   "https://sso.agc.gov.sg/Act/PDPA2012", "official"),
  ("SA-CST-SPAM-2018", "Regulation for Reduction of SPAM (2018, draft English translation; Arabic prevails)", "Communications, Space and Technology Commission (CST)", "SA", "regulation", "REGULATOR_POLICY",
   "https://cst.gov.sa/ar/RulesandSystems/RegulatoryDocuments/ReductionofSPAM/Documents/IT%20008%20E%20-%20Regulation_For_The_Reduction_of_SPAM_Eng.pdf", "historical_draft_translation_possibly_superseded"),
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
