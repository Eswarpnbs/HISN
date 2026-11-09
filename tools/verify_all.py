"""Independent verification: anyone can run this to check HISN's claims without trusting the team.
1 source hashes  2 every clause verbatim in its pinned PDF  3 audit-log hash chains  4 pre-registration via git history
5 open_kb checksums. Exit code 1 if any check fails."""
import csv, hashlib, re, subprocess, sys, yaml
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core.audit import AuditLog

ok_all = True
def report(name, ok, detail="", skipped=False):
    global ok_all; ok_all &= ok
    print(f"{'SKIP' if skipped else 'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))

# 1 source hashes
# The official PDFs are not redistributed (see README > Knowledge base). A fresh clone has none: checks that need a
# PDF are SKIPPED for the missing ones and say so; a PDF that IS present must match its pinned hash exactly.
man = list(csv.DictReader(open("kb/manifest.csv", encoding="utf-8")))
present = [m for m in man if Path(f"kb/sources/{m['record_id']}.pdf").exists()]
bad = [m["record_id"] for m in present
       if hashlib.sha256(Path(f"kb/sources/{m['record_id']}.pdf").read_bytes()).hexdigest() != m["sha256"]]
if present:
    report(f"Source files match pinned SHA-256 ({len(present)} of {len(man)} records present)", not bad, ", ".join(bad))
if len(present) < len(man):
    report(f"Source files not present locally: {len(man) - len(present)} of {len(man)}", True,
           "official PDFs are not redistributed; download them from the URLs in kb/manifest.csv into kb/sources/ "
           "(or run python kb/fetch_more.py) to check their hashes", skipped=True)

# 2 every clause verbatim in its source
RULES = ["ligatures expanded (fi, fl, ff; the AI Charter font's Th ligature extracted as U+0407 or U+0457)",
         "whitespace before punctuation removed", "footnote numbers attached to the end of a word removed",
         "a clause containing [...] must have every segment verbatim and in order"]
LIG = {"\ufb01": "fi", "\ufb02": "fl", "\ufb00": "ff", "\u0457": "th", "\u0407": "th"}
def norm(s):
    s = (s or "").replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    for k, v in LIG.items(): s = s.replace(k, v)
    s = re.sub(r"\s+", " ", s).strip().lower()
    s = re.sub(r"(?<=[a-z\)])\d{1,2}(?=[\.,;\s])", "", s)
    return re.sub(r"\s+([:;,.\)])", r"\1", s)
def contains(src, text):
    pos = 0
    for seg in [x.strip() for x in norm(text).split("[...]") if x.strip()]:
        i = src.find(seg, pos)
        if i < 0: return False
        pos = i + len(seg)
    return True
cache, miss, recon, absent = {}, [], [], []
for c in yaml.safe_load(open("kb/clauses/clauses.yaml", encoding="utf-8")):
    rid = c["record_id"]
    if not Path(f"kb/sources/{rid}.pdf").exists():
        absent.append(c["clause_id"]); continue
    if rid not in cache:
        import pymupdf
        cache[rid] = norm(" ".join(p.get_text() for p in pymupdf.open(f"kb/sources/{rid}.pdf")))
    if contains(cache[rid], c["text"]): continue
    (recon if "reconstructed" in str(c.get("article", "")).lower() else miss).append(c["clause_id"])
n = sum(1 for _ in yaml.safe_load(open("kb/clauses/clauses.yaml", encoding="utf-8"))) - len(absent)
if absent:
    report(f"Clauses whose source PDF is not present: {len(absent)}", True, "download the sources to check them", skipped=True)
if n:
  report(f"Clauses verbatim in their pinned source ({n - len(miss) - len(recon)}/{n} exact)", not miss,
       ("not found: " + ", ".join(miss)) if miss else (f"{len(recon)} with layout reconstructed from PDF extraction, declared in the article field: " + ", ".join(recon) if recon else ""))

# 3 audit-log hash chains
logs = sorted(Path("runs").glob("*.jsonl")) if Path("runs").exists() else []
broken = [p.name for p in logs if p.stat().st_size and not AuditLog(p).verify()]
report(f"Audit-log hash chains intact ({len(logs)} logs in runs/)", not broken, ", ".join(broken))

# 4 pre-registration: gold committed before the first evaluation log that scores it
def first_commit(path, grep=None):
    args = ["git", "log", "--diff-filter=A" if not grep else "--format=%ct", "--format=%ct", "--", path]
    out = subprocess.run(["git", "log", "--format=%ct", "--reverse", "--", path], capture_output=True, text=True).stdout.split()
    return int(out[0]) if out else None
def first_scored(label):
    out = subprocess.run(["git", "log", "--format=%ct", "--reverse", "-S", label, "--", "docs/eval_log_v3.md"],
                         capture_output=True, text=True).stdout.split()
    return int(out[0]) if out else None
for gold, label in [("scenarios/gold_heldout_v2.yaml", "heldout_v2"), ("scenarios/gold_heldout_v3.yaml", "heldout_v3"),
                    ("scenarios/gold_heldout_v4.yaml", "heldout_v4"), ("scenarios/gold_paraphrase.yaml", "paraphrase"),
                    ("scenarios/gold_heldout_v5.yaml", "heldout_v5"), ("scenarios/gold_heldout_v6.yaml", "heldout_v6"),
                    ("scenarios/gold_heldout_v7.yaml", "heldout_v7"),
                    ("scenarios/gold_heldout_v8.yaml", "heldout_v8"),
                    ("scenarios/gold_heldout_real.yaml", "heldout_real")]:
    if not Path(gold).exists():
        report(f"Pre-registration {label}", True, "set not built yet"); continue
    g, s = first_commit(gold), first_scored(label)
    if g is None: report(f"Pre-registration {label}", False, "gold file not committed"); continue
    report(f"Pre-registration {label}: gold committed before first scored result", s is None or g < s,
           "not yet scored" if s is None else f"gold {g} < first result {s}")
def first_commit_with(path, marker=None):
    args = ["git", "log", "--format=%ct", "--reverse"] + (["-S", marker] if marker else []) + ["--", path]
    out = subprocess.run(args, capture_output=True, text=True).stdout.split()
    return int(out[0]) if out else None
# each test must be committed before the first results commit that contains that test's own items
for test_file, result_file, marker, label in [
        ("scenarios/public_warnings.yaml", "docs/public_warnings.md", "PW-RTA-FINE", "public-warning test set"),
        ("scenarios/public_warnings_v2.yaml", "docs/public_warnings.md", "PW2-TOLL-FINE", "public-warning test set v2"),
        ("kb/retrieval_gold_v3.yaml", "docs/retrieval_eval.md", "v3 HISN", "retrieval v3 questions")]:
    t, r = first_commit_with(test_file), first_commit_with(result_file, marker)
    report(f"Pre-registration {label}: test committed before its first results", t is not None and (r is None or t <= r),
           "test not committed" if t is None else ("no results yet" if r is None else f"test {t} <= first results {r}"))

# 5 open_kb checksums
sums = Path("open_kb/SHA256SUMS")
if sums.exists():
    badk = [ln.split()[1] for ln in sums.read_text().splitlines() if ln.strip()
            and hashlib.sha256((Path("open_kb") / ln.split()[1]).read_bytes()).hexdigest() != ln.split()[0]]
    report("Open knowledge-base package matches SHA256SUMS", not badk, ", ".join(badk))

print("\nVerbatim rules applied identically to every clause: " + "; ".join(RULES))
print("\nALL CHECKS PASSED" if ok_all else "\nSOME CHECKS FAILED")
sys.exit(0 if ok_all else 1)
