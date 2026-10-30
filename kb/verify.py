"""Re-hash every source in kb/sources against kb/manifest.csv. Exit code 1 on any mismatch."""
import csv, hashlib, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
bad = missing = present = 0
for m in csv.DictReader(open(ROOT / "manifest.csv", encoding="utf-8")):
    p = ROOT / "sources" / f"{m['record_id']}.pdf"
    if not p.exists():
        missing += 1
        print(f"MISSING  {m['record_id']}  (source files are not redistributed; fetch from: {m['url']})"); continue
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    ok = h == m["sha256"]
    bad += not ok; present += 1
    print(f"{'OK      ' if ok else 'MISMATCH'} {m['record_id']:<24} {h[:16]}…  ({m['verification']})")
if bad:
    print(f"\n{bad} MISMATCH(ES): a source differs from its pinned hash")
elif missing:
    print(f"\n{present} source(s) verified; {missing} not present locally (not redistributed). "
          "Download them from the URLs above into kb/sources/ to verify their hashes.")
else:
    print("\nALL SOURCES VERIFIED")
sys.exit(1 if bad else 0)
