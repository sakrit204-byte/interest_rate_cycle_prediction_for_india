"""Nepal binary model (decision D039): will the interbank rate fall, or rise, by more than 0.5 points?

Walk forward with real time refit over every origin: each model is fitted only on labels public
at the origin (four month embargo). Rows are tagged by evaluation period:
  train     label month up to October 2021, the period the design was chosen on (D038)
  post_hoc  label month November 2021 onwards and already public; the blind window, seen before
            this model was declared, so these scores are a second look, not a blind test
  sealed    outcome not yet public on 27 October 2026; forecasts are stored now and scored later

The script refuses to run unless configs/nepal_binary.yaml is frozen and matches its hash.

Outputs: reports/tables/nepal_binary_predictions.csv, nepal_binary_metrics.csv
Usage: python -m src.models.nepal_binary [--freeze]
"""

from __future__ import annotations

import hashlib
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score

from src.evaluation.metrics import block_bootstrap_ci
from src.models import walk_forward as wf
from src.models.nepal_target_search import panel

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs" / "nepal_binary.yaml"
HASH = ROOT / "configs" / "nepal_binary.sha256"
TABLES = ROOT / "reports" / "tables"
QUESTIONS = {"fall": -1, "rise": 1}


def config_hash() -> str:
    return hashlib.sha256(CONFIG.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def check_frozen() -> dict:
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    if cfg.get("status") != "frozen" or not HASH.exists() or HASH.read_text().split()[0] != config_hash():
        raise RuntimeError("configs/nepal_binary.yaml is not frozen or does not match configs/nepal_binary.sha256")
    return cfg


def fit_predict(tr: pd.DataFrame, te: pd.DataFrame, features: list[str], y: pd.Series, c: float) -> float:
    xtr, xte = wf.standardize(tr, te, features)
    if y.nunique() < 2:
        return float(y.iloc[0])
    m = LogisticRegression(C=c, max_iter=5000, class_weight="balanced").fit(xtr, y)
    return float(m.predict_proba(xte)[0, 1])


def run(cfg: dict) -> pd.DataFrame:
    d, _ = panel(cfg["information_lag_months"]["interbank"], "raw", cfg["horizon_months"],
                 last_label=pd.Period("2100-01", freq="M"), unlabelled=True)
    features, emb, c = cfg["features"], cfg["embargo_months"], 0.3
    train_last = pd.Period(cfg["training_last_label"], freq="M")
    sealed_after = pd.Period(cfg["sealed_after"][:7], freq="M")
    rows = []
    for i in range(cfg["min_train"] + emb, len(d)):
        te = d.iloc[[i]].copy()
        origin = te["period"].iloc[0]
        tr = d[(d["period"] <= origin - emb) & d["y"].notna()].copy()
        means = tr.groupby("month_of_year")["change"].mean()
        tr["calendar"] = tr["month_of_year"].map(means)
        te["calendar"] = te["month_of_year"].map(means).fillna(0.0)
        label_month = origin + cfg["horizon_months"]
        # the label is public once the interbank rate for its month is out (one month lag)
        period = ("train" if label_month <= train_last else
                  "sealed" if label_month + cfg["information_lag_months"]["interbank"] > sealed_after or
                  pd.isna(te["y"].iloc[0]) else "post_hoc")
        lab = tr.set_index("period")["y"]
        last = lab.get(origin - emb, np.nan)
        for q, k in QUESTIONS.items():
            yb = (tr["y"] == k).astype(int)
            rows.append({"origin": str(origin), "label_month": str(label_month), "period": period, "question": q,
                         "y": (np.nan if pd.isna(te["y"].iloc[0]) else int(te["y"].iloc[0] == k)),
                         "p_model": fit_predict(tr, te, features, yb, c),
                         "p_calendar": fit_predict(tr, te, ["calendar"], yb, c),
                         "persistence": (np.nan if pd.isna(last) else int(last == k))})
    return pd.DataFrame(rows)


def metrics(pred: pd.DataFrame) -> pd.DataFrame:
    out = []
    scored = pred.dropna(subset=["y"])
    for (period, q), g in scored.groupby(["period", "question"], sort=False):
        y = g["y"].astype(int).to_numpy()
        for name, yhat in [("model", (g["p_model"] >= 0.5).astype(int)),
                           ("calendar_only", (g["p_calendar"] >= 0.5).astype(int)),
                           ("persistence", g["persistence"].fillna(0).astype(int))]:
            yhat = np.asarray(yhat)
            lo, hi = block_bootstrap_ci(y, yhat)
            out.append({"period": period, "question": q, "benchmark": name, "n": len(y), "base_rate": y.mean(),
                        "accuracy": (yhat == y).mean(), "balanced_accuracy": balanced_accuracy_score(y, yhat),
                        "bal_acc_ci_low": lo, "bal_acc_ci_high": hi})
    return pd.DataFrame(out)


def main() -> int:
    if "--freeze" in sys.argv:
        HASH.write_text(f"{config_hash()}  configs/nepal_binary.yaml\n")
        print("frozen:", config_hash())
        return 0
    cfg = check_frozen()
    pred = run(cfg)
    table = metrics(pred)
    pred.round(4).to_csv(TABLES / "nepal_binary_predictions.csv", index=False)
    table.round(4).to_csv(TABLES / "nepal_binary_metrics.csv", index=False)
    print(table.round(3).to_string(index=False))
    print(pred[pred["period"] == "sealed"].round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
