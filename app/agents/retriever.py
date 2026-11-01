import os, sys, pathlib, re, math
import yaml
ITU = pathlib.Path(os.environ.get("ITU_DIR", pathlib.Path.home() / "ITUAIReadiness/simulation"))

class ItuRetriever:
    """Retrieves from the ITU reference KnowledgeBase, filtered to one country pack.
    Verbatim clauses are retrieved first (exact citation), then general document chunks."""
    def __init__(self, country="United Arab Emirates", k_clause=3, k_doc=2, hybrid=True):
        sys.path.insert(0, str(ITU))
        from server.knowledge.kb import KnowledgeBase
        from server.knowledge.ingest import embed_texts
        self.kb, self.embed, self.country = KnowledgeBase(), embed_texts, country
        self.k_clause, self.k_doc = k_clause, k_doc
        self.hybrid = hybrid
        if hybrid:  # BM25 index over this country's verbatim clauses (textbook parameters, not tuned)
            pre = {"United Arab Emirates": "UAE-", "India": "IN-", "Singapore": "SG-"}.get(country, "UAE-")
            cl = yaml.safe_load(open(pathlib.Path(__file__).resolve().parents[2] / "kb/clauses/clauses.yaml", encoding="utf-8"))
            self._bm = {c["clause_id"]: self._tok(c["text"] + " " + str(c.get("article", ""))) for c in cl if c["record_id"].startswith(pre)}
            self._avg = sum(len(v) for v in self._bm.values()) / max(len(self._bm), 1)
            self._df = {}
            for toks in self._bm.values():
                for w in set(toks): self._df[w] = self._df.get(w, 0) + 1

    STOP = set("the a an of to in on for and or is are be by with as at from that this which any shall may can its it their "
               "what who how when does do must if not no into than such other under".split())
    @classmethod
    def _tok(cls, s): return [w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 1 and w not in cls.STOP]

    def _bm25(self, query, k1=1.5, b=0.75):
        q, N, out = set(self._tok(query)), len(self._bm), {}
        for cid, toks in self._bm.items():
            sc = 0.0
            for w in q:
                tf = toks.count(w)
                if tf:
                    idf = math.log(1 + (N - self._df[w] + 0.5) / (self._df[w] + 0.5))
                    sc += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * len(toks) / self._avg))
            out[cid] = sc
        return out

    def _hybrid_clauses(self, query, emb, c=60):
        n = max(self.k_clause, min(50, len(self._bm)))
        cand = self._search(emb, {"$and": [{"country": self.country}, {"entity_type": "verbatim_clause"}]}, n)
        er = {e["id"]: i for i, e in enumerate(cand)}
        bm = sorted(((k, v) for k, v in self._bm25(query).items() if v > 0), key=lambda x: -x[1])
        br = {k: i for i, (k, _) in enumerate(bm)}
        fused = {k: sum(1 / (c + r + 1) for r in (er.get(k), br.get(k)) if r is not None) for k in set(er) | set(br)}
        by = {e["id"]: e for e in cand}
        return [by[k] for k in sorted(fused, key=lambda k: -fused[k]) if k in by][: self.k_clause]

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
        clauses = (self._hybrid_clauses(query, emb) if self.hybrid else
                   self._search(emb, {"$and": [{"country": self.country}, {"entity_type": "verbatim_clause"}]}, self.k_clause))
        docs = self._search(emb, {"country": self.country}, self.k_doc + self.k_clause)
        seen = {e["id"] for e in clauses}
        return clauses + [d for d in docs if d["id"] not in seen][: self.k_doc]
