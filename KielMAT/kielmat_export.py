from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from scipy.io import loadmat, savemat
import os
from pathlib import Path
from kielmat.modules.gsd import ParaschivIonescuGaitSequenceDetection
from kielmat.modules.icd import ParaschivIonescuInitialContactDetection
from kielmat.config import cfg_colors

root = Path.cwd().parent
data_path = root / "data"

# print(type(root), type(data_path))

file_list = list(data_path.rglob("xsens.csv"))


def run_file(file_path):
    data = pd.read_csv(file_path)

    sampling_frequency = 60 # 6 recordings in 100 ms -> 60 recordings per second
    # Calculate the time values
    acceleration_data =  data[['acceleration_Pelvis_x', 'acceleration_Pelvis_y', 'acceleration_Pelvis_z']]

    # Create an instance of the ParaschivIonescuGaitSequenceDetection class
    gsd = ParaschivIonescuGaitSequenceDetection()

    # Call the gait sequence detection using gsd.detect to detect gait sequences
    gsd = gsd.detect(
        acceleration_data, 
        sampling_frequency
    )

    # Gait sequences are stored in gait_sequences_ attribute of gsd
    gait_sequences = gsd.gait_sequences_

    # print(gait_sequences)

    # Now, use Paraschiv-Ionescu initial contact detection algortihm to find initial contacts within detected gait sequences.
    icd = ParaschivIonescuInitialContactDetection()

    # Call the initial contact detection using icd.detect
    icd = icd.detect(
        acceleration_data,
        sampling_frequency,
        "acceleration_Pelvis_z"
    )

    y_pred = icd.initial_contacts_['onset'].to_numpy().reshape(-1,1)*1000 # IC times in ms

    # File naming convention {id}_{course}.mat
    id = file_path.parts[-2]
    course = file_path.parts[-3]
    y = get_ytrue(course,id)

    # Create a structure matching what the pipeline expects:
    # results.y and results.y_hat
    results = {
        'y': y,         # true
        'y_hat': y_pred # pred
    }

    dir_path = data_path / "toolbox1" / "KielMAT"

    dir_path.mkdir(parents=True, exist_ok=True)

    savemat(dir_path / f'{id}_{course}.mat', {'results': results})

    return results

def get_ytrue(course, id):
    file_path = data_path / "toolbox1" / "Mizrahi" / f'{id}_{course}.mat'

    mat = loadmat(file_path, struct_as_record = False, squeeze_me = True)
    results = mat['results']

    if not hasattr(results, 'y'):
        ImportError(".mat file doesn't have the correct structure. Expected 'results' key.")
    
    y_true = results.y

    return y_true
    

for file in file_list:
    run_file(file)
