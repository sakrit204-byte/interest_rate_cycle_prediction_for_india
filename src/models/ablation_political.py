"""Political event ablation on the training period (Step 8, H2, D034).

Each primary model is run with and without the political indicators in the same walk
forward; the Diebold Mariano test on log loss answers whether events add predictive value.

Outputs: reports/tables/ablation_political_metrics.csv, ablation_political_dm.csv
Usage: python -m src.models.ablation_political
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from src.events import political_features as pf
from src.features.build_nepal_features import LIQUIDITY_MODEL_FEATURES
from src.features.nepal_target import HORIZON
from src.models import walk_forward as wf
from src.models import walk_forward_nepal as wfn

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "reports" / "tables"
INDIA_EVENTS = ["election_pending", "budget_since_last"]
NEPAL_EVENTS = ["gov_change_6m", "disruption_3m"]


def india() -> tuple[pd.DataFrame, pd.DataFrame]:
    data = wf.load_training("complete_econ")
    prev = data["date"].shift(1)
    data = data.join(pf.india(data["date"], data["cutoff"], prev))
    models = {"ordered_probit_economic": lambda tr, te: wf.ordered_probit(tr, te, wf.ECON_MODEL_FEATURES),
              "ordered_probit_economic_events": lambda tr, te: wf.ordered_probit(tr, te, wf.ECON_MODEL_FEATURES + INDIA_EVENTS)}
    pred = wf.run(data, models)
    print("india event counts:", data[INDIA_EVENTS].sum().to_dict(), "of", len(data))
    return pred.assign(country="india"), wf.dm_table(pred, [("ordered_probit_economic_events", "ordered_probit_economic")])


def nepal() -> tuple[pd.DataFrame, pd.DataFrame]:
    data = wfn.load_training("complete_liquidity")
    data = data.join(pf.nepal(pd.to_datetime(data["origin"])))
    models = {"ordered_probit_liquidity": lambda tr, te: wf.ordered_probit(tr, te, LIQUIDITY_MODEL_FEATURES),
              "ordered_probit_liquidity_events": lambda tr, te: wf.ordered_probit(tr, te, LIQUIDITY_MODEL_FEATURES + NEPAL_EVENTS)}
    pred = wfn.run(data, models)
    print("nepal event months:", (data[NEPAL_EVENTS] > 0).sum().to_dict(), "of", len(data))
    return pred.assign(country="nepal"), wf.dm_table(pred, [("ordered_probit_liquidity_events", "ordered_probit_liquidity")],
                                                     horizon=HORIZON)


def main() -> int:
    preds, dms = zip(india(), nepal())
    pred = pd.concat(preds)
    table = wf.metrics_table(pred)
    dm = pd.concat(dms)
    TABLES.mkdir(parents=True, exist_ok=True)
    table.round(4).to_csv(TABLES / "ablation_political_metrics.csv", index=False)
    dm.round(4).to_csv(TABLES / "ablation_political_dm.csv", index=False)
    print(table[["model", "n", "balanced_accuracy", "macro_f1", "log_loss", "brier"]].round(3).to_string(index=False))
    print(dm.round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
