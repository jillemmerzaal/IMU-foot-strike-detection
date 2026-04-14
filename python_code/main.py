import pandas as pd
import os
from pathlib import Path
from python_code.src.processing.no_recognized_steps import missing_data
from python_code.src.utils.Visualize import box_all, box_segmented
from python_code.src.processing.metrics import calculate_metrics


# Set relevant paths
root = Path(__file__).parent.parent
fld = os.path.join(root, "data", "toolbox1")

# Determine the algorithms that have missing data.
missing_data(fld, "output")
# Exclude benson from further analysis --> not suited for walking.

#%% Full walking course analysis
calculate_metrics(fld, "output", surface_split=False, fname="metrics_all.csv")

df_all = pd.read_csv(os.path.join(root, "data","output", "metrics_all.csv"), index_col=0)

# Set x and y columns
x = "algorithm"
y= "accuracy"
# Calculate basis descriptives statistics per algorithm.
descriptives = df_all.groupby(x, observed=True).agg({'total': ["sum"],
                                                     'TP': ["sum"],
                                                     'FP': ["sum"],
                                                     'FN': ["sum"],
                                                     'f1_score':['mean', 'std', 'count'],
                                                     'accuracy': ['mean', 'std', 'count'],
                                                     'precision':['mean', 'std', 'count'],
                                                     'recall': ['mean', 'std', 'count'],
                                                     "error (ms)": ['mean', 'std', 'count'],}).sort_values(('accuracy', 'mean'))

descriptives[("detected", "sum")] =descriptives[("TP", "sum")] + descriptives[("FP", "sum")]
descriptives.to_csv(os.path.join(root, "data", "output", "desciptives_all.csv"))

# Get performance order
average_y = df_all.groupby([x])["accuracy"].mean()
desired_order_algo = average_y.sort_values(ascending=False).index.to_list()

# Plot the accuracy results
fig = box_all(data=df_all, x=x, y=y, desired_order=desired_order_algo, points="outliers")
fig.write_image(os.path.join(root, "data", "output", "performance_all.png"),  width=1650, height=900, scale=1)

# Plot the timing error results
y="error (ms)"
fig = box_all(data=df_all, x=x, y=y, desired_order=desired_order_algo, points="outliers")
fig.write_image(os.path.join(root, "data", "output", "error_all.png"), width=1650, height=900, scale=1)

#%% Analysis per surface for best algorithm
calculate_metrics(fld, "output", surface_split=True, fname="metrics_split.csv")

# Calculate basis descriptives statistics per algorithms per surface.
df_split = pd.read_csv(os.path.join(root, "data", "output", "metrics_split.csv"), index_col=0)
# Only retain the best algorithm
best = desired_order_algo[0]
df_best = df_split[df_split.algorithm == best].copy().reset_index(drop=True)

# Set x and y columns
x = "condition"
y= "accuracy"
# Calculate basis descriptives statistics per surface.
descriptives = df_best.groupby(x, observed=True).agg({'total': ["sum"],
                                                     'TP': ["sum"],
                                                     'FP': ["sum"],
                                                      'FN': ["sum"],
                                                     'f1_score':['mean', 'std', 'count'],
                                                     'accuracy': ['mean', 'std', 'count'],
                                                     'precision':['mean', 'std', 'count'],
                                                     'recall': ['mean', 'std', 'count'],
                                                      "error (ms)": ['mean', 'std', 'count']}).sort_values(('accuracy', 'mean'))

descriptives[("detected", "sum")] = descriptives[("TP", "sum")] + descriptives[("FP", "sum")]

descriptives.to_csv(os.path.join(root, "data", "output", "desciptives_best.csv"))

#get performance order per surface
average_f1 = df_best.groupby([x])[y].mean()
desired_order = average_f1.sort_values(ascending=False).index.to_list()

fig_best = box_all(data=df_best, x=x, y=y, desired_order=desired_order, points="outliers")
fig_best.write_image(os.path.join(root, "data", "output", "performance_best.png"), width=1650, height=900, scale=1)

# Plot the timing error results
y="error (ms)"
fig_best = box_all(data=df_best, x=x, y=y, desired_order=desired_order, points="outliers")
fig_best.write_image(os.path.join(root, "data", "output", "error_best.png"), width=1650, height=900, scale=1)

#%% Analysis per surface for all algorithms
df_surface = pd.read_csv(os.path.join(root, "data", "output", "metrics_split.csv"), index_col=0)
# df_segmented = pd.read_csv(os.path.join(outcome_fld, "results_segmented.csv"))

# Set x and y columns
dim1 = "algorithm"
x = "condition"
y= "accuracy"

fig_surface = box_segmented(df_surface, dim1, x, y, desired_order=desired_order_algo, points="outliers")
fig_surface.write_image(os.path.join(root, "data", "output", "performance_surface.png"), width=1650, height=900, scale=1)
