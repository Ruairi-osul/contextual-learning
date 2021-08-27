from typing import Optional, List
import pandas as pd


def downsample(
    df: pd.DataFrame,
    new_interval: str,
    time_col="time",
    grouping_cols: Optional[List[str]] = None,
):
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

