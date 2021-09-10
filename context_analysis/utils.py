from pathlib import Path
from typing import Tuple
import pandas as pd
import numpy as np
from spiketimes.df.binning import which_bin


def get_default_data_dir() -> Path:
    """Get the path of the default data dir

    Returns:
        Path: Pathlib Path object to data dir
    """
    return Path(".").absolute().parents[1] / "data"


def get_default_fig_dir() -> Path:
    """Get the path of the default fig dir

    Returns:
        Path: Pathlib Path object to fig dir
    """
    return Path(".").absolute().parents[1] / "figs"


def get_derived_data_dir(experiment: str) -> Path:
    """Get the path to the derived data dir of the experiment

    Args:
        experiment (str): Name of experiment

    Returns:
        Path: Path to the datadir
    """
    return get_default_data_dir() / experiment / "derived"
