"""Monthly liquidity series from the NRB "Database on Nepalese Economy" (decision D046).

Source workbooks (saved unchanged by src.ingestion.nrb_live under data/raw/nepal/nrb_database/):

* Monetary_Operation_DDD.xlsx, sheet Summary_OMO: amount of every NRB monetary operation by
  mid month, August 2004 onwards; sheet FX Intervention Buy and Sale: NRB purchase and sale of
  foreign exchange; sheet Interbank Transaction: interbank volume and weighted average rate.
* Liquidity_and_interbank_rate_DDD.xlsx, sheet Liquidity Series: daily balance of banks at the
  NRB minus the cash reserve requirement (excess reserves), August 2016 onwards.

Operations are signed by their effect on bank reserves, following NRB usage: repo, outright
purchase, the standing liquidity facility (SLF) and the overnight liquidity facility (OLF) inject
liquidity; reverse repo, outright sale, deposit auctions, the standing deposit facility (SDF),
the corridor deposit auction and NRB bonds absorb it.

Two corrections make the totals match the CME tables (checked month by month):
* in 46 months the 14 day repo columns repeat the 7 day amount and rate exactly; such a copy is
  counted once;
* the column labelled corridor repo is left out of the injection total and kept as its own
  series (irc_repo), because the CME totals exclude it and its rate sits at the corridor floor
  (3 percent in 2021), so it is not clearly a liquidity injection at the ceiling.
After both, injection matches the CME series in 98 percent of the 237 common months and
absorption in 98 percent; FX purchase net of sale matches in more than 99 percent.

These are latest vintage series: unlike the CME tables they carry no record of what was
published when, which is the same limitation stated for the India data (D021). Values are in
million rupees; the month is the mid month label of the workbook (2016-08 is mid August 2016).

Output: data/interim/nepal/nrb_database_monthly.csv
Usage: python -m src.ingestion.nrb_database
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "nepal" / "nrb_database" / "financial_sector"
OUT = ROOT / "data" / "interim" / "nepal" / "nrb_database_monthly.csv"
INJECT = ("Repo Auction", "Outright Purchase Auction", "SLF", "Overnight Liquidity Facility (OLF)")
IRC_REPO = ("Interest Rate Corridor (IRC)", "Repo")
ABSORB = ("Reverse Repo (Regular)", "Outright Sale Auction", "Deposit Auction (Regular)", "SDF", "NRB Bond",
          ("Interest Rate Corridor (IRC)", "Deposit Auction"))


def _book(stem: str) -> Path:
    return sorted(RAW.glob(f"*{stem}*.xlsx"))[-1]


def _monthly(frame: pd.DataFrame, first_row: int) -> pd.DataFrame:
    """Rows from first_row with a date in column 0, indexed by monthly period."""
    body = frame.iloc[first_row:].copy()
    dates = pd.to_datetime(body.iloc[:, 0], errors="coerce")
    body = body[dates.notna()]
    body.index = dates[dates.notna()].dt.to_period("M")
    body = body.iloc[:, 1:].apply(pd.to_numeric, errors="coerce")
    # a month repeated with identical values (mid May 2025 in the FX sheet) is kept once
    body.index.name = "period"
    body = body[~body.reset_index().duplicated().to_numpy()]
    if body.index.duplicated().any():
        raise ValueError(f"conflicting rows for {sorted(set(body.index[body.index.duplicated()].astype(str)))}")
    return body


def _matches(top: str, mid: str, rule) -> bool:
    return (top, mid) == rule if isinstance(rule, tuple) else rule in (top, mid)


def operations() -> pd.DataFrame:
    raw = pd.read_excel(_book("Monetary_Operation_DDD"), "Summary_OMO", header=None)
    top, mid, low = ((raw.iloc[i].ffill() if i < 2 else raw.iloc[i]).map(str) for i in range(3))
    values = _monthly(raw, 3)
    inject, absorb, irc = [], [], []
    for col in values.columns:
        # amount columns only; the unlabelled 12 day pair is amount then rate
        is_amount = low[col].startswith("Amount") or (low[col] == "nan" and low.get(col - 1, "") != "nan")
        if not is_amount:
            continue
        if _matches(top[col], mid[col], IRC_REPO):
            irc.append(col)
        elif any(_matches(top[col], mid[col], r) for r in INJECT):
            inject.append(col)
        elif any(_matches(top[col], mid[col], r) for r in ABSORB):
            absorb.append(col)
    r7, r14 = (next(c for c in inject if mid[c].startswith(d) and top[c] == "Repo Auction") for d in ("7 Days", "14 Days"))
    copy = values[r7].gt(0) & values[r7].eq(values[r14]) & values[r7 + 1].eq(values[r14 + 1])
    values.loc[copy, r14] = 0
    out = pd.DataFrame({"omo_injection": values[inject].fillna(0).sum(axis=1),
                        "omo_absorption": values[absorb].fillna(0).sum(axis=1),
                        "irc_repo": values[irc].fillna(0).sum(axis=1)})
    fx = _monthly(pd.read_excel(_book("Monetary_Operation_DDD"), "FX Intervention Buy and Sale", header=None), 3)
    out["fx_purchase"], out["fx_sale"] = fx.iloc[:, 0], fx.iloc[:, 1]
    ib = _monthly(pd.read_excel(_book("Monetary_Operation_DDD"), "Interbank Transaction", header=None), 3)
    out = out.join(ib.set_axis(["ib_volume_cb", "ib_rate_cb", "ib_volume_all", "ib_rate_all"], axis=1), how="outer")
    return out


def excess_reserves() -> pd.Series:
    raw = pd.read_excel(_book("Liquidity_and_interbank_rate_DDD"), 0, header=None)
    dates = pd.to_datetime(raw.iloc[3:, 1], errors="coerce")
    values = pd.to_numeric(raw.iloc[3:, 2], errors="coerce")
    daily = pd.Series(values.to_numpy(), index=dates).dropna()
    daily = daily[daily.index.notna()]
    return daily.groupby(daily.index.to_period("M")).mean().rename("excess_reserves_avg")


def main() -> int:
    out = operations().join(excess_reserves(), how="outer").sort_index()
    out.index.name = "period"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.round(3).to_csv(OUT)
    print(f"{len(out)} months, {out.index.min()} to {out.index.max()}")
    print(out.notna().sum().to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
