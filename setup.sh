#!/bin/bash
# HISN one-command setup from a fresh clone. Synthetic data only.
set -e
echo "== HISN setup =="
command -v python3 >/dev/null || { echo "Python 3.10+ required"; exit 1; }
python3 -c 'import sys; assert sys.version_info >= (3,10), "Python 3.10+ required"'
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
[ -d "$HOME/ITUAIReadiness" ] || git clone https://github.com/CrashingGuru/ITUAIReadiness.git "$HOME/ITUAIReadiness"
pip install -q -r requirements.txt
command -v ollama >/dev/null || { echo "Install Ollama from https://ollama.com/download, then re-run"; exit 1; }
ollama pull nomic-embed-text
ollama pull qwen2.5:14b
echo "== verifying knowledge-base sources (PDFs are not redistributed; see README > Knowledge base) =="
python kb/verify.py || echo "Some sources missing: download them from the URLs in kb/manifest.csv into kb/sources/"
echo "== building the knowledge base with the ITU reference ingest pipeline =="
python kb/ingest_uae.py
echo "== tests =="
python -m pytest -q
echo "== done. Try: python run_demo.py | python inject_console.py | python run_gap_engine.py | python selftest.py =="
