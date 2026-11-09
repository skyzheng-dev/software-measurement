"""Step 6: per-function static metrics from SciTools Understand.

For each dataset (COSMIC, MicroM):
  1. writes every usable function's `code_restored` to its own file,
     data/derived/functions/<dataset>/<id>.py (shared with step 7, Joern);
  2. builds an Understand database over that folder and runs `und metrics` with all metrics;
  3. keeps the one Function row per file that matches the labeled function (Understand names
     functions `<file stem>.<function>`, and nested defs show up as extra rows);
  4. writes data/derived/features/understand_<dataset>.csv (one row per id, metrics prefixed `und_`).

Note: CK metrics (WMC, CBO, LCOM, ...) are class-level and do not apply, because each sample is a
single function with its enclosing class removed. Understand reports function-level size and
complexity metrics instead. Coding-standard violation counts (CCViol*) are dropped.

Requires a licensed `und` on PATH (see tools/understand/README.md).
Run: uv run python scripts/06_extract_understand.py
"""

import shutil
import subprocess
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "derived" / "repaired"
FUNCS = ROOT / "data" / "derived" / "functions"
UND = ROOT / "data" / "derived" / "understand"
OUT = ROOT / "data" / "derived" / "features"

DATASETS = ["cosmic", "microm"]


def und(*args):
    res = subprocess.run(["und", *map(str, args)], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"und {' '.join(map(str, args))} failed:\n{res.stdout}\n{res.stderr}")
    return res.stdout


def write_functions(df, folder):
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)
    for row in df.itertuples():
        (folder / f"{row.id}.py").write_text(row.code_restored)


def run_understand(src, name):
    UND.mkdir(parents=True, exist_ok=True)
    db = UND / f"{name}.und"
    csv = UND / f"{name}_metrics.csv"
    if db.exists():
        shutil.rmtree(db)
    csv.unlink(missing_ok=True)
    und("create", "-db", db, "-languages", "python")
    und("add", src, db)
    # Understand defaults to Python 2 (PythonExe=`python`, which macOS does not have), and Python 2
    # rejects valid Python 3 syntax (print(..., file=...), async). All usable functions parse under
    # Python 3, so point it at a system python3. Not the project venv: Understand would then also
    # analyze torch & co. from site-packages.
    python3 = shutil.which("python3", path="/opt/homebrew/bin:/usr/local/bin:/usr/bin")
    und("settings", "-PythonSetVersion", "Python3", "-PythonExe", python3,
        "-metric", "all", "-metricsOutputFile", csv, db)
    log = und("analyze", db)
    print("   ", [line for line in log.splitlines() if "Analyze Completed" in line])
    und("metrics", db)
    return pd.read_csv(csv)


def select_rows(metrics, df):
    funcs = metrics[metrics["Kind"].str.contains("Function", na=False)].copy()
    wanted = df["id"] + "." + df["func_name"].str.split(".").str[-1]
    funcs = funcs[funcs["Name"].isin(set(wanted))]
    funcs["id"] = funcs["Name"].str.split(".").str[0]
    funcs = funcs.drop_duplicates("id")  # same-named redefinition in one file: keep the first
    drop = ["Kind", "Name"] + [c for c in funcs.columns if c.startswith(("CCViol", "CountCCViol"))]
    funcs = funcs.drop(columns=drop).dropna(axis=1, how="all")
    funcs = funcs.rename(columns={c: f"und_{c}" for c in funcs.columns if c != "id"})
    return funcs


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name in DATASETS:
        df = pd.read_csv(IN / f"code_{name}_repaired.csv")
        df = df[df["usable"]]
        src = FUNCS / name
        print(f"{name}: {len(df)} usable functions")
        write_functions(df, src)
        feats = select_rows(run_understand(src, name), df)
        missing = sorted(set(df["id"]) - set(feats["id"]))
        print(f"    metrics for {len(feats)}/{len(df)} functions, {feats.shape[1] - 1} metrics")
        if missing:
            print(f"    missing ({len(missing)}): {missing[:10]}{' ...' if len(missing) > 10 else ''}")
        feats.to_csv(OUT / f"understand_{name}.csv", index=False)


if __name__ == "__main__":
    main()
