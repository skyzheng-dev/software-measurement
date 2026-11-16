"""Step 9: plain-language summary figures for non-specialist readers (advisor meetings, slides).

Reads only the summary CSVs written by step 8 and writes, into figures/advisor/ (tracked in git):
  - fig1_coverage.png        how many functions were analyzed by both tools
  - fig2_what_tracks_size.png strongest correlation of selected features with any COSMIC label
  - fig3_read_write_swap.png  Read/Write labels for SELECT-only vs. INSERT/UPDATE/DELETE-only functions
  - fig4_crossover.png        read-like / write-like clues vs. the Read and Write labels

Run: uv run python scripts/09_advisor_figures.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "figures" / "features"
OUT = ROOT / "figures" / "advisor"

# Reference palette (dataviz skill, light mode; blue/orange pair validated).
BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#c3c2b7"
TEXT, TEXT_2, GRID, TRACK = "#0b0b0b", "#52514e", "#e4e3df", "#f0efec"

plt.rcParams.update(
    {
        "font.size": 11,
        "axes.edgecolor": GRID,
        "axes.labelcolor": TEXT_2,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.color": TEXT_2,
        "ytick.color": TEXT,
        "legend.frameon": False,
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.3,
    }
)


def titles(fig, title, subtitle, sub_y=0.915):
    fig.text(0.01, 0.99, title, fontsize=16, fontweight="bold", color=TEXT, ha="left", va="top",
             transform=fig.transFigure)
    fig.text(0.01, sub_y, subtitle, fontsize=11, color=TEXT_2, ha="left", va="top",
             transform=fig.transFigure, linespacing=1.4)


def footnote(fig, text, y=-0.04):
    fig.text(0.01, y, text, fontsize=8.5, color=TEXT_2, ha="left", va="top", transform=fig.transFigure)


def fig_coverage(summary):
    s = summary.set_index(["dataset", "tool"])
    tiles = [
        (f"{s.loc[('cosmic', 'understand'), 'usable_functions']:,}", "functions labeled\nwith COSMIC size"),
        (f"{s.loc[('microm', 'understand'), 'usable_functions']:,}", "functions labeled\nwith MicroM size"),
        (f"{100 * (s['functions_with_features'] / s['usable_functions']).min():.0f}%", "analyzed by\nboth tools"),
        (f"{s.loc[('cosmic', 'understand'), 'features'] + s.loc[('cosmic', 'joern'), 'features']}",
         "measurements\nper function"),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(10, 2.8))
    for ax, (big, small) in zip(axes, tiles):
        ax.set_axis_off()
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, color=TRACK, zorder=0))
        ax.text(0.08, 0.62, big, fontsize=26, fontweight="bold", color=TEXT, transform=ax.transAxes)
        ax.text(0.08, 0.15, small, fontsize=10.5, color=TEXT_2, transform=ax.transAxes, linespacing=1.3)
    fig.subplots_adjust(left=0, right=1, top=0.7, wspace=0.08)
    titles(fig, "Every function in the dataset has now been analyzed",
           "Two code-analysis tools ran on every usable function. Each finishes in under a minute.", sub_y=0.86)
    footnote(fig, "Source: figures/features/summary.csv (step 8).")
    fig.savefig(OUT / "fig1_coverage.png")
    plt.close(fig)


def fig_tracks_size(corr):
    cosmic = ["entry", "read", "write", "exit", "cfp"]
    picks = [  # (feature, plain name, is call-based)
        ("jn_calls_write", 'Calls to "write"-style functions', True),
        ("jn_calls_read", 'Calls to "read"-style functions', True),
        ("jn_sql_insert", "Database save commands (INSERT)", True),
        ("jn_sql_select", "Database fetch commands (SELECT)", True),
        ("und_RatioCommentToCode", "Share of lines that are comments", False),
        ("und_MaxNesting", "How deeply code is nested", False),
        ("und_Cyclomatic", "Complexity (number of branches)", False),
        ("und_CountLineCode", "Lines of code", False),
        ("und_CountLine", "Total lines", False),
    ]
    strength = corr[cosmic].abs().max(axis=1)
    rows = sorted(picks, key=lambda p: strength[p[0]])
    fig, ax = plt.subplots(figsize=(10, 4.6))
    fig.subplots_adjust(left=0.3, right=0.97, top=0.8)
    y = range(len(rows))
    vals = [strength[f] for f, _, _ in rows]
    ax.barh(y, [1] * len(rows), color=TRACK, height=0.62, zorder=0)
    ax.barh(y, vals, color=[BLUE if c else GRAY for _, _, c in rows], height=0.62, zorder=1)
    for i, v in zip(y, vals):
        ax.text(v + 0.012, i, f"{v:.2f}", va="center", fontsize=10, color=TEXT_2)
    ax.set_yticks(list(y), [name for _, name, _ in rows])
    ax.set_xlim(0, 1)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1], ["0\nno relationship", "0.25", "0.5", "0.75", "1\nperfect"])
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=BLUE), plt.Rectangle((0, 0), 1, 1, color=GRAY)],
              labels=["What the function calls", "Length and complexity"],
              loc="lower right", fontsize=10)
    titles(fig, "Code length and complexity barely relate to COSMIC size",
           "How closely each measurement moves with the COSMIC labels (strongest of Entry, Read, Write,\n"
           "Exit and total). What a function calls is a better clue, but still a weak one.")
    footnote(fig, "Absolute Spearman correlation, 1,766 functions. Source: figures/features/correlations_cosmic.csv.",
             y=-0.08)
    fig.savefig(OUT / "fig2_what_tracks_size.png")
    plt.close(fig)


def fig_swap(sql):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4), sharey=True)
    info = {
        "SELECT only": ("Functions that only fetch data", "COSMIC expects: Read"),
        "INSERT / UPDATE / DELETE only": ("Functions that only save, change or delete", "COSMIC expects: Write"),
    }
    for ax, (_, r) in zip(axes, sql.iterrows()):
        head, expect = info[r["group"]]
        n = int(r["n"])
        shares = [r["share_read_ge1"], r["share_write_ge1"]]
        bars = ax.bar(["Has a Read label", "Has a Write label"], shares, color=[BLUE, ORANGE], width=0.55)
        for b, s in zip(bars, shares):
            ax.text(b.get_x() + b.get_width() / 2, s + 0.02, f"{round(s * n)} of {n}\n({s:.0%})",
                    ha="center", va="bottom", fontsize=11, color=TEXT)
        ax.set_title(f"{head}\n{expect}", fontsize=11.5, color=TEXT, loc="left", linespacing=1.5)
        ax.set_ylim(0, 1)
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1], ["0%", "25%", "50%", "75%", "100%"])
        ax.yaxis.grid(True, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(axis="x", length=0, labelsize=10.5)
    fig.subplots_adjust(top=0.68, wspace=0.12)
    titles(fig, "Database fetches are mostly labeled Write, not Read",
           "In COSMIC, fetching data is a Read. The left group looks swapped; the right group is mixed,\n"
           "so this is a strong hint, not proof. Total size is not affected either way.")
    footnote(fig, "Labels are identical in the original download, so our data cleanup did not cause this. "
                  "Source: figures/features/sql_vs_read_write.csv.")
    fig.savefig(OUT / "fig3_read_write_swap.png")
    plt.close(fig)


def fig_crossover(corr):
    clues = [
        ("jn_calls_read", 'Calls to "read"-style functions'),
        ("jn_sql_select", "Database fetch commands (SELECT)"),
        ("jn_calls_write", 'Calls to "write"-style functions'),
        ("jn_sql_insert", "Database save commands (INSERT)"),
    ]
    fig, ax = plt.subplots(figsize=(10, 4.6))
    fig.subplots_adjust(left=0.3, right=0.97, top=0.74)
    h = 0.36
    for i, (f, _) in enumerate(clues):
        y = len(clues) - 1 - i
        for off, lab, color in [(h / 2, "read", BLUE), (-h / 2, "write", ORANGE)]:
            v = corr.loc[f, lab]
            ax.barh(y + off, v, height=h - 0.04, color=color)
            ax.text(max(v, 0) + 0.006, y + off, f"{v:.2f}", va="center", fontsize=10, color=TEXT_2)
    ax.set_yticks([len(clues) - 1 - i for i in range(len(clues))], [name for _, name in clues])
    ax.axhline(1.5, color=GRID, linewidth=1)
    ax.text(0.495, 3.0, "Looks like reading\n→ should match Read", fontsize=9.5, color=TEXT_2, va="center", ha="right")
    ax.text(0.495, 1.0, "Looks like writing\n→ should match Write", fontsize=9.5, color=TEXT_2, va="center", ha="right")
    ax.set_xlim(0, 0.5)
    ax.set_xticks([0, 0.1, 0.2, 0.3, 0.4, 0.5])
    ax.set_xlabel("How closely the clue moves with the label (0 = not at all, 1 = perfectly)")
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=BLUE), plt.Rectangle((0, 0), 1, 1, color=ORANGE)],
              labels=["Read label", "Write label"], loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2,
              fontsize=10)
    titles(fig, "Each clue lines up with the opposite label",
           "Reading-type clues match the Write label, and writing-type clues match the Read label.\n"
           "This supports the idea that Read and Write were swapped in the published data.")
    footnote(fig, 'Spearman correlation, 1,766 functions. "read"/"write" call clues come from our own keyword lists '
                  "(e.g. read, get, load vs. write, save, insert),\nso they are rough. "
                  "Source: figures/features/correlations_cosmic.csv.", y=-0.06)
    fig.savefig(OUT / "fig4_crossover.png")
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    corr = pd.read_csv(SRC / "correlations_cosmic.csv", index_col=0)
    fig_coverage(pd.read_csv(SRC / "summary.csv"))
    fig_tracks_size(corr)
    fig_swap(pd.read_csv(SRC / "sql_vs_read_write.csv"))
    fig_crossover(corr)
    print(f"Wrote 4 figures to {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
