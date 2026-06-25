import pandas as pd
import numpy as np

def extract_golden_standard(output_data):
    output = output_data
    col_names_r = ["time", "insoles_RightFoot_is_step", "insoles_RightFoot_is_lifted"]
    col_names_l = ["time", "insoles_LeftFoot_is_step", "insoles_LeftFoot_is_lifted"]

    y_right = output[col_names_r]
    y_left = output[col_names_l]

    # Initial Contact Extraction (heel strike)
    HS_r = y_right[["time"]].iloc[np.where(y_right["insoles_RightFoot_is_step"])].reset_index(drop=True)
    HS_l = y_left[["time"]].iloc[np.where(y_left["insoles_LeftFoot_is_step"])].reset_index(drop=True)

    if HS_r.empty:
        HS_r = HS_r
    elif HS_r.time[0] == 0:
        HS_r = HS_r.drop([0])

    if HS_l.empty:
        HS_l = HS_l
    elif HS_l.time[0] == 0:
        HS_l = HS_l.drop([0])

    y_timings_r = HS_r.copy()

    y_timings_l = HS_l.copy()

    frames = [y_timings_r, y_timings_l]

    y_HS = pd.concat(frames)

    # Final Contact Extraction (foot off)
    FO_r = y_right[["time"]].iloc[np.where(y_right["insoles_RightFoot_is_lifted"])].reset_index(drop=True)
    FO_l = y_left[["time"]].iloc[np.where(y_left["insoles_LeftFoot_is_lifted"])].reset_index(drop=True)

    if FO_r.empty:
        FO_r = FO_r
    elif FO_r.time[0] == 0:
        FO_r = FO_r.drop([0])

    if FO_l.empty:
        FO_l = FO_l
    elif FO_l.time[0] == 0:
        FO_l = FO_l.drop([0])

    y_timings_r = FO_r.copy()

    y_timings_l = FO_l.copy()

    frames = [y_timings_r, y_timings_l]

    y_FO = pd.concat(frames)
    
    return y_HS, y_FO