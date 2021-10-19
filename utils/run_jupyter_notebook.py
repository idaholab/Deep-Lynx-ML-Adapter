# Copyright 2021, Battelle Energy Alliance, LLC

import os
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor


def run_jupyter_notebook(file_path: str, kernel: str):
    """
    Runs a Jupyter Notebook programmatically

    Args
        file_path (string): the file path to the Jupyter Notebook
        kernel (string): name of Jupyter Notebook kernel e.g. (python3, ir) 
    """
    path = os.path.split(file_path)
    with open(file_path) as f:
        nb = nbformat.read(f, as_version=4)
    ep = ExecutePreprocessor(timeout=600, kernel_name=kernel)
    ep.preprocess(nb, {'metadata': {'path': path[0]}})