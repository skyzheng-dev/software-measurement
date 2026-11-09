"""Step 8: describe the structural features from steps 6 (Understand) and 7 (Joern).

Writes, into figures/features/ (tracked in git):
  - summary.csv                          coverage and feature counts per dataset and tool
  - correlations_<dataset>.csv           Spearman correlation of every feature with every label
  - fig1_correlation_cosmic.png          heatmap: features x COSMIC labels
  - fig2_correlation_microm.png          heatmap: features x MicroM labels
  - fig3_sql_vs_read_write.png           COSMIC Read/Write labels for functions whose only SQL verb
                                         is SELECT vs. INSERT/UPDATE/DELETE (label-direction check)

Run: uv run python scripts/08_report_features.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parents[1]
REPAIRED = ROOT / "data" / "derived" / "repaired"
FEATS = ROOT / "data" / "derived" / "features"
OUT = ROOT / "figures" / "features"

LABELS = {
    "cosmic": ["entry", "read", "write", "exit", "cfp"],
    "microm": ["interaction", "communication", "process", "microm"],
}
TITLES = {"cosmic": "COSMIC", "microm": "MicroM"}

# Reference palette (dataviz skill, light mode).
BLUE, ORANGE, RED = "#2a78d6", "#eb6834", "#e34948"
MID = "#f0efec"
TEXT, TEXT_2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
DIVERGING = LinearSegmentedColormap.from_list("blue_red", [BLUE, MID, RED])

plt.rcParams.update(
    {
        "font.size": 9,
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


def load(name):
    df = pd.read_csv(REPAIRED / f"code_{name}_repaired.csv")
    df = df[df["usable"]]
    und = pd.read_csv(FEATS / f"understand_{name}.csv")
    jn = pd.read_csv(FEATS / f"joern_{name}.csv")
    merged = df.merge(und, on="id").merge(jn, on="id")
    return df, und, jn, merged


def correlations(merged, und, jn, labels):
    feats = [c for c in list(und.columns) + list(jn.columns) if c != "id"]
    feats = [f for f in feats if merged[f].nunique() > 1]  # constant columns have no correlation
    return merged[feats + labels].corr("spearman").loc[feats, labels]


def heatmap(corr, title, path):
    fig, ax = plt.subplots(figsize=(1.0 * corr.shape[1] + 3.2, 0.24 * corr.shape[0] + 1.2))
    lim = max(0.35, float(np.abs(corr.values).max()))
    im = ax.imshow(corr.values, cmap=DIVERGING, vmin=-lim, vmax=lim, aspect="auto")
    ax.set_xticks(range(corr.shape[1]), [c.upper() if c == "cfp" else c.capitalize() for c in corr.columns])
    ax.set_yticks(range(corr.shape[0]), corr.index)
    ax.xaxis.tick_top()
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for i in range(corr.shape[0]):
        for j in range(corr.shape[1]):
            v = corr.values[i, j]
            ax.text(j, i, f"{v:+.2f}", ha="center", va="center", fontsize=7,
                    color="white" if abs(v) > 0.6 * lim else TEXT)
    # separate the two tools' features
    n_und = sum(i.startswith("und_") for i in corr.index)
    ax.axhline(n_und - 0.5, color="white", lw=3)
    cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cbar.outline.set_visible(False)
    cbar.set_label("Spearman ρ", color=TEXT_2)
    ax.set_title(title, pad=28)
    fig.savefig(path)
    plt.close(fig)


def sql_direction(merged):
    sql = ["jn_sql_select", "jn_sql_insert", "jn_sql_update", "jn_sql_delete"]
    only_select = merged[(merged["jn_sql_select"] > 0) & (merged[sql[1:]].sum(axis=1) == 0)]
    only_modify = merged[(merged["jn_sql_select"] == 0) & (merged[sql[1:]].sum(axis=1) > 0)]
    rows = []
    for group, sub in [("SELECT only", only_select), ("INSERT / UPDATE / DELETE only", only_modify)]:
        rows.append({"group": group, "n": len(sub),
                     "share_read_ge1": (sub["read"] > 0).mean(), "share_write_ge1": (sub["write"] > 0).mean()})
    return pd.DataFrame(rows)


def sql_figure(tab, path):
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    y = np.arange(len(tab))
    h = 0.36
    for k, (col, color, name) in enumerate([("share_read_ge1", BLUE, "labeled Read ≥ 1"),
                                            ("share_write_ge1", ORANGE, "labeled Write ≥ 1")]):
        ys = y - h / 2 - 0.02 + k * (h + 0.04)
        ax.barh(ys, tab[col], height=h, color=color, label=name)
        for yy, v in zip(ys, tab[col]):
            ax.text(v + 0.015, yy, f"{v:.0%}", va="center", color=TEXT, fontsize=8)
    ax.set_yticks(y, [f"{g}\n(n = {n})" for g, n in zip(tab["group"], tab["n"])])
    ax.invert_yaxis()
    ax.set_xlim(0, 1.08)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    ax.set_xlabel("Share of functions")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_title("SQL verbs in string literals vs. released COSMIC Read/Write labels")
    fig.savefig(path)
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    summary = []
    for i, name in enumerate(LABELS, start=1):
        df, und, jn, merged = load(name)
        for tool, feats in [("understand", und), ("joern", jn)]:
            summary.append({"dataset": name, "tool": tool, "usable_functions": len(df),
                            "functions_with_features": int(feats["id"].isin(df["id"]).sum()),
                            "features": feats.shape[1] - 1})
        corr = correlations(merged, und, jn, LABELS[name])
        corr.round(4).to_csv(OUT / f"correlations_{name}.csv")
        heatmap(corr, f"Structural features vs. {TITLES[name]} labels (Spearman, n = {len(merged)})",
                OUT / f"fig{i}_correlation_{name}.png")
        if name == "cosmic":
            tab = sql_direction(merged)
            tab.round(4).to_csv(OUT / "sql_vs_read_write.csv", index=False)
            sql_figure(tab, OUT / "fig3_sql_vs_read_write.png")
            print(tab.to_string(index=False))
    pd.DataFrame(summary).to_csv(OUT / "summary.csv", index=False)
    print(pd.DataFrame(summary).to_string(index=False))
    print(f"figures in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
