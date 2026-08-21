#!/usr/bin/env bash
# Simple CI script to run dev checks: install deps, run tests, and compile grading results.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [ -f requirements-dev.txt ]; then
  python -m pip install -r requirements-dev.txt
fi

python check_setup.py

python -m pytest -q

# regenerate grading prompts and compile results.
# Both exit non-zero when there is simply nothing to do yet (no outputs,
# no grades), which is a normal state for a fresh checkout, not a failure.
python scripts/prepare_grading.py || true
python scripts/compile_results.py || true

echo "CI checks passed."
