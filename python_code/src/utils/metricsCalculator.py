from dataclasses import dataclass, field
from typing import Dict, Any
import numpy as np

@dataclass
class MetaData:
    subj: str
    parcours: str
    condition: str
    algorithm: str
    total: int
    features: Dict[str, Any] = field(default_factory=dict)


def enrich_metadata(metadata: MetaData, features: Dict[str, Any]) -> MetaData:
    metadata.features.update(features)
    return metadata


def evaluate_algorithm(insole_IC, algorithm_IC, tol=300):
    tp = 0
    fp = 0
    ms_error = []
    matched_ref = np.zeros(len(insole_IC), dtype=bool)
    for ic in algorithm_IC:
        window_start = ic - tol
        window_end = ic + tol

        mask = (insole_IC >= window_start) & (insole_IC <= window_end) & (~matched_ref.astype(bool))
        idx = np.where(mask)[0]

        if len(idx) == 0:
            fp += 1
        elif len(idx) == 1:
            tp += 1
            matched_ref[idx[0]] = True
            e = ic - insole_IC[idx[0]]
            ms_error.append(e)
        else:
            tp += 1
            differences = np.abs(insole_IC[idx] - ic)
            min_idx = np.argmin(differences)
            matched_idx = idx[min_idx]
            matched_ref[matched_idx] = True

            e = ic - insole_IC[matched_idx]
            ms_error.append(e)
    fn = np.sum(~matched_ref)

    return tp, fp, fn, np.mean(ms_error) if ms_error else np.nan

def evaluate_algorithm_per_surface(insole_ic, algorithm_ic, surface_ic, tol=300):
    unique_surfaces = list(dict.fromkeys(surface_ic))
    outcome = {}
    for surface in unique_surfaces:
        outcome[surface] = {}
        outcome[surface]["tp"] = 0
        outcome[surface]["fp"] = 0
        outcome[surface]["fn"] = 0
        outcome[surface]["ms_error"] = []

    # Create a reference to track matched insole steps
    matched_ref = np.zeros(len(insole_ic), dtype=bool)
    for algo_idx, algo_ic in enumerate(algorithm_ic):
        window_start = algo_ic - tol
        window_end = algo_ic + tol

        mask = (insole_ic >= window_start) & (insole_ic <= window_end) & (~matched_ref.astype(bool))
        idx = np.where(mask)[0]

        if len(idx) == 0:
            # situation where no matches were found....
            difference = np.abs(insole_ic - algo_ic)
            min_idx = np.argmin(difference)
            surface = surface_ic[min_idx]
            # surface = surface_AL[algo_idx]
            outcome[surface]["fp"] += 1


        elif len(idx) == 1:
            # find the matching surface according to the insole data
            surface = surface_ic[idx[0]]
            outcome[surface]["tp"] += 1

            matched_ref[idx[0]] = True # to prevent double matching
            # determine error
            e = algo_ic - insole_ic[idx[0]]
            outcome[surface]["ms_error"].append(e)

        else:
            differences = np.abs(insole_ic[idx] - algo_ic)
            min_idx = np.argmin(differences)
            matched_idx = idx[min_idx]
            matched_ref[matched_idx] = True

            surface = surface_ic[matched_idx]
            outcome[surface]["tp"] += 1
            e = algo_ic - insole_ic[matched_idx]
            outcome[surface]["ms_error"].append(e)

    for m, match in enumerate(matched_ref):
        if not match:
            surface = surface_ic[m]
            outcome[surface]["fn"] += 1

    return outcome


def calculate_performance_metrics(tp, fp, fn, metadata):
    if tp != 0:
        features = {
            "f1_score": round(2 * tp / (2 * tp + fp + fn),2),
            "accuracy": round(tp / (tp + fp + fn),2),
            "precision": round(tp / (tp + fp),2),
            "recall": round(tp / (tp + fn),2)
        }
    else:
        features = {
            "f1_score": 0,
            "accuracy": 0,
            "precision": 0,
            "recall": 0}



    return enrich_metadata(metadata, features)
