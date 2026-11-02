"""Step 3: summarize the data repair as a table and figures.

Reads data/derived/repaired/*.csv (from scripts/02_match_codesearchnet.py) and writes, into
figures/data_repair/ (tracked in git, unlike data/):
  - summary.csv                   counts reported in PAPER.md Section 3.2
  - fig1_match_outcome.png        how each labeled function was matched
  - fig2_valid_python.png         functions that parse as Python 3, before and after the repair
  - fig3_cosmic_labels.png        distribution of each COSMIC label in the usable set
  - fig4_functions_per_repo.png   how many functions each repository contributes

Run: uv run python scripts/03_report_repair.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "derived" / "repaired"
OUT = ROOT / "figures" / "data_repair"

DATASETS = {"code_cosmic": "COSMIC", "code_microm": "MicroM"}

# Reference palette (dataviz skill, light mode), categorical slots in fixed order.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]
MUTED = "#c3c2b7"
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"
GRID = "#e4e3df"

plt.rcParams.update(
    {
        "font.size": 10,
        "axes.edgecolor": GRID,
        "axes.labelcolor": TEXT_2,
        "axes.titlecolor": TEXT,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.color": TEXT_2,
        "ytick.color": TEXT_2,
        "legend.frameon": False,
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    }
)


def load():
    return {label: pd.read_csv(IN / f"{name}_repaired.csv") for name, label in DATASETS.items()}


def summarize(data):
    rows = []
    for label, d in data.items():
        rows.append(
            {
                "dataset": label,
                "functions": len(d),
                "exact": (d.match_type == "exact").sum(),
                "fuzzy": d.match_type.str.startswith("fuzzy").sum(),
                "unmatched": (d.match_type == "none").sum(),
                "parses_before": d.code_parses.sum(),
                "parses_after": d.restored_parses.sum(),
                "usable": d.usable.sum(),
                "repositories_usable": d[d.usable].repository.nunique(),
                "max_functions_per_repo": d[d.usable].repository.value_counts().max(),
            }
        )
    return pd.DataFrame(rows)


def save(fig, name):
    fig.savefig(OUT / name, facecolor="white")
    plt.close(fig)


def fig_match_outcome(data):
    labels = list(data)
    parts = {
        "Exact match": [((d.match_type == "exact") & d.usable).sum() for d in data.values()],
        "Fuzzy match": [((d.match_type != "exact") & d.usable).sum() for d in data.values()],
        "Excluded": [(~d.usable).sum() for d in data.values()],
    }
    colors = [SERIES[0], SERIES[1], MUTED]
    fig, ax = plt.subplots(figsize=(7, 2.2))
    left = [0] * len(labels)
    for (name, vals), color in zip(parts.items(), colors):
        ax.barh(labels, vals, left=left, color=color, height=0.55, label=name, edgecolor="white", linewidth=2)
        for i, v in enumerate(vals):
            if v / sum(p[i] for p in parts.values()) > 0.04:
                ax.text(left[i] + v / 2, i, f"{v:,}", ha="center", va="center", color="white", fontsize=9)
        left = [a + b for a, b in zip(left, vals)]
    for i, total in enumerate(left):
        ax.text(total + 20, i, f"{parts['Excluded'][i]} excluded", va="center", color=TEXT_2, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Labeled functions")
    ax.set_title("How each labeled function was matched to CodeSearchNet")
    ax.legend(ncol=3, loc="upper left", bbox_to_anchor=(0, -0.3))
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    save(fig, "fig1_match_outcome.png")


def fig_valid_python(data):
    labels = list(data)
    before = [d.code_parses.sum() for d in data.values()]
    after = [d.restored_parses.sum() for d in data.values()]
    totals = [len(d) for d in data.values()]
    fig, ax = plt.subplots(figsize=(6, 3.2))
    x = range(len(labels))
    w = 0.36
    b1 = ax.bar([i - w / 2 - 0.01 for i in x], before, w, color=MUTED, label="As released")
    b2 = ax.bar([i + w / 2 + 0.01 for i in x], after, w, color=SERIES[0], label="After repair")
    for bars in (b1, b2):
        for bar, total in zip(bars, totals):
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 25, f"{h:,}\n({h / total:.0%})", ha="center", fontsize=8.5, color=TEXT)
    ax.set_xticks(list(x), labels)
    ax.set_ylabel("Functions that parse as Python 3")
    ax.set_ylim(0, max(totals) * 1.18)
    ax.set_title("Valid Python before and after the repair")
    ax.legend(loc="upper left", bbox_to_anchor=(0, -0.1), ncol=2)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    save(fig, "fig2_valid_python.png")


def fig_cosmic_labels(data):
    d = data["COSMIC"]
    d = d[d.usable]
    cols = [("entry", "Entry"), ("exit", "Exit"), ("read", "Read"), ("write", "Write"), ("cfp", "Total CFP")]
    fig, axes = plt.subplots(1, len(cols), figsize=(10, 2.6), sharey=True)
    for ax, (col, name) in zip(axes, cols):
        counts = d[col].value_counts().sort_index()
        ax.bar(counts.index, counts.values, color=SERIES[0], width=0.7)
        ax.set_title(name, fontsize=10)
        ax.set_xticks(range(int(counts.index.max()) + 1))
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.set_xlabel("Count per function")
    axes[0].set_ylabel("Functions")
    fig.suptitle(f"COSMIC label distribution (usable set, n = {len(d):,})", x=0.07, ha="left", fontweight="bold", fontsize=11)
    fig.tight_layout()
    save(fig, "fig3_cosmic_labels.png")


def fig_functions_per_repo(data):
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    bins = [1, 2, 3, 4, 6, 11, 21, 1000]
    names = ["1", "2", "3", "4–5", "6–10", "11–20", "21+"]
    w = 0.38
    for k, (label, d) in enumerate(data.items()):
        per_repo = d[d.usable].repository.value_counts()
        counts = pd.cut(per_repo, bins, right=False, labels=names).value_counts().reindex(names)
        xs = [i + (k - 0.5) * (w + 0.02) for i in range(len(names))]
        bars = ax.bar(xs, counts.values, w, color=SERIES[k], label=f"{label} ({len(per_repo):,} repositories)")
        ax.bar_label(bars, padding=2, fontsize=8, color=TEXT)
    ax.set_xticks(range(len(names)), names)
    ax.set_xlabel("Labeled functions contributed by one repository")
    ax.set_ylabel("Repositories")
    ax.set_title("Most repositories contribute only one function")
    ax.legend(loc="upper right")
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    save(fig, "fig4_functions_per_repo.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = load()
    summary = summarize(data)
    summary.to_csv(OUT / "summary.csv", index=False)
    print(summary.T.to_string())
    fig_match_outcome(data)
    fig_valid_python(data)
    fig_cosmic_labels(data)
    fig_functions_per_repo(data)


if __name__ == "__main__":
    main()
