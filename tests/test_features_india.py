"""Leakage tests for the point in time India feature builder."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.features import build_india_features as bf
from src.features.india_macro import available_from

ROOT = Path(__file__).resolve().parents[1]
BUILT = ROOT / "data" / "processed" / "india" / "india_features_cutoff7.csv"


def synthetic_macro(spike_after: pd.Timestamp | None = None) -> pd.DataFrame:
    months = pd.period_range("2015-01", "2016-12", freq="M")
    macro = pd.DataFrame({"cpi_yoy": np.linspace(5, 6, len(months)),
                          "wpi_yoy": np.linspace(2, 3, len(months)),
                          "iip_yoy": np.linspace(1, 4, len(months))}, index=months)
    for s in ("cpi", "wpi", "iip"):
        macro[f"{s}_available_from"] = available_from(months, s)
    if spike_after is not None:
        for col, s in (("cpi_yoy", "cpi"), ("wpi_yoy", "wpi"), ("iip_yoy", "iip")):
            macro.loc[macro[f"{s}_available_from"] > spike_after, col] = 999.0
    return macro


def flat_rate() -> pd.Series:
    return pd.Series(6.0, index=pd.date_range("2014-01-01", "2016-12-31"))


def test_future_values_do_not_change_features():
    day = pd.Timestamp("2016-04-05")
    cutoff = day - pd.Timedelta(days=7)
    past = pd.DataFrame({"date": [pd.Timestamp("2016-02-02")], "decision": ["hold"]})
    clean = bf.row_features(day, synthetic_macro(), flat_rate(), flat_rate(), past, 7)
    spiked = bf.row_features(day, synthetic_macro(spike_after=cutoff), flat_rate(), flat_rate(), past, 7)
    assert clean == spiked


def test_decision_after_cutoff_is_not_known():
    day = pd.Timestamp("2016-04-05")
    past = pd.DataFrame({"date": [pd.Timestamp("2016-02-02"), pd.Timestamp("2016-04-01")],
                         "decision": ["cut", "hike"]})
    row = bf.row_features(day, synthetic_macro(), flat_rate(), flat_rate(), past, 7)
    assert row["prev_decision"] == -1  # the 1 April move is after the 29 March cutoff


def test_release_rules():
    cpi = available_from(pd.PeriodIndex(["2013-11", "2016-08"], freq="M"), "cpi")
    assert list(cpi.dt.strftime("%Y-%m-%d")) == ["2013-12-31", "2016-09-15"]
    iip = available_from(pd.PeriodIndex(["2016-07"], freq="M"), "iip")
    assert iip.iloc[0] == pd.Timestamp("2016-09-15")


@pytest.mark.skipif(not BUILT.exists(), reason="feature table not built")
def test_built_table_respects_cutoffs():
    f = pd.read_csv(BUILT, parse_dates=["date", "cutoff"])
    assert ((f["date"] - f["cutoff"]).dt.days == bf.CUTOFF_DAYS).all()
    for col, series in (("infl_month", None), ("iip_month", "iip")):
        rows = f[f[col].notna()]
        months = pd.PeriodIndex(rows[col], freq="M")
        names = series or rows["infl_measure"].str.replace("_yoy", "")
        for month, name, cutoff in zip(months, names if series is None else [series] * len(rows), rows["cutoff"]):
            assert available_from(pd.PeriodIndex([month]), name).iloc[0] <= cutoff
