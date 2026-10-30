"""Recall@k and MRR on kb/retrieval_gold.yaml: HISN clause-first retriever vs plain ITU kb.search (UAE filter)."""
import sys, pathlib, datetime, yaml
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from app.agents.retriever import ItuRetriever

gold = yaml.safe_load(open("kb/retrieval_gold.yaml", encoding="utf-8"))
r = ItuRetriever(k_clause=3, k_doc=5)

def plain(q, k=5):
    res = r.kb.search(query_embedding=r.embed([q])[0], n_results=k, where={"country": r.country})
    return [{"id": m.get("clause_id") or f"{m.get('record_id')}#c{m.get('chunk_index')}", "similarity": round(1 - float(d), 3), "text": doc}
            for doc, m, d in zip(res["documents"][0], res["metadatas"][0], res["distances"][0])]

def clause_first(q):
    return r(q)[:5]  # retriever order, exactly as the agents receive evidence: verbatim clauses first

import re as _re
_norm = lambda s: _re.sub(r"\s+", " ", str(s)).strip().lower()
CLAUSE_TEXT = {c["clause_id"]: _norm(c["text"])[:80] for c in yaml.safe_load(open("kb/clauses/clauses.yaml", encoding="utf-8"))}

def hit(e, expected, lenient=False):
    """Strict: the exact clause (or any chunk of an expected RECORD#). Lenient: also a passage containing the clause text."""
    eid = e["id"]
    if any(eid == x or (x.endswith("#") and eid.startswith(x)) for x in expected):
        return True
    return lenient and any(x in CLAUSE_TEXT and CLAUSE_TEXT[x] in _norm(e.get("text", "")) for x in expected)

def evaluate(fn, name, lenient=False):
    rec = {1: 0, 3: 0, 5: 0}; mrr = 0.0; inq = [g for g in gold if g["expected"]]; neg = []
    for g in gold:
        ranked = fn(g["q"])
        if not g["expected"]:
            neg.append(ranked[0]["similarity"] if ranked else 0); continue
        rank = next((i + 1 for i, e in enumerate(ranked) if hit(e, g["expected"], lenient)), None)
        for k in rec: rec[k] += rank is not None and rank <= k
        mrr += 1 / rank if rank else 0
    n = len(inq)
    line = (f"{name:<22} Recall@1 {rec[1]}/{n} | Recall@3 {rec[3]}/{n} | Recall@5 {rec[5]}/{n} | MRR {mrr/n:.2f} "
            f"| out-of-corpus top similarity {', '.join(str(x) for x in neg)}")
    print(line); return line

lines = [evaluate(plain, "plain ITU search"), evaluate(plain, "plain, passage contains clause", lenient=True), evaluate(clause_first, "HISN clause-first")]
with open("docs/retrieval_eval.md", "w", encoding="utf-8") as f:
    f.write(f"# Retrieval evaluation ({datetime.datetime.now():%Y-%m-%d %H:%M})\n\n{len(gold)} questions "
            f"({sum(1 for g in gold if g['expected'])} in-corpus, {sum(1 for g in gold if not g['expected'])} out-of-corpus). nomic-embed-text via ITU pipeline.\n\n")
    for l in lines: f.write(f"- {l}\n")
print("written docs/retrieval_eval.md")
