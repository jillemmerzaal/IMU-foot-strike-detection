import pandas as pd
import numpy as np
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

# Import your preprocessing and toolbox functions
from python_code.src.preprocessing.extractGoldenStandard import extract_golden_standard
from python_code.Toolboxes.KielMAT.kielmat_export import kielmat_process_single_file
from python_code.Toolboxes.PyShoe.pyshoe_export import pyshoe_process_single_file

# Constants
DATA_PATH = Path(__file__).resolve().parent.parent / "data"
COLS = ["time", "insoles_RightFoot_is_step", "insoles_LeftFoot_is_step", "insoles_RightFoot_is_lifted", "insoles_LeftFoot_is_lifted"]

def get_ytrue(course, id):
    try:
        file_path = DATA_PATH / "data_set" / course / id / "labels.csv"

        data = pd.read_csv(file_path, usecols = COLS)

        temp = extract_golden_standard(data)

        y_HS = np.zeros((len(temp[0]), 2))
        y_HS[:,0] = temp[0]

        y_FO = np.zeros((len(temp[1]), 2))
        y_FO[:,0] = temp[1]

        return y_HS, y_FO
    
    except Exception as e:
        return f"ERR: {str(e)}"
    
def process_file_all_toolboxes(file_path):
    id = file_path.parts[-2]
    course = file_path.parts[-3]

    # Get ground truth
    y_HS, y_FO = get_ytrue(course, id)
    if y_HS is None or y_FO is None:
        return f'FAILED: {id}_{course} - Could not load labels.csv'
    
    res_kielmat = kielmat_process_single_file(file_path, course, id, y_HS, y_FO, DATA_PATH)
    res_pyshoe = pyshoe_process_single_file(file_path, course, id, y_HS, y_FO, DATA_PATH)

    return f"{id}_{course} => KielMAT: [{res_kielmat}] | PyShoe: [{res_pyshoe}]"

if __name__ == "__main__":
    file_list = list(DATA_PATH.rglob("xsens.csv"))
    print(f"Found {len(file_list)} files to process.")

    if not file_list:
        print("No files found. Exiting.")
        exit()

    # Multiprocessing
    with ProcessPoolExecutor() as executor:
        results = executor.map(process_file_all_toolboxes, file_list)

        for r in results:
            print(r)
