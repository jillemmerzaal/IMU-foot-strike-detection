from scipy.io import loadmat
import numpy as np
import json

def recursive_struct_to_dict(mat_struct):
    if isinstance(mat_struct, np.ndarray):
        if mat_struct.dtype.names:
            return {
                field: recursive_struct_to_dict(mat_struct[field][0])
                for field in mat_struct.dtype.names
            }
        else:
            return [recursive_struct_to_dict(el) for el in mat_struct]
    elif hasattr(mat_struct, '__dict__') and hasattr(mat_struct, '_fieldnames'):
        return {
            field: recursive_struct_to_dict(getattr(mat_struct, field))
            for field in mat_struct._fieldnames
        }
    else:
        return mat_struct

def load_mat_results(filepath):
    mat_data = loadmat(filepath, struct_as_record=False, squeeze_me=True)
    raw_results = mat_data['results']
    results = {}

    for subj_id in raw_results._fieldnames:
        subj_data = getattr(raw_results, subj_id)
        results[subj_id] = {}

        for course in subj_data._fieldnames:
            course_data = getattr(subj_data, course)
            results[subj_id][course] = {}
            for section in course_data._fieldnames:
                section_data = getattr(course_data, section)
                y = getattr(section_data, 'y', None)
                y_hat = getattr(section_data, 'y_hat', None)
                get_walk_mode = getattr(section_data, 'get_walk_mode', None)


                # Handle nested y_hat structures (e.g., multiple algorithms)
                if hasattr(y_hat, '_fieldnames'):
                    y_hat = recursive_struct_to_dict(y_hat)

                results[subj_id][course][section] = {
                    'y': y,
                    'y_hat': y_hat,
                    "get_walk_mode": get_walk_mode,
                }
    return results

def load_json_results(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)