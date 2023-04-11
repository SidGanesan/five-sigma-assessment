import pytest
import pandas as pd

from problem_c.main import group_by_categories


def test_group_by__single_category() -> None:
    df_dict = [
        {"cat_1": "test", "val": 10},
        {"cat_1": "test", "val": 10},
        {"cat_1": "test", "val": 10},
    ]
    df = pd.DataFrame(df_dict)

    groups = group_by_categories(df, ["cat_1"], dict(orient="index"))

    assert groups["test"]["val"] == sum([d["val"] for d in df_dict])  # type: ignore


def test_group_by__two_category() -> None:
    df_dict = [
        {"cat_1": "foo", "cat_2": "bar", "val": 10},
        {"cat_1": "foo", "cat_2": "bar", "val": 10},
        {"cat_1": "foo", "cat_2": "bar", "val": 10},
        {"cat_1": "foo", "cat_2": "baz", "val": 20},
        {"cat_1": "foo", "cat_2": "baz", "val": 20},
        {"cat_1": "foo", "cat_2": "baz", "val": 20},
    ]
    df = pd.DataFrame(df_dict)

    groups = group_by_categories(df, ["cat_1", "cat_2"], dict(orient="index"))

    assert groups[("foo", "bar")]["val"] == sum([d["val"] for d in df_dict if d["cat_2"] == "bar"])  # type: ignore
    assert groups[("foo", "baz")]["val"] == sum([d["val"] for d in df_dict if d["cat_2"] == "baz"])  # type: ignore
