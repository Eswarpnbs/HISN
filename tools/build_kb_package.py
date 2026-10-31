"""Build open_kb/: HISN's contribution to the ITU AI for Good Lab open knowledge base (no source PDFs: they remain the
property of their issuers and are referenced by official URL and SHA-256)."""
import csv, hashlib, shutil, yaml
from pathlib import Path

OUT = Path("open_kb"); shutil.rmtree(OUT, ignore_errors=True); OUT.mkdir()
files = {"kb/manifest.csv": "records_manifest.csv", "kb/clauses/clauses.yaml": "verbatim_clauses.yaml",
         "docs/gap_register.yaml": "gap_register.yaml", "docs/global_examples.yaml": "global_examples.yaml",
         "kb/rulepacks/gap_mechanisms.yaml": "gap_coverage_by_country.yaml", "kb/retrieval_gold.yaml": "retrieval_test_questions.yaml",
         "kb/automation_levels.yaml": "automation_levels_y3173.yaml", "docs/agents.json": "agent_cards.json",
         "docs/datasheet_sms_dataset.md": "dataset_datasheet.md"}
for src, dst in files.items():
    shutil.copy(src, OUT / dst)
ds = next(Path("datasets").glob("**/hisn_synthetic_sms.csv"))
shutil.copy(ds, OUT / "hisn_synthetic_sms.csv")
recs = list(csv.DictReader(open("kb/manifest.csv", encoding="utf-8")))
cl = yaml.safe_load(open("kb/clauses/clauses.yaml", encoding="utf-8"))
by_country = {}
for r in recs:
    by_country[r.get("country", "?")] = by_country.get(r.get("country", "?"), 0) + 1
(OUT / "README.md").write_text(f"""# HISN open knowledge base contribution

Contributed by Team Sankalp to the ITU AI for Good Lab open knowledge base, **with acknowledgement to the United Arab Emirates**
for the leadership and coordination of the AI for Good Lab Hackathon (UAE edition, 2026).

**Domain:** governance of telecom AI that filters essential health and government messages (telecom, healthcare, public services).

## Contents
- `records_manifest.csv`: {len(recs)} official instruments ({", ".join(f"{k}: {v}" for k, v in sorted(by_country.items()))}) with official URLs and SHA-256 of the pinned source files
- `verbatim_clauses.yaml`: {len(cl)} provisions, each verified verbatim against its pinned source, with article, legal basis, Y.3172 nodes and Readiness metric IDs
- `gap_register.yaml`, `gap_coverage_by_country.yaml`, `global_examples.yaml`: domain-level policy gaps with evidence, country coverage and verified global examples
- `retrieval_test_questions.yaml`: 50 pre-registered retrieval questions (46 answerable, 4 out-of-corpus)
- `automation_levels_y3173.yaml`: declared ITU-T Y.3173 capability levels per component
- `agent_cards.json`: agent cards with ITU-T Y.3176-style metadata
- `hisn_synthetic_sms.csv` + `dataset_datasheet.md`: synthetic SMS governance dataset (CC-BY-4.0)
- `SHA256SUMS`: checksums of every file in this folder

## Licences and sources
HISN-authored metadata, gaps, questions and the dataset: CC-BY-4.0. Legal texts quoted in `verbatim_clauses.yaml` remain the
property of their issuers; source documents are not redistributed and can be obtained from the official URLs in the manifest.
Synthetic data only; no real messages, senders or people. Ingest with the ITU AI Readiness reference pipeline (CrashingGuru/ITUAIReadiness).
""", encoding="utf-8")
sums = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}" for p in sorted(OUT.iterdir()) if p.name != "SHA256SUMS"]
(OUT / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
print(f"built {OUT}/ with {len(sums)} files + SHA256SUMS: {len(recs)} records, {len(cl)} clauses")
