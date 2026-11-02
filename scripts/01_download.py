"""Step 1: download the raw data for the data repair.

Downloads, at pinned versions so the result is reproducible:
  - the COSMIC- and MicroM-labeled Python functions released with the Stage 2 paper
    (github.com/smtnkc/CodeSizeBERT)
  - the Python part of CodeSearchNet (huggingface.co/datasets/code-search-net/code_search_net),
    the corpus those functions were originally taken from

Everything goes to data/raw/ (gitignored). Files that already exist are skipped.

Run: uv run python scripts/01_download.py
"""

import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

CODESIZEBERT_SHA = "c279c456bf28879de9f6f1475613262ab4dc0f5d"  # main on 2025-07-14
CSN_SHA = "bd0cf261e357a3eb5c8fba490d23ec1a1cd59555"  # main on 2026-02-23

DOWNLOADS = {
    RAW / "codesizebert" / name: f"https://raw.githubusercontent.com/smtnkc/CodeSizeBERT/{CODESIZEBERT_SHA}/data/{name}"
    for name in ["code_cosmic.csv", "code_microm.csv"]
} | {
    RAW / "codesearchnet" / "python" / name: (
        f"https://huggingface.co/datasets/code-search-net/code_search_net/resolve/{CSN_SHA}/python/{name}"
    )
    for name in [
        "train-00000-of-00001.parquet",
        "validation-00000-of-00001.parquet",
        "test-00000-of-00001.parquet",
    ]
}


def main():
    for dest, url in DOWNLOADS.items():
        if dest.exists():
            print(f"skip (exists)  {dest.relative_to(ROOT)}")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        print(f"downloading    {dest.relative_to(ROOT)}")
        tmp = dest.with_suffix(dest.suffix + ".part")
        urllib.request.urlretrieve(url, tmp)
        tmp.rename(dest)
    (RAW / "SOURCES.txt").write_text(
        f"CodeSizeBERT commit: {CODESIZEBERT_SHA}\nCodeSearchNet (HF) revision: {CSN_SHA}\n"
        + "".join(f"{p.relative_to(ROOT)} <- {u}\n" for p, u in DOWNLOADS.items())
    )


if __name__ == "__main__":
    main()
