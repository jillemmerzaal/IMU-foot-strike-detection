"""
Generate a LaTeX results table from descriptives_all.csv for HS and FO.

Columns per event: Total | TP | FP | FN | Accuracy | Error (ms, mean ± SD)
Events are shown side-by-side with grouped column headers.
"""

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUT  = ROOT / "data" / "output"

# ── Load ──────────────────────────────────────────────────────────────────────
def load(event: str) -> pd.DataFrame:
    path = OUT / event / "descriptives_all.csv"
    df = pd.read_csv(path, header=[0, 1], index_col=0)
    df.index.name = "algorithm"
    return df

hs = load("HS")
fo = load("FO")

# Align on the same algorithm set (outer join, fill missing with NaN)
algorithms = hs.index.union(fo.index)
hs = hs.reindex(algorithms)
fo = fo.reindex(algorithms)

# Sort by HS aggregate accuracy descending
acc_agg_col = [c for c in hs.columns if c[0] == "accuracy_aggregate"][0]
order = hs[acc_agg_col].sort_values(ascending=False).index
hs = hs.loc[order]
fo = fo.loc[order]

# ── Build rows ────────────────────────────────────────────────────────────────
def fmt_error(mean, sd):
    if pd.isna(mean):
        return "--"
    return f"${mean:.0f} \\pm {sd:.0f}$"

def fmt_int(val):
    return "--" if pd.isna(val) else f"{int(val):,}"

def fmt_acc(val):
    return "--" if pd.isna(val) else f"{val:.2f}"

rows = []
for algo in order:
    row = [algo.replace("_", r"\_")]
    for df in (hs, fo):
        row += [
            fmt_acc(df.loc[algo, acc_agg_col]),
            fmt_error(df.loc[algo, ("error (ms)", "mean")],
                      df.loc[algo, ("error (ms)", "std")]),
            fmt_int(df.loc[algo, ("total",      "sum")]),
            fmt_int(df.loc[algo, ("TP",         "sum")]),
            fmt_int(df.loc[algo, ("FP",         "sum")]),
            fmt_int(df.loc[algo, ("FN",         "sum")]),

        ]
    rows.append(row)

# ── Assemble LaTeX ────────────────────────────────────────────────────────────
n_event_cols = 6  # Total, TP, FP, FN, Acc, Error

header_top = (
    r"\begin{table}[ht]" + "\n"
    r"\centering" + "\n"
    r"\caption{Detection performance for heel strike (HS) and foot-off (FO) events. "
    r"Accuracy is the aggregate Jaccard index (TP\,/\,(TP+FP+FN)). "
    r"Timing error is mean\,$\pm$\,SD in ms.}" + "\n"
    r"\label{tab:results}" + "\n"
    r"\begin{tabular}{l" + " rrrr rr" * 2 + "}" + "\n"
    r"\toprule" + "\n"
    r" & \multicolumn{6}{c}{\textbf{Heel Strike}} & \multicolumn{6}{c}{\textbf{Foot Off}} \\" + "\n"
    r"\cmidrule(lr){2-7} \cmidrule(lr){8-13}" + "\n"
    r"\textbf{Algorithm} "
    r"& \textbf{Acc} & \textbf{Error (ms)} & \textbf{Total} & \textbf{TP} & \textbf{FP} & \textbf{FN}"
    r" & \textbf{Acc} & \textbf{Error (ms)} & \textbf{Total} & \textbf{TP} & \textbf{FP} & \textbf{FN}"
    r" \\" + "\n"
    r"\midrule"
)

body_lines = []
for row in rows:
    body_lines.append(" & ".join(row) + r" \\")

footer = (
    r"\bottomrule" + "\n"
    r"\end{tabular}" + "\n"
    r"\end{table}"
)

latex = "\n".join([header_top] + body_lines + [footer])

# ── Save ──────────────────────────────────────────────────────────────────────
out_path = OUT / "results_table.tex"
out_path.write_text(latex)
print(f"Saved to {out_path}")
print("\n" + latex)
