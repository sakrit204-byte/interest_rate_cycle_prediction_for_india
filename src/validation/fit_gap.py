"""Over and underfitting check for the final models (decision D051).

For each final model, balanced accuracy is compared at three stages:

* in sample: fitted once on all training data and scored on the same data;
* walk forward: refit at every origin on past data only, scored on the training period;
* unseen: the blind window (India, 2021 to 2026) or the post hoc period (Nepal binary).

A model that overfits scores much better in sample than out of sample. A model that underfits
scores low everywhere and close to its benchmark. The walk forward and unseen values are read
from the tables written by the earlier steps, so this module only adds the in sample fit.

Output: reports/tables/fit_gap.csv
Usage: python -m src.validation.fit_gap
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score

from src.models import walk_forward as wf
from src.models.nepal_binary import CONFIG, QUESTIONS
from src.models.nepal_target_search import panel
from src.simulation import scenarios as sc

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "reports" / "tables"


def _read(name: str, **match) -> pd.Series:
    t = pd.read_csv(TABLES / f"{name}.csv")
    for k, v in match.items():
        t = t[t[k] == v]
    return t.iloc[0]


def india() -> dict:
    h = sc.history()
    tr = h[(h["blind_window"] == 0) & h["complete_econ"]]
    p = np.vstack([wf.ordered_probit(tr, r, wf.ECON_MODEL_FEATURES) for _, r in tr.iterrows()])
    wfr = _read("walk_forward_train_econ_metrics", model="ordered_probit_economic")
    bl = _read("blind_india_metrics", model="ordered_probit_economic")
    per = _read("blind_india_metrics", model="persistence")
    return {"model": "India economic ordered probit", "classes": 3,
            "n_in_sample": len(tr), "in_sample": balanced_accuracy_score(tr["y"], p.argmax(1) - 1),
            "n_walk_forward": wfr["n"], "walk_forward": wfr["balanced_accuracy"],
            "n_unseen": bl["n"], "unseen": bl["balanced_accuracy"], "unseen_persistence": per["balanced_accuracy"],
            "unseen_period": "blind 2021 to 2026"}


def nepal() -> list[dict]:
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    d, _ = panel(cfg["information_lag_months"]["interbank"], "raw", cfg["horizon_months"],
                 last_label=pd.Period(cfg["training_last_label"], freq="M"))
    d["calendar"] = d["month_of_year"].map(d.groupby("month_of_year")["change"].mean())
    x = wf.standardize(d, d, cfg["features"])[0]
    rows = []
    for q, k in QUESTIONS.items():
        y = (d["y"] == k).astype(int)
        m = LogisticRegression(C=0.3, max_iter=5000, class_weight="balanced").fit(x, y)
        wfr = _read("nepal_binary_metrics", period="train", question=q, benchmark="model")
        ph = _read("nepal_binary_metrics", period="post_hoc", question=q, benchmark="model")
        per = _read("nepal_binary_metrics", period="post_hoc", question=q, benchmark="persistence")
        rows.append({"model": f"Nepal binary logistic, {q}", "classes": 2,
                     "n_in_sample": len(d), "in_sample": balanced_accuracy_score(y, m.predict(x)),
                     "n_walk_forward": wfr["n"], "walk_forward": wfr["balanced_accuracy"],
                     "n_unseen": ph["n"], "unseen": ph["balanced_accuracy"],
                     "unseen_persistence": per["balanced_accuracy"], "unseen_period": "post hoc 2021 to 2026"})
    return rows


def main() -> int:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        rows = [india(), *nepal()]
    t = pd.DataFrame(rows)
    t["gap_in_sample_minus_unseen"] = t["in_sample"] - t["unseen"]
    t.round(3).to_csv(TABLES / "fit_gap.csv", index=False)
    pd.set_option("display.width", 200)
    print(t.round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
