"""Policy and legal adviser: answers a question using only retrieved, verified evidence. Deterministic code checks that
every citation was retrieved and that a binding-basis claim rests on a binding source; otherwise it reports no binding
basis and points to the related gap and its verified global examples."""
import csv, yaml
from .institution import BINDING

SYSTEM = """You are a policy and legal adviser in a governance simulation (synthetic data only).
Answer the QUESTION using ONLY the EVIDENCE. Cite evidence by its exact id in "cited_ids". Never invent laws, articles or ids.
If the evidence does not give a binding legal basis for what is asked, say so plainly and set "binding_basis_found" to false.
If the question relates to any of these known policy gaps, list their ids in "related_gaps": {gaps}
Reply with JSON only:
{{"answer": "...", "cited_ids": ["..."], "binding_basis_found": true, "related_gaps": ["..."], "uncertainty": "low|medium|high"}}"""

def _gaps(path="docs/gap_register.yaml"):
    data = yaml.safe_load(open(path, encoding="utf-8"))
    items = data if isinstance(data, list) else data.get("gaps", [])
    return {g["id"]: g.get("title", "") for g in items if isinstance(g, dict) and "id" in g}

def _examples(path="docs/global_examples.yaml"):
    return yaml.safe_load(open(path, encoding="utf-8"))["examples"]

class PolicyAdviser:
    def __init__(self, retriever, llm, audit):
        self.retriever, self.llm, self.audit = retriever, llm, audit
        self.gaps, self.examples = _gaps(), _examples()
        self.urls = {m["record_id"]: m["url"] for m in csv.DictReader(open("kb/manifest.csv", encoding="utf-8"))}

    def answer(self, question):
        evidence = self.retriever(question)
        ev = {e["id"]: e for e in evidence}
        ev_text = "\n".join(f"[{e['id']}] ({e['basis']} {e['article']}) {e['text'][:600]}" for e in evidence)
        gaps_txt = "; ".join(f"{k}: {v}" for k, v in self.gaps.items())
        try:
            out = self.llm(SYSTEM.format(gaps=gaps_txt), f"QUESTION:\n{question}\n\nEVIDENCE:\n{ev_text}")
        except Exception as ex:
            out = {"answer": "", "cited_ids": [], "binding_basis_found": False, "related_gaps": [], "error": str(ex)}
        cited = [c for c in out.get("cited_ids", []) if isinstance(c, str)]
        valid, rejected = [c for c in cited if c in ev], [c for c in cited if c not in ev]
        binding = [c for c in valid if ev[c].get("basis") in BINDING]
        if rejected:
            status, answer = "CITATION_REJECTED", "(withheld: the model cited sources that were not retrieved)"
        elif out.get("binding_basis_found") and binding:
            status, answer = "ANSWERED_WITH_BINDING_BASIS", str(out.get("answer", ""))
        else:
            status, answer = "NO_BINDING_BASIS", str(out.get("answer", ""))
        gaps = [g for g in out.get("related_gaps", []) if g in self.gaps]
        examples = [e for e in self.examples if e["gap"] in gaps and e["status"] == "verified_official"]
        rec = {"question": question[:500], "status": status, "answer": answer[:1200],
               "cited_ids": valid, "binding_ids": binding, "rejected_citations": rejected, "related_gaps": gaps,
               "global_examples": [{"gap": e["gap"], "jurisdiction": e["jurisdiction"], "instrument": e["instrument"],
                                    "url": e["url"]} for e in examples],
               "evidence": [{"id": e["id"], "article": e["article"], "basis": e["basis"], "similarity": e["similarity"], "url": self.urls.get(e.get("record_id"), "")}
                            for e in evidence],
               "uncertainty": out.get("uncertainty")}
        self.audit.write({"kind": "adviser_answer", **rec})
        return rec
