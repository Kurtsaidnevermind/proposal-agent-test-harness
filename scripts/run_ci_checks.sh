#!/usr/bin/env bash
# Simple CI script to run dev checks: install deps, run tests, and compile grading results.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [ -f requirements-dev.txt ]; then
  python -m pip install -r requirements-dev.txt
fi

python -m pytest -q

# regenerate grading prompts and compile results
python scripts/prepare_grading.py
python scripts/compile_results.py

echo "CI checks passed."
