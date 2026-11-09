# SciTools Understand (CK metrics)

Understand is installed as a system app (`und`, `upython` on PATH). This folder holds
our own Understand scripts and metric plugins. Project databases (`*.und`) go in
`data/derived/` and are gitignored.

Per-function metrics for the labeled datasets: `uv run python scripts/06_extract_understand.py`.
It sets `PythonSetVersion=Python3` and `PythonExe` to a system `python3`; Understand's default
(`python`, absent on macOS) silently falls back to Python 2 parsing.
