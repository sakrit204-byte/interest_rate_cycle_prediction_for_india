"""Decision level India feature table, built point in time (no look ahead).

For each RBI decision the information cutoff is the decision date minus CUTOFF_DAYS
(D004). Every feature uses only data public on or before the cutoff: monthly values whose
available_from date is on or before it (src.features.india_macro), the BIS repo rate on
or before it, and decisions dated on or before it. The reference month behind each monthly
value is stored in an audit column so tests/test_features_india.py can check every row.

Realized inflation only in this version (the first training run, as agreed); RBI
projections are added later as a separate model.

Usage: python -m src.features.build_india_features [cutoff_days]
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DECISIONS = ROOT / "data" / "interim" / "india" / "rbi_decisions.csv"
MACRO = ROOT / "data" / "interim" / "india" / "india_macro_monthly.csv"
BIS_IN = "data/raw/international/bis_cbpol/WS_CBPOL_D_IN_*.csv"
BIS_US = "data/raw/international/bis_cbpol/WS_CBPOL_D_US_*.csv"
OUT_DIR = ROOT / "data" / "processed" / "india"

CUTOFF_DAYS = 7
# The RBI moved its inflation focus from WPI to CPI combined with the Expert Committee
# (Patel) report of January 2014 (date to verify); before that the headline measure in
# policy statements was WPI. Robustness: switch at the FIT start, 20 February 2015.
CPI_FOCUS_START = pd.Timestamp("2014-01-21")
CLASS_CODE = {"cut": -1, "hold": 0, "hike": 1}

PROJECTIONS = ROOT / "data" / "interim" / "india" / "rbi_projections.csv"

FEATURES = ["infl", "infl_change_3m", "iip_yoy_3m", "repo_level", "real_rate",
            "repo_change_6m", "us_rate_change_6m", "prev_decision", "fit_regime", "mpc_regime"]
# second model (D025): RBI published projections, known at the cutoff only if published by then
PROJECTION_FEATURES = ["proj_infl", "proj_revision"]


def daily_rate(pattern: str) -> pd.Series:
    path = sorted(ROOT.glob(pattern))[-1]
    d = pd.read_csv(path, usecols=["TIME_PERIOD", "OBS_VALUE"]).dropna()
    return pd.Series(d.OBS_VALUE.astype(float).values, index=pd.to_datetime(d.TIME_PERIOD)).sort_index()


def rate_on(rate: pd.Series, day: pd.Timestamp) -> float:
    s = rate.loc[:day]
    return float(s.iloc[-1]) if len(s) else np.nan


def available(macro: pd.DataFrame, value: str, series: str, cutoff: pd.Timestamp) -> pd.Series:
    """Values of one monthly column public by the cutoff, indexed by reference month."""
    ok = macro[f"{series}_available_from"] <= cutoff
    return macro.loc[ok, value].dropna()


def projection_features(proj: pd.DataFrame, cutoff: pd.Timestamp) -> dict:
    """Latest coded projection published on or before the cutoff, and its revision.

    The revision compares projections for the same measure and horizon only; when the
    horizon rolls forward (for example from March 2010 to March 2011) it is set to zero.
    """
    known = proj[(proj["date"] <= cutoff) & proj["proj_infl"].notna()]
    if known.empty:
        return {"proj_infl": np.nan, "proj_revision": np.nan, "proj_date": ""}
    last = known.iloc[-1]
    revision = 0.0
    prev = known.iloc[-2] if len(known) > 1 else None
    if prev is not None and prev["measure"] == last["measure"] and prev["horizon"] == last["horizon"]:
        revision = last["proj_infl"] - known.iloc[-2]["proj_infl"]
    return {"proj_infl": last["proj_infl"], "proj_revision": revision, "proj_date": last["date"].date(),
            "proj_measure": last["measure"]}


def row_features(day: pd.Timestamp, macro: pd.DataFrame, repo: pd.Series, us: pd.Series,
                 past: pd.DataFrame, cutoff_days: int, proj: pd.DataFrame | None = None) -> dict:
    cutoff = day - pd.Timedelta(days=cutoff_days)
    measure, series = ("cpi_yoy", "cpi") if day >= CPI_FOCUS_START else ("wpi_yoy", "wpi")
    infl = available(macro, measure, series, cutoff)
    iip = available(macro, "iip_yoy", "iip", cutoff)
    known = past[past["date"] <= cutoff]
    row = {
        "cutoff": cutoff.date(),
        "infl_measure": measure,
        "infl_month": str(infl.index[-1]) if len(infl) else "",
        "iip_month": str(iip.index[-1]) if len(iip) else "",
        "infl": infl.iloc[-1] if len(infl) else np.nan,
        # change over three reference months on the same measure
        "infl_change_3m": infl.iloc[-1] - infl.get(infl.index[-1] - 3, np.nan) if len(infl) else np.nan,
        "iip_yoy_3m": iip.iloc[-3:].mean() if len(iip) >= 3 else np.nan,
        "repo_level": rate_on(repo, cutoff),
        "repo_change_6m": rate_on(repo, cutoff) - rate_on(repo, cutoff - pd.Timedelta(days=182)),
        "us_rate_change_6m": rate_on(us, cutoff) - rate_on(us, cutoff - pd.Timedelta(days=182)),
        "prev_decision": CLASS_CODE[known["decision"].iloc[-1]] if len(known) else np.nan,
    }
    row["real_rate"] = row["repo_level"] - row["infl"]
    if proj is not None:
        row.update(projection_features(proj, cutoff))
        if row.get("proj_measure") and row["proj_measure"].lower() != series:
            # projection on a different index from the targeted inflation measure (January 2014)
            row["proj_infl"] = row["proj_revision"] = np.nan
    return row


def build(cutoff_days: int = CUTOFF_DAYS) -> pd.DataFrame:
    decisions = pd.read_csv(DECISIONS, parse_dates=["date"])
    macro = pd.read_csv(MACRO)
    macro["month"] = pd.PeriodIndex(macro["month"], freq="M")
    macro = macro.set_index("month")
    for series in ("cpi", "wpi", "iip"):
        macro[f"{series}_available_from"] = pd.to_datetime(macro[f"{series}_available_from"])
    repo, us = daily_rate(BIS_IN), daily_rate(BIS_US)
    proj = pd.read_csv(PROJECTIONS, parse_dates=["decision_date"]).rename(columns={"decision_date": "date"})
    proj = proj.sort_values("date")
    rows = []
    for _, d in decisions.iterrows():
        f = row_features(d["date"], macro, repo, us, decisions[decisions["date"] < d["date"]], cutoff_days, proj)
        rows.append({"date": d["date"].date(), "decision": d["decision"], "y": CLASS_CODE[d["decision"]],
                     "change_bp": d["change_bp"], "inter_meeting": d["inter_meeting"],
                     "regime": d["regime"], "blind_window": d["blind_window"], **f})
    out = pd.DataFrame(rows)
    out["fit_regime"] = (out["regime"] != "multiple_indicator").astype(int)
    out["mpc_regime"] = (out["regime"] == "mpc").astype(int)
    out["complete"] = out[FEATURES].notna().all(axis=1)
    out["complete_projection"] = out["complete"] & out[PROJECTION_FEATURES].notna().all(axis=1)
    return out


def main() -> int:
    cutoff_days = int(sys.argv[1]) if len(sys.argv) > 1 else CUTOFF_DAYS
    out = build(cutoff_days)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"india_features_cutoff{cutoff_days}.csv"
    out.to_csv(path, index=False)
    train = out[~out["blind_window"]]
    print(f"{len(out)} decisions, {int(out['complete'].sum())} with all features; "
          f"training {len(train)} ({int(train['complete'].sum())} complete)")
    missing = out.loc[~out["complete"], FEATURES].isna().sum()
    print("missing by feature:", missing[missing > 0].to_dict())
    print(f"written {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
