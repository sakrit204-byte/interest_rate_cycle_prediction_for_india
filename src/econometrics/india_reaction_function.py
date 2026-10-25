"""Estimated RBI reaction function: ordered probit in natural units on the training period.

Reads the walk forward hybrid specification (D025) as economics: how the probability of a
hike or cut responds to one percentage point more realized inflation, projected inflation,
industrial growth, and to the previous decision (interest rate smoothing). Estimated once on
all training decisions up to 31 October 2021; the blind window is not used.

Output: reports/tables/india_reaction_function_<spec>.csv
Usage: python -m src.econometrics.india_reaction_function [hybrid|economic]
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.miscmodels.ordinal_model import OrderedModel

from src.models.walk_forward import ECON_MODEL_FEATURES, HYBRID_FEATURES, load_training

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "tables" / "india_reaction_function.csv"
LABELS = {
    "infl": "Realized inflation, latest (pp)",
    "infl_change_3m": "Change in realized inflation over three months (pp)",
    "iip_yoy_3m": "Industrial production growth, three month average (pp)",
    "prev_decision": "Previous decision (cut -1, hold 0, hike 1)",
    "proj_infl": "RBI projected inflation (pp)",
    "proj_revision": "Latest revision to the projection (pp)",
    "infl_gap": "Realized inflation minus the regime nominal anchor (pp)",
    "proj_gap": "Projected inflation minus the regime nominal anchor (pp)",
    "growth_gap": "IIP growth minus its trailing five year mean (pp)",
    "inr_depr_3m": "Rupee depreciation against the US dollar over three months (percent)",
}
SPECS = {"hybrid": HYBRID_FEATURES, "economic": ECON_MODEL_FEATURES}


def average_marginal_effects(res, x: np.ndarray, step: float = 1.0) -> np.ndarray:
    """Change in P(cut), P(hike) when one variable rises by `step`, averaged over decisions."""
    base = np.asarray(res.model.predict(res.params, exog=x))
    out = []
    for j in range(x.shape[1]):
        bumped = x.copy()
        bumped[:, j] += step
        p = np.asarray(res.model.predict(res.params, exog=bumped))
        out.append([(p[:, 0] - base[:, 0]).mean(), (p[:, 2] - base[:, 2]).mean()])
    return np.array(out)


def main() -> int:
    spec = sys.argv[1] if len(sys.argv) > 1 else "economic"
    features = SPECS[spec]
    data = load_training("complete_econ")
    x = data[features].to_numpy(float)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = OrderedModel(data["y"].to_numpy(), x, distr="probit").fit(method="bfgs", disp=False, maxiter=5000)
    k = len(features)
    ame = average_marginal_effects(res, x)
    table = pd.DataFrame({
        "spec": spec, "variable": features,
        "meaning": [LABELS[v] for v in features],
        "coefficient": res.params[:k], "std_error": res.bse[:k], "z": res.tvalues[:k], "p_value": res.pvalues[:k],
        "ame_p_cut_pp": ame[:, 0] * 100, "ame_p_hike_pp": ame[:, 1] * 100,
    })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    table.round(4).to_csv(OUT.with_name(f"india_reaction_function_{spec}.csv"), index=False)
    print(f"n = {len(data)} decisions ({data['date'].min().date()} to {data['date'].max().date()}); "
          f"pseudo R2 = {res.prsquared:.3f}")
    print(table.drop(columns="meaning").round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
