"""Walk forward evaluation of India decision models on the training period only.

For each test decision, every model is fitted on the earlier decisions whose outcome was
known by the test decision's information cutoff, then predicts the test decision. Features
are standardized on the training rows of each fold. Rows inside the blind window are
refused (see configs/blind_test.yaml); this module never reads them.

Models: majority class, Markov persistence, inflation change threshold rule, ordered
probit (primary, D010), L2 multinomial logistic with C chosen by an inner walk forward and
the one standard error rule, and a shallow random forest with fixed settings.

Outputs: reports/tables/walk_forward_train_metrics.csv and
reports/tables/walk_forward_train_predictions.csv
Usage: python -m src.models.walk_forward [--projections]
"""

from __future__ import annotations

import sys
import warnings

warnings.filterwarnings("ignore", message="y_pred contains classes not in y_true")
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from statsmodels.miscmodels.ordinal_model import OrderedModel

from src.evaluation.metrics import CLASSES, block_bootstrap_ci, diebold_mariano, log_loss, summary
from src.features.build_india_features import FEATURES, PROJECTION_FEATURES

ROOT = Path(__file__).resolve().parents[2]
FEATURE_FILE = ROOT / "data" / "processed" / "india" / "india_features_cutoff7.csv"
CONFIG = ROOT / "configs" / "blind_test.yaml"
TABLES = ROOT / "reports" / "tables"
MIN_TRAIN = 40          # first test decision is the 41st (January 2010)
C_GRID = [0.01, 0.03, 0.1, 0.3, 1.0, 3.0]
INNER_TEST = 15         # last decisions of each training window used to choose C
THRESHOLD_GRID = np.round(np.arange(0.0, 2.01, 0.25), 2)
SMOOTH = 1.0            # additive smoothing for frequency based probabilities


def load_training(complete_col: str = "complete") -> pd.DataFrame:
    blind_start = pd.Timestamp(yaml.safe_load(CONFIG.read_text())["blind_window_start"])
    f = pd.read_csv(FEATURE_FILE, parse_dates=["date", "cutoff"])
    train = f[(f["date"] < blind_start) & f[complete_col]].reset_index(drop=True)
    if train["blind_window"].any():
        raise RuntimeError("blind window rows reached the training evaluation")
    return train


def freq(y: np.ndarray) -> np.ndarray:
    counts = np.array([(y == c).sum() for c in CLASSES], float) + SMOOTH
    return counts / counts.sum()


def full_proba(model_classes: np.ndarray, proba: np.ndarray) -> np.ndarray:
    """Place predicted probabilities in CLASSES order, zero for classes absent in training."""
    out = np.zeros((proba.shape[0], len(CLASSES)))
    out[:, np.searchsorted(CLASSES, model_classes)] = proba
    return out


def majority(tr: pd.DataFrame, te: pd.Series) -> np.ndarray:
    return freq(tr["y"].to_numpy())


def persistence(tr: pd.DataFrame, te: pd.Series) -> np.ndarray:
    """Transition frequencies from the previous decision class (a first order Markov chain)."""
    same = tr[tr["prev_decision"] == te["prev_decision"]]
    return freq(same["y"].to_numpy())


def threshold_bins(x: np.ndarray, a: float) -> np.ndarray:
    return np.where(x > a, 1, np.where(x < -a, -1, 0))


def threshold_rule(tr: pd.DataFrame, te: pd.Series) -> np.ndarray:
    """Hike if inflation rose by more than a over three months, cut if it fell by more than a.

    a is chosen on the training window by balanced accuracy; probabilities are the training
    class frequencies within the predicted bin.
    """
    from sklearn.metrics import balanced_accuracy_score
    x, y = tr["infl_change_3m"].to_numpy(), tr["y"].to_numpy()
    best = max(THRESHOLD_GRID, key=lambda a: balanced_accuracy_score(y, threshold_bins(x, a)))
    b = threshold_bins(np.array([te["infl_change_3m"]]), best)[0]
    return freq(y[threshold_bins(x, best) == b])


def standardize(tr: pd.DataFrame, te: pd.DataFrame, features: list[str] = FEATURES) -> tuple[np.ndarray, np.ndarray]:
    mu, sd = tr[features].mean(), tr[features].std(ddof=0).replace(0, 1)
    return ((tr[features] - mu) / sd).to_numpy(), ((te[features] - mu) / sd).to_numpy()


# Declared after the first run (decision D023): the standard inertial Taylor type
# specification, inflation, its change, output growth and the lagged decision.
TAYLOR_FEATURES = ["infl", "infl_change_3m", "iip_yoy_3m", "prev_decision"]


def ordered_probit(tr: pd.DataFrame, te: pd.Series, features: list[str] = FEATURES) -> np.ndarray:
    xtr, xte = standardize(tr, te.to_frame().T, features)
    keep = xtr.std(axis=0) > 0  # regime dummies are constant in early windows
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = OrderedModel(tr["y"].to_numpy(), xtr[:, keep], distr="probit").fit(method="bfgs", disp=False, maxiter=2000)
        return np.asarray(res.model.predict(res.params, exog=xte[:, keep].astype(float)))[0]


def logistic_fit(xtr: np.ndarray, ytr: np.ndarray, c: float) -> LogisticRegression:
    return LogisticRegression(C=c, max_iter=5000).fit(xtr, ytr)


def choose_c(tr: pd.DataFrame, features: list[str] = FEATURES) -> float:
    """Inner walk forward over the last INNER_TEST training decisions, one standard error rule."""
    losses = {c: [] for c in C_GRID}
    for i in range(len(tr) - INNER_TEST, len(tr)):
        inner = tr.iloc[:i]
        inner = inner[inner["date"] <= tr["cutoff"].iloc[i]]
        xtr, xte = standardize(inner, tr.iloc[[i]], features)
        for c in C_GRID:
            m = logistic_fit(xtr, inner["y"].to_numpy(), c)
            p = full_proba(m.classes_, m.predict_proba(xte))
            losses[c].append(log_loss(tr["y"].to_numpy()[[i]], p)[0])
    mean = {c: np.mean(v) for c, v in losses.items()}
    best = min(mean, key=mean.get)
    limit = mean[best] + np.std(losses[best], ddof=1) / np.sqrt(INNER_TEST)
    return min(c for c in C_GRID if mean[c] <= limit)  # strongest regularization within 1 SE


def logistic(tr: pd.DataFrame, te: pd.Series, features: list[str] = FEATURES) -> np.ndarray:
    c = choose_c(tr, features)
    xtr, xte = standardize(tr, te.to_frame().T, features)
    m = logistic_fit(xtr, tr["y"].to_numpy(), c)
    return full_proba(m.classes_, m.predict_proba(xte))[0]


def random_forest(tr: pd.DataFrame, te: pd.Series) -> np.ndarray:
    m = RandomForestClassifier(n_estimators=300, max_depth=3, min_samples_leaf=5, random_state=0)
    m.fit(tr[FEATURES].to_numpy(), tr["y"].to_numpy())
    return full_proba(m.classes_, m.predict_proba(te[FEATURES].to_numpy(dtype=float)[None, :]))[0]


MODELS = {
    "majority": majority,
    "persistence": persistence,
    "threshold_rule": threshold_rule,
    "ordered_probit": ordered_probit,
    "ordered_probit_taylor": lambda tr, te: ordered_probit(tr, te, TAYLOR_FEATURES),
    "logistic_l2": logistic,
    "random_forest": random_forest,
}


# Model 2 (D025), declared before its first run: the Taylor type ordered probit plus the
# RBI projection and its latest revision, against the same baselines on identical rows.
HYBRID_FEATURES = TAYLOR_FEATURES + PROJECTION_FEATURES
MODELS_PROJECTION = {
    "majority": majority,
    "persistence": persistence,
    "ordered_probit_taylor": lambda tr, te: ordered_probit(tr, te, TAYLOR_FEATURES),
    "ordered_probit_hybrid": lambda tr, te: ordered_probit(tr, te, HYBRID_FEATURES),
    "logistic_l2_hybrid": lambda tr, te: logistic(tr, te, HYBRID_FEATURES),
}


def run(data: pd.DataFrame, models: dict = MODELS) -> pd.DataFrame:
    rows = []
    for i in range(MIN_TRAIN, len(data)):
        te = data.iloc[i]
        tr = data.iloc[:i]
        tr = tr[tr["date"] <= te["cutoff"]]  # outcomes known by the cutoff only
        for name, model in models.items():
            try:
                p = np.asarray(model(tr, te), float)
                p = p / p.sum()
                status = "ok"
            except Exception as err:  # a failed fit is recorded, never silently replaced
                p, status = freq(tr["y"].to_numpy()), f"fallback_majority: {type(err).__name__}"
            rows.append({"date": te["date"].date(), "model": name, "y": te["y"],
                         "pred": int(CLASSES[np.argmax(p)]), "p_cut": p[0], "p_hold": p[1],
                         "p_hike": p[2], "n_train": len(tr), "status": status})
    return pd.DataFrame(rows)


def metrics_table(pred: pd.DataFrame, by: str | None = None) -> pd.DataFrame:
    out = []
    keys = ["model"] + ([by] if by else [])
    for key, g in pred.groupby(keys, sort=False):
        name = key[0]
        y, yhat = g["y"].to_numpy(), g["pred"].to_numpy()
        proba = g[["p_cut", "p_hold", "p_hike"]].to_numpy()
        lo, hi = block_bootstrap_ci(y, yhat)
        extra = {by: key[1]} if by else {}
        out.append({"model": name, **extra, **summary(y, yhat, proba), "bal_acc_ci_low": lo,
                    "bal_acc_ci_high": hi, "fallbacks": int((g["status"] != "ok").sum())})
    return pd.DataFrame(out)


def dm_table(pred: pd.DataFrame, pairs: list[tuple[str, str]], horizon: int = 1) -> pd.DataFrame:
    """Diebold Mariano tests on per decision log loss for the given model pairs."""
    out = []
    for a, b in pairs:
        ga = pred[pred["model"] == a].set_index("date")
        gb = pred[pred["model"] == b].set_index("date").loc[ga.index]
        la = log_loss(ga["y"].to_numpy(), ga[["p_cut", "p_hold", "p_hike"]].to_numpy())
        lb = log_loss(gb["y"].to_numpy(), gb[["p_cut", "p_hold", "p_hike"]].to_numpy())
        stat, p = diebold_mariano(la, lb, horizon)
        out.append({"model_a": a, "model_b": b, "mean_loss_a": la.mean(), "mean_loss_b": lb.mean(),
                    "dm_stat_hln": stat, "p_value": p, "n": len(la)})
    return pd.DataFrame(out)


def main_projection() -> int:
    data = load_training("complete_projection")
    pred = run(data, MODELS_PROJECTION)
    table = metrics_table(pred)
    dm = dm_table(pred, [("ordered_probit_hybrid", "persistence"), ("ordered_probit_hybrid", "ordered_probit_taylor"),
                         ("ordered_probit_hybrid", "majority"), ("logistic_l2_hybrid", "ordered_probit_hybrid")])
    TABLES.mkdir(parents=True, exist_ok=True)
    pred.round(4).to_csv(TABLES / "walk_forward_train_projection_predictions.csv", index=False)
    table.round(4).to_csv(TABLES / "walk_forward_train_projection_metrics.csv", index=False)
    dm.round(4).to_csv(TABLES / "walk_forward_train_projection_dm.csv", index=False)
    print(f"training decisions {len(data)}; test decisions {len(data) - MIN_TRAIN} "
          f"({data['date'].iloc[MIN_TRAIN].date()} to {data['date'].iloc[-1].date()})")
    print(table.round(3).to_string(index=False))
    print(dm.round(3).to_string(index=False))
    return 0


def main() -> int:
    if "--projections" in sys.argv:
        return main_projection()
    data = load_training()
    pred = run(data)
    pred["period"] = np.where(pd.to_datetime(pred["date"]) < pd.Timestamp("2014-01-21"),
                              "2010_to_2013", "2014_to_2021")
    table = metrics_table(pred)
    by_period = metrics_table(pred, "period")
    TABLES.mkdir(parents=True, exist_ok=True)
    pred.round(4).to_csv(TABLES / "walk_forward_train_predictions.csv", index=False)
    table.round(4).to_csv(TABLES / "walk_forward_train_metrics.csv", index=False)
    by_period.round(4).to_csv(TABLES / "walk_forward_train_metrics_by_period.csv", index=False)
    print(f"training decisions {len(data)}; test decisions {len(data) - MIN_TRAIN} "
          f"({data['date'].iloc[MIN_TRAIN].date()} to {data['date'].iloc[-1].date()})")
    print(table.round(3).to_string(index=False))
    print(by_period[["model", "period", "n", "accuracy", "balanced_accuracy", "log_loss"]].round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
