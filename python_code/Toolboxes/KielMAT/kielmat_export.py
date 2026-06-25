import numpy as np
import pandas as pd
from scipy.io import savemat

from kielmat.utils.preprocessing import signal_decomposition_algorithm

# Define global constants
COLS = ['acceleration_Pelvis_x', 'acceleration_Pelvis_y', 'acceleration_Pelvis_z']
SAMPLING_FREQUENCY = 60



def kielmat_process_single_file(file_path, course, id, y_HS_true, y_FO_true, data_path):
    output_dir = data_path / "toolbox1" / "KielMAT"
    output_file = output_dir / f"{id}_{course}.mat"

    if output_file.exists():
        return f"Skipped {id}_{course}.mat (already processed)"

    try:
        acceleration_data = pd.read_csv(file_path, usecols=COLS) # KielMAT takes in a pandas dataframe object

        vertical_accel_array = acceleration_data['acceleration_Pelvis_z'].to_numpy()

        HS_times, FO_times = signal_decomposition_algorithm(
            vertical_accelerarion_data=vertical_accel_array,
            initial_sampling_frequency=SAMPLING_FREQUENCY
        )

        temp = HS_times*1000 # heel strike times in ms
        y_HS_pred = np.zeros((len(temp), 2)) # expected structure by the rest of the pipeline
        y_HS_pred[:,0] = temp 

        temp = FO_times*1000 # foot off times in ms
        y_FO_pred = np.zeros((len(temp), 2)) # expected structure by the rest of the pipeline
        y_FO_pred[:,0] = temp 

        # Create a structure matching what the pipeline expects:
        # results.y and results.y_hat
        results = {
            'y_HS': y_HS_true,         # true
            'y_FO': y_FO_true,
            'y_hat_HS': y_HS_pred,     # pred
            'y_hat_FO': y_FO_pred
        }

        output_dir.mkdir(parents = True, exist_ok = True)
        savemat(output_file, {'results': results})

        return f'{id}_{course} Success'
    
    except Exception as e:
        return f"FAILED: {id}_{course} - Error: {str(e)}"