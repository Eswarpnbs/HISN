"""Ingest HISN's country corpora (UAE, India) through the unmodified ITU reference pipeline.
Resets the KB, loads ITU framework + use-case docs, then each record and verbatim clause tagged with its country."""
import csv, os, sys, pathlib, yaml

ITU = pathlib.Path(os.environ.get("ITU_DIR", pathlib.Path.home() / "ITUAIReadiness/simulation"))
sys.path.insert(0, str(ITU))
from server.knowledge.kb import KnowledgeBase
from server.knowledge.ingest import ingest_file, ingest_framework_definitions, ingest_usecase_docs, embed_texts

ROOT = pathlib.Path(__file__).resolve().parent
COUNTRY = {"UAE": "United Arab Emirates", "IN": "India", "SG": "Singapore", "SA": "Saudi Arabia",
           "AU": "Australia", "EU": "European Union"}
CATEGORY = {"UAE": "UAE_Health_Telecom_Policies", "IN": "India_Health_Telecom_Policies", "SG": "Singapore_Health_Telecom_Policies", "SA": "Saudi_Arabia_Historical",
            "AU": "Global_Examples", "EU": "Global_Examples"}
pre = lambda rid: rid.split("-")[0]

def main():
    kb = KnowledgeBase()
    kb.reset()
    print("Framework definitions:", ingest_framework_definitions(kb))
    print("ITU use-case docs:", sum(ingest_usecase_docs(kb).values()), "chunks")
    with open(ROOT / "manifest.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            pdf = ROOT / "sources" / f"{row['record_id']}.pdf"
            if not pdf.exists() or not row["sha256"]:
                print("SKIP", row["record_id"]); continue
            c = pre(row["record_id"])
            arabic = row["record_id"].endswith("-AR")
            country = COUNTRY[c] + (" (Arabic)" if arabic else "")
            category = "UAE_Arabic_Authoritative_Text" if arabic else CATEGORY[c]
            extra = {"country": country, "document_category": category, "record_id": row["record_id"], "language": "ar" if arabic else "en",
                     "issuer": row["issuer"], "jurisdiction": row["jurisdiction"], "basis": row["basis"],
                     "verification": row["verification"], "sha256": row["sha256"]}
            print(f"DOC   {row['record_id']:24s} {ingest_file(pdf, kb, extra_metadata=extra)} chunks ({country})")
    clauses = yaml.safe_load(open(ROOT / "clauses" / "clauses.yaml", encoding="utf-8"))
    texts = [c["text"] for c in clauses]
    metas = [{"source_file": f"{c['record_id']}.pdf", "country": COUNTRY[pre(c["record_id"])],
              "document_category": CATEGORY[pre(c["record_id"])], "entity_type": "verbatim_clause",
              "clause_id": c["clause_id"], "record_id": c["record_id"], "article": c["article"],
              "basis": c["basis"], "dimension_id": int(c["dimension_ids"][0]), "factor": c["factor"],
              "metric_ids": ",".join(c["metric_ids"]), "y3172_nodes": ",".join(c["y3172_nodes"])} for c in clauses]
    kb.add_documents(texts=texts, embeddings=embed_texts(texts), metadatas=metas, ids=[c["clause_id"] for c in clauses])
    by = {}
    for m in metas: by[m["country"]] = by.get(m["country"], 0) + 1
    print(f"CLAUSE {len(texts)} verbatim clauses stored {by}")
    print("KB stats:", kb.stats())

if __name__ == "__main__":
    main()
