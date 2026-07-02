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

# Sort by unrounded aggregate accuracy (TP / (TP+FP+FN)) to avoid tie-breaking errors
acc_agg_col = [c for c in hs.columns if c[0] == "accuracy_aggregate"][0]

def agg_accuracy(df):
    tp = df[("TP", "sum")]
    fp = df[("FP", "sum")]
    fn = df[("FN", "sum")]
    return tp / (tp + fp + fn)

order    = agg_accuracy(hs).sort_values(ascending=False).index
fo_order = agg_accuracy(fo).sort_values(ascending=False).index
hs = hs.loc[order]
fo = fo.loc[fo_order]

# Build rows
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

# Assemble LaTeX
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

# Save
out_path = OUT / "results_table.tex"
out_path.write_text(latex)
print(f"Saved to {out_path}")
print("\n" + latex)


#%% Timing error table — top 2 algorithms per event, per surface
SURFACE_LABELS = {
    "walk":          "Walk",
    "pavement_up":   "Pavement (up)",
    "pavement_down": "Pavement (down)",
    "slope_up":      "Slope (up)",
    "slope_down":    "Slope (down)",
    "stairs_up":     "Stairs (up)",
    "stairs_down":   "Stairs (down)",
}
SURFACE_ORDER = list(SURFACE_LABELS.keys())


def load_surface(event: str, fname: str) -> pd.DataFrame:
    df = pd.read_csv(OUT / event / fname, header=[0, 1], index_col=0)
    df.index.name = "condition"
    return df


# HS: best=KielMAT, second=GreeneMcGrath
# FO: best=GreeneMcGrath, second=KielMAT  (determined by orders dict at runtime)
# We identify them by reading the first row of the per-surface descriptives,
# which are already written in rank order by main.py.
hs_best   = load_surface("HS", "descriptives_best.csv")
hs_second = load_surface("HS", "descriptives_second.csv")
fo_best   = load_surface("FO", "descriptives_best.csv")
fo_second = load_surface("FO", "descriptives_second.csv")

# Recover algorithm names from descriptives_all so we can label the columns
hs_best_name   = order[0]
hs_second_name = order[1]

fo_best_name   = fo_order[0]
fo_second_name = fo_order[1]


def fmt_ms(df, surface):
    if surface not in df.index:
        return "--"
    mean = df.loc[surface, ("error (ms)", "mean")]
    sd   = df.loc[surface, ("error (ms)", "std")]
    if pd.isna(mean):
        return "--"
    sign = "+" if mean >= 0 else ""
    return f"${sign}{mean:.0f} \\pm {sd:.0f}$"


def fmt_acc_surface(df, surface):
    if surface not in df.index:
        return "--"
    tp = df.loc[surface, ("TP", "sum")]
    fp = df.loc[surface, ("FP", "sum")]
    fn = df.loc[surface, ("FN", "sum")]
    if pd.isna(tp):
        return "--"
    acc = tp / (tp + fp + fn)
    return f"{acc:.2f}"


error_header = (
    r"\begin{table}[ht]" + "\n"
    r"\centering" + "\n"
    r"\caption{Per-surface aggregate accuracy and timing error (mean\,$\pm$\,SD, ms) "
    r"for the two best algorithms for heel strike (HS) and foot-off (FO) detection. "
    r"Negative timing error values indicate early detection; positive values indicate late detection.}" + "\n"
    r"\label{tab:timing_error}" + "\n"
    r"\begin{tabular}{l rr rr rr rr}" + "\n"
    r"\toprule" + "\n"
    rf" & \multicolumn{{4}}{{c}}{{\textbf{{Heel Strike}}}} & \multicolumn{{4}}{{c}}{{\textbf{{Foot Off}}}} \\" + "\n"
    rf"\cmidrule(lr){{2-5}} \cmidrule(lr){{6-9}}" + "\n"
    rf" & \multicolumn{{2}}{{c}}{{\textbf{{{hs_best_name}}}}} & \multicolumn{{2}}{{c}}{{\textbf{{{hs_second_name}}}}}"
    rf" & \multicolumn{{2}}{{c}}{{\textbf{{{fo_best_name}}}}} & \multicolumn{{2}}{{c}}{{\textbf{{{fo_second_name}}}}} \\" + "\n"
    rf"\cmidrule(lr){{2-3}} \cmidrule(lr){{4-5}} \cmidrule(lr){{6-7}} \cmidrule(lr){{8-9}}" + "\n"
    r"\textbf{Surface} & \textbf{Acc} & \textbf{Error (ms)} & \textbf{Acc} & \textbf{Error (ms)}"
    r" & \textbf{Acc} & \textbf{Error (ms)} & \textbf{Acc} & \textbf{Error (ms)} \\" + "\n"
    r"\midrule"
)

error_rows = []
for surface in SURFACE_ORDER:
    label = SURFACE_LABELS[surface]
    row = [
        label,
        fmt_acc_surface(hs_best,   surface),
        fmt_ms(hs_best,            surface),
        fmt_acc_surface(hs_second, surface),
        fmt_ms(hs_second,          surface),
        fmt_acc_surface(fo_best,   surface),
        fmt_ms(fo_best,            surface),
        fmt_acc_surface(fo_second, surface),
        fmt_ms(fo_second,          surface),
    ]
    error_rows.append(" & ".join(row) + r" \\")

error_footer = (
    r"\bottomrule" + "\n"
    r"\end{tabular}" + "\n"
    r"\end{table}"
)

error_latex = "\n".join([error_header] + error_rows + [error_footer])

error_path = OUT / "timing_error_table.tex"
error_path.write_text(error_latex)
print(f"\nSaved to {error_path}")
print("\n" + error_latex)
