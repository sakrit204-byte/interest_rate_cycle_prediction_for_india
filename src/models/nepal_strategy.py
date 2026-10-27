"""Training strategy comparison for the Nepal binary model (decision D041), training period only.

Same questions, features, information lags and embargo as the frozen D039 model; only the way
each window is used changes:
  expanding    all labels public at the origin (the D039 baseline)
  rolling_120  only the last 120 months of public labels
  recency_hl60 all labels, weighted by 0.5 ** (age in months / 60)
  regime       expanding, plus a floor pinned indicator and a corridor era indicator
  combination  equal average of the model, calendar only and persistence probabilities

Only labels up to October 2021 are scored, so the post hoc window is never used to choose.

Output: reports/tables/nepal_strategy_train.csv
Usage: python -m src.models.nepal_strategy
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, brier_score_loss

from src.evaluation.metrics import block_bootstrap_ci
from src.models import walk_forward as wf
from src.models.nepal_binary import CONFIG, QUESTIONS
from src.models.nepal_target_search import panel

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "tables" / "nepal_strategy_train.csv"
CORRIDOR_START = pd.Period("2016-08", freq="M")  # Monetary Policy 2016/17, date to verify
PINNED = 0.5
REGIME = ["floor_pinned", "corridor_era"]
STRATEGIES = ["expanding", "rolling_120", "recency_hl60", "regime", "combination"]


def prob(tr, te, features, y, weight=None) -> float:
    if y.nunique() < 2:
        return float(y.iloc[0])
    xtr, xte = wf.standardize(tr, te, features)
    m = LogisticRegression(C=0.3, max_iter=5000, class_weight="balanced").fit(xtr, y, sample_weight=weight)
    return float(m.predict_proba(xte)[0, 1])


def run(cfg: dict) -> pd.DataFrame:
    d, _ = panel(cfg["information_lag_months"]["interbank"], "raw", cfg["horizon_months"],
                 last_label=pd.Period(cfg["training_last_label"], freq="M"))
    d["floor_pinned"] = (d["ib_minus_floor"] < PINNED).astype(float)
    d["corridor_era"] = (d["period"] >= CORRIDOR_START).astype(float)
    base, emb = cfg["features"], cfg["embargo_months"]
    lab = d.set_index("period")["y"]
    d["last"] = [lab.get(p - emb, np.nan) for p in d["period"]]
    rows = []
    for i in range(cfg["min_train"] + emb, len(d)):
        te = d.iloc[[i]].copy()
        origin = te["period"].iloc[0]
        full = d[d["period"] <= origin - emb].copy()
        means = full.groupby("month_of_year")["change"].mean()
        full["calendar"] = full["month_of_year"].map(means)
        te["calendar"] = te["month_of_year"].map(means).fillna(0.0)
        age = np.array([(origin - p).n for p in full["period"]], float)
        for q, k in QUESTIONS.items():
            y_full = (full["y"] == k).astype(int)
            yes = int(te["y"].iloc[0] == k)
            roll = full[full["period"] > origin - emb - 120]
            p_model = prob(full, te, base, y_full)
            p_cal = prob(full, te, ["calendar"], y_full)
            same = full[full["last"] == te["last"].iloc[0]]
            p_pers = ((same["y"] == k).sum() + 1) / (len(same) + 2)
            # put persistence on the same balanced footing as the class weighted logistic models
            pi = y_full.mean()
            p_pers = (p_pers / pi) / (p_pers / pi + (1 - p_pers) / (1 - pi))
            out = {
                "expanding": p_model,
                "rolling_120": prob(roll, te, base, (roll["y"] == k).astype(int)),
                "recency_hl60": prob(full, te, base, y_full, weight=0.5 ** (age / 60)),
                "regime": prob(full, te, base + REGIME, y_full),
                "combination": (p_model + p_cal + p_pers) / 3,
            }
            for s, p in out.items():
                rows.append({"origin": str(origin), "question": q, "strategy": s, "y": yes, "p": p})
    return pd.DataFrame(rows)


def main() -> int:
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    pred = run(cfg)
    out = []
    for (q, s), g in pred.groupby(["question", "strategy"], sort=False):
        y, yhat = g["y"].to_numpy(), (g["p"] >= 0.5).astype(int).to_numpy()
        lo, hi = block_bootstrap_ci(y, yhat)
        out.append({"question": q, "strategy": s, "n": len(g), "balanced_accuracy": balanced_accuracy_score(y, yhat),
                    "bal_acc_ci_low": lo, "bal_acc_ci_high": hi, "brier": brier_score_loss(y, g["p"])})
    table = pd.DataFrame(out).round(4)
    table.to_csv(OUT, index=False)
    print(table.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
