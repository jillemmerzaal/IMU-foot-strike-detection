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

    count = 0
    if HS_r.empty:
        HS_r = HS_r
    elif HS_r.time[0] == 0:
        count += 1
        HS_r = HS_r.drop([0])

    if HS_l.empty:
        HS_l = HS_l
    elif HS_l.time[0] == 0:
        count += 1
        HS_l = HS_l.drop([0])

    y_timings_r = HS_r.copy()

    y_timings_l = HS_l.copy()

    frames = [y_timings_r, y_timings_l]

    y_HS = pd.concat(frames).to_numpy().squeeze()
    y_HS.sort()

    # Final Contact Extraction (foot off)
    FO_r = y_right[["time"]].iloc[np.where(y_right["insoles_RightFoot_is_lifted"])].reset_index(drop=True)
    FO_l = y_left[["time"]].iloc[np.where(y_left["insoles_LeftFoot_is_lifted"])].reset_index(drop=True)

    y_timings_r = FO_r.copy()

    y_timings_l = FO_l.copy()

    frames = [y_timings_r, y_timings_l]

    y_FO = pd.concat(frames).to_numpy().squeeze()
    y_FO.sort()
    
    if count == 2: # if both feet started on the ground void the first feet lift as it's not a real step
        y_FO = y_FO[1:]
        
    if np.max(y_FO) < np.max(y_HS): # ensure the sequence to end with a foot off 
        y_HS = y_HS[:-1]

    return y_HS, y_FO