import pandas as pd
import os
from pathlib import Path
from python_code.src.processing.no_recognized_steps import missing_data
from python_code.src.utils.Visualize import box_all, box_segmented
from python_code.src.processing.metrics import calculate_metrics

# Initialize paths
root = Path(__file__).parent.parent
fld  = root / "data" / "toolbox_results"
OUT  = root / "data" / "output"

# Algorithms to exclude based on missing data
SKIP = {
    "HS": ["Auvinet", "Benson"],
    "FO": ["Auvinet", "Benson", "Mizrahi", "Norris", "Reenalda", "Whelan"],
}

# Aggregation spec (shared across all groupby calls)
AGG_SPEC = {
    "total":      ["sum"],
    "TP":         ["sum"],
    "FP":         ["sum"],
    "FN":         ["sum"],
    "f1_score":   ["mean", "std", "count"],
    "accuracy":   ["mean", "std", "count"],
    "precision":  ["mean", "std", "count"],
    "recall":     ["mean", "std", "count"],
    "error (ms)": ["mean", "std", "count"],
}

# Helpers
def load_metrics(event: str, fname: str) -> pd.DataFrame:
    df = pd.read_csv(OUT / event / fname, index_col=0)
    df["algorithm"] = df["algorithm"].astype(str).str.split(r"[\\/]").str[-1]
    return df


def save_descriptives(df: pd.DataFrame, group_col: str, event: str, fname: str) -> None:
    descriptives = df.groupby(group_col, observed=True).agg(AGG_SPEC)
    descriptives[("detected", "sum")] = descriptives[("TP", "sum")] + descriptives[("FP", "sum")]
    descriptives[("accuracy_aggregate", "")] = (
        descriptives[("TP", "sum")] /
        (descriptives[("TP", "sum")] + descriptives[("FP", "sum")] + descriptives[("FN", "sum")])
    ).round(2)
    descriptives = descriptives.sort_values(("accuracy_aggregate", ""))
    descriptives.to_csv(OUT / event / fname)


def plot_and_save(df: pd.DataFrame, x: str, order: list, event: str, prefix: str) -> None:
    fig = box_all(data=df, x=x, y="accuracy", desired_order=order, points="outliers")
    fig.write_image(OUT / event / f"{prefix}_performance.png", width=1650, height=900, scale=1)

    fig = box_all(data=df, x=x, y="error (ms)", desired_order=order, points="outliers")
    fig.write_image(OUT / event / f"{prefix}_error.png", width=1650, height=900, scale=1)


def get_order(df: pd.DataFrame, group_col: str) -> list:
    agg = df.groupby(group_col)[["TP", "FP", "FN"]].sum()
    agg["accuracy_aggregate"] = agg["TP"] / (agg["TP"] + agg["FP"] + agg["FN"])
    return agg["accuracy_aggregate"].sort_values(ascending=False).index.to_list()


# Check missing data (already done a priori, but for clarity it is still here)
for event in ("HS", "FO"):
    missing_data(str(fld), event, "output")

# Full walking course analysis
orders = {}
for event in ("HS", "FO"):
    calculate_metrics(str(fld), event=event, skip=SKIP[event], out_folder="output",
                      surface_split=False, fname="metrics_all.csv")

    df_all = load_metrics(event, "metrics_all.csv")
    save_descriptives(df_all, "algorithm", event, "descriptives_all.csv")

    orders[event] = get_order(df_all, "algorithm")
    plot_and_save(df_all, x="algorithm", order=orders[event], event=event, prefix="all")

#  Per-surface analysis — all algorithms
for event in ("HS", "FO"):
    df_surface = load_metrics(event, "metrics_split.csv")
    fig = box_segmented(df_surface, dim1="algorithm", x="condition", y="accuracy",
                        desired_order=orders[event], points="outliers")
    fig.write_image(OUT / event / "performance_surface.png", width=1650, height=900, scale=1)

#  Per-surface analysis — best algorithm only
for event in ("HS", "FO"):
    calculate_metrics(str(fld), event=event, skip=SKIP[event], out_folder="output",
                      surface_split=True, fname="metrics_split.csv")

    df_split = load_metrics(event, "metrics_split.csv")
    best = orders[event][0]
    df_best = df_split[df_split.algorithm == best].copy().reset_index(drop=True)

    save_descriptives(df_best, "condition", event, "descriptives_best.csv")

    surface_order = get_order(df_best, "condition")
    plot_and_save(df_best, x="condition", order=surface_order, event=event, prefix="best")