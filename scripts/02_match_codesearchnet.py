"""Step 2: restore the original source of each labeled function from CodeSearchNet.

The released labeled data (CodeSizeBERT) stores each function with its docstring moved to a
separate column, comments removed, and (for COSMIC) indentation flattened, so most functions are
no longer valid Python. Each function is matched back to its CodeSearchNet record, which gives the
original source, the repository it came from, and its file path.

Matching:
  - key = the code with all whitespace removed. For CodeSearchNet the key is built from
    `func_code_tokens` (which already excludes the docstring) after dropping comment tokens.
  - "exact": the keys are identical.
  - "fuzzy": no exact key; among CodeSearchNet functions with the same signature (the text up to the
    first ':'), take the one whose key is most similar. The released code also had every
    triple-quoted string removed (not only docstrings; e.g. embedded SQL), so the similarity ratio
    is computed with triple-quoted strings (and any leftover r/b/u/f prefix) removed from both keys.
  - "fuzzy_name": no function with the same signature (e.g. comments inside the signature); same
    as "fuzzy" but candidates are the functions with the same bare name.
  - "none": no candidate at all.

A row is `usable` when the match is exact, or fuzzy with ratio >= MIN_RATIO, and the restored
source parses as Python 3. Fuzzy matches below MIN_RATIO were all checked by hand on 2026-11-01:
the one COSMIC case (run_instances) is a correct match whose labeled copy kept a 27k-character
docstring; it is still left out because its body is only `pass`.

Labels and the original `code` text are kept unchanged; the restored source is added next to them.

Run: uv run python scripts/02_match_codesearchnet.py
Output: data/derived/repaired/code_{cosmic,microm}_repaired.csv
"""

import ast
import difflib
import re
import warnings
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "derived" / "repaired"

DATASETS = ["code_cosmic", "code_microm"]
MIN_RATIO = 0.80
CSN_COLUMNS = [
    "repository_name",
    "func_path_in_repository",
    "func_name",
    "whole_func_string",
    "func_code_tokens",
    "split_name",
    "func_code_url",
]

WHITESPACE = re.compile(r"\s+")
TRIPLE_QUOTED = re.compile(r'[rRbBuUfF]{0,2}("""|\'\'\')(?:.|\n)*?\1')


def key_from_text(code):
    return WHITESPACE.sub("", code)


def key_from_tokens(tokens):
    return WHITESPACE.sub("", "".join(t for t in tokens if not t.startswith("#")))


def without_triple_quoted(key):
    return TRIPLE_QUOTED.sub("", key)


def signature(code):
    return WHITESPACE.sub("", code.split(":", 1)[0])


def bare_name(code):
    m = re.match(r"\s*(?:async\s+)?def\s+(\w+)", code)
    return m.group(1) if m else None


def parses(code):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False


def load_codesearchnet():
    files = sorted((RAW / "codesearchnet" / "python").glob("*.parquet"))
    csn = pd.concat([pd.read_parquet(f, columns=CSN_COLUMNS) for f in files], ignore_index=True)
    csn["key"] = csn.func_code_tokens.map(key_from_tokens)
    csn["sig"] = csn.whole_func_string.map(signature)
    csn["name"] = csn.whole_func_string.map(bare_name)
    return csn.drop(columns="func_code_tokens")


def match(labeled, csn, by_key, by_sig, by_name):
    rows = []
    for code in labeled.code:
        k = key_from_text(code)
        if k in by_key:
            idx = by_key[k]
            # Identical keys can occur for copied functions; take the first and record how many.
            rows.append(("exact", 1.0, idx[0], len(idx)))
            continue
        match_type = "fuzzy"
        candidates = by_sig.get(signature(code), [])
        if len(candidates) == 0:
            match_type = "fuzzy_name"
            candidates = by_name.get(bare_name(code), [])
        if len(candidates) == 0:
            rows.append(("none", float("nan"), None, 0))
            continue
        k_bare = without_triple_quoted(k)
        ratios = [
            difflib.SequenceMatcher(None, k_bare, without_triple_quoted(csn.key.iat[j]), autojunk=False).ratio()
            for j in candidates
        ]
        best = max(range(len(candidates)), key=ratios.__getitem__)
        rows.append((match_type, ratios[best], candidates[best], len(candidates)))
    return pd.DataFrame(rows, columns=["match_type", "match_ratio", "csn_index", "n_candidates"])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    csn = load_codesearchnet()
    by_key = csn.groupby("key").indices
    by_sig = csn.groupby("sig").indices
    by_name = csn.groupby("name").indices

    for name in DATASETS:
        labeled = pd.read_csv(RAW / "codesizebert" / f"{name}.csv")
        m = match(labeled, csn, by_key, by_sig, by_name)
        hit = csn.iloc[m.csn_index.dropna().astype(int)].reset_index(drop=True)
        hit.index = m.index[m.csn_index.notna()]
        out = labeled.copy()
        out.insert(0, "id", [f"{name}_{i:04d}" for i in range(len(out))])
        out["code_parses"] = out.code.map(parses)
        out["code_restored"] = hit.whole_func_string
        out["restored_parses"] = out.code_restored.map(lambda s: parses(s) if isinstance(s, str) else False)
        out["repository"] = hit.repository_name
        out["path"] = hit.func_path_in_repository
        out["func_name"] = hit.func_name
        out["url"] = hit.func_code_url
        out["csn_split"] = hit.split_name
        out = pd.concat([out, m[["match_type", "match_ratio", "n_candidates"]]], axis=1)
        out["usable"] = (out.match_ratio >= MIN_RATIO) & out.restored_parses
        out.to_csv(OUT / f"{name}_repaired.csv", index=False)

        print(f"\n{name}: {len(out)} functions")
        print(out.match_type.value_counts().to_string())
        print(f"  original code parses:  {out.code_parses.sum()}")
        print(f"  restored code parses:  {out.restored_parses.sum()}")
        print(f"  usable:                {out.usable.sum()}")
        print(f"  distinct repositories: {out.repository.nunique()} (usable: {out[out.usable].repository.nunique()})")


if __name__ == "__main__":
    main()
