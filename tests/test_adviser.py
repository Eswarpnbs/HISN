from app.agents.adviser import PolicyAdviser

class A:
    def __init__(self): self.rows = []
    def write(self, r): self.rows.append(r); return "h"

EV = [{"id": "UAE-FL-2-2019-ART16", "text": "t", "similarity": 0.7, "record_id": "UAE-FL-2-2019", "article": "Art. 16", "basis": "FEDERAL_LAW"},
      {"id": "UAE-AI-CHARTER-P6", "text": "t", "similarity": 0.6, "record_id": "UAE-AI-CHARTER-2024", "article": "P6", "basis": "SOFT_LAW"}]

def adv(out):
    return PolicyAdviser(lambda q: EV, lambda s, u: out, A())

def test_invented_citation_withheld():
    r = adv({"answer": "x", "cited_ids": ["FAKE-1"], "binding_basis_found": True}).answer("q")
    assert r["status"] == "CITATION_REJECTED" and "withheld" in r["answer"]

def test_soft_law_only_means_no_binding_basis_and_points_to_gap():
    r = adv({"answer": "x", "cited_ids": ["UAE-AI-CHARTER-P6"], "binding_basis_found": True, "related_gaps": ["G3"]}).answer("q")
    assert r["status"] == "NO_BINDING_BASIS" and r["related_gaps"] == ["G3"] and r["global_examples"]

def test_binding_answer():
    r = adv({"answer": "x", "cited_ids": ["UAE-FL-2-2019-ART16"], "binding_basis_found": True}).answer("q")
    assert r["status"] == "ANSWERED_WITH_BINDING_BASIS" and r["binding_ids"] == ["UAE-FL-2-2019-ART16"]
