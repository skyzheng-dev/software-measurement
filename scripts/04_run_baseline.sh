#!/bin/bash
# Run the full CodeBERT baseline (scripts/04_baseline_codebert.py): every target on the released
# set first (the reproduction), then on the usable subset. Safe to rerun: finished folds are skipped.
# Run: bash scripts/04_run_baseline.sh   (takes several hours; progress goes to stdout)
set -e
cd "$(dirname "$0")/.."
for subset in released usable; do
  for target in entry read write exit; do
    uv run python scripts/04_baseline_codebert.py --subset "$subset" --target "$target"
  done
done
