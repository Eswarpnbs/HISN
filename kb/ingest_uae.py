"""Ingest HISN's UAE corpus through the unmodified ITU reference pipeline.
Resets the KB, loads ITU framework + use-case docs, then UAE documents and verbatim clauses."""
import csv, os, sys, pathlib, yaml

ITU = pathlib.Path(os.environ.get("ITU_DIR", pathlib.Path.home() / "ITUAIReadiness/simulation"))
sys.path.insert(0, str(ITU))
from server.knowledge.kb import KnowledgeBase
from server.knowledge.ingest import (ingest_file, ingest_framework_definitions,
                                     ingest_usecase_docs, embed_texts)

ROOT = pathlib.Path(__file__).resolve().parent
CATEGORY = "UAE_Health_Telecom_Policies"

def main():
    kb = KnowledgeBase()
    kb.reset()
    print("Framework definitions:", ingest_framework_definitions(kb))
    uc = ingest_usecase_docs(kb)
    print("ITU use-case docs:", sum(uc.values()), "chunks")

    with open(ROOT / "manifest.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            pdf = ROOT / "sources" / f"{row['record_id']}.pdf"
            if not pdf.exists() or not row["sha256"]:
                print("SKIP", row["record_id"]); continue
            extra = {"country": "United Arab Emirates", "document_category": CATEGORY,
                     "record_id": row["record_id"], "issuer": row["issuer"],
                     "jurisdiction": row["jurisdiction"], "basis": row["basis"],
                     "verification": row["verification"], "sha256": row["sha256"]}
            n = ingest_file(pdf, kb, extra_metadata=extra)
            print(f"DOC   {row['record_id']:24s} {n} chunks")

    clauses = yaml.safe_load(open(ROOT / "clauses" / "clauses.yaml", encoding="utf-8"))
    texts = [c["text"] for c in clauses]
    metas = [{"source_file": f"{c['record_id']}.pdf", "country": "United Arab Emirates",
              "document_category": CATEGORY, "entity_type": "verbatim_clause",
              "clause_id": c["clause_id"], "record_id": c["record_id"], "article": c["article"],
              "basis": c["basis"], "dimension_id": int(c["dimension_ids"][0]),
              "factor": c["factor"], "metric_ids": ",".join(c["metric_ids"]),
              "y3172_nodes": ",".join(c["y3172_nodes"])} for c in clauses]
    kb.add_documents(texts=texts, embeddings=embed_texts(texts), metadatas=metas,
                     ids=[c["clause_id"] for c in clauses])
    print(f"CLAUSE {len(texts)} verbatim clauses stored")
    print("KB stats:", kb.stats())

if __name__ == "__main__":
    main()
