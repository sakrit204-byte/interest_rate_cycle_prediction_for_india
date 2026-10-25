"""Stability of what the models learn and of their accuracy across years (training period only).

Three checks, all on walk forward output that never saw the blind window:

1. Accuracy by multi year block: does the model beat persistence in most blocks, or only in
   the pooled number? India blocks are three calendar years (about 18 decisions each);
   Nepal blocks are three years of months.
2. Coefficient stability: the ordered probit is refit at every walk forward origin and the
   share of windows in which each coefficient keeps its full sample sign is reported. A
   learned relationship is called stable only if its sign holds in at least 80 percent of
   windows.
3. Reproducibility: SHA256 of the feature tables and prediction files. Rerunning the
   pipeline from the same raw files must give the same hashes (checked with --check).

Outputs: reports/tables/stability_accuracy_by_block.csv, stability_coefficients.csv,
reproducibility_hashes.csv
Usage: python -m src.validation.stability [--check]
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.miscmodels.ordinal_model import OrderedModel

from src.evaluation.metrics import summary
from src.features.build_nepal_features import LIQUIDITY_MODEL_FEATURES, OUT as NEPAL_FEATURES
from src.models import walk_forward as wf
from src.models import walk_forward_nepal as wfn

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "reports" / "tables"
BLOCK_YEARS = 3
SIGN_STABLE = 0.8
PAIRS = {  # (prediction file, model, benchmark)
    "india": ("walk_forward_train_econ_predictions.csv", "ordered_probit_economic", "persistence"),
    "nepal": ("nepal_walk_forward_train_liquidity_predictions.csv", "ordered_probit_liquidity", "persistence"),
}
HASHED = [wf.FEATURE_FILE, NEPAL_FEATURES] + [TABLES / f for f, _, _ in PAIRS.values()]


def accuracy_by_block() -> pd.DataFrame:
    rows = []
    for country, (fname, model, bench) in PAIRS.items():
        p = pd.read_csv(TABLES / fname)
        year = pd.to_datetime(p["date"]).dt.year
        start = year.min()
        p["block"] = [f"{start + (y - start) // BLOCK_YEARS * BLOCK_YEARS}-{start + (y - start) // BLOCK_YEARS * BLOCK_YEARS + BLOCK_YEARS - 1}"
                      for y in year]
        for block, g in p.groupby("block"):
            r = {"country": country, "block": block}
            for role, name in (("model", model), ("benchmark", bench)):
                h = g[g["model"] == name]
                s = summary(h["y"].to_numpy(), h["pred"].to_numpy(), h[["p_cut", "p_hold", "p_hike"]].to_numpy())
                r.update({"n": len(h), f"{role}_bal_acc": s["balanced_accuracy"], f"{role}_brier": s["brier"]})
            r["model_better_bal_acc"] = r["model_bal_acc"] > r["benchmark_bal_acc"]
            r["model_better_brier"] = r["model_brier"] < r["benchmark_brier"]
            rows.append(r)
    return pd.DataFrame(rows)


def coefficients(data: pd.DataFrame, features: list[str], min_train: int, embargo) -> pd.DataFrame:
    """Standardised ordered probit coefficients at every walk forward origin plus the full sample."""
    def fit(tr):
        xtr, _ = wf.standardize(tr, tr.iloc[[0]], features)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            res = OrderedModel(tr["y"].to_numpy(), xtr, distr="probit").fit(method="bfgs", disp=False, maxiter=2000)
        return pd.Series(np.asarray(res.params)[: len(features)], index=features)
    windows = []
    for i in range(min_train + (embargo if isinstance(embargo, int) else 0), len(data)):
        tr = embargo_rows(data, i, embargo)
        if tr[features].std().gt(0).all():
            windows.append(fit(tr))
    w, full = pd.DataFrame(windows), fit(data)
    out = pd.DataFrame({"full_sample_coef": full, "windows": len(w),
                        "share_same_sign": (np.sign(w) == np.sign(full)).mean(),
                        "coef_min": w.min(), "coef_median": w.median(), "coef_max": w.max()})
    out["stable"] = out["share_same_sign"] >= SIGN_STABLE
    return out.rename_axis("feature").reset_index()


def embargo_rows(data, i, embargo):
    if embargo == "india":  # outcomes known by the cutoff (same rule as the India walk forward)
        tr = data.iloc[:i]
        return tr[tr["date"] <= data["cutoff"].iloc[i]]
    return data[data["period"] <= data["period"].iloc[i] - embargo]


def hashes() -> pd.DataFrame:
    return pd.DataFrame([{"file": p.relative_to(ROOT).as_posix(),
                          "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in HASHED])


def check() -> int:
    """Rebuild features and rerun both walk forwards, then compare hashes with the stored ones."""
    before = pd.read_csv(TABLES / "reproducibility_hashes.csv")
    py = sys.executable
    for args in (["src.features.build_india_features"], ["src.features.build_nepal_features"],
                 ["src.models.walk_forward", "--econ"], ["src.models.walk_forward_nepal", "--liquidity"]):
        subprocess.run([py, "-m", *args], cwd=ROOT, check=True, capture_output=True)
    after = hashes()
    same = before.merge(after, on="file", suffixes=("_stored", "_rerun"))
    same["identical"] = same["sha256_stored"] == same["sha256_rerun"]
    print(same[["file", "identical"]].to_string(index=False))
    return 0 if same["identical"].all() else 1


def main() -> int:
    if "--check" in sys.argv:
        return check()
    blocks = accuracy_by_block()
    india = wf.load_training("complete_econ")
    nepal = wfn.load_training("complete_liquidity")
    coefs = pd.concat([
        coefficients(india, wf.ECON_MODEL_FEATURES, wf.MIN_TRAIN, "india").assign(country="india"),
        coefficients(nepal, LIQUIDITY_MODEL_FEATURES, wfn.MIN_TRAIN, wfn.EMBARGO).assign(country="nepal"),
    ])
    TABLES.mkdir(parents=True, exist_ok=True)
    blocks.round(4).to_csv(TABLES / "stability_accuracy_by_block.csv", index=False)
    coefs.round(4).to_csv(TABLES / "stability_coefficients.csv", index=False)
    hashes().to_csv(TABLES / "reproducibility_hashes.csv", index=False)
    print(blocks.round(3).to_string(index=False))
    print(coefs.round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
