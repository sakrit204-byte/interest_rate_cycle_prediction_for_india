"""Confirmatory blind test (Step 11). Refuses to run unless configs/blind_test.yaml is frozen
and its SHA256 matches configs/blind_test.sha256 (research protocol, D033).

Every model is the frozen specification, refit in real time at each origin on outcomes public
by then; nothing is retuned on blind window results. Metrics are computed on blind window
decisions (India) and months (Nepal) only.

Outputs (reports/tables): blind_india_predictions.csv, blind_india_metrics.csv, blind_india_dm.csv,
blind_nepal_predictions.csv, blind_nepal_metrics.csv, blind_nepal_dm.csv, blind_turning_points.csv,
suggestions_blind.csv, suggestions_blind_agreement.csv
Usage: python -m src.validation.blind_test
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from src.features.build_nepal_features import OUT as NEPAL_FILE
from src.features.nepal_target import HORIZON
from src.models import walk_forward as wf
from src.models import walk_forward_nepal as wfn
from src.policy import suggestion_engine as se

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "reports" / "tables"
INDIA_MODELS = {
    "majority": wf.majority,
    "persistence": wf.persistence,
    "ordered_probit_taylor": lambda tr, te: wf.ordered_probit(tr, te, wf.TAYLOR_FEATURES),
    "ordered_probit_hybrid": lambda tr, te: wf.ordered_probit(tr, te, wf.HYBRID_FEATURES),
    "ordered_probit_economic": lambda tr, te: wf.ordered_probit(tr, te, wf.ECON_MODEL_FEATURES),
    "random_forest": wf.random_forest,
}


def india() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    f = pd.read_csv(wf.FEATURE_FILE, parse_dates=["date", "cutoff"])
    data = f[f["complete_econ"]].reset_index(drop=True)
    pred = wf.run(data, INDIA_MODELS)
    pred = pred[pd.to_datetime(pred["date"]) >= se.config()["blind_start"]]
    dm = wf.dm_table(pred, [("ordered_probit_economic", "persistence"), ("ordered_probit_economic", "majority"),
                            ("random_forest", "ordered_probit_economic"),
                            ("ordered_probit_economic", "ordered_probit_hybrid")])
    return pred, wf.metrics_table(pred), dm


def nepal() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    f = pd.read_csv(NEPAL_FILE)
    data = f[f["complete_liquidity"]].reset_index(drop=True)
    data["period"] = pd.PeriodIndex(data["month"], freq="M")
    data["y"] = data["y"].astype(int)
    known = pd.Series(data["y"].values, index=data["period"])
    data["prev_decision"] = [known.get(p - wfn.EMBARGO, np.nan) for p in data["period"]]
    pred = wfn.run(data, wfn.MODELS_LIQUIDITY)
    blind = set(data.loc[data["blind_window"], "month"])
    pred = pred[pred["date"].isin(blind)]
    dm = wf.dm_table(pred, [("ordered_probit_liquidity", "ordered_probit_liquidity_no_india"),
                            ("ordered_probit_liquidity", "persistence"), ("ordered_probit_liquidity", "majority"),
                            ("random_forest_liquidity", "ordered_probit_liquidity")], horizon=HORIZON)
    return pred, wf.metrics_table(pred), dm


def turning_points(s: pd.DataFrame, source: str = "suggestion") -> pd.DataFrame:
    """For each actual change of cycle (first hike after cuts, first cut after hikes), how many
    decisions earlier (negative) or later (positive) the source first called the new direction."""
    rows, last, prev_tp = [], None, 0
    acts = s["actual"].tolist()
    for i, a in enumerate(acts):
        if a in ("hike", "cut") and a != last:
            if last is not None:
                window = s.iloc[prev_tp:].reset_index(drop=True)
                hits = [j for j, v in enumerate(window[source]) if v == a]
                lag = (prev_tp + hits[0] - i) if hits else np.nan
                rows.append({"date": s["date"].iloc[i], "new_direction": a, "source": source, "lag_decisions": lag})
            last, prev_tp = a, i
    return pd.DataFrame(rows)


def main() -> int:
    se.check_frozen()
    TABLES.mkdir(parents=True, exist_ok=True)
    for name, fn in (("india", india), ("nepal", nepal)):
        pred, table, dm = fn()
        pred.round(4).to_csv(TABLES / f"blind_{name}_predictions.csv", index=False)
        table.round(4).to_csv(TABLES / f"blind_{name}_metrics.csv", index=False)
        dm.round(4).to_csv(TABLES / f"blind_{name}_dm.csv", index=False)
        print(name, "\n", table.round(3).to_string(index=False), "\n", dm.round(3).to_string(index=False))
    cfg = se.config()
    s = se.run(se.load(unblind=True), cfg)
    s = s[s["blind_window"]].reset_index(drop=True)
    s.round(4).to_csv(TABLES / "suggestions_blind.csv", index=False)
    a = se.agreement(s)
    a.round(4).to_csv(TABLES / "suggestions_blind_agreement.csv", index=False)
    tp = pd.concat([turning_points(s, c) for c in ("classifier", "rule", "taylor", "suggestion")])
    tp.to_csv(TABLES / "blind_turning_points.csv", index=False)
    print(a.round(3).to_string(index=False), "\n", tp.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
