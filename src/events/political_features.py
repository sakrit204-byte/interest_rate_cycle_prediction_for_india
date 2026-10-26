"""Point in time political event indicators (D034), from data/events/political_events.csv.

Every event is joined on its announcement date: an indicator at a cutoff uses only events
announced on or before that cutoff.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
EVENTS = ROOT / "data" / "events" / "political_events.csv"
DISRUPTIONS = {"royal_takeover", "unrest", "unrest_start", "natural_disaster", "government_collapse"}


def load() -> pd.DataFrame:
    e = pd.read_csv(EVENTS, parse_dates=["event_date", "announcement_date"])
    e["known"] = e["announcement_date"].fillna(e["event_date"])
    return e[e["verified"] == "yes"]


def india(dates: pd.Series, cutoffs: pd.Series, prev_dates: pd.Series) -> pd.DataFrame:
    e = load()
    e = e[e["country"] == "India"]
    sched = e[e["event_type"] == "election_schedule_announcement"]["event_date"]
    results = e[e["event_type"] == "election_results"]["event_date"].sort_values()
    budgets = e[e["event_type"].str.startswith("budget")]["event_date"]
    rows = []
    for d, c, p in zip(dates, cutoffs, prev_dates):
        announced = sched[sched <= c]
        pending = 0
        if len(announced):
            nxt = results[results >= announced.max()]
            pending = int(len(nxt) > 0 and nxt.iloc[0] > c)
        since = budgets[(budgets <= c) & (budgets > p)] if pd.notna(p) else budgets.iloc[:0]
        rows.append({"election_pending": pending, "budget_since_last": int(len(since) > 0)})
    return pd.DataFrame(rows, index=dates.index)


def nepal(origins: pd.Series) -> pd.DataFrame:
    e = load()
    e = e[e["country"] == "Nepal"]
    pm = e[e["event_type"] == "pm_swearing_in"]["known"]
    dis = e[e["event_type"].isin(DISRUPTIONS)]["known"]
    b_start = e[e["event_type"] == "unrest_start"]["event_date"]
    b_end = e[e["event_type"] == "unrest_end"]["event_date"]
    rows = []
    for o in origins:
        recent = dis[(dis <= o) & (dis > o - pd.DateOffset(months=3))]
        ongoing = any((s <= o) and not any((b_end >= s) & (b_end <= o)) for s in b_start)
        rows.append({"gov_change_6m": int(((pm <= o) & (pm > o - pd.DateOffset(months=6))).sum()),
                     "disruption_3m": int(len(recent) > 0 or ongoing)})
    return pd.DataFrame(rows, index=origins.index)
