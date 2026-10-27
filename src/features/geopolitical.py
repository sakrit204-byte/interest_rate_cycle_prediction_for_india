"""Monthly geopolitical and global risk features (decision D042).

  gpr_global     log of the Caldara and Iacoviello Geopolitical Risk Index (GPR)
  gpr_india      log of its India country index (GPRC_IND, share of articles)
  vix            monthly average of the daily VIX close
  oil_change_3m  three month change in the log of the monthly average Brent price, in percent

Values are indexed by reference month; callers apply the one month publication lag.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "international"
FEATURES = ["gpr_global", "gpr_india", "vix", "oil_change_3m"]


def _latest(pattern: str) -> Path:
    return sorted(RAW.glob(pattern))[-1]


def _daily_monthly(path: Path) -> pd.Series:
    d = pd.read_csv(path)
    s = pd.to_numeric(d.iloc[:, 1], errors="coerce")
    s.index = pd.to_datetime(d.iloc[:, 0])
    return s.dropna().groupby(s.dropna().index.to_period("M")).mean()


def monthly() -> pd.DataFrame:
    g = pd.read_excel(_latest("gpr/gpr_*.xls"))
    g.index = pd.to_datetime(g["month"]).dt.to_period("M")
    brent = _daily_monthly(_latest("fred/DCOILBRENTEU_*.csv"))
    out = pd.DataFrame({"gpr_global": np.log(g["GPR"]), "gpr_india": np.log(g["GPRC_IND"])})
    out = out.join(_daily_monthly(_latest("fred/VIXCLS_*.csv")).rename("vix"), how="outer")
    out = out.join((np.log(brent) - np.log(brent.shift(3))).mul(100).rename("oil_change_3m"), how="outer")
    return out


def at(periods, lag: int = 1) -> pd.DataFrame:
    """Features for each information period, lagged by `lag` months."""
    m = monthly()
    rows = [m.loc[p - lag].to_dict() if (p - lag) in m.index else dict.fromkeys(FEATURES, np.nan) for p in periods]
    return pd.DataFrame(rows, columns=FEATURES)
