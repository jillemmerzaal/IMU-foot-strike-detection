import numpy as np
from biomechzoo import biomechzoo
from python_code.src.utils.fileparts import fileparts

def clean_filelist(fl):
    fl_new = []
    for f in fl:
        _, filename, _, _ = fileparts(f)
        if not filename.startswith('._'):
            fl_new.append(f)
    return np.array(fl_new)

