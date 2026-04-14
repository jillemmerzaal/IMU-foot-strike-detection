import pandas as pd
from scipy.io import loadmat
import os
from pathlib import Path

from biomechzoo.utils.engine import engine
from python_code.src.utils.fileparts import fileparts


def missing_data(fld:str, out_folder:"str") -> None:
    """
    Small function to determine the amount of missing data.

    Parameters:
        fld (str): file path to the root data folder.
        out_folder (str): to name the output folder

    Notes:
        * Reads .Mat files
        * Specifically looks for the fieldnames "y" and "y_hat"
        * Automatically saves a Pandas DataFrame to csv
    """

    fl = engine(fld, extension=".mat")
    fl_x = [f for f in fl if "/._" not in f]

    missing_data = {}
    for f in fl_x:
        print(f"check percentage of missing data for {f}")
        # Extract meta-data
        directory, filename, extension, _ = fileparts(f)
        algo = directory.split("/")[-1]

        if algo not in missing_data:
            missing_data.update({algo: {"missing": 0, "no_missing": 0}})

        # load matlab data
        mat_data = loadmat(f, struct_as_record=False, squeeze_me=True)
        temp_results = mat_data["results"]
        yhat_data = getattr(temp_results, "y_hat")

        # determine if yhat data is empty
        if len(yhat_data) == 0:
            no_steps = missing_data[algo]["missing"] + 1
            missing_data[algo]["missing"] = no_steps
        else:
            steps = data = missing_data[algo]["no_missing"] + 1
            missing_data[algo]["no_missing"] = steps

    # calculate percentage missing
    for key, value in missing_data.items():
        total = value["missing"] + value["no_missing"]
        perc_missing = (value["missing"] / total) * 100
        missing_data[key].update({"perc_missing": perc_missing})

    missing_data_df = pd.DataFrame.from_dict(missing_data).T


    save_fld = os.path.join(Path(fld).parent, out_folder)
    if not os.path.exists(save_fld):
        os.makedirs(save_fld)

    missing_data_df.to_csv(os.path.join(save_fld, "missing_data.csv"))