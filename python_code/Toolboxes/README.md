# Compatibility Considerations

The main.py file needs python 3.11 or newer aswell as some other newer packages (scipy, pyarrow) for biomechzoo. KielMAT and PyShoe are older toolboxes that depend on older versions of these packages so you should have 2 envioronments.

Recommended : python 3.10

Important: scipy < 1.14.0

`python_code/Toolboxes> pip install -r toolboxes_requirements.txt`

More info on [KielMAT&#39;s website](https://neurogeriatricskiel.github.io/KielMAT/examples/modules_05_icd/) and [PyShoe&#39;s Repo](https://github.com/utiasSTARS/pyshoe)

## Running the toolboxes

From the root directory, run the `run_toolboxes.py` script:

```
IMU-foot-strike-detection> python -m python_code.run_toolboxes
```

Note only necessary ins_tools were kept, machine learning algorithms are not used.
