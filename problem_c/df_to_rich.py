from __future__ import annotations
from operator import index

import pandas as pd
from rich.table import Table
from typing import Optional


def dataframe_to_rich_table(
    df: pd.DataFrame,
    limit: Optional[int] = None,
    add_index: bool = True,
    float_rounding: int = 4,
):
    # If limit not given then just print all rows
    if not limit:
        limit = len(df.index)

    # We need to work with the indexes given, which might be greater
    # than one
    if df.index.names:
        index_names = list(df.index.names)
    else:
        index_names = [df.index.name]

    table = Table()
    if add_index:
        for name in index_names:
            table.add_column(name)

    for column_name in df.columns:
        table.add_column(column_name.capitalize())

    count = 0
    for idx, row in df.iterrows():
        if count > limit:
            break
        str_row = []
        if add_index:
            if len(index_names) > 1:
                str_row.extend(idx)
            else:
                str_row.append(idx)
        for val in row:
            if isinstance(val, str):
                str_row.append(val)
            elif isinstance(val, float):
                str_row.append(str(round(val, float_rounding)))
            elif isinstance(val, int):
                str_row.append(str(val))
            else:
                raise TypeError(f"No unstructuring strategy for {val}")
        table.add_row(*str_row)
        count += 1

    return table
