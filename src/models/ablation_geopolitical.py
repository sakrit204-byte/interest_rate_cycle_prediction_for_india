"""Geopolitical ablation (decision D042), training period only.

India: economic ordered probit with and without the four geopolitical features, same walk
forward as walk_forward, Diebold Mariano on log loss. The features use the month before the
information cutoff of each decision.

Nepal: the D039 binary logistic for the fall and rise questions with and without the features,
same walk forward and embargo as nepal_strategy, compared by balanced accuracy and Brier score.

Outputs: reports/tables/ablation_geopolitical_india.csv, ablation_geopolitical_nepal.csv
Usage: python -m src.models.ablation_geopolitical
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.metrics import balanced_accuracy_score, brier_score_loss

from src.evaluation.metrics import block_bootstrap_ci, diebold_mariano
from src.features import geopolitical as geo
from src.models import walk_forward as wf
from src.models.nepal_binary import CONFIG, QUESTIONS
from src.models.nepal_strategy import prob
from src.models.nepal_target_search import panel

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "reports" / "tables"


def india() -> pd.DataFrame:
    data = wf.load_training("complete_econ")
    info = pd.to_datetime(data["cutoff"]).dt.to_period("M")
    data = pd.concat([data, geo.at(info).set_index(data.index)], axis=1)
    if data[geo.FEATURES].isna().any().any():
        raise RuntimeError("missing geopolitical values for India decisions")
    models = {"economic": lambda tr, te: wf.ordered_probit(tr, te, wf.ECON_MODEL_FEATURES),
              "economic_geopolitical": lambda tr, te: wf.ordered_probit(tr, te, wf.ECON_MODEL_FEATURES + geo.FEATURES)}
    pred = wf.run(data, models)
    table = wf.metrics_table(pred)[["model", "n", "accuracy", "balanced_accuracy", "bal_acc_ci_low",
                                     "bal_acc_ci_high", "log_loss", "brier"]]
    dm = wf.dm_table(pred, [("economic_geopolitical", "economic")])
    return table.assign(dm_p_value=[np.nan, dm["p_value"].iloc[0]])


def nepal() -> pd.DataFrame:
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    d, _ = panel(cfg["information_lag_months"]["interbank"], "raw", cfg["horizon_months"],
                 last_label=pd.Period(cfg["training_last_label"], freq="M"))
    d = pd.concat([d, geo.at(d["period"]).set_index(d.index)], axis=1).dropna(subset=geo.FEATURES).reset_index(drop=True)
    base, emb = cfg["features"], cfg["embargo_months"]
    rows = []
    for i in range(cfg["min_train"] + emb, len(d)):
        te = d.iloc[[i]].copy()
        tr = d[d["period"] <= te["period"].iloc[0] - emb].copy()
        means = tr.groupby("month_of_year")["change"].mean()
        tr["calendar"] = tr["month_of_year"].map(means)
        te["calendar"] = te["month_of_year"].map(means).fillna(0.0)
        for q, k in QUESTIONS.items():
            y = (tr["y"] == k).astype(int)
            rows.append({"question": q, "y": int(te["y"].iloc[0] == k),
                         "baseline": prob(tr, te, base, y), "geopolitical": prob(tr, te, base + geo.FEATURES, y)})
    pred = pd.DataFrame(rows)
    out = []
    for q, g in pred.groupby("question", sort=False):
        yv = g["y"].to_numpy()
        sq = {m: (g[m].to_numpy() - yv) ** 2 for m in ("baseline", "geopolitical")}
        _, p = diebold_mariano(sq["geopolitical"], sq["baseline"], cfg["horizon_months"])
        for m in ("baseline", "geopolitical"):
            yhat = (g[m] >= 0.5).astype(int).to_numpy()
            lo, hi = block_bootstrap_ci(yv, yhat)
            out.append({"question": q, "model": m, "n": len(g), "balanced_accuracy": balanced_accuracy_score(yv, yhat),
                        "bal_acc_ci_low": lo, "bal_acc_ci_high": hi, "brier": brier_score_loss(yv, g[m]),
                        "dm_p_value_brier": p if m == "geopolitical" else np.nan})
    return pd.DataFrame(out)


def main() -> int:
    a, b = india().round(4), nepal().round(4)
    a.to_csv(TABLES / "ablation_geopolitical_india.csv", index=False)
    b.to_csv(TABLES / "ablation_geopolitical_nepal.csv", index=False)
    print(a.to_string(index=False))
    print(b.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
