"""Build the India policy decision table: one row per RBI monetary policy announcement.

Inputs:
  data/interim/india/rbi_policy_index_entries.csv  (dated announcements, from the RBI index)
  data/raw/international/bis_cbpol/WS_CBPOL_D_IN_*.csv  (daily repo rate, from BIS)
Output:
  data/interim/india/rbi_decisions.csv

Each announcement gets the repo rate change between the day before it and two days after
it. Repo rate changes in the BIS series that match no announcement are added as inter
meeting moves, flagged so they can be kept or dropped in robustness runs.

Usage: python -m src.features.targets_india
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ENTRIES = ROOT / "data" / "interim" / "india" / "rbi_policy_index_entries.csv"
BIS_GLOB = "data/raw/international/bis_cbpol/WS_CBPOL_D_IN_*.csv"
OUT = ROOT / "data" / "interim" / "india" / "rbi_decisions.csv"

POLICY_TITLE = re.compile(
    r"policy statement|review of .*policy|monetary policy review|bi.?monthly .*policy|statement on monetary policy"
    r"|monetary policy statement|annual policy|mid.?term review",
    re.IGNORECASE,
)
NOT_DECISION = re.compile(
    r"macroeconomic and monetary developments|minutes|technical advisory|schedule|rescheduling|transcript",
    re.IGNORECASE,
)
DECISION_DOC = re.compile(
    r"resolution|statement by|governor's statement|press release|full statement|full document|policy statement",
    re.IGNORECASE,
)
FIT_START =pd.Timestamp("2015-02-20")  # Monetary Policy Framework Agreement
MPC_START = pd.Timestamp("2016-10-04")  # first MPC decision
MERGE_DAYS = 5
MATCH_WINDOW_DAYS = 3


def load_repo_rate() -> pd.Series:
    path = sorted(ROOT.glob(BIS_GLOB))[-1]
    d = pd.read_csv(path, usecols=["TIME_PERIOD", "OBS_VALUE"]).dropna()
    s = pd.Series(d.OBS_VALUE.astype(float).values, index=pd.to_datetime(d.TIME_PERIOD)).sort_index()
    return s["2001-04-03":]


def announcements(entries: pd.DataFrame) -> pd.DataFrame:
    """Policy announcements, with entries for the same event within MERGE_DAYS merged to the earliest."""
    e = entries.copy()
    e["date"] = pd.to_datetime(e["date"])
    body = e["body"].fillna("")
    is_policy = e["title"].str.contains(POLICY_TITLE, na=False)
    # Post meeting transcripts reuse the meeting title; they carry no decision document.
    transcript_only = body.str.match(r"\s*Edited Transcript", case=False) & ~body.str.contains(DECISION_DOC, na=False)
    keep = is_policy & ~e["title"].str.contains(NOT_DECISION, na=False) & ~transcript_only
    a = e[keep].sort_values("date")
    rows, last = [], None
    for _, r in a.iterrows():
        if last is not None and (r.date - last).days <= MERGE_DAYS:
            continue
        rows.append(r)
        last = r.date
    out = pd.DataFrame(rows)[["date", "title", "body", "fiscal_year_end"]].reset_index(drop=True)
    out["source"] = "rbi_policy_index"
    return out


def rate_change(rate: pd.Series, date: pd.Timestamp) -> tuple[float, float, float]:
    before = rate[: date - pd.Timedelta(days=1)]
    after = rate[: date + pd.Timedelta(days=MATCH_WINDOW_DAYS - 1)]
    if before.empty or after.empty:
        return float("nan"), float("nan"), float("nan")
    return before.iloc[-1], after.iloc[-1], round((after.iloc[-1] - before.iloc[-1]) * 100)


def build(entries: pd.DataFrame, rate: pd.Series) -> pd.DataFrame:
    a = announcements(entries)
    a = a[a.date >= rate.index.min() + pd.Timedelta(days=1)].copy()
    vals = [rate_change(rate, d) for d in a.date]
    a["repo_before"], a["repo_after"], a["change_bp"] = zip(*vals)

    changes = rate.diff()
    change_dates = changes[changes.abs() > 1e-9].index
    matched = set()
    for d in a.date:
        window = change_dates[(change_dates >= d) & (change_dates <= d + pd.Timedelta(days=MATCH_WINDOW_DAYS - 1))]
        matched.update(window)
    extra = [d for d in change_dates if d not in matched]
    inter = pd.DataFrame({
        "date": extra,
        "title": "Repo rate change with no policy announcement in the RBI index (inter meeting move)",
        "body": "",
        "fiscal_year_end": [d.year + (1 if d.month >= 4 else 0) for d in extra],
        "source": "bis_rate_change",
    })
    if not inter.empty:
        vals = [(rate[: d - pd.Timedelta(days=1)].iloc[-1], rate[d], round((rate[d] - rate[: d - pd.Timedelta(days=1)].iloc[-1]) * 100)) for d in extra]
        inter["repo_before"], inter["repo_after"], inter["change_bp"] = zip(*vals)

    out = pd.concat([a, inter], ignore_index=True).sort_values("date").reset_index(drop=True)
    out["decision"] = pd.cut(out.change_bp, [-1e9, -0.5, 0.5, 1e9], labels=["cut", "hold", "hike"])
    out["inter_meeting"] = out.source == "bis_rate_change"
    out["regime"] = pd.cut(out.date, [pd.Timestamp("2000-01-01"), FIT_START, MPC_START, pd.Timestamp("2100-01-01")],
                           labels=["multiple_indicator", "fit_pre_mpc", "mpc"], right=False)
    out["blind_window"] = out.date >= pd.Timestamp("2021-11-01")
    out["date"] = out.date.dt.date
    return out


def main() -> int:
    out = build(pd.read_csv(ENTRIES), load_repo_rate())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    print(f"{len(out)} decisions written to {OUT.relative_to(ROOT)}")
    print(pd.crosstab([out.blind_window, out.regime], out.decision, margins=True).to_string())
    print("inter meeting moves:", int(out.inter_meeting.sum()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
