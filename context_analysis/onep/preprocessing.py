from typing import Tuple
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin
from spiketimes.df.binning import which_bin
from context_analysis.resample import downsample


class PivotTransformer(BaseEstimator, TransformerMixin):
    """Transformer for pivoting data in long format
    """

    def __init__(
        self,
        cell_col: str = "cell_id",
        time_col: str = "time",
        value_col: str = "value",
    ):
        """Construct a transformer object

        Args:
            cell_col (str, optional): Column name containing cell IDS. Defaults to "cell_id".
            time_col (str, optional): Column name containing time values. Defaults to "time".
            value_col (str, optional): Column name containing cell activity values. Defaults to "value".
        """
        self.cell_col = cell_col
        self.time_col = time_col
        self.value_col = value_col

    def fit(self, X: pd.DataFrame, _y: int = 0):
        return self

    def transform(self, X: pd.DataFrame):
        return X.pivot(
            index=self.time_col, columns=self.cell_col, values=self.value_col
        )


class FloatIndexDownsampler(BaseEstimator, TransformerMixin):
    """Transformer for downsampling data in wide format
    """

    def __init__(
        self, new_interval: str, index_name: str = "time",
    ):
        """Construct a downsampler transformer

        Args:
            new_interval (str): String of the new time interval
            index_name (str, optional): Name of the time index. Defaults to "time".
        """
        self.new_interval = new_interval
        self.index_name = index_name

    def fit(self, X: pd.DataFrame, y=0):
        return self

    def transform(self, X: pd.DataFrame, y=0):
        X = downsample(X.reset_index(), new_interval=self.new_interval)
        X.set_index(self.index_name, inplace=True)
        return X


def block_from_time(
    df: pd.DataFrame, session_name: str, time_col: str = "time"
) -> pd.Series:
    """Get context for each data point in a dataframe

    Args:
        df (pd.DataFrame): DataFrame of data points format
        session_name (str): Name of the session. Time-Context relationship depends on experimental session. 
        time_col (str, optional): Name of the column containing time info. Defaults to "time".

    Returns:
        pd.Series: Series of contexts.
    """
    df = align_to_block(df, session_name, time_col)
    y = df["block"]
    return y


def get_pivoted_X(
    df: pd.DataFrame,
    downsample_interval: str,
    cell_col: str = "cell_id",
    time_col: str = "time",
    value_col: str = "value",
) -> pd.DataFrame:
    """Transform a dataframe in long format into a feature matrix in wide format

    Args:
        df (pd.DataFrame): DataFrame of data in long format
        downsample_interval (str): Interval for downsampling
        cell_col (str, optional): Name of column containing cell_ids. Defaults to "cell_id".
        time_col (str, optional): Name of column containing time values. Defaults to "time".
        value_col (str, optional): Name of column containing activity values. Defaults to "value".

    Returns:
        pd.DataFrame: The transformed DataFrame with one column per cell and one row per time point
    """

    pipe = Pipeline(
        [
            (
                "pivot",
                PivotTransformer(
                    cell_col=cell_col, time_col=time_col, value_col=value_col
                ),
            ),
            (
                "downsample",
                FloatIndexDownsampler(
                    new_interval=downsample_interval, index_name="time"
                ),
            ),
        ]
    )
    X = pipe.fit_transform(df)
    return X


def align_to_block(
    df: pd.DataFrame, session_name: str, time_col: str = "time"
) -> pd.DataFrame:
    """Add column to DataFrame containing the experimental block

    Args:
        df (pd.DataFrame): DataFrame containing the data
        session_name (str): Name of the session on which the data was recorded. The time-context relationship depends on the session.
        time_col (str, optional): Name of the column containing time points. Defaults to "time".

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
    df = which_bin(df, bin_edges=bins, spiketimes_col=time_col)
    df = df.assign(block=df["bin_values"].map(bin_mapper))

    if session_name == "day5-test2":
        df.loc[df["bin_idx"] == 6, "block"] = "mixed"

    df.loc[df["bin_idx"] > max_idx] = np.nan
    return df


def remove_nan_ys(X: pd.DataFrame, y: pd.Series) -> Tuple[pd.DataFrame, pd.Series]:
    y.index = X.index
    X = X[~y.isnull()]
    y = y[~y.isnull()]
    return X, y


def remove_mixed_ys(X: pd.DataFrame, y: pd.Series) -> Tuple[pd.DataFrame, pd.Series]:
    X = X[y != "mixed"]
    y = y[y != "mixed"]
    return X, y
