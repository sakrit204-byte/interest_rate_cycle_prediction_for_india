"""How the peg to the Indian rupee shows in Nepal's prices and interest rates (decision D052).

Descriptive, not a forecast and not a test. It puts side by side the two channels the peg
theory predicts, using the same monthly panel as the local projections (D032):

* prices: with the rupee fixed at 1.6 and two thirds of imports from India, Nepal's inflation
  should track India's. Measured by the correlation of the two inflation rates (India WPI before
  2014, CPI after, as in D032), at lags of 0 to 24 months, by the same correlation with India's
  CPI only (from 2013), and by the mean gap.
* interest rates: with a closed capital account the peg need not carry India's policy rate.
  Measured by the correlation of 12 month changes in the RBI repo rate and in Nepal's interbank
  and 91 day treasury bill rates.

Each is reported for the whole sample and for three periods: before the NRB corridor
(to mid 2016), corridor years before the blind window, and the blind window.

Outputs: reports/tables/peg_channels.csv, reports/figures/peg_channels.png and .svg
Usage: python -m src.econometrics.peg_channels
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.econometrics.local_projections import monthly_panel

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "reports" / "tables"
FIGURE = ROOT / "reports" / "figures" / "peg_channels"
PERIODS = {"2001 to 2026": ("2001-01", "2026-07"), "before corridor, 2001 to 2016": ("2001-01", "2016-07"),
           "corridor, 2016 to 2021": ("2016-08", "2021-10"), "blind window, 2021 to 2026": ("2021-11", "2026-07")}
LAGS = (0, 3, 6, 12, 24)
INK, SECONDARY, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"
INDIA, NEPAL, NEPAL2 = "#eb6834", "#2a78d6", "#1baf7a"


def panel() -> pd.DataFrame:
    p = monthly_panel()
    p["repo_change_12m"] = p["repo"] - p["repo"].shift(12)
    p["interbank_change_12m"] = p["interbank_rate"] - p["interbank_rate"].shift(12)
    p["tbill_change_12m"] = p["tbill_91d"] - p["tbill_91d"].shift(12)
    macro = pd.read_csv(ROOT / "data" / "interim" / "india" / "india_macro_monthly.csv", index_col="month")
    macro.index = pd.PeriodIndex(macro.index, freq="M")
    p["india_cpi"] = macro["cpi_yoy"]  # CPI on both sides, from 2013 (India's combined CPI starts 2012)
    return p


def table(p: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, (a, b) in PERIODS.items():
        s = p.loc[pd.Period(a, freq="M"):pd.Period(b, freq="M")]
        row = {"period": name, "months": int(s[["india_infl", "nepal_cpi_yoy"]].dropna().shape[0]),
               "india_inflation_mean": s["india_infl"].mean(), "nepal_inflation_mean": s["nepal_cpi_yoy"].mean()}
        for lag in LAGS:  # India leading Nepal by lag months; the lag reaches back before the period start
            row[f"inflation_corr_lag{lag}"] = s["nepal_cpi_yoy"].corr(p["india_infl"].shift(lag).reindex(s.index))
        row["inflation_corr_cpi_only"] = s["nepal_cpi_yoy"].corr(s["india_cpi"].where(s.index >= pd.Period("2013-01", freq="M")))
        row["interbank_vs_repo_corr_12m_change"] = s["interbank_change_12m"].corr(s["repo_change_12m"])
        row["tbill_vs_repo_corr_12m_change"] = s["tbill_change_12m"].corr(s["repo_change_12m"])
        row["interbank_minus_repo_mean"] = (s["interbank_rate"] - s["repo"]).mean()
        rows.append(row)
    return pd.DataFrame(rows)


def chart(p: pd.DataFrame) -> None:
    s = p.loc[pd.Period("2001-01", freq="M"):pd.Period("2026-07", freq="M")]
    x = s.index.to_timestamp()
    fig, (top, bot) = plt.subplots(2, 1, figsize=(10, 7), sharex=True, facecolor=SURFACE)
    top.plot(x, s["india_infl"], color=INDIA, linewidth=2)
    top.plot(x, s["nepal_cpi_yoy"], color=NEPAL, linewidth=2)
    top.set_title("Prices move together: inflation, percent over 12 months", loc="left", fontsize=11, color=INK)
    bot.step(x, s["repo"], where="post", color=INDIA, linewidth=2)
    bot.plot(x, s["interbank_rate"], color=NEPAL, linewidth=1.6)
    bot.plot(x, s["tbill_91d"], color=NEPAL2, linewidth=1.6)
    bot.set_title("Interest rates do not: RBI repo rate and Nepal's short rates, percent", loc="left",
                  fontsize=11, color=INK)
    for ax, series in ((top, {"India": ("india_infl", INDIA), "Nepal": ("nepal_cpi_yoy", NEPAL)}),
                       (bot, {"RBI repo": ("repo", INDIA), "Nepal interbank": ("interbank_rate", NEPAL),
                              "Nepal 91 day T bill": ("tbill_91d", NEPAL2)})):
        for label, (col, color) in series.items():
            last = s[col].dropna()
            nudge = {"Nepal interbank": 0.4, "Nepal 91 day T bill": -0.4, "India": 0.3, "Nepal": -0.3}.get(label, 0)
            ax.text(last.index[-1].to_timestamp(), last.iloc[-1] + nudge, f" {label}", va="center", fontsize=8,
                    color=color)
        ax.set_facecolor(SURFACE)
        ax.grid(axis="y", color=GRID, linewidth=0.6)
        ax.tick_params(colors=SECONDARY, labelsize=8)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(GRID)
    top.axhline(0, color=MUTED, linewidth=0.8)
    fig.text(0.01, 0.005, "India inflation: WPI before 2014, CPI after. Sources: IMF CPI and MFS, BIS policy rates, "
             "NRB, MOSPI.", fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.02, 0.9, 1))
    FIGURE.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(FIGURE.with_suffix(f".{ext}"), dpi=200, facecolor=SURFACE)
    plt.close(fig)


def main() -> int:
    p = panel()
    t = table(p).round(3)
    t.to_csv(TABLES / "peg_channels.csv", index=False)
    chart(p)
    pd.set_option("display.width", 250)
    print(t.T.to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
