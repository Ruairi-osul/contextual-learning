import pandas as pd
from .load import load_mice
from typing import Tuple, Dict


def split_by_group(
    df: pd.DataFrame, group_col: str = "group"
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    exp_df = df.loc[df[group_col] == "Experimental"]
    one_ctx_df = df.loc[df[group_col] == "One Context"]
    no_shock_df = df.loc[df[group_col] == "No Shock"]
    return exp_df, one_ctx_df, no_shock_df


def split_by_mouse(
    df: pd.DataFrame, experiment: str, mouse_col: str = "mouse"
) -> Dict[str, Dict[str, pd.DataFrame]]:
    """Split a master dataset into one split by group and mouse

    Args:
        df (pd.DataFrame): DataFrame containing all the data
        experiment (str): Name of experiment
        mouse_col (str, optional): Name of column containing mouse identifiers. Defaults to "mouse".

    Returns:
        Dict[str, Dict[str, pd.DataFrame]]: A nested dictionary. The first level is group. the second level is mouse and values are dataframes for that mouse.
    """
    d = load_mice(experiment=experiment).groupby("group")["mouse"].unique().to_dict()
    out = {}
    for exp, mouse_list in d.items():
        df_dict = {
            mouse: df.loc[lambda x: x[mouse_col] == mouse] for mouse in mouse_list
        }
        out[exp] = df_dict
        del df_dict
    return out
