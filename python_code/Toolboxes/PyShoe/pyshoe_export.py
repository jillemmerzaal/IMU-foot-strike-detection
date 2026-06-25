import sys
import numpy as np
from pathlib import Path
import pandas as pd
from scipy.io import savemat

PYSHOE_DIR = Path(__file__).resolve().parent
if str(PYSHOE_DIR) not in sys.path:
    sys.path.insert(0, str(PYSHOE_DIR))

from ins_tools.INS import INS

# Necessary data for pyshoe algorithm (order matters)
RIGHT_FOOT_COLS = ['acceleration_RightFoot_x', 'acceleration_RightFoot_y', 'acceleration_RightFoot_z', 'angularVelocity_RightFoot_x', 'angularVelocity_RightFoot_y', 'angularVelocity_RightFoot_z']
LEFT_FOOT_COLS = ['acceleration_LeftFoot_x', 'acceleration_LeftFoot_y', 'acceleration_LeftFoot_z', 'angularVelocity_LeftFoot_x', 'angularVelocity_LeftFoot_y', 'angularVelocity_LeftFoot_z']
TARGET_COLS = ["time"] + RIGHT_FOOT_COLS + LEFT_FOOT_COLS

SAMPLING_FREQUENCY = 60
DETECTORS = ['shoe', 'ared', 'amvd', 'mbgtd']
SPECS = {  # G values are sensor dependent more at https://github.com/utiasSTARS/pyshoe/tree/master
    'shoe': {"G":2e8},
    'ared': {"G":2.0},
    'amvd': {"G":7},
    'mbgtd': {"G":10},
}


def pyshoe_process_single_file(file_path, course, id, y_HS_true, y_FO_true, data_path):
    """
    Reads the file, then runs all 4 detectors.
    """
    # Look at the disk first to see which detectors actually need to be run
    detectors_to_run = []
    for detector_name in DETECTORS:
        out_file = data_path / "toolbox1" / detector_name / f'{id}_{course}.mat'
        if not out_file.exists():
            detectors_to_run.append((detector_name, out_file))
            
    # If the list is empty, every single detector has already been processed. 
    if not detectors_to_run:
        return f"Skipped {id}_{course} (Already completely processed)"

    try:
        df = pd.read_csv(file_path, usecols=TARGET_COLS)
        imu_left = df[LEFT_FOOT_COLS].to_numpy() 
        imu_right = df[RIGHT_FOOT_COLS].to_numpy() # PyShoe takes in an N x 6 numpy array
        time = df["time"].to_numpy().squeeze()

        # loop detectors
        for detector_name, out_file in detectors_to_run:
            G_val = SPECS[detector_name]['G']

            # Left Foot
            ins_left = INS(imu_left, sigma_a=0.00098, sigma_w=8.7266463e-5, T=1.0/SAMPLING_FREQUENCY) 
            ins_left.baseline(W=5, G=G_val, detector=detector_name)
            steps_left = ins_left.zv
            
            padded_left = np.insert(steps_left, 0, False).astype(int)
            diff_left = np.diff(padded_left)
            HS_indices_left = np.where(diff_left == 1)[0]
            FO_indices_left = np.where(diff_left == -1)[0]
            # Case where foot started stationary
            if steps_left[0]:
                HS_indices_left = HS_indices_left[1:]
                FO_indices_left = FO_indices_left[1:]
            HS_times_left = time[HS_indices_left]
            FO_times_left = time[FO_indices_left]

            # Right Foot
            ins_right = INS(imu_right, sigma_a=0.00098, sigma_w=8.7266463e-5, T=1.0/60) 
            ins_right.baseline(W=5, G=G_val, detector=detector_name)
            steps_right = ins_right.zv 
            
            padded_right = np.insert(steps_right, 0, False).astype(int)
            diff_right = np.diff(padded_right)
            HS_indices_right = np.where(diff_right == 1)[0]
            FO_indices_right = np.where(diff_right == -1)[0]
            if steps_right[0]:
                HS_indices_right = HS_indices_right[1:]
                FO_indices_right = FO_indices_right[1:]
            HS_times_right = time[HS_indices_right]
            FO_times_right = time[FO_indices_right]

            # Combine
            all_HS_times = np.concatenate((HS_times_left, HS_times_right))
            all_FO_times = np.concatenate((FO_times_left, FO_times_right))
            
            y_HS_pred = np.zeros((len(all_HS_times), 2))
            y_FO_pred = np.zeros((len(all_FO_times), 2))
            y_HS_pred[:,0] = all_HS_times
            y_FO_pred[:,0] = all_FO_times

            results = {
                'y_HS': y_HS_true,         # true
                'y_FO': y_FO_true,
                'y_hat_HS': y_HS_pred,     # pred
                'y_hat_FO': y_FO_pred
            }

            # Save specific detector output
            out_file.parent.mkdir(parents=True, exist_ok=True)
            savemat(out_file, {'results': results})

        return f"{id}_{course}.mat Success"
    
    except Exception as e:
        return f"Error: {str(e)}"

