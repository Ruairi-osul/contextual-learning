from typing import Tuple
from context_analysis.resample import downsample
import pandas as pd
import numpy as np


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
