from typing import Optional, List
import pandas as pd
from pathlib import Path
import context_analysis.utils
import warnings


def load_mice(
    experiment: str,
    group_names: Optional[List[str]] = None,
    data_dir: Optional[Path] = None,
) -> pd.DataFrame:

    # Turn this into decorator
    if data_dir is None:
        data_dir = context_analysis.utils.get_default_data_dir()
    data_dir = data_dir / experiment
    if not data_dir.exists():
        print(str(data_dir))
        raise FileNotFoundError("Unknown data dir")

    mouse_file = data_dir / "mice.parquet.gzip"
    if not mouse_file.exists():
        print(str(mouse_file))
        raise FileNotFoundError("Mouse file not found")
    df = pd.read_parquet(mouse_file)
    if group_names is not None:
        df = df.loc[df["group"].isin(group_names)]
    return df


def load_behaviour(
    experiment: str,
    session_names: List[str],
    mouse_names: Optional[List[str]] = None,
    group_names: Optional[List[str]] = None,
    data_dir: Optional[Path] = None,
    warn_on_missing: bool = True,
) -> pd.DataFrame:
    if data_dir is None:
        data_dir = context_analysis.utils.get_default_data_dir()
    data_dir = data_dir / experiment
    if not data_dir.exists():
        print(str(data_dir))
        raise FileNotFoundError("Unknown data dir")

    df_list: List[pd.DataFrame] = []
    for session_name in session_names:
        data_path = data_dir / session_name / "behaviour.parquet.gzip"
        if not data_path.exists():
            if warn_on_missing:
                msg = str(data_path) + " is missing"
                warnings.warn(msg)
            continue
        df_list.append(pd.read_parquet(data_path).assign(session_name=session_name))

    df = pd.concat(df_list)
    if mouse_names is not None:
        df = df.loc[df["mouse"].isin(mouse_names)]

    df_mice = load_mice(experiment="", group_names=group_names, data_dir=data_dir)
    df = df.merge(df_mice)
    return df


def load_cells(
    experiment: str,
    mice_names: Optional[List[str]] = None,
    group_names: Optional[List[str]] = None,
    data_dir: Optional[Path] = None,
):
    session_mapper = {
        i: session_name
        for i, session_name in enumerate(
            [
                "day1-epm",
                "day2-morning",
                "day2-afternoon",
                "day3-morning",
                "day3-afternoon",
                "day4-test1",
                "day5-test2",
            ]
        )
    }
    if data_dir is None:
        data_dir = context_analysis.utils.get_default_data_dir()
    data_dir = data_dir / experiment
    if not data_dir.exists():
        print(str(data_dir))
        raise FileNotFoundError("Unknown data dir")

    cell_file = data_dir / "cells.parquet.gzip"
    if not cell_file.exists():
        print(str(cell_file))
        raise FileNotFoundError("Cell file not found")
    df = pd.read_parquet(cell_file).rename(columns={"mouse_name": "mouse"}).iloc[:, 1:]
    df_mice = load_mice(experiment="", group_names=group_names, data_dir=data_dir)
    df = df.merge(df_mice)
    if mice_names is not None:
        df = df.loc[df["mouse"].isin(mice_names)]
    df["session_name"] = df["session_index"].map(session_mapper)
    df["cell_id"] = pd.Categorical(df["cell_id"])
    return df


def load_traces(
    experiment: str,
    session_names: List[str],
    mouse_names: Optional[List[str]] = None,
    group_names: Optional[List[str]] = None,
    data_dir: Optional[Path] = None,
    warn_on_missing: bool = True,
) -> pd.DataFrame:
    df = _load_datafile(
        file_name="traces",
        experiment=experiment,
        session_names=session_names,
        mouse_names=mouse_names,
        group_names=group_names,
        data_dir=data_dir,
        warn_on_missing=warn_on_missing,
    )
    return df


def load_spikes(
    experiment: str,
    session_names: List[str],
    mouse_names: Optional[List[str]] = None,
    group_names: Optional[List[str]] = None,
    data_dir: Optional[Path] = None,
    warn_on_missing: bool = True,
) -> pd.DataFrame:
    df = _load_datafile(
        file_name="spikes",
        experiment=experiment,
        session_names=session_names,
        mouse_names=mouse_names,
        group_names=group_names,
        data_dir=data_dir,
        warn_on_missing=warn_on_missing,
    )
    return df


def _load_datafile(
    file_name: str,
    experiment: str,
    session_names: List[str],
    mouse_names: Optional[List[str]] = None,
    group_names: Optional[List[str]] = None,
    data_dir: Optional[Path] = None,
    warn_on_missing: bool = True,
):
    if data_dir is None:
        data_dir = context_analysis.utils.get_default_data_dir()
    data_dir = data_dir / experiment
    if not data_dir.exists():
        print(str(data_dir))
        raise FileNotFoundError("Unknown data dir")

    df_list: List[pd.DataFrame] = []
    for session_name in session_names:
        data_path = data_dir / session_name / f"{file_name}-{session_name}.parquet.gzip"
        if not data_path.exists():
            if warn_on_missing:
                msg = str(data_path) + " is missing"
                warnings.warn(msg)
            continue
        df_list.append(pd.read_parquet(data_path).assign(session_name=session_name))

    df = pd.concat(df_list)
    if mouse_names is not None:
        df = df.loc[df["mouse"].isin(mouse_names)]

    df_cells = load_cells(experiment="", group_names=group_names, data_dir=data_dir)
    df = df.merge(df_cells)
    df["cell_id"] = pd.Categorical(df["cell_id"])
    return df
