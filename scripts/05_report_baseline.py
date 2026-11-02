"""Step 5: score the CodeBERT baseline and compare it with the published numbers.

Reads data/derived/baseline/<subset>/<target>_epoch_preds.csv (from scripts/04) and scores them the
way upstream does (calculate_metrics.py / sum_preds.py): predictions are rounded to integers, total
CFP is the sum of the four rounded movement predictions, and MMRE / PRED(30) use only functions whose
actual value is non-zero.

Two ways of picking each fold's predictions are scored:
  upstream  the epoch with the lowest MSE on the test fold (what the paper did; it looks at test data)
  epoch5    always the last epoch (chosen in advance, so it does not look at test data)

Works on partial results: targets that have not finished are skipped, and total CFP is only scored
once all four movements are complete.

Run:    uv run python scripts/05_report_baseline.py
Output: figures/baseline/metrics.csv and fig*.png
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "derived" / "baseline"
PUBLISHED = ROOT / "data" / "raw" / "codesizebert" / "upstream" / "stats" / "COSMIC.csv"
OUT = ROOT / "figures" / "baseline"

TARGETS = ["entry", "exit", "read", "write"]
LABELS = {"entry": "Entry", "exit": "Exit", "read": "Read", "write": "Write", "cfp": "Total CFP"}
FOLDS, EPOCHS = 5, 5

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


def metrics(actual, pred):
    """Upstream calculate_metrics(), applied to rounded predictions."""
    actual, pred = np.asarray(actual, float), np.asarray(pred, float)
    mae = np.mean(np.abs(pred - actual))
    nonzero = actual != 0
    mre = np.abs(pred[nonzero] - actual[nonzero]) / actual[nonzero]
    return {
        "acc": np.mean(pred == actual),
        "mse": np.mean((pred - actual) ** 2),
        "mae": mae,
        "nmae": mae / np.mean(actual),
        "mmre": np.mean(mre),
        "pred30": np.mean(mre <= 0.30),
        "n": len(actual),
    }


def load_complete(subset):
    """Per-epoch predictions for each target whose 5 folds x 5 epochs are all present."""
    out = {}
    for t in TARGETS:
        p = IN / subset / f"{t}_epoch_preds.csv"
        if p.exists():
            df = pd.read_csv(p)
            if df.groupby("fold").epoch.nunique().reindex(range(1, FOLDS + 1)).eq(EPOCHS).all():
                out[t] = df
    return out


def select(df, rule):
    if rule == "epoch5":
        return df[df.epoch == EPOCHS]
    mse = df.assign(se=(df.pred - df.actual) ** 2).groupby(["fold", "epoch"]).se.mean()
    best = mse.groupby(level="fold").idxmin().tolist()
    return df.set_index(["fold", "epoch"]).loc[best].reset_index()


def score(subset, rule, preds):
    rows, rounded = [], {}
    for t, df in preds.items():
        sel = select(df, rule).set_index("id")
        rounded[t] = sel.pred.round()
        rows.append({"subset": subset, "selection": rule, "target": t, **metrics(sel.actual, rounded[t])})
        rounded[t + "_actual"] = sel.actual
    if all(t in preds for t in TARGETS):
        r = pd.DataFrame(rounded)
        cfp_pred = sum(r[t] for t in TARGETS)
        cfp_actual = sum(r[t + "_actual"] for t in TARGETS)
        rows.append({"subset": subset, "selection": rule, "target": "cfp", **metrics(cfp_actual, cfp_pred)})
    return rows


def grouped_bars(ax, groups, series, colors, fmt="{:.1%}"):
    n = len(series)
    w = 0.8 / n
    for k, ((name, values), color) in enumerate(zip(series.items(), colors)):
        xs = [i + (k - (n - 1) / 2) * w for i in range(len(groups))]
        vals = [values.get(g, np.nan) for g in groups]
        bars = ax.bar(xs, vals, w * 0.94, color=color, label=name)
        ax.bar_label(bars, labels=["" if np.isnan(v) else fmt.format(v) for v in vals], padding=2, fontsize=7.5, color=TEXT)
    ax.set_xticks(range(len(groups)), [LABELS[g] for g in groups])
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def save(fig, name):
    fig.savefig(OUT / name, facecolor="white")
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    published = pd.read_csv(PUBLISHED).set_index("metric")
    rows = []
    preds = {s: load_complete(s) for s in ["released", "usable"]}
    for subset, p in preds.items():
        for rule in ["upstream", "epoch5"]:
            rows += score(subset, rule, p)
    if not rows:
        print("No complete targets yet.")
        return
    m = pd.DataFrame(rows)
    pub = pd.DataFrame(
        [{"subset": "published", "selection": "upstream", "target": t, **published[t].to_dict()} for t in published.columns]
    )
    m = pd.concat([pub.drop(columns="nonzero"), m], ignore_index=True)
    m.to_csv(OUT / "metrics.csv", index=False, float_format="%.4f")
    print(m.pivot_table(index=["subset", "selection"], columns="target", values="acc").round(4).to_string())

    groups = [g for g in ["entry", "exit", "read", "write", "cfp"] if g in set(m[m.subset == "released"].target)]
    acc = lambda s, r: m[(m.subset == s) & (m.selection == r)].set_index("target").acc.to_dict()

    # Figure 1: does the reproduction match the paper?
    fig, ax = plt.subplots(figsize=(7.5, 3.4))
    grouped_bars(ax, groups, {"Published [2]": acc("published", "upstream"), "Reproduced": acc("released", "upstream")}, [MUTED, SERIES[0]])
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Exact-match accuracy")
    ax.set_title("CodeBERT baseline: published vs. reproduced (released data, 5-fold CV)")
    ax.legend(ncol=2, loc="upper left", bbox_to_anchor=(0, -0.1))
    save(fig, "fig1_reproduction.png")

    # Figure 2: effect of choosing the epoch by looking at the test fold.
    fig, ax = plt.subplots(figsize=(7.5, 3.4))
    grouped_bars(
        ax,
        groups,
        {"Best epoch on test fold (as published)": acc("released", "upstream"), "Fixed last epoch": acc("released", "epoch5")},
        [SERIES[0], SERIES[1]],
    )
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Exact-match accuracy")
    ax.set_title("How much does epoch selection on the test fold inflate accuracy?")
    ax.legend(ncol=2, loc="upper left", bbox_to_anchor=(0, -0.1))
    save(fig, "fig2_epoch_selection.png")

    # Figure 3: test accuracy per epoch, averaged over the 5 folds.
    if preds["released"]:
        targets = [t for t in TARGETS if t in preds["released"]]
        fig, axes = plt.subplots(1, len(targets), figsize=(2.4 * len(targets) + 0.6, 2.8), sharey=True, squeeze=False)
        for ax, t in zip(axes[0], targets):
            df = preds["released"][t]
            per = df.assign(hit=df.pred.round() == df.actual).groupby(["fold", "epoch"]).hit.mean().unstack("fold")
            for fold in per.columns:
                ax.plot(per.index, per[fold], color=MUTED, linewidth=1)
            ax.plot(per.index, per.mean(axis=1), color=SERIES[0], linewidth=2, marker="o", markersize=4, label="Mean of 5 folds")
            ax.set_title(LABELS[t], fontsize=10)
            ax.set_xticks(range(1, EPOCHS + 1))
            ax.set_xlabel("Epoch")
            ax.grid(axis="y", color=GRID, linewidth=0.8)
        axes[0][0].set_ylabel("Test-fold accuracy")
        axes[0][0].legend(loc="lower right", fontsize=8)
        fig.suptitle("Accuracy by epoch (gray: individual folds)", x=0.06, ha="left", fontweight="bold", fontsize=11)
        fig.tight_layout()
        save(fig, "fig3_epoch_curves.png")

    # Figure 4: released vs. usable subset (the rows later models will use).
    if preds["usable"]:
        fig, ax = plt.subplots(figsize=(7.5, 3.4))
        grouped_bars(
            ax,
            groups,
            {"Released (1,787)": acc("released", "upstream"), "Usable subset (1,766)": acc("usable", "upstream")},
            [SERIES[0], SERIES[2]],
        )
        ax.set_ylim(0, 1.08)
        ax.set_ylabel("Exact-match accuracy")
        ax.set_title("Baseline on all released functions vs. the restorable subset")
        ax.legend(ncol=2, loc="upper left", bbox_to_anchor=(0, -0.1))
        save(fig, "fig4_released_vs_usable.png")


if __name__ == "__main__":
    main()
