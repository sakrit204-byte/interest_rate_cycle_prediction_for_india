"""Local projections of Nepali rates, inflation and credit on RBI repo rate changes (D032).

For horizon h = 0..24:
  y(t+h) - y(t-1) = a_h + b_h shock(t) + sum_{j=1..6} [c_j shock(t-j) + d_j dy(t-j)]
                    + controls(t) + month dummies + e
where shock(t) is the monthly change in the RBI repo rate. b_h is the cumulative response of
the Nepali variable, in percentage points, h months after a one point (100 bp) RBI move.
Newey West errors with h + 1 lags. Only months with t + h no later than the training cutoff
enter, so the blind window is never used.

State dependence (H4): for the interbank rate the shock is interacted with an excess
liquidity indicator (excess reserves above their training median, known with a two month lag).

Outputs: reports/tables/local_projections.csv, local_projections_state.csv
Usage: python -m src.econometrics.local_projections
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import yaml

from src.features.build_india_features import BIS_IN, BIS_US, CPI_FOCUS_START, daily_rate, fred_daily
from src.features.build_nepal_features import MFS, imf_series, liquidity_panel

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "reports" / "tables"
CONFIG = ROOT / "configs" / "blind_test.yaml"
HORIZONS = range(0, 25)
LAGS = 6
OUTCOMES = ["interbank_rate", "tbill_91d", "nepal_cpi_yoy", "private_credit_growth"]


def monthly_panel() -> pd.DataFrame:
    month_end = lambda s: s.resample("ME").last().to_period("M")
    p = pd.DataFrame({"repo": month_end(daily_rate(BIS_IN)), "us_rate": month_end(daily_rate(BIS_US))})
    p["shock"] = p["repo"].diff()
    p["us_change"] = p["us_rate"].diff()
    brent = np.log(fred_daily("data/raw/international/fred/DCOILBRENTEU_*.csv").resample("ME").mean())
    p["brent_change"] = (brent.diff() * 100).to_period("M")
    macro = pd.read_csv(ROOT / "data" / "interim" / "india" / "india_macro_monthly.csv", index_col="month")
    macro.index = pd.PeriodIndex(macro.index, freq="M")
    focus = CPI_FOCUS_START.to_period("M")
    p["india_infl"] = macro["wpi_yoy"].where(macro.index < focus, macro["cpi_yoy"])
    p["india_infl_change_3m"] = p["india_infl"] - p["india_infl"].shift(3)
    ib = pd.read_csv(ROOT / "data" / "interim" / "nepal" / "nepal_interbank_monthly.csv", index_col="month")
    p["interbank_rate"] = pd.Series(ib["interbank_rate"].values, index=pd.PeriodIndex(ib.index, freq="M"))
    p["tbill_91d"] = imf_series("MFS_IR_npl_interest_rates", lambda d: d["INDICATOR"] == "GSTBILY_RT_PT_A_PT")
    p["nepal_cpi_yoy"] = imf_series("CPI_npl_cpi", lambda d: (d["COICOP_1999"] == "_T") &
                                    (d["TYPE_OF_TRANSFORMATION"] == "SRP_YOY_PCH_PA_PT"))
    flow, code = MFS["private_credit"]
    credit = imf_series(f"{flow}_npl", lambda d: (d["INDICATOR"] == code) & (d["TYPE_OF_TRANSFORMATION"] == "XDC"))
    p["private_credit_growth"] = (credit / credit.shift(12) - 1) * 100
    p["excess_reserves"] = liquidity_panel()["reserves_to_deposits"].shift(2)  # public two months later
    return p.sort_index()


def design(p: pd.DataFrame, outcome: str, h: int, state: pd.Series | None = None) -> tuple[pd.Series, pd.DataFrame]:
    y = p[outcome].shift(-h) - p[outcome].shift(1)
    dy = p[outcome].diff()
    x = {"shock": p["shock"]}
    if state is not None:
        x = {"shock_high_liquidity": p["shock"] * state, "shock_low_liquidity": p["shock"] * (1 - state),
             "high_liquidity": state}
    for j in range(1, LAGS + 1):
        x[f"shock_l{j}"] = p["shock"].shift(j)
        x[f"dy_l{j}"] = dy.shift(j)
    for j in range(4):
        x[f"brent_l{j}"] = p["brent_change"].shift(j)
    x["us_change"] = p["us_change"]
    x["india_infl_l1"] = p["india_infl"].shift(1)
    x["india_infl_change_3m_l1"] = p["india_infl_change_3m"].shift(1)
    X = pd.DataFrame(x)
    X = X.join(pd.get_dummies(pd.Series(p.index.month, index=p.index), prefix="m", drop_first=True, dtype=float))
    return y, sm.add_constant(X)


def estimate(p: pd.DataFrame, cutoff: pd.Period, outcome: str, h: int, terms: list[str],
             state: pd.Series | None = None) -> list[dict]:
    y, X = design(p, outcome, h, state)
    ok = y.notna() & X.notna().all(axis=1) & (y.index + h <= cutoff)
    res = sm.OLS(y[ok], X[ok]).fit(cov_type="HAC", cov_kwds={"maxlags": h + 1})
    return [{"outcome": outcome, "horizon": h, "term": t, "coef": res.params[t], "se": res.bse[t],
             "p_value": res.pvalues[t], "ci_low": res.params[t] - 1.96 * res.bse[t],
             "ci_high": res.params[t] + 1.96 * res.bse[t], "n": int(ok.sum()),
             "first_month": str(y[ok].index[0]), "last_month": str(y[ok].index[-1])} for t in terms]


def main() -> int:
    cutoff = pd.Period(yaml.safe_load(CONFIG.read_text())["training_information_cutoff"][:7], freq="M")
    p = monthly_panel()
    rows = [r for o in OUTCOMES for h in HORIZONS for r in estimate(p, cutoff, o, h, ["shock"])]
    lp = pd.DataFrame(rows)
    train = p.loc[:cutoff, "excess_reserves"].dropna()
    state = (p["excess_reserves"] > train.median()).astype(float).where(p["excess_reserves"].notna())
    terms = ["shock_high_liquidity", "shock_low_liquidity"]
    st = pd.DataFrame([r for h in HORIZONS for r in estimate(p, cutoff, "interbank_rate", h, terms, state)])
    TABLES.mkdir(parents=True, exist_ok=True)
    lp.round(4).to_csv(TABLES / "local_projections.csv", index=False)
    st.round(4).to_csv(TABLES / "local_projections_state.csv", index=False)
    show = lp[lp["horizon"].isin([0, 3, 6, 12, 18, 24])]
    print(show[["outcome", "horizon", "coef", "se", "p_value", "n", "first_month", "last_month"]].round(3).to_string(index=False))
    print(st[st["horizon"].isin([0, 3, 6, 12, 18, 24])][["horizon", "term", "coef", "se", "p_value", "n"]].round(3).to_string(index=False))
    print("RBI moves in sample:", int((p.loc[:cutoff, "shock"].fillna(0) != 0).sum()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
