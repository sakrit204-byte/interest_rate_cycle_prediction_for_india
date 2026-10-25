"""Walk forward evaluation of Nepal interbank direction models on the training period only.

Target: seasonally adjusted three month change in the interbank rate (D027). For test month t
the models train only on months whose label was public by the origin: label month plus the
three month horizon plus the two month Nepal publication lag, so months up to t - 5 (the
embargo). Blind window months are refused.

Models: majority, Markov persistence on the last known label, a mean reversion rule on the
adjusted level, ordered probit (all six features), L2 multinomial logistic (C by inner walk
forward and the one standard error rule), and a shallow random forest with fixed settings.

Outputs: reports/tables/nepal_walk_forward_train_metrics.csv, _predictions.csv, _dm.csv
Usage: python -m src.models.walk_forward_nepal [--liquidity]

With --liquidity: the second Nepal model (D030) on liquidity features from IMF monetary
surveys, its variant without the India repo change (the transmission test), and the baselines.
Outputs carry the prefix nepal_walk_forward_train_liquidity.
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from src.features.build_nepal_features import (FEATURES, LIQUIDITY_MODEL_FEATURES, NEPAL_LAG,
                                               OUT as FEATURE_FILE)
from src.features.nepal_target import HORIZON
from src.models import walk_forward as wf

warnings.filterwarnings("ignore", message="y_pred contains classes not in y_true")

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "reports" / "tables"
EMBARGO = HORIZON + NEPAL_LAG  # months
MIN_TRAIN = 60


NO_INDIA_FEATURES = [f for f in LIQUIDITY_MODEL_FEATURES if f != "india_repo_change_3m"]


def load_training(complete_col: str = "complete") -> pd.DataFrame:
    f = pd.read_csv(FEATURE_FILE)
    train = f[~f["blind_window"] & f[complete_col]].reset_index(drop=True)
    if train["blind_window"].any():
        raise RuntimeError("blind window rows reached the Nepal training evaluation")
    train["period"] = pd.PeriodIndex(train["month"], freq="M")
    train["y"] = train["y"].astype(int)
    # last label known at the origin, used by the persistence baseline
    known = pd.Series(train["y"].values, index=train["period"])
    train["prev_decision"] = [known.get(p - EMBARGO, np.nan) for p in train["period"]]
    return train


def mean_reversion(tr: pd.DataFrame, te: pd.Series) -> np.ndarray:
    """Up if the adjusted level is more than one training sd below its training mean, down if above."""
    mu, sd = tr["ib_adj_level"].mean(), tr["ib_adj_level"].std()
    z = (te["ib_adj_level"] - mu) / sd
    bins = np.where((tr["ib_adj_level"] - mu) / sd > 1, -1, np.where((tr["ib_adj_level"] - mu) / sd < -1, 1, 0))
    b = -1 if z > 1 else (1 if z < -1 else 0)
    return wf.freq(tr["y"].to_numpy()[bins == b])


def persistence(tr: pd.DataFrame, te: pd.Series) -> np.ndarray:
    if np.isnan(te["prev_decision"]):
        return wf.freq(tr["y"].to_numpy())
    return wf.persistence(tr.dropna(subset=["prev_decision"]), te)


def random_forest(tr: pd.DataFrame, te: pd.Series, features: list[str] = FEATURES) -> np.ndarray:
    m = RandomForestClassifier(n_estimators=300, max_depth=3, min_samples_leaf=10, random_state=0)
    m.fit(tr[features].to_numpy(), tr["y"].to_numpy())
    return wf.full_proba(m.classes_, m.predict_proba(te[features].to_numpy(dtype=float)[None, :]))[0]


def choose_c(tr: pd.DataFrame) -> float:
    """Inner walk forward over the last INNER_TEST months with the same embargo, one SE rule."""
    losses = {c: [] for c in wf.C_GRID}
    for i in range(len(tr) - wf.INNER_TEST, len(tr)):
        inner = tr[tr["period"] <= tr["period"].iloc[i] - EMBARGO]
        xtr, xte = wf.standardize(inner, tr.iloc[[i]], FEATURES)
        for c in wf.C_GRID:
            m = wf.logistic_fit(xtr, inner["y"].to_numpy(), c)
            losses[c].append(wf.log_loss(tr["y"].to_numpy()[[i]], wf.full_proba(m.classes_, m.predict_proba(xte)))[0])
    mean = {c: np.mean(v) for c, v in losses.items()}
    best = min(mean, key=mean.get)
    limit = mean[best] + np.std(losses[best], ddof=1) / np.sqrt(wf.INNER_TEST)
    return min(c for c in wf.C_GRID if mean[c] <= limit)


def logistic(tr: pd.DataFrame, te: pd.Series) -> np.ndarray:
    xtr, xte = wf.standardize(tr, te.to_frame().T, FEATURES)
    m = wf.logistic_fit(xtr, tr["y"].to_numpy(), choose_c(tr))
    return wf.full_proba(m.classes_, m.predict_proba(xte))[0]


MODELS = {
    "majority": wf.majority,
    "persistence": persistence,
    "mean_reversion_rule": mean_reversion,
    "ordered_probit": lambda tr, te: wf.ordered_probit(tr, te, FEATURES),
    "logistic_l2": logistic,
    "random_forest": random_forest,
}
# second Nepal model (D030) and the pre declared transmission test (with and without the India repo)
MODELS_LIQUIDITY = {
    "majority": wf.majority,
    "persistence": persistence,
    "mean_reversion_rule": mean_reversion,
    "ordered_probit_liquidity": lambda tr, te: wf.ordered_probit(tr, te, LIQUIDITY_MODEL_FEATURES),
    "ordered_probit_liquidity_no_india": lambda tr, te: wf.ordered_probit(tr, te, NO_INDIA_FEATURES),
    "random_forest_liquidity": lambda tr, te: random_forest(tr, te, LIQUIDITY_MODEL_FEATURES),
}


def run(data: pd.DataFrame, models: dict = MODELS) -> pd.DataFrame:
    rows = []
    for i in range(MIN_TRAIN + EMBARGO, len(data)):
        te = data.iloc[i]
        tr = data[data["period"] <= te["period"] - EMBARGO]
        for name, model in models.items():
            try:
                p = np.asarray(model(tr, te), float)
                p = p / p.sum()
                status = "ok"
            except Exception as err:  # recorded, never silently replaced
                p, status = wf.freq(tr["y"].to_numpy()), f"fallback_majority: {type(err).__name__}"
            rows.append({"date": te["month"], "model": name, "y": te["y"],
                         "pred": int(wf.CLASSES[np.argmax(p)]), "p_cut": p[0], "p_hold": p[1],
                         "p_hike": p[2], "n_train": len(tr), "status": status})
    return pd.DataFrame(rows)


def main() -> int:
    liquidity = "--liquidity" in sys.argv
    if liquidity:
        data, models, tag = load_training("complete_liquidity"), MODELS_LIQUIDITY, "nepal_walk_forward_train_liquidity"
        pairs = [("ordered_probit_liquidity", "ordered_probit_liquidity_no_india"),  # transmission test
                 ("ordered_probit_liquidity", "persistence"), ("ordered_probit_liquidity", "majority"),
                 ("ordered_probit_liquidity", "mean_reversion_rule"),
                 ("random_forest_liquidity", "ordered_probit_liquidity")]
    else:
        data, models, tag = load_training(), MODELS, "nepal_walk_forward_train"
        pairs = [("ordered_probit", "persistence"), ("ordered_probit", "majority"),
                 ("ordered_probit", "mean_reversion_rule"), ("random_forest", "ordered_probit"),
                 ("logistic_l2", "ordered_probit")]
    pred = run(data, models)
    table = wf.metrics_table(pred)
    dm = wf.dm_table(pred, pairs, horizon=HORIZON)  # overlapping labels
    TABLES.mkdir(parents=True, exist_ok=True)
    pred.round(4).to_csv(TABLES / f"{tag}_predictions.csv", index=False)
    table.round(4).to_csv(TABLES / f"{tag}_metrics.csv", index=False)
    dm.round(4).to_csv(TABLES / f"{tag}_dm.csv", index=False)
    print(f"training months {len(data)}; test months {len(pred) // len(models)} "
          f"({pred['date'].iloc[0]} to {pred['date'].iloc[-1]})")
    print(table.round(3).to_string(index=False))
    print(dm.round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
