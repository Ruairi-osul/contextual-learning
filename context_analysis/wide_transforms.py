from typing import Optional
from context_analysis.load import load_cells
import pandas as pd
import numpy as np
from spiketimes.df.binning import which_bin


def subset_neurons(
    df: pd.DataFrame,
    group: Optional[str] = None,
    session: Optional[str] = None,
    mouse: Optional[str] = None,
    exp: str = "pfc",
) -> pd.DataFrame:
    """Subset neurons based on experimental conditions

    Args:
        df (pd.DataFrame): Wide df (time, neurons)
        group (Optional[str], optional): Group name. Defaults to None.
        session (Optional[str], optional): Sessuib name. Defaults to None.
        mouse (Optional[str], optional): Mouse name. Defaults to None.
        exp (str, optional): Experimental cohort. Defaults to "pfc".

    Returns:
        pd.DataFrame: Subsetted DataFrame
    """
    neurons = load_cells(experiment=exp)
    if session is not None:
        neurons = neurons.loc[lambda x: x.session_name == session]
    if group is not None:
        neurons = neurons.loc[lambda x: x.group == group]
    if mouse is not None:
        neurons = neurons.loc[lambda x: x.mouse == mouse]
    idx = neurons["cell_id"].unique()
    return df[[c for c in df.columns if str(c) in list(map(str, idx))]]


def align_to_block(df: pd.DataFrame, session_name: str,) -> pd.DataFrame:
    """Add column to DataFrame containing the experimental block

    Args:
        df (pd.DataFrame): DataFrame containing the data
        session_name (str): Name of the session on which the data was recorded. The time-context relationship depends on the session.

    Returns:
        pd.DataFrame: Original dataframe augmented with context column
    """
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
    df.index.name = "time"
    df = df.reset_index()
    df = which_bin(df, bin_edges=bins, spiketimes_col="time")
    df = df.assign(block=df["bin_values"].map(bin_mapper))

    if session_name == "day5-test2":
        df.loc[df["bin_idx"] == 6, "block"] = "mixed"

    df.loc[df["bin_idx"] > max_idx] = np.nan
    df = df.set_index("time")
    return df
