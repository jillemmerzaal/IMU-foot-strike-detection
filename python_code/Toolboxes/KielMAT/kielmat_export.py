import numpy as np
import pandas as pd
from scipy.io import savemat

from kielmat.modules.gsd import ParaschivIonescuGaitSequenceDetection
from kielmat.modules.icd import ParaschivIonescuInitialContactDetection

# Define global constants
COLS = ['acceleration_Pelvis_x', 'acceleration_Pelvis_y', 'acceleration_Pelvis_z']
SAMPLING_FREQUENCY = 60



def kielmat_process_single_file(file_path, course, id, y_true, data_path):
    output_dir = data_path / "toolbox1" / "KielMAT"
    output_file = output_dir / f"{id}_{course}.mat"

    if output_file.exists():
        return f"Skipped {id}_{course}.mat (already processed)"

    try:
        acceleration_data = pd.read_csv(file_path, usecols=COLS) # KielMAT takes in a pandas dataframe object

        # Create an instance of the ParaschivIonescuGaitSequenceDetection class
        gsd = ParaschivIonescuGaitSequenceDetection()

        # Call the gait sequence detection using gsd.detect to detect gait sequences
        gsd = gsd.detect(
            acceleration_data, 
            SAMPLING_FREQUENCY
        )

        # Gait sequences are stored in gait_sequences_ attribute of gsd
        gait_sequences = gsd.gait_sequences_

        # Now, use Paraschiv-Ionescu initial contact detection algortihm to find initial contacts within detected gait sequences.
        icd = ParaschivIonescuInitialContactDetection()

        # initial contact detection using icd.detect
        icd = icd.detect(
            acceleration_data,
            SAMPLING_FREQUENCY,
            "acceleration_Pelvis_z",
            gait_sequences
        )

        temp = icd.initial_contacts_['onset'].to_numpy()*1000 # IC times in ms
        y_pred = np.zeros((len(temp), 2)) # expected structure by the rest of the pipeline
        y_pred[:,0] = temp 

        # Create a structure matching what the pipeline expects:
        # results.y and results.y_hat
        results = {
            'y': y_true,         # true
            'y_hat': y_pred # pred
        }

        output_dir.mkdir(parents = True, exist_ok = True)
        savemat(output_file, {'results': results})

        return f'{id}_{course}.mat Success'
    
    except Exception as e:
        return f"FAILED: {file_path.name} - Error: {str(e)}"