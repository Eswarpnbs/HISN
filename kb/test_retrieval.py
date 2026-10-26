import os, sys, pathlib
sys.path.insert(0, str(pathlib.Path.home() / "ITUAIReadiness/simulation"))
from server.knowledge.kb import KnowledgeBase
from server.knowledge.ingest import embed_texts
kb = KnowledgeBase()
q = "Can health data be transferred or stored outside the UAE?"
r = kb.search(query_embedding=embed_texts([q])[0], n_results=3)
for doc, meta in zip(r["documents"][0], r["metadatas"][0]):
    print("-", meta.get("source_file"), "|", meta.get("article", ""), "|", doc[:120].replace("\n", " "))
