"""Appends the results added on 1 Nov 2026 to docs/headline_numbers.md: held-out v4, paraphrase set, retrieval v3
(pre-registered) with the adoption decision, and run-to-run stability. Each figure is read from the file that produced it."""
import math, re
from pathlib import Path

def wilson(k, n, z=1.96):
    if not n: return "-"
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return f"{100 * max(0, c - h):.0f}-{100 * min(1, c + h):.0f}%"

ev = Path("docs/eval_log_v3.md").read_text(encoding="utf-8") if Path("docs/eval_log_v3.md").exists() else ""
L = ["", "## Added 1 Nov 2026 (pre-registered before running)", "", "| Result | Value | Source |", "|---|---|---|"]
for label, name in (("heldout_v4", "Agents held-out v4"), ("paraphrase", "Agents paraphrase robustness"),
                    ("heldout_v5", "Agents held-out v5 (after gate 6; pre-registered 7 Nov)")):
    m = re.findall(rf"\|\s*[\d-]+ [\d:]+\s*\|\s*qwen2\.5:14b\s*\|\s*{label}\s*\|\s*(\d+)/(\d+)\s*\|\s*(\d+)\s*\|", ev)
    if m:
        # A held-out set counts once: its FIRST scored run. Later runs (after system changes) are shown as post-hoc.
        k, n, h = map(int, m[0]); L.append(f"| {name} (accuracy / harmful) | {k}/{n} ({wilson(k, n)}) / {h} | docs/eval_log_v3.md (first scored run) |")
        if len(m) > 1 and m[-1] != m[0]:
            k, n, h = map(int, m[-1]); L.append(f"| {name}, latest re-run (post-hoc, not held-out) | {k}/{n} ({wilson(k, n)}) / {h} | docs/eval_log_v3.md (latest run) |")
    else:
        L.append(f"| {name} | not yet run | docs/eval_log_v3.md |")
rt = Path("docs/retrieval_eval.md").read_text(encoding="utf-8") if Path("docs/retrieval_eval.md").exists() else ""
for tag in ("v3 HISN clause-first", "v3 HISN hybrid"):
    m = re.search(rf"{re.escape(tag)}\s+Recall@1 (\d+)/(\d+) \| Recall@3 \d+/\d+ \| Recall@5 (\d+)/\d+ \| MRR ([\d.]+)", rt)
    if m:
        r1, n, r5, mrr = int(m[1]), int(m[2]), int(m[3]), m[4]
        L.append(f"| Retrieval {tag[3:]} (pre-registered v3) | Recall@5 {r5}/{n} ({wilson(r5, n)}), Recall@1 {r1}/{n}, MRR {mrr} | docs/retrieval_eval.md |")
d = re.search(r"Decision: (.+)", rt)
if d: L.append(f"| Retrieval decision (rule committed before running) | {d[1].strip()} | docs/retrieval_decision_rule.md |")
st = Path("docs/stability.md").read_text(encoding="utf-8") if Path("docs/stability.md").exists() else ""
m = re.search(r"\*\*(\d+)/(\d+) agent decisions identical in every run\*\*", st)
L.append(f"| Run-to-run stability of agent decisions | {m[1]}/{m[2]} identical | docs/stability.md |" if m else "| Run-to-run stability | not yet run | docs/stability.md |")
hp = Path("docs/headline_numbers.md"); s = hp.read_text(encoding="utf-8") if hp.exists() else ""
s = s.split("\n## Added 1 Nov 2026")[0].rstrip("\n") + "\n" + "\n".join(L) + "\n"
hp.write_text(s, encoding="utf-8"); print("\n".join(L)); print("updated docs/headline_numbers.md")
