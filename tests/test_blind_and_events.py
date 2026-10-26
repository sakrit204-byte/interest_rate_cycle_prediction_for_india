import pandas as pd
import pytest

from src.events import political_features as pf
from src.policy import suggestion_engine as se


def test_unblinding_refused_while_config_is_draft():
    if se.config()["status"] == "frozen":
        pytest.skip("config already frozen")
    with pytest.raises(RuntimeError):
        se.check_frozen()


def test_engine_training_load_excludes_blind_window():
    data = se.load(unblind=False)
    assert (data["date"] < se.config()["blind_start"]).all()


def test_election_pending_uses_announcement_not_results():
    # 2019: schedule announced 10 Mar, results 23 May
    d = pd.Series(pd.to_datetime(["2019-03-01", "2019-04-04", "2019-06-06"]))
    f = pf.india(d, d - pd.Timedelta(days=7), d - pd.Timedelta(days=60))
    assert f["election_pending"].tolist() == [0, 1, 0]


def test_budget_counted_only_after_presentation():
    d = pd.Series(pd.to_datetime(["2021-02-05", "2021-02-10"]))
    cutoffs = pd.Series(pd.to_datetime(["2021-01-31", "2021-02-03"]))
    prev = pd.Series(pd.to_datetime(["2020-12-04", "2020-12-04"]))
    assert pf.india(d, cutoffs, prev)["budget_since_last"].tolist() == [0, 1]


def test_blockade_ongoing_until_its_end():
    o = pd.Series(pd.to_datetime(["2015-09-15", "2016-01-15", "2016-06-15"]))
    assert pf.nepal(o)["disruption_3m"].tolist()[1:] == [1, 0]
