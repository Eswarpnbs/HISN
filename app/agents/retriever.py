import os, sys, pathlib
ITU = pathlib.Path(os.environ.get("ITU_DIR", pathlib.Path.home() / "ITUAIReadiness/simulation"))

class ItuRetriever:
    """Retrieves from the ITU reference KnowledgeBase, filtered to one country pack.
    Verbatim clauses are retrieved first (exact citation), then general document chunks."""
    def __init__(self, country="United Arab Emirates", k_clause=3, k_doc=2):
        sys.path.insert(0, str(ITU))
        from server.knowledge.kb import KnowledgeBase
        from server.knowledge.ingest import embed_texts
        self.kb, self.embed, self.country = KnowledgeBase(), embed_texts, country
        self.k_clause, self.k_doc = k_clause, k_doc

    def _search(self, emb, where, k):
        r = self.kb.search(query_embedding=emb, n_results=k, where=where)
        out = []
        for doc, meta, dist in zip(r["documents"][0], r["metadatas"][0], r["distances"][0]):
            eid = meta.get("clause_id") or f"{meta.get('record_id', '?')}#c{meta.get('chunk_index', '?')}"
            out.append({"id": eid, "text": doc, "similarity": round(1 - float(dist), 3),
                        "record_id": meta.get("record_id"), "article": meta.get("article", ""),
                        "basis": meta.get("basis", ""), "verbatim": "clause_id" in meta})
        return out

    def __call__(self, query):
        emb = self.embed([query])[0]
        clauses = self._search(emb, {"$and": [{"country": self.country}, {"entity_type": "verbatim_clause"}]}, self.k_clause)
        docs = self._search(emb, {"country": self.country}, self.k_doc + self.k_clause)
        seen = {e["id"] for e in clauses}
        return clauses + [d for d in docs if d["id"] not in seen][: self.k_doc]
