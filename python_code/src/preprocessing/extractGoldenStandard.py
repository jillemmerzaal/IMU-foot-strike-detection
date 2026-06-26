import numpy as np
import pandas as pd

def extract_goldenstandard(output):
    """
    Extract the 'golden standard' for heel strike and toe off.
    Expects `output` to be a pandas DataFrame containing the columns:
    'time', 'insoles_RightFoot_is_step', 'insoles_RightFoot_is_lifted',
    'insoles_LeftFoot_is_step', 'insoles_LeftFoot_is_lifted'.
    """
    
    # Helper function to handle both string "True" and boolean True
    def get_event_times(df, col_name):
        mask = (df[col_name] == "True") | (df[col_name] == True)
        return df.loc[mask, "time"].values

    # Right Leg
    ic_r = get_event_times(output, "insoles_RightFoot_is_step")
    tc_r = get_event_times(output, "insoles_RightFoot_is_lifted")

    # Left Leg
    ic_l = get_event_times(output, "insoles_LeftFoot_is_step")
    tc_l = get_event_times(output, "insoles_LeftFoot_is_lifted")
    
    # Remove heel strikes at time index 0 -> means walking has not yet started
    ic_r = remove_t0(ic_r)
    ic_l = remove_t0(ic_l)
    
    # Ensure first FO comes AFTER first IC per foot
    tc_r = align_fo_to_hs(ic_r, tc_r)
    tc_l = align_fo_to_hs(ic_l, tc_l)

    # Pair each HS with its following FO (0 for Right, 1 for Left)
    paired_r = pair_events(ic_r, tc_r, 0)
    paired_l = pair_events(ic_l, tc_l, 1)
        
    # Combine and sort by InitialContact
    timings = pd.concat([paired_r, paired_l], ignore_index=True)
    timings = timings.sort_values(by='InitialContact').reset_index(drop=True)

    # Extract final arrays as Nx2 matrices [time, foot_label]
    y_HS = timings[['InitialContact', 'LeftStance']].to_numpy()
    y_FO = timings[['TerminalContact', 'LeftStance']].to_numpy()
    
    return y_HS, y_FO

# -------------------------------------------------------------------------
# HELPER FUNCTIONS

def remove_t0(ic):
    if len(ic) > 0 and ic[0] == 0:
        return ic[1:]
    return ic

def align_fo_to_hs(ic, tc):
    if len(ic) > 0 and len(tc) > 0:
        while len(tc) > 0 and tc[0] < ic[0]:
            tc = tc[1:]
    return tc

def pair_events(ic, tc, foot_label):
    tc_matched = np.full(len(ic), np.nan)

    for i in range(len(ic)):
        # upper bound
        if i < len(ic) - 1:
            upper_bound = ic[i+1]
        else:
            upper_bound = np.inf

        # Find first TC satisfying ic[i] < TC < ic[i+1]
        valid_tcs = tc[(tc > ic[i]) & (tc < upper_bound)]
        if len(valid_tcs) > 0:
            tc_matched[i] = valid_tcs[0]

    valid = ~np.isnan(tc_matched)
    
    # DataFrame to mimic the MATLAB table
    T = pd.DataFrame({
        'InitialContact': ic[valid],
        'TerminalContact': tc_matched[valid],
        'LeftStance': np.full(np.sum(valid), foot_label)
    })
    
    return T