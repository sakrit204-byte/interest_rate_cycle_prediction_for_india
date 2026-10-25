"""Tests for the India decision table, using small synthetic inputs (not real data)."""

import pandas as pd

from src.features.targets_india import announcements, build


def _rate(points):
    """Daily step series from {date: rate} change points."""
    idx = pd.date_range("2018-01-01", "2018-12-31", freq="D")
    s = pd.Series(index=idx, dtype=float)
    for d, v in points.items():
        s[pd.Timestamp(d):] = v
    return s


ENTRIES = pd.DataFrame([
    {"fiscal_year_end": 2019, "date": "2018-06-06", "title": "Second Bi-monthly Monetary Policy Statement for 2018-19",
     "body": "Audio Recording of RBI Press Conference Resolution of the Monetary Policy Committee"},
    {"fiscal_year_end": 2019, "date": "2018-06-09", "title": "Second Bi-monthly Monetary Policy Statement for 2018-19",
     "body": "Edited Transcript of Reserve Bank of India's Second Bi-Monthly Policy Press Conference"},
    {"fiscal_year_end": 2019, "date": "2018-06-20", "title": "Minutes of the Monetary Policy Committee",
     "body": "Minutes of the Monetary Policy Committee Meeting, June 4 to 6, 2018"},
    {"fiscal_year_end": 2019, "date": "2018-08-01", "title": "Third Bi-monthly Monetary Policy Statement for 2018-19",
     "body": "Edited Transcript Governor's Statement Resolution of the Monetary Policy Committee"},
    {"fiscal_year_end": 2019, "date": "2018-10-05", "title": "Fourth Bi-monthly Monetary Policy Statement for 2018-19",
     "body": "Resolution of the Monetary Policy Committee"},
])


def test_announcements_drop_minutes_and_transcripts_and_merge_same_event():
    a = announcements(ENTRIES)
    assert [d.date().isoformat() for d in a.date] == ["2018-06-06", "2018-08-01", "2018-10-05"]


def test_build_classifies_decisions_and_flags_inter_meeting_moves():
    rate = _rate({"2018-01-01": 6.0, "2018-06-07": 6.25, "2018-08-02": 6.5, "2018-11-15": 6.25})
    out = build(ENTRIES, rate)
    by_date = {str(d): r for d, r in zip(out.date, out.itertuples())}
    assert by_date["2018-06-06"].decision == "hike" and by_date["2018-06-06"].change_bp == 25
    assert by_date["2018-08-01"].decision == "hike"
    assert by_date["2018-10-05"].decision == "hold" and by_date["2018-10-05"].change_bp == 0
    inter = out[out.inter_meeting]
    assert [str(d) for d in inter.date] == ["2018-11-15"] and inter.change_bp.iloc[0] == -25
    assert set(out.regime.astype(str)) == {"mpc"}
    assert not out.blind_window.any()
