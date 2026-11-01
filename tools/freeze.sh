#!/usr/bin/env bash
# Freeze run: regenerate every number and page from the final system. Run with Ollama up and the laptop plugged in.
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
mkdir -p runs; LOG="runs/freeze_$(date +%Y%m%d_%H%M).log"
exec > >(tee "$LOG") 2>&1
echo "== freeze run $(date) on commit $(git rev-parse --short HEAD)"
[ -z "$(git status --porcelain)" ] || { echo "Uncommitted changes: commit first"; exit 1; }
python -m pytest -q
python tools/verify_all.py
python run_agents.py --model qwen2.5:14b
python tools/stability.py --runs 3 --include-current
python run_baselines.py --model qwen2.5:14b && cp docs/baselines.md docs/baselines_14b.md
python selftest.py
python kb/eval_retrieval.py
python daily_report.py --policy none && python daily_report.py --policy adopted
python tools/fairness_check.py
python tools/filter_change_check.py --threshold 0.2 && python tools/filter_change_check.py --threshold 0.15
python tools/what_if.py --policy none && python tools/what_if.py --policy adopted
python tools/cross_border.py
python tools/automation_report.py && python tools/build_datasheet.py
python build_agent_cards.py && python tools/build_kb_package.py
python build_dashboard.py && python build_report_site.py
python -m pytest -q
echo "== freeze run finished $(date). Log: $LOG"
