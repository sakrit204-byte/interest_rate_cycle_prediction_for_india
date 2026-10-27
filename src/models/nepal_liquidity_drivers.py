"""Direct liquidity drivers from the NRB tables in the Nepal binary model (decision D044).

Training period only. Five features, each a three month sum to month t minus 2 divided by broad
money at t minus 2, in percent (see the decision log for the economics). The D039 baseline and
the model with the drivers are fitted on the same months, those where all five are reported,
with the same walk forward, embargo and calendar effect as nepal_strategy.

Outputs: reports/tables/nepal_liquidity_drivers_train.csv
Usage: python -m src.models.nepal_liquidity_drivers
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
from src.features.build_nepal_features import imf_series
from src.models.nepal_binary import CONFIG, QUESTIONS
from src.models.nepal_strategy import prob
from src.models.nepal_target_search import panel

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
CME = ROOT / "data" / "interim" / "nepal" / "nrb_cme_monthly.csv"
OUT = ROOT / "reports" / "tables" / "nepal_liquidity_drivers_train.csv"
LAG = 2
DRIVERS = ["remit_3m", "fx_purchase_3m", "nrb_net_absorption_3m", "fiscal_injection_3m", "interbank_volume_3m"]


def drivers() -> pd.DataFrame:
    c = pd.read_csv(CME, index_col=0)
    c.index = pd.PeriodIndex(c.index, freq="M")
    c = c.reindex(pd.period_range(c.index.min(), c.index.max(), freq="M"))
    bm = imf_series("MFS_DC_npl_depository", lambda d: (d["INDICATOR"] == "DCORP_L_BM") &
                    (d["TYPE_OF_TRANSFORMATION"] == "XDC")).reindex(c.index)
    flows = pd.DataFrame({
        "remit_3m": c["workers_remittances_flow"],
        "fx_purchase_3m": c["nrb_fx_net_purchase"],
        "nrb_net_absorption_3m": c["nrb_liquidity_absorption"] - c["nrb_liquidity_injection"],
        "fiscal_injection_3m": c["gov_expenditure_total_flow"] - c["gov_revenue_total_flow"],
        "interbank_volume_3m": c["interbank_volume"],
    })
    # min_periods=3: a sum is formed only when all three months are reported, never from a gap
    return flows.rolling(3, min_periods=3).sum().div(bm, axis=0).mul(100)


def main() -> int:
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    d, _ = panel(cfg["information_lag_months"]["interbank"], "raw", cfg["horizon_months"],
                 last_label=pd.Period(cfg["training_last_label"], freq="M"))
    dr = drivers()
    d = d.join(pd.DataFrame([dr.loc[p - LAG].to_dict() if (p - LAG) in dr.index else {} for p in d["period"]],
                            index=d.index, columns=DRIVERS))
    d = d.dropna(subset=DRIVERS).reset_index(drop=True)
    print(f"months with all drivers: {len(d)} ({d['period'].iloc[0]} to {d['period'].iloc[-1]})")
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
            rows.append({"origin": str(te["period"].iloc[0]), "question": q, "y": int(te["y"].iloc[0] == k),
                         "baseline": prob(tr, te, base, y), "drivers": prob(tr, te, base + DRIVERS, y)})
    pred = pd.DataFrame(rows)
    out = []
    for q, g in pred.groupby("question", sort=False):
        yv = g["y"].to_numpy()
        sq = {m: (g[m].to_numpy() - yv) ** 2 for m in ("baseline", "drivers")}
        _, p = diebold_mariano(sq["drivers"], sq["baseline"], cfg["horizon_months"])
        for m in ("baseline", "drivers"):
            yhat = (g[m] >= 0.5).astype(int).to_numpy()
            lo, hi = block_bootstrap_ci(yv, yhat)
            out.append({"question": q, "model": m, "n": len(g), "first_origin": g["origin"].iloc[0],
                        "balanced_accuracy": balanced_accuracy_score(yv, yhat), "bal_acc_ci_low": lo,
                        "bal_acc_ci_high": hi, "brier": brier_score_loss(yv, g[m]),
                        "dm_p_value_brier": p if m == "drivers" else np.nan})
    table = pd.DataFrame(out).round(4)
    table.to_csv(OUT, index=False)
    print(table.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
