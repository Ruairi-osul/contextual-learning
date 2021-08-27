def pivot(df, cell_col: str = "cell_id", value_col="value", time_col="time"):
    return df.pivot(columns=cell_col, values=value_col, index=time_col)

