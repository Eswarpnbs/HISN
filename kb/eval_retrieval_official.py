"""Retrieval on the UAE Government's own descriptions of its laws (kb/retrieval_gold_official.yaml, pre-registered).
Record-level Recall@1/@5 and MRR for the default (hybrid) and clause-first retrievers. Writes docs/retrieval_official.md.

    python kb/eval_retrieval_official.py
"""
import csv, datetime, sys, pathlib, yaml
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from app.agents.retriever import ItuRetriever

def wilson(k, n, z=1.96):
    import math
    if not n: return "n/a"
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return f"{100 * max(0, c - h):.0f}-{100 * min(1, c + h):.0f}%"

gold = yaml.safe_load(open("kb/retrieval_gold_official.yaml", encoding="utf-8"))
have = {r["record_id"] for r in csv.DictReader(open("kb/manifest.csv", encoding="utf-8")) if r["sha256"]}
run = [g for g in gold if any(e in have for e in g["expected"])]
skipped = [g for g in gold if g not in run]
lines = [f"# Retrieval on official UAE Government wording ({datetime.datetime.now():%Y-%m-%d %H:%M})", "",
         f"{len(gold)} pre-registered queries copied from u.ae; {len(run)} have their expected record in the KB "
         f"({len(skipped)} not in KB: {', '.join(g['expected'][0] for g in skipped) or 'none'}). Record-level scoring.", "",
         "| Retriever | Recall@1 | Recall@5 | MRR |", "|---|---|---|---|"]
for name, r in (("HISN hybrid (default)", ItuRetriever(k_clause=3, k_doc=5, hybrid=True)),
                ("HISN clause-first", ItuRetriever(k_clause=3, k_doc=5, hybrid=False))):
    r1 = r5 = 0; mrr = 0.0; miss = []
    for g in run:
        ranked = r(g["q"])[:5]
        rank = next((i + 1 for i, e in enumerate(ranked) if (e.get("record_id") or e["id"].split("#")[0]) in g["expected"]), None)
        r1 += rank == 1; r5 += rank is not None; mrr += 1 / rank if rank else 0
        if not rank: miss.append(g["q"][:60])
    n = len(run)
    lines.append(f"| {name} | {r1}/{n} ({wilson(r1, n)}) | {r5}/{n} ({wilson(r5, n)}) | {mrr / max(n, 1):.2f} |")
    if miss: lines.append(f"|  misses | {'; '.join(miss)} | | |")
pathlib.Path("docs/retrieval_official.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
