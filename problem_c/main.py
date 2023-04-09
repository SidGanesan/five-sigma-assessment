from pathlib import Path
import pandas as pd

from rich.console import Console
from rich.columns import Columns
from typing import Callable, Dict, Tuple

from df_to_rich import dataframe_to_rich_table


COUNTRY_INITIALS_MAPPING = {
    "de": "Germany",
    "es": "Spain",
    "fr": "France",
    "it": "Italy",
    "nl": "Netherlands",
}


def _weighted_average_row_calc(
    totals_mappings: Dict[Tuple[str, str], Dict[str, float]]
) -> Callable[[pd.Series], float]:
    def row_calculation(row: pd.Series) -> float:
        group_total = totals_mappings[
            (row["Initial duration type"], row["October Rating"])
        ]["Remaining capital"]
        if group_total == 0:
            return 0
        return row["Annual rate"] * row["Remaining capital"] / group_total

    return row_calculation


def problem_c() -> None:
    console = Console()
    path = Path("problem_c") / "input" / "data.xlsx"
    df = pd.read_excel(path)

    # DATA CLEAN UP
    # Add country names
    df["Country"] = df["Country"].apply(lambda x: COUNTRY_INITIALS_MAPPING[x])

    # Normalise mistyped rates
    df["Annual rate"] = df["Annual rate"].apply(
        lambda x: x / 100 if x > 0.1 else x
    )

    # Normalise credit ratings and strip whitespace
    df["October Rating"] = df["October Rating"].apply(lambda x: x.strip())

    bin_mappings = {
        "initial duration": dict(
            name="Initial duration type",
            bins=[0.0, 10.0, 20.0, 30.0, 40.0, 50, 60, 70, 80, float("inf")],
            labels=[
                "<10 years",
                "10-20 years",
                "20-30 years",
                "30-40 years",
                "40-50 years",
                "50-60 years",
                "60-70 years",
                "70-80 years",
                "80+ years",
            ],
        ),
        "Annual rate": dict(
            name="Annual rate bucket",
            bins=[
                0.0,
                0.02,
                0.03,
                0.04,
                0.05,
                0.06,
                0.07,
                0.08,
                0.09,
                float("inf"),
            ],
            labels=[
                "<2%",
                "2% - 3%",
                "3% - 4%",
                "4% - 5%",
                "5% - 6%",
                "6% - 7%",
                "7% - 8%",
                "8% - 9%",
                ">9%",
            ],
        ),
    }

    # TABLE MAPPING
    stratifications = [
        "October Rating",
        "Country",
        "Status",
        "Initial duration type",
        "Annual rate bucket",
    ]

    total_remaining = df["Remaining capital"].sum()

    strat_columns = Columns(padding=1)

    # Create the bins we need for histograms
    for strat, cut_config in bin_mappings.items():
        cut = cut_config.pop("name")
        df[cut] = pd.cut(df[strat], **cut_config)

    # Basic table creatation of enum like data
    for strat in stratifications:
        strat_df = (
            df[[strat, "Remaining capital"]]
            .set_index(strat)
            .groupby([strat])
            .sum()
            / total_remaining
        )
        strat_columns.add_renderable(dataframe_to_rich_table(strat_df))

    # This loop is for all of the buckets we want to cut our data up by

    # Final grouping for multiple grouping
    capital_grouping = (
        df[
            [
                "Initial duration type",
                "October Rating",
                "Remaining capital",
            ]
        ]
        .groupby(["Initial duration type", "October Rating"])
        .sum()
    ).to_dict(orient="index")

    # Calculate the weighted average annual return for each row
    df["Weighted Avg Annual Return"] = df.apply(
        _weighted_average_row_calc(capital_grouping), axis=1
    )

    # Group by "Initial duration" and "October Rating" and calculate the
    # weighted average annual return
    grouped = (
        df[
            [
                "Initial duration type",
                "October Rating",
                "Weighted Avg Annual Return",
            ]
        ]
        .groupby(["Initial duration type", "October Rating"])
        .sum()
    )
    compare = (
        df[
            [
                "Initial duration type",
                "October Rating",
                "Annual rate",
            ]
        ]
        .groupby(["Initial duration type", "October Rating"])
        .mean()
    )

    strat_columns.add_renderable(dataframe_to_rich_table(grouped))
    strat_columns.add_renderable(dataframe_to_rich_table(compare))
    console.print(strat_columns)


if __name__ == "__main__":
    problem_c()
