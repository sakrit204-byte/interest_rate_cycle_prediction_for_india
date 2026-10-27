"""Exploratory search for a better Nepal model, training period only (decision D038).

Every candidate here is scored on the same walk forward as walk_forward_nepal (expanding
window, five month embargo, blind window refused) and every candidate tried is written to the
output table, so the size of the search is visible. Nothing here touches the blind window.

Two kinds of change are tried.

Decision rule. The probability models never call the middle class (flat), which is the rarest,
so balanced accuracy cannot exceed about two thirds. The prior corrected rule picks the class
with the highest ratio of predicted probability to its training frequency, which is the
decision that maximises expected balanced accuracy when the probabilities are calibrated.

Features from the interest rate corridor and the Treasury bill market (IMF MFS_IR, one month
lag like the other corridor rates in D028):
  ib_minus_floor     interbank rate (t - 2) minus the NRB floor rate (t - 1): a rate pinned
                     near the floor cannot fall much further
  ceiling_minus_ib   NRB bank rate (t - 1) minus the interbank rate (t - 2): room to rise
  tbill_minus_ib     91 day Treasury bill yield (t - 1) minus the interbank rate (t - 2):
                     the bill market is weekly, so it carries more recent liquidity news
  tbill_change_3m    change in the bill yield from t - 4 to t - 1

Output: reports/tables/nepal_candidates_train.csv
Usage: python -m src.models.nepal_candidates
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score

from src.features.build_nepal_features import LIQUIDITY_MODEL_FEATURES, imf_series
from src.models import walk_forward as wf
from src.models.walk_forward_nepal import EMBARGO, MIN_TRAIN, load_training

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "data" / "interim" / "nepal" / "nepal_target_monthly.csv"
OUT = ROOT / "reports" / "tables" / "nepal_candidates_train.csv"
RATES = {"floor": "DISR_RT_PT_A_PT", "ceiling": "MFS166_RT_PT_A_PT", "tbill": "GSTBILY_RT_PT_A_PT"}
CORRIDOR = ["ib_minus_floor", "ceiling_minus_ib"]
BILL = ["tbill_minus_ib", "tbill_change_3m"]
FEATURE_SETS = {
    "liquidity": LIQUIDITY_MODEL_FEATURES,
    "liquidity_corridor": LIQUIDITY_MODEL_FEATURES + CORRIDOR,
    "liquidity_corridor_bill": LIQUIDITY_MODEL_FEATURES + CORRIDOR + BILL,
}


def market_features(periods: pd.Series) -> pd.DataFrame:
    raw = pd.read_csv(TARGET, index_col=0)["interbank_rate"]
    raw.index = pd.PeriodIndex(raw.index, freq="M")
    r = {k: imf_series("MFS_IR_npl_interest_rates", lambda d, c=c: d["INDICATOR"] == c) for k, c in RATES.items()}
    rows = []
    for p in periods:
        ib, c = raw.get(p - 2, np.nan), p - 1
        rows.append({"ib_minus_floor": ib - r["floor"].get(c, np.nan),
                     "ceiling_minus_ib": r["ceiling"].get(c, np.nan) - ib,
                     "tbill_minus_ib": r["tbill"].get(c, np.nan) - ib,
                     "tbill_change_3m": r["tbill"].get(c, np.nan) - r["tbill"].get(c - 3, np.nan)})
    return pd.DataFrame(rows, index=periods.index)


def logistic(tr: pd.DataFrame, te: pd.Series, features: list[str]) -> np.ndarray:
    xtr, xte = wf.standardize(tr, te.to_frame().T, features)
    m = LogisticRegression(C=0.3, max_iter=5000).fit(xtr, tr["y"].to_numpy())  # C fixed in advance
    return wf.full_proba(m.classes_, m.predict_proba(xte))[0]


def forest(tr: pd.DataFrame, te: pd.Series, features: list[str]) -> np.ndarray:
    m = RandomForestClassifier(n_estimators=300, max_depth=3, min_samples_leaf=10, random_state=0)
    m.fit(tr[features].to_numpy(), tr["y"].to_numpy())
    return wf.full_proba(m.classes_, m.predict_proba(te[features].to_numpy(dtype=float)[None, :]))[0]


MODELS = {"ordered_probit": wf.ordered_probit, "logistic": logistic, "random_forest": forest}


def walk(data: pd.DataFrame, model, features: list[str]) -> pd.DataFrame:
    rows = []
    for i in range(MIN_TRAIN + EMBARGO, len(data)):
        te = data.iloc[i]
        tr = data[data["period"] <= te["period"] - EMBARGO]
        p = np.asarray(model(tr, te, features), float)
        p = p / p.sum()
        prior = wf.freq(tr["y"].to_numpy())
        rows.append({"month": te["month"], "y": te["y"], "p_cut": p[0], "p_hold": p[1], "p_hike": p[2],
                     "pred_argmax": int(wf.CLASSES[np.argmax(p)]),
                     "pred_prior": int(wf.CLASSES[np.argmax(p / prior)])})
    return pd.DataFrame(rows)


def main() -> int:
    data = load_training("complete_liquidity")
    data = data.join(market_features(data["period"]))
    data = data.dropna(subset=CORRIDOR + BILL).reset_index(drop=True)
    print(f"training months with all candidate features: {len(data)} ({data['month'].iloc[0]} to {data['month'].iloc[-1]})")
    out = []
    for fs, features in FEATURE_SETS.items():
        for name, model in MODELS.items():
            g = walk(data, model, features)
            proba = g[["p_cut", "p_hold", "p_hike"]].to_numpy()
            for rule in ("argmax", "prior"):
                yhat = g[f"pred_{rule}"].to_numpy()
                lo, hi = wf.block_bootstrap_ci(g["y"].to_numpy(), yhat)
                out.append({"features": fs, "model": name, "rule": rule, "n": len(g),
                            "accuracy": (yhat == g["y"]).mean(),
                            "balanced_accuracy": balanced_accuracy_score(g["y"], yhat),
                            "bal_acc_ci_low": lo, "bal_acc_ci_high": hi,
                            "log_loss": wf.log_loss(g["y"].to_numpy(), proba).mean(),
                            "flat_calls": int((yhat == 0).sum())})
            print(fs, name, "done")
    table = pd.DataFrame(out).round(4)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUT, index=False)
    print(table.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
