"""Step 10: Understand on a small, complete real project (Flaskr), compared with a hand COSMIC count.

Advisor request (2026-11-15): try the tools on a toy example or a small real GitHub project while the
training environment is being set up. Flaskr is the official tutorial app of Flask (BSD-3-Clause):
a ~200-line blog with registration, login and a two-table SQLite database. Unlike the labeled
dataset, the code is analyzed as a whole project, so Understand sees files, imports and call
relations, not isolated functions.

Steps:
  1. sparse-clone pallets/flask at a pinned commit into data/raw/projects/flask (gitignored);
  2. build an Understand database over examples/tutorial/flaskr (app code only, tests excluded);
  3. export all metrics for every entity (data/derived/understand/flaskr_metrics.csv);
  4. join the function rows with the hand COSMIC count in labels/flaskr_cosmic_draft.csv
     (a DRAFT by the assistant, to be checked by the researcher);
  5. write figures/flaskr/: entities.csv, functions.csv, fig1_cosmic_vs_understand.png.

Run: uv run python scripts/10_understand_flaskr.py
"""

import shutil
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / "data" / "raw" / "projects" / "flask"
COMMIT = "49943b5a94413a530761350f04e896f76e8d620e"
SRC = REPO / "examples" / "tutorial" / "flaskr"
UND = ROOT / "data" / "derived" / "understand"
LABELS = ROOT / "labels" / "flaskr_cosmic_draft.csv"
OUT = ROOT / "figures" / "flaskr"

KEEP = {  # Understand metric -> plain name
    "CountLineCode": "lines of code",
    "CountStmtExe": "statements",
    "Cyclomatic": "branches (cyclomatic)",
    "MaxNesting": "max nesting",
    "CountInput": "fan-in",
    "CountOutput": "fan-out",
}

BLUE, GRAY = "#2a78d6", "#c3c2b7"
TEXT, TEXT_2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update(
    {
        "font.size": 10.5,
        "axes.edgecolor": GRID,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.color": TEXT_2,
        "ytick.color": TEXT,
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.3,
    }
)


def run(cmd, cwd=None):
    res = subprocess.run(list(map(str, cmd)), capture_output=True, text=True, cwd=cwd)
    if res.returncode != 0:
        raise RuntimeError(f"{' '.join(map(str, cmd))} failed:\n{res.stdout}\n{res.stderr}")
    return res.stdout


def fetch():
    if not REPO.exists():
        REPO.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "-q", "--filter=blob:none", "--sparse",
             "https://github.com/pallets/flask.git", REPO])
        run(["git", "sparse-checkout", "set", "examples/tutorial"], cwd=REPO)
    head = run(["git", "rev-parse", "HEAD"], cwd=REPO).strip()
    if head != COMMIT:
        run(["git", "fetch", "-q", "--depth", "1", "origin", COMMIT], cwd=REPO)
        run(["git", "checkout", "-q", COMMIT], cwd=REPO)


def understand():
    UND.mkdir(parents=True, exist_ok=True)
    db, csv = UND / "flaskr.und", UND / "flaskr_metrics.csv"
    if db.exists():
        shutil.rmtree(db)
    csv.unlink(missing_ok=True)
    run(["und", "create", "-db", db, "-languages", "python"])
    run(["und", "add", SRC, db])
    # Same Python 3 fix as step 6: Understand otherwise falls back to Python 2 parsing.
    python3 = shutil.which("python3", path="/opt/homebrew/bin:/usr/local/bin:/usr/bin")
    run(["und", "settings", "-PythonSetVersion", "Python3", "-PythonExe", python3,
         "-metric", "all", "-metricsOutputFile", csv, db])
    run(["und", "analyze", db])
    run(["und", "metrics", db])
    return pd.read_csv(csv)


def figure(df):
    df = df.sort_values("cfp")
    panels = [("cfp", "COSMIC size (CFP, draft)", BLUE),
              ("CountLineCode", "Lines of code", GRAY),
              ("Cyclomatic", "Branches (cyclomatic)", GRAY)]
    fig, axes = plt.subplots(1, 3, figsize=(10, 4.2), sharey=True)
    fig.subplots_adjust(left=0.17, right=0.98, top=0.72, wspace=0.25)
    y = range(len(df))
    for ax, (col, title, color) in zip(axes, panels):
        vals = df[col].to_numpy()
        ax.barh(y, vals, color=color, height=0.62)
        for i, v in zip(y, vals):
            ax.text(v + vals.max() * 0.03, i, f"{v:g}", va="center", fontsize=9.5, color=TEXT_2)
        ax.set_title(title, fontsize=11, color=TEXT, loc="left")
        ax.set_xlim(0, vals.max() * 1.25)
        ax.tick_params(axis="y", length=0)
        ax.spines["left"].set_visible(False)
        ax.xaxis.grid(True, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
    axes[0].set_yticks(list(y), df["process"])
    rho = df[["cfp", "CountLineCode", "Cyclomatic"]].corr("spearman")["cfp"]
    fig.text(0.01, 0.99, "Flaskr: COSMIC size vs. what Understand measures", fontsize=15,
             fontweight="bold", color=TEXT, va="top")
    fig.text(0.01, 0.905, f"Each row is one user-facing feature of the app. Spearman correlation with COSMIC size: "
             f"lines of code {rho['CountLineCode']:.2f},\nbranches {rho['Cyclomatic']:.2f} "
             f"(only {len(df)} features, so these are illustrative, not evidence).",
             fontsize=10.5, color=TEXT_2, va="top", linespacing=1.4)
    fig.text(0.01, -0.02, "COSMIC counts are a draft hand count (labels/flaskr_cosmic_draft.csv), not yet "
             "verified. Flaskr from pallets/flask @ 49943b5, BSD-3-Clause.",
             fontsize=8.5, color=TEXT_2, va="top")
    fig.savefig(OUT / "fig1_cosmic_vs_understand.png")
    plt.close(fig)
    return rho


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fetch()
    m = understand()

    kinds = m["Kind"].fillna("").str.replace(r"^(Python )", "", regex=True)
    entities = kinds.value_counts().rename_axis("kind").reset_index(name="count")
    entities.to_csv(OUT / "entities.csv", index=False)
    print("entities:", dict(zip(entities["kind"], entities["count"])))

    funcs = m[m["Kind"].str.contains("Function", na=False)].copy()
    funcs["function"] = funcs["Name"].str.split(".").str[-1]
    cols = [c for c in KEEP if c in funcs.columns]
    labels = pd.read_csv(LABELS)
    table = funcs[["Name", "function"] + cols].merge(labels, on="function", how="left")
    table["is_cosmic_process"] = table["process"].notna()
    table.sort_values(["is_cosmic_process", "Name"], ascending=[False, True]).to_csv(
        OUT / "functions.csv", index=False)
    procs = table[table["is_cosmic_process"]]
    missing = set(labels["function"]) - set(procs["function"])
    if missing:
        raise SystemExit(f"labeled functions not found by Understand: {missing}")
    print(f"functions: {len(table)} found, {len(procs)} are COSMIC functional processes, "
          f"{len(table) - len(procs)} are helpers")

    rho = figure(procs)
    print("Spearman with CFP:", rho.round(2).to_dict())


if __name__ == "__main__":
    main()
