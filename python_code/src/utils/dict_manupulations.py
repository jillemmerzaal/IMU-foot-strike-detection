import numpy as np
import pandas as pd
from python_code.src.utils.metricsCalculator import MetaData, enrich_metadata, evaluate_algorithm, calculate_performance_metrics

class DictManupulations:
    @staticmethod
    def combine_data(data1, data2, data3):
        combined_results = data1.copy()
        for subj_id, subj_data in data2.items():
            for course_name, course_data in subj_data.items():
                for section_name, section_data in course_data.items():
                    combined_results[subj_id][course_name][section_name]["y_hat"]["Oxford"] = \
                    data2[subj_id][course_name][section_name]["y_hat"]

        for subj_id, subj_data in data3.items():
            for course_name, course_data in subj_data.items():
                for section_name, section_data in course_data.items():
                    for algo_name, algo_data in section_data["y_hat"].items():
                        combined_results[subj_id][course_name][section_name]["y_hat"][algo_name] = \
                            data3[subj_id][course_name][section_name]["y_hat"][algo_name]


        return combined_results

    @staticmethod
    def metrics(data):
        all_metadata = []
        for subj_id, subj_data in data.items():
            for course_name, course_data in subj_data.items():
                for section_name, section_data in course_data.items():
                    insole_IC = np.array(section_data["y"])
                    if insole_IC.ndim == 2:
                        insole_IC = insole_IC[:, 0]

                    y_hat_dict = section_data.get("y_hat", {})
                    walk_mode = section_data.get("get_walk_mode")
                    if walk_mode is None:
                        walk_mode = "all"

                    if isinstance(y_hat_dict, dict):
                        for algo_name, algo_data in y_hat_dict.items():
                            if algo_data:
                                try:
                                    algorithm_IC = np.array(algo_data)[:, 0]
                                except IndexError:
                                    algorithm_IC = np.array(algo_data)

                                # evaluate the algorithms.
                                tp, fp, fn, error = evaluate_algorithm(insole_IC, algorithm_IC)
                            else:
                                metadata = MetaData(subj=subj_id, parcours=course_name, condition=walk_mode, algorithm=algo_name)
                                tp = 0
                                fp = 0
                                fn = len(insole_IC)
                                error = -999

                            metadata = MetaData(subj=subj_id, parcours=course_name, condition=walk_mode, algorithm=algo_name)
                            features = {"TP": tp, "FP": fp, "FN": fn, "error (ms)": error}
                            metadata = enrich_metadata(metadata, features)
                            metadata = calculate_performance_metrics(tp=tp, fn=fn, fp=fp, metadata=metadata)
                            all_metadata.append(metadata)

        return all_metadata

    @staticmethod
    def from_dataclass_to_dataframe(data):
        records = []
        for m in data:
            row = {
                "subj": m.subj,
                "condition": m.condition,
                "parcours": m.parcours,
                "algorithm": m.algorithm,
                "total": m.total,
                **m.features
            }
            records.append(row)

        return pd.DataFrame(records)
