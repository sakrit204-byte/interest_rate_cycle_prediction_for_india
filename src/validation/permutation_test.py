"""Label shift permutation test for the walk forward models (training period only).

Decisions come in runs, so plain shuffling would give a null that is too easy to beat. The
labels are instead shifted in a circle against the features by every offset from MIN_SHIFT
to n minus MIN_SHIFT, which keeps the run structure of the labels. Each shifted data set
goes through the same walk forward; the p value is the share of shifts whose balanced
accuracy (and log loss) is at least as good as the real one.

Output: reports/tables/permutation_test.csv
Usage: python -m src.validation.permutation_test [model ...]
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score

from src.evaluation.metrics import log_loss
from src.models import walk_forward as wf

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "tables" / "permutation_test.csv"
MIN_SHIFT = 10
DEFAULT_MODELS = ["ordered_probit_hybrid", "ordered_probit_taylor"]


def score(data: pd.DataFrame, name: str) -> tuple[float, float]:
    pred = wf.run(data, {name: wf.MODELS_PROJECTION[name]})
    proba = pred[["p_cut", "p_hold", "p_hike"]].to_numpy()
    return (balanced_accuracy_score(pred["y"], pred["pred"]),
            float(log_loss(pred["y"].to_numpy(), proba).mean()))


def main() -> int:
    names = sys.argv[1:] or DEFAULT_MODELS
    data = wf.load_training("complete_projection")
    n = len(data)
    rows = []
    for name in names:
        real_bacc, real_loss = score(data, name)
        null = []
        for shift in range(MIN_SHIFT, n - MIN_SHIFT + 1):
            shifted = data.copy()
            shifted["y"] = np.roll(data["y"].to_numpy(), shift)
            null.append(score(shifted, name))
        null = np.array(null)
        rows.append({
            "model": name, "n_decisions": n, "n_shifts": len(null),
            "balanced_accuracy": real_bacc, "null_bal_acc_mean": null[:, 0].mean(),
            "null_bal_acc_95th": np.percentile(null[:, 0], 95),
            "p_value_bal_acc": (1 + (null[:, 0] >= real_bacc).sum()) / (1 + len(null)),
            "log_loss": real_loss, "null_log_loss_mean": null[:, 1].mean(),
            "null_log_loss_5th": np.percentile(null[:, 1], 5),
            "p_value_log_loss": (1 + (null[:, 1] <= real_loss).sum()) / (1 + len(null)),
        })
        print(pd.DataFrame(rows[-1:]).round(3).to_string(index=False), flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).round(4).to_csv(OUT, index=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
