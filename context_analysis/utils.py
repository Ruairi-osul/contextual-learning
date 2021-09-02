from pathlib import Path
from typing import Tuple
import pandas as pd
import numpy as np
from spiketimes.df.binning import which_bin


def get_default_data_dir() -> Path:
    return Path(".").absolute().parents[1] / "data"


def get_default_fig_dir() -> Path:
    return Path(".").absolute().parents[1] / "figs"


def align_to_block(
    df: pd.DataFrame, session_name: str, time_col: str = "time"
) -> pd.DataFrame:
    if "morn" in session_name:
        return df.assign(block="safe")
    elif "noon" in session_name:
        return df.assign(block="scary")

    if session_name == "day4-test1":
        blocks = ["safe", "scary"]
        max_idx = 5
    else:  # session_name == "day5-test2":
        blocks = ["scary", "safe"]
        max_idx = 6
    bins = np.array([i * 120 for i in range(8)])
    blocks = [blocks[i % 2] for i, _ in enumerate(bins)]
    bin_mapper = {b: block for b, block in zip(bins, blocks)}
    df = which_bin(df, bin_edges=bins, spiketimes_col=time_col)
    df = df.assign(block=df["bin_values"].map(bin_mapper))

    if session_name == "day5-test2":
        df.loc[df["bin_idx"] == 6, "block"] = "mixed"

    df = df.loc[df["bin_idx"] <= max_idx]
    return df

