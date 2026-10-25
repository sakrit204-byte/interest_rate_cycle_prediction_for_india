"""Nepal training target: seasonally adjusted three month change in the interbank rate (D027).

Seasonal factors are additive monthly effects estimated only from training data: the
deviation of the rate from its centred 2x12 moving average, averaged by calendar month over
months whose whole moving average window ends by the training cutoff, then centred to sum
to zero. The factors are frozen and applied unchanged to later months.

Label for month t: the change in the adjusted rate from t to t + HORIZON, coded down, flat
or up with a deadband of DEADBAND percentage points. The label is only known HORIZON months
later, which the walk forward respects through an embargo.

Output: data/interim/nepal/nepal_target_monthly.csv and
reports/tables/nepal_seasonal_factors.csv
Usage: python -m src.features.nepal_target
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "interim" / "nepal" / "nepal_interbank_monthly.csv"
CONFIG = ROOT / "configs" / "blind_test.yaml"
OUT = ROOT / "data" / "interim" / "nepal" / "nepal_target_monthly.csv"
FACTORS = ROOT / "reports" / "tables" / "nepal_seasonal_factors.csv"
HORIZON = 3
DEADBAND = 0.5  # declared before looking at class counts (D027)


def load_rate() -> pd.Series:
    s = pd.read_csv(SOURCE, index_col=0)["interbank_rate"]
    s.index = pd.PeriodIndex(s.index, freq="M")
    return s.asfreq("M")


def seasonal_factors(rate: pd.Series, cutoff: pd.Period) -> pd.Series:
    """Additive calendar month effects from data up to the cutoff only."""
    ma = rate.rolling(12, center=False).mean()
    centred = ((ma + ma.shift(-1)) / 2).shift(-5)  # 2x12 moving average centred on t
    # the centred average at t uses months up to t + 6; keep only those known by the cutoff
    dev = (rate - centred)[: cutoff - 6].dropna()
    effect = dev.groupby(dev.index.month).mean()
    return (effect - effect.mean()).rename("seasonal_effect")


def build() -> tuple[pd.DataFrame, pd.Series]:
    cfg = yaml.safe_load(CONFIG.read_text())
    cutoff = pd.Period(cfg["training_information_cutoff"][:7], freq="M")
    rate = load_rate()
    factors = seasonal_factors(rate, cutoff)
    adjusted = rate - rate.index.month.map(factors).to_numpy()
    change = adjusted.shift(-HORIZON) - adjusted
    label = pd.Series(np.select([change > DEADBAND, change < -DEADBAND], [1, -1], 0),
                      index=rate.index).where(change.notna())
    out = pd.DataFrame({"interbank_rate": rate, "interbank_adj": adjusted.round(4),
                        "change_3m_adj": change.round(4), "y": label})
    out["label_known_month"] = (out.index + HORIZON).astype(str)
    out["blind_window"] = (out.index + HORIZON) > cutoff  # outcome falls after the cutoff
    out.index.name = "month"
    return out, factors


def main() -> int:
    out, factors = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT)
    factors.round(4).to_csv(FACTORS, header=True)
    train = out[~out["blind_window"] & out["y"].notna()]
    print("seasonal effects (pp):", factors.round(2).to_dict())
    print(f"training months {len(train)}; classes {train['y'].value_counts().sort_index().to_dict()}")
    adj = out["interbank_adj"].diff().dropna()
    print(f"lag one autocorrelation of monthly change: raw {out['interbank_rate'].diff().autocorr():.2f}, "
          f"adjusted {adj.autocorr():.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
