import pandas as pd
import os
import numpy as np
from biomechzoo import biomechzoo
from pathlib import Path
from scipy.io import loadmat

from biomechzoo.utils.engine import engine
from python_code.src.utils.fileparts import fileparts
from python_code.src.utils.metricsCalculator import MetaData, enrich_metadata, evaluate_algorithm, \
    calculate_performance_metrics, evaluate_algorithm_per_surface
from python_code.src.utils.dict_manupulations import DictManupulations


def calculate_metrics(fld:str, out_folder:str, surface_split:bool=False, fname:str=None) -> None:
    """
    Small function to calculate the performance metric per algorithm, per subject, per course.
    It has two modes: 1) full walking course; 2) split per surface.

    Parameters:
        fld (str): file path to the root data folder.
        out_folder (str): to name the output folder
        surface_split (bool):

    Notes:
        * Reads .Mat files
        * Specifically looks for the fieldnames "y" and "y_hat"
        * Automatically saves a Pandas DataFrame to csv
    """

    fl = engine(fld, extension=".mat")
    fl_x = [f for f in fl if "/._" not in f] # Clean up file list --> needed for my external hard drive

    metrics = []
    for f in fl_x:
        print(f"calculating metrics for {f}")
        # Extract meta-data
        directory, filename, extension, _ = fileparts(f)
        algo = directory.split("/")[-1]
        subj_id = filename.split("_")[0]
        course_name = filename.split("_")[1]

        # loop through the algorithms.
        if algo != "Benson" and algo != "Auvinet":
            # load matlab data
            mat_data = loadmat(f, struct_as_record=False, squeeze_me=True)
            temp_results = mat_data["results"]
            yhat = getattr(temp_results, "y_hat")[:,0]
            y = getattr(temp_results, "y")[:,0]
            if surface_split:
                surface_ic = split_by_surface(f, y)
                outcome = evaluate_algorithm_per_surface(y, yhat, surface_ic)
                for walk_mode, values in outcome.items():
                    total_steps = surface_ic.count(walk_mode)
                    metadata = MetaData(subj=subj_id, parcours=course_name, condition=walk_mode, algorithm=algo, total=total_steps)

                    features = {"TP": values["tp"], "FP": values["fp"], "FN": values["fn"],
                                "error (ms)": np.mean(values['ms_error'])}
                    metadata = enrich_metadata(metadata, features)
                    metadata = calculate_performance_metrics(tp=values["tp"], fn=values["fn"], fp=values["fp"],metadata=metadata)
                    metrics.append(metadata)
            #
            else:
                total_steps = len(y)
                walk_mode = "all"
                # evaluate the algorithms.
                tp, fp, fn, error = evaluate_algorithm(y, yhat)

                # metrics[algo][filename] = features
                # Built the results table
                metadata = MetaData(subj=subj_id, parcours=course_name, condition=walk_mode, algorithm=algo, total=total_steps)
                features = {"TP": tp, "FP": fp, "FN": fn, "error (ms)": round(error)}
                metadata = enrich_metadata(metadata, features)
                metadata = calculate_performance_metrics(tp=tp, fn=fn, fp=fp, metadata=metadata)
                metrics.append(metadata)


    df_all = DictManupulations.from_dataclass_to_dataframe(metrics)

    save_fld = os.path.join(Path(fld).parent, out_folder)
    if not os.path.exists(save_fld):
        os.makedirs(save_fld)

    if not fname:
        fname = "metrics.csv"

    df_all.to_csv(os.path.join(save_fld, fname))


def split_by_surface(f:str, data:str) -> list:
    # Extract meta data and match label file
    directory, filename, extension, _ = fileparts(f)
    root = Path(directory).parent.parent
    subj_id = filename.split("_")[0]
    course_name = filename.split("_")[1]

    # map the label data
    f_y = os.path.join(root, "data_set", course_name, subj_id, "labels.csv")
    raw_labels = pd.read_csv(f_y)

    # Get the label associated to the steps
    label = []
    for step in data:
        # # This is the step in milliseconds. Find in the time colum of the labels
        temp = raw_labels.loc[np.where(raw_labels.time == step)[0], "walk_mode"]
        walk_mode_list = temp.tolist()
        label.extend(walk_mode_list)
        del temp

    return label