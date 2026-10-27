"""How predictable is the Nepal interbank rate under different target designs? (decision D038)

Training period only, same walk forward and embargo logic as walk_forward_nepal, one model
(ordered probit on the liquidity and corridor features, prior corrected decision rule, the best
row of nepal_candidates_train). Every design tried is written out.

Design choices varied:
  lag      months between the interbank observation used and the origin month. D028 uses two
           (the bulletin table); banks trade at the rate daily, so one month is what a market
           participant knows
  target   adj: seasonally adjusted change (D027); raw: change in the published rate, with the
           point in time calendar effect (mean raw change for that origin month in the training
           window) added as a feature, since the fiscal year liquidity cycle is economics too
  horizon  months ahead, 1 or 3

Liquidity aggregates from the IMF monetary surveys stay at a two month lag throughout.

Output: reports/tables/nepal_target_search_train.csv
Usage: python -m src.models.nepal_target_search
"""

from __future__ import annotations

import sys
import warnings
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score

from src.features.build_nepal_features import LIQUIDITY_FEATURES, OUT as FEATURE_FILE, imf_series
from src.features.nepal_target import DEADBAND
from src.models import walk_forward as wf
from src.models.nepal_candidates import RATES

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "data" / "interim" / "nepal" / "nepal_target_monthly.csv"
OUT = ROOT / "reports" / "tables" / "nepal_target_search_train.csv"
LAST_TRAIN_LABEL = pd.Period("2021-10", freq="M")
MIN_TRAIN = 60


def panel(lag: int, target: str, horizon: int,
          last_label: pd.Period = LAST_TRAIN_LABEL, unlabelled: bool = False) -> tuple[pd.DataFrame, list[str]]:
    """Point in time panel; with unlabelled, origins whose outcome is not yet public are kept with y missing."""
    t = pd.read_csv(TARGET, index_col=0)
    t.index = pd.PeriodIndex(t.index, freq="M")
    series = t["interbank_adj"] if target == "adj" else t["interbank_rate"]
    raw = t["interbank_rate"]
    change = series.shift(-horizon) - series
    f = pd.read_csv(FEATURE_FILE)
    f.index = pd.PeriodIndex(f["month"], freq="M")
    r = {k: imf_series("MFS_IR_npl_interest_rates", lambda d, c=c: d["INDICATOR"] == c) for k, c in RATES.items()}
    rows = []
    for p in t.index:
        ib, c = raw.get(p - lag, np.nan), p - 1
        rows.append({"period": p, "change": change.get(p, np.nan), "month_of_year": p.month,
                     "level": series.get(p - lag, np.nan),
                     "momentum": series.get(p - lag, np.nan) - series.get(p - lag - 3, np.nan),
                     "ib_minus_floor": ib - r["floor"].get(c, np.nan),
                     "ceiling_minus_ib": r["ceiling"].get(c, np.nan) - ib,
                     # the realised change already visible at the origin, used for the calendar effect
                     "past_change": series.get(p - lag, np.nan) - series.get(p - lag - horizon, np.nan),
                     **{k: (f.at[p, k] if p in f.index else np.nan)
                        for k in LIQUIDITY_FEATURES + ["nrb_bank_rate_change_6m", "india_repo_change_3m"]}})
    d = pd.DataFrame(rows)
    d["y"] = np.select([d["change"] > DEADBAND, d["change"] < -DEADBAND], [1, -1], 0)
    d.loc[d["change"].isna(), "y"] = np.nan
    feats = ["level", "momentum", "ib_minus_floor", "ceiling_minus_ib", "nrb_bank_rate_change_6m",
             "india_repo_change_3m"] + LIQUIDITY_FEATURES
    d = d[(d["period"] + horizon) <= last_label].dropna(subset=feats + ([] if unlabelled else ["y"]))
    d = d.reset_index(drop=True)
    if not unlabelled:
        d["y"] = d["y"].astype(int)
    return d, feats


def run(lag: int, target: str, horizon: int) -> dict:
    d, feats = panel(lag, target, horizon)
    embargo = horizon + lag
    if target == "raw":
        feats = feats + ["calendar"]
    rows = []
    for i in range(MIN_TRAIN + embargo, len(d)):
        te = d.iloc[i].copy()
        tr = d[d["period"] <= te["period"] - embargo].copy()
        if target == "raw":
            means = tr.groupby("month_of_year")["change"].mean()
            tr["calendar"] = tr["month_of_year"].map(means)
            te["calendar"] = means.get(te["month_of_year"], 0.0)
        p = np.asarray(wf.ordered_probit(tr, te, feats), float)
        p = p / p.sum()
        prior = wf.freq(tr["y"].to_numpy())
        rows.append({"y": te["y"], "pred": int(wf.CLASSES[np.argmax(p / prior)]), "p": p})
    g = pd.DataFrame(rows)
    y, yhat = g["y"].to_numpy(), g["pred"].to_numpy()
    lo, hi = wf.block_bootstrap_ci(y, yhat)
    # persistence benchmark: the last label already public at the origin
    lab = d.set_index("period")["y"]
    pers = [lab.get(p - embargo, np.nan) for p in d["period"].iloc[MIN_TRAIN + embargo:]]
    pers = np.nan_to_num(np.asarray(pers, float), nan=0).astype(int)
    return {"lag": lag, "target": target, "horizon": horizon, "n": len(g),
            "classes_down_flat_up": "/".join(str((y == k).sum()) for k in (-1, 0, 1)),
            "accuracy": (yhat == y).mean(), "balanced_accuracy": balanced_accuracy_score(y, yhat),
            "bal_acc_ci_low": lo, "bal_acc_ci_high": hi,
            "log_loss": wf.log_loss(y, np.vstack(g["p"])).mean(),
            "persistence_bal_acc": balanced_accuracy_score(y, pers)}


def main() -> int:
    out = [run(*k) for k in product((2, 1), ("adj", "raw"), (3, 1))]
    table = pd.DataFrame(out).round(4)
    table.to_csv(OUT, index=False)
    print(table.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
