from pathlib import Path
from typing import Tuple
import pandas as pd
import numpy as np
from spiketimes.df.binning import which_bin


def get_default_data_dir() -> Path:
    return Path(".").absolute().parents[1] / "data"


def get_default_fig_dir() -> Path:
    return Path(".").absolute().parents[1] / "figs"

