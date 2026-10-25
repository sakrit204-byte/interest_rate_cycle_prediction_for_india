"""Tests for metrics and the blind window guard of the walk forward evaluation."""

import numpy as np
import pandas as pd
import pytest

from src.evaluation.metrics import brier, log_loss
from src.models import walk_forward as wf


def test_log_loss_and_brier():
    y = np.array([-1, 0, 1])
    perfect = np.eye(3)
    assert np.allclose(log_loss(y, perfect), 0, atol=1e-5)
    assert np.allclose(brier(y, perfect), 0)
    uniform = np.full((3, 3), 1 / 3)
    assert np.allclose(log_loss(y, uniform), np.log(3))
    assert np.allclose(brier(y, uniform), 2 / 3)


def test_full_proba_fills_missing_classes():
    p = wf.full_proba(np.array([0, 1]), np.array([[0.4, 0.6]]))
    assert p.tolist() == [[0.0, 0.4, 0.6]]


@pytest.mark.skipif(not wf.FEATURE_FILE.exists(), reason="feature table not built")
def test_training_load_excludes_blind_window():
    data = wf.load_training()
    assert pd.to_datetime(data["date"]).max() < pd.Timestamp("2021-11-01")
    assert not data["blind_window"].any()


@pytest.mark.skipif(not wf.FEATURE_FILE.exists(), reason="feature table not built")
def test_training_rows_know_only_past_outcomes():
    data = wf.load_training()
    for i in range(wf.MIN_TRAIN, len(data)):
        tr = data.iloc[:i]
        tr = tr[tr["date"] <= data["cutoff"].iloc[i]]
        assert (tr["date"] < data["date"].iloc[i]).all()
