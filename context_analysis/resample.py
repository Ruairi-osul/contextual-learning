from typing import Optional, List
import pandas as pd
from typing import Tuple
import pandas as pd
import numpy as np


def downsample(
    df: pd.DataFrame,
    new_interval: str,
    time_col="time",
    grouping_cols: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Resample a dataset. Works best if in long format

    Args:
        df (pd.DataFrame): DataFrame containing the dataset
        new_interval (str): String code for new time interval
        time_col (str, optional): Time column in existing dataset. Defaults to "time".
        grouping_cols (Optional[List[str]], optional): Columns used to group by for resampling. Defaults to None.

    Returns:
        pd.DataFrame: [description]
    """
    df["time"] = pd.to_timedelta(df[time_col], unit="s")
    df = df.set_index(time_col)
    if grouping_cols is not None:
        df = df.groupby(grouping_cols, as_index=False)
    return (
        df.resample(new_interval)
        .mean()
        .reset_index()
        .assign(time=lambda x: x[time_col].dt.total_seconds())
    )


def temporally_align_onep_behaviour(
    df_onep: pd.DataFrame,
    df_behaviour: pd.DataFrame,
    new_interval: str,
    time_col: str = "time",
    drop_max: bool = True,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Temporally align onep and behaviour DataFrames

    Args:
        df_onep (pd.DataFrame): One Photon DataFrame
        df_behaviour (pd.DataFrame): Behaviour DataFrame
        new_interval (str): Time string for desired sampling interval
        time_col (str, optional): Label of time column in both DataFrames, must be the same. Asumed to be in seconds. Defaults to "time".
        drop_max (bool, optional): If True, times after which there is no behaviour and onep [i.e. if one dataframe covers a longer time period than the other]. Defaults to True.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: Tuple of original DataFrames, resampled
    """
    df_onep = downsample(df_onep, new_interval=new_interval)
    df_behaviour = downsample(df_behaviour, new_interval=new_interval)
    if drop_max:
        max_time = np.min([df_onep[time_col].max(), df_behaviour[time_col].max()])
        df_onep = df_onep.loc[lambda x: x[time_col] < max_time]
        df_behaviour = df_behaviour.loc[lambda x: x[time_col] < max_time]
    return df_onep, df_behaviour
