"""Monthly Nepal feature table, built point in time (no look ahead).

The forecast origin for target month t is the 15th of month t. Information lags are
conservative (D028): Nepal monthly values (interbank rate, CPI) from month t - 2, NRB
corridor rates from month t - 1 (announced at decisions, recorded monthly by the IMF), the
India repo rate on the origin date, and India inflation as available by the origin.

Features (six, for 318 training months):
  ib_adj_level        seasonally adjusted interbank rate, t - 2
  ib_adj_change_3m    its change from t - 5 to t - 2
  india_repo_level    RBI repo rate at the origin
  india_repo_change_3m  RBI repo change over the 91 days to the origin (transmission channel)
  nepal_cpi_yoy       Nepal CPI inflation, t - 2 (IMF, spliced series)
  nrb_bank_rate_change_6m  change in the NRB bank rate (corridor ceiling), t - 7 to t - 1

Output: data/processed/nepal/nepal_features_monthly.csv
Usage: python -m src.features.build_nepal_features
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from src.features.build_india_features import daily_rate, rate_on, BIS_IN

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "data" / "interim" / "nepal" / "nepal_target_monthly.csv"
IMF = ROOT / "data" / "raw" / "international" / "imf"
OUT = ROOT / "data" / "processed" / "nepal" / "nepal_features_monthly.csv"
NEPAL_LAG = 2
CORRIDOR_LAG = 1

FEATURES = ["ib_adj_level", "ib_adj_change_3m", "india_repo_level", "india_repo_change_3m",
            "nepal_cpi_yoy", "nrb_bank_rate_change_6m"]
# second Nepal model (D030): liquidity channel under the peg, IMF MFS lagged two months
LIQUIDITY_FEATURES = ["reserves_to_deposits", "nfa_cb_growth_3m", "gov_deposit_change_3m", "credit_minus_deposit_growth"]
LIQUIDITY_MODEL_FEATURES = ["ib_adj_level", "ib_adj_change_3m", "nrb_bank_rate_change_6m",
                            "india_repo_change_3m"] + LIQUIDITY_FEATURES
MFS = {  # name: (dataflow, indicator)
    "claims_on_cb": ("MFS_ODC", "ODCORP_A_ACO_S121_ODCS"),
    "transferable_deposits": ("MFS_ODC", "ODCORP_L_F22_IBM_ODCS"),
    "other_deposits": ("MFS_ODC", "ODCORP_L_F29_IBM_ODCS"),
    "private_credit": ("MFS_ODC", "ODCORP_A_ACO_PS_ODCS"),
    "cb_nfa": ("MFS_CBS", "S121_N_NFRA_CBS"),
    "gov_deposits_cb": ("MFS_CBS", "S121_L_LT_S1311MIXED_CBS"),
    "broad_money": ("MFS_DC", "DCORP_L_BM"),
}


def liquidity_panel() -> pd.DataFrame:
    """Monthly liquidity indicators by reference month (values public two months later)."""
    raw = {}
    for name, (flow, code) in MFS.items():
        raw[name] = imf_series(f"{flow}_npl", lambda d, c=code: (d["INDICATOR"] == c) &
                               (d["TYPE_OF_TRANSFORMATION"] == "XDC"))
    m = pd.DataFrame(raw)
    deposits = m["transferable_deposits"] + m["other_deposits"]
    out = pd.DataFrame(index=m.index)
    out["reserves_to_deposits"] = m["claims_on_cb"] / deposits * 100
    out["nfa_cb_growth_3m"] = (m["cb_nfa"] / m["cb_nfa"].shift(3) - 1) * 100
    out["gov_deposit_change_3m"] = (m["gov_deposits_cb"] - m["gov_deposits_cb"].shift(3)) / m["broad_money"] * 100
    out["credit_minus_deposit_growth"] = ((m["private_credit"] / m["private_credit"].shift(12) - 1)
                                          - (deposits / deposits.shift(12) - 1)) * 100
    return out


def imf_series(prefix: str, mask) -> pd.Series:
    df = pd.read_csv(sorted(IMF.glob(f"{prefix}_*.csv"))[-1])
    df = df[mask(df)].dropna(subset=["OBS_VALUE"])
    return pd.Series(df["OBS_VALUE"].astype(float).values,
                     index=pd.PeriodIndex(df["TIME_PERIOD"].str.replace("-M", "-"), freq="M")).sort_index()


def build() -> pd.DataFrame:
    t = pd.read_csv(TARGET, index_col=0)
    t.index = pd.PeriodIndex(t.index, freq="M")
    cpi = imf_series("CPI_npl_cpi", lambda d: (d["COICOP_1999"] == "_T") &
                     (d["TYPE_OF_TRANSFORMATION"] == "SRP_YOY_PCH_PA_PT"))
    bank_rate = imf_series("MFS_IR_npl_interest_rates", lambda d: d["INDICATOR"] == "MFS166_RT_PT_A_PT")
    repo = daily_rate(BIS_IN)
    liq = liquidity_panel()
    adj = t["interbank_adj"]
    rows = []
    for month in t.index:
        origin = month.start_time + pd.Timedelta(days=14)
        info = month - NEPAL_LAG
        corridor = month - CORRIDOR_LAG
        rows.append({
            "month": str(month), "origin": origin.date(), "nepal_info_month": str(info),
            "y": t.at[month, "y"], "change_3m_adj": t.at[month, "change_3m_adj"],
            "blind_window": bool(t.at[month, "blind_window"]),
            "label_known_month": t.at[month, "label_known_month"],
            "ib_adj_level": adj.get(info, np.nan),
            "ib_adj_change_3m": adj.get(info, np.nan) - adj.get(info - 3, np.nan),
            "india_repo_level": rate_on(repo, origin),
            "india_repo_change_3m": rate_on(repo, origin) - rate_on(repo, origin - pd.Timedelta(days=91)),
            "nepal_cpi_yoy": cpi.get(info, np.nan),
            "nrb_bank_rate_change_6m": bank_rate.get(corridor, np.nan) - bank_rate.get(corridor - 6, np.nan),
            **{f: (liq.at[info, f] if info in liq.index else np.nan) for f in LIQUIDITY_FEATURES},
        })
    out = pd.DataFrame(rows)
    out["complete"] = out[FEATURES].notna().all(axis=1) & out["y"].notna()
    out["complete_liquidity"] = out[LIQUIDITY_MODEL_FEATURES].notna().all(axis=1) & out["y"].notna()
    return out


def main() -> int:
    out = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    train = out[~out["blind_window"] & out["complete"]]
    print(f"{len(out)} months; complete {int(out['complete'].sum())}; training complete {len(train)} "
          f"({train['month'].iloc[0]} to {train['month'].iloc[-1]})")
    print("missing:", out[FEATURES].isna().sum()[lambda s: s > 0].to_dict())
    tl = out[~out["blind_window"] & out["complete_liquidity"]]
    print(f"liquidity model training months {len(tl)} ({tl['month'].iloc[0]} to {tl['month'].iloc[-1]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
