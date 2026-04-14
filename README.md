# IMU Foot Strike Detection

Code accompanying the manuscript:
submitted to Gait and Posture April 2026

[//]: # (> **[Insert full citation here]**)

[//]: # (> *[Journal Name]*, [Year]. DOI: [insert DOI])

---

## Overview

This repository provides the MATLAB and Python code used to evaluate IMU-based footstrike detection algorithms on walking data. 
The pipeline applies and benchmarks a set of established gait event detection methods using a multi-modal dataset collected 
in a real-world urban enviromnent. 

---

## Repository Structure
```
IMU-foot-strike-detection/
├── data/
│   └── data-set/               ← Download NEWBEE dataset here (see below)
├── matlab/
│   ├── biomechZoo/
│   └── main.m
│   ├── preprocessing/
│   ├── Toolboxes/
│   │   └── REID_IMU_Running_Event_ID/   ← Download REID toolbox here (see below)
│   ├── utils/
├── python_code/
│   ├── src/
│   ├── main.py
└── README.md
```
---
## Dependencies

### 1. Data — NEWBEE Gait Database
The analysis in this manuscript uses the **NEWBEE** dataset: 
> *NEWBEE: A Multi-Modal Gait Database of Natural Everyday-Walk in an Urban Environment*
> Available at: https://springernature.figshare.com/collections/NEWBEE_A_Multi-Modal_Gait_Database_of_Natural_Everyday-Walk_in_an_Urban_Environment/5758997/1

**Setup instructions:**
1. Navigate to the NEWBEE collection page linked above.
2. Download the dataset files.
3. Place all downloaded files into the following folder within this repository:

```
data/
```

> if the data/ directory does not exists, creat it manually before placing the data.
---

### 2. Gait Event Detection Toolbox -- REID_IMU
This repository relies on the **REID_IMU_Running_Event_ID** toolbox for gait event identification:

> Kiernan, D. (2023). *REID_IMU — Running Event ID: Unsupervised gait event detection using a single wearable accelerometer and/or gyroscope.*
> Available at: https://github.com/DovinKiernan/REID_IMU_Running_Event_ID

The toolbox implements 21 published gait event detection methods, of which we use 16, for IMU data from the shank or low-back/sacrum, and
returns timings of initial and terminal contact events.

**Setup instructions**
1. Clone or download the REID toolbox from the link aboce
2. Place the toolbox forlder into the following location within this repository: 

```
matlab/Toolboxes/
```

> If the `matlab/Toolboxes/` directory does not exist, create it manually before placing the toolbox.

---

## Getting Started 
Once the data and toolbox are in place, open MATLAB and: 
1. Set the *IMU-foot-strike-detection* as current working directory and add all the subfolders to your MATLAB path: 
```matlab
addpath(genpath("./"))
```
2. Run the main analysis script:
```matlab
% main.m
```

Per algorithm foot-strike detection results are saved in: 
```
data/toobox1
```

---
## Visualizations
All descriptives and visualizations are done in Python. This code reads the results from the folder `matlab/toolbox1`, 
calulates the metrics and visualizes the results in boxplot. 
To run it: 
1. Install biomechzoo

```python
pip install [biomechzoo]
```

2. run the main analysis script

```python
main.py
```

## Citation

If you use this code, please cite both the manuscript and the original toolbox:
**This manuscript:**
> [Insert full citation here]

**REID_IMU toolbox:**
> Kiernan, D. et al. (2023). Unsupervised gait event detection using a single wearable accelerometer and/or gyroscope: A comparison of methods across running speeds, surfaces, and foot strike patterns. *Sensors*.

**NEWBEE dataset:**
> V. Losing, M. Hasenjäger, NEWBEE: A multi-modal gait database of natural everyday-walk in an urban environment, collection (2022).
doi:10.6084/m9.figshare.c.5758997.v1.

---
