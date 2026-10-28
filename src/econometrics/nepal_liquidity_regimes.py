"""Descriptive account of Nepal's corridor regimes, mid August 2019 to mid July 2026 (decision D049).

Not a forecast and not a test: it shows which liquidity flows were large when the interbank
rate sat at the floor or the ceiling of the NRB corridor. Each month is classified by a rule
fixed before looking at the flows (as in D041): floor when the interbank rate is less than 0.5
points above the corridor floor (DISR), ceiling when it is less than 0.5 points below the
ceiling (bank rate, MFS166), inside otherwise. Consecutive months in the same class form one
episode.

Flows, each in percent of broad money at the end of the previous month, monthly:
  fx_net          NRB purchase minus sale of foreign currency (NRB database), the rupee
                  liquidity created when remittance and other inflows are converted at the peg
  remittances     workers' remittances (CME tables)
  fiscal_net      government expenditure minus revenue, FCGO basis (CME tables, from 2019/20):
                  positive spends money into bank deposits, negative pulls it into the treasury
  credit_growth   private sector credit growth over 12 months (IMF MFS_ODC), the demand for
                  liquidity
  deposit_growth  deposit growth over 12 months (IMF MFS_ODC)
  excess_reserves balance of banks at the NRB minus the cash reserve requirement, monthly
                  average of daily values, in percent of deposits (NRB database)
  nrb_net_absorbing  share of months in which NRB absorption exceeded injection; a share
                  rather than an amount, because overnight operations are reported as gross
                  turnover and their sums are not comparable with the other flows

Outputs: reports/tables/nepal_liquidity_regimes.csv (episodes),
         reports/tables/nepal_liquidity_fiscal_years.csv (fiscal years),
         reports/figures/nepal_liquidity_regimes.png and .svg
Usage: python -m src.econometrics.nepal_liquidity_regimes
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.features.build_nepal_features import MFS, imf_series

ROOT = Path(__file__).resolve().parents[2]
INTERIM = ROOT / "data" / "interim" / "nepal"
TABLES = ROOT / "reports" / "tables"
FIGURE = ROOT / "reports" / "figures" / "nepal_liquidity_regimes"
START, END = pd.Period("2019-08", freq="M"), pd.Period("2026-07", freq="M")
BAND = 0.5
FLOWS = ["fx_net", "remittances", "fiscal_net"]
INK, SECONDARY, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"
SERIES = {"fx_net": "#2a78d6", "remittances": "#eb6834", "fiscal_net": "#1baf7a"}
SHADE = {"floor": "#cde2fb", "ceiling": "#fbd9cc"}


def _monthly(path: Path) -> pd.DataFrame:
    d = pd.read_csv(path, index_col=0)
    d.index = pd.PeriodIndex(d.index, freq="M")
    return d


def frame() -> pd.DataFrame:
    db, cme = _monthly(INTERIM / "nrb_database_monthly.csv"), _monthly(INTERIM / "nrb_cme_monthly.csv")
    imf = {k: imf_series(f"{f}_npl", lambda d, c=c: (d["INDICATOR"] == c) & (d["TYPE_OF_TRANSFORMATION"] == "XDC"))
           for k, (f, c) in MFS.items()}
    floor = imf_series("MFS_IR_npl_interest_rates", lambda d: d["INDICATOR"] == "DISR_RT_PT_A_PT")
    ceiling = imf_series("MFS_IR_npl_interest_rates", lambda d: d["INDICATOR"] == "MFS166_RT_PT_A_PT")
    idx = pd.period_range(START - 12, END, freq="M")
    bm = imf["broad_money"].reindex(idx).shift(1) / 1e6  # IMF in rupees, NRB flows in million rupees
    deposits = (imf["transferable_deposits"] + imf["other_deposits"]).reindex(idx) / 1e6
    m = pd.DataFrame(index=idx)
    m["interbank"], m["floor"], m["ceiling"] = db["ib_rate_cb"], floor, ceiling
    m["fx_net"] = (db["fx_purchase"] - db["fx_sale"]) / bm * 100
    m["remittances"] = cme["workers_remittances_flow"] / bm * 100
    m["fiscal_net"] = (cme["gov_expenditure_total_fcgo_flow"] - cme["gov_revenue_total_fcgo_flow"]) / bm * 100
    m["credit_growth"] = (imf["private_credit"] / imf["private_credit"].shift(12) - 1).reindex(idx) * 100
    m["deposit_growth"] = (deposits / deposits.shift(12) - 1) * 100
    m["excess_reserves"] = db["excess_reserves_avg"] / deposits * 100
    m["nrb_net_absorbing"] = (db["omo_absorption"] > db["omo_injection"]).astype(float).where(db["omo_absorption"].notna())
    m["regime"] = "inside"
    m.loc[m["interbank"] - m["floor"] < BAND, "regime"] = "floor"
    m.loc[m["ceiling"] - m["interbank"] < BAND, "regime"] = "ceiling"
    for k in FLOWS:  # 12 month sums for the chart, formed before the window is cut
        m[f"{k}_12m"] = m[k].rolling(12, min_periods=12).sum()
    m = m.loc[START:END]
    if m[["interbank", "floor", "ceiling", "fx_net", "fiscal_net"]].isna().any().any():
        raise RuntimeError("missing corridor or flow values inside the window")
    return m


MEASURES = FLOWS + ["credit_growth", "deposit_growth", "excess_reserves", "nrb_net_absorbing"]


def episodes(m: pd.DataFrame) -> pd.DataFrame:
    run = (m["regime"] != m["regime"].shift()).cumsum()
    rows = []
    for _, g in m.groupby(run):
        rows.append({"regime": g["regime"].iloc[0], "first": str(g.index[0]), "last": str(g.index[-1]),
                     "months": len(g), "interbank_mean": g["interbank"].mean(),
                     **{k: g[k].mean() for k in MEASURES}})
    return pd.DataFrame(rows)


def fiscal_years(m: pd.DataFrame) -> pd.DataFrame:
    fy = [f"{p.year}/{(p.year + 1) % 100:02d}" if p.month >= 8 else f"{p.year - 1}/{p.year % 100:02d}" for p in m.index]
    g = m.groupby(fy)
    out = g[FLOWS].sum().join(g[["credit_growth", "deposit_growth", "excess_reserves", "interbank"]].mean())
    out["floor_months"] = g["regime"].apply(lambda r: (r == "floor").sum())
    out["ceiling_months"] = g["regime"].apply(lambda r: (r == "ceiling").sum())
    out.index.name = "fiscal_year"
    return out


def chart(m: pd.DataFrame) -> None:
    x = m.index.to_timestamp()
    fig, (top, mid, bot) = plt.subplots(3, 1, figsize=(10, 9), sharex=True, facecolor=SURFACE,
                                        gridspec_kw={"height_ratios": [1.1, 1, 0.9]})
    run = (m["regime"] != m["regime"].shift()).cumsum()
    for _, g in m.groupby(run):
        r = g["regime"].iloc[0]
        if r in SHADE:
            a, b = g.index[0].to_timestamp(), (g.index[-1] + 1).to_timestamp()
            for ax in (top, mid, bot):
                ax.axvspan(a, b, color=SHADE[r], zorder=0, linewidth=0)
            if len(g) >= 3:
                top.text(a, 0.97, f" {r}", transform=top.get_xaxis_transform(), va="top", fontsize=8, color=SECONDARY)
    top.step(x, m["ceiling"], where="post", color=MUTED, linewidth=1.5, linestyle="--")
    top.step(x, m["floor"], where="post", color=MUTED, linewidth=1.5)
    top.plot(x, m["interbank"], color=INK, linewidth=2)
    top.text(x[-1], m["ceiling"].iloc[-1], " ceiling", va="center", fontsize=8, color=SECONDARY)
    top.text(x[-1], m["floor"].iloc[-1] - 0.4, " floor", va="center", fontsize=8, color=SECONDARY)
    top.annotate("interbank rate", xy=(x[10], m["interbank"].iloc[10]), xytext=(x[11], 7.2), fontsize=8, color=INK,
                 arrowprops={"arrowstyle": "-", "color": MUTED, "linewidth": 0.8})
    top.set_ylabel("percent", fontsize=8, color=SECONDARY)
    top.set_title("Nepal: interbank rate inside the NRB corridor and the flows that moved it", loc="left",
                  fontsize=11, color=INK)
    roll = m[[f"{k}_12m" for k in FLOWS]].set_axis(FLOWS, axis=1)
    labels = {"fx_net": "NRB net FX purchase", "remittances": "remittances", "fiscal_net": "government spending minus revenue"}
    for k in FLOWS:
        mid.plot(x, roll[k], color=SERIES[k], linewidth=2, label=labels[k])
        last = roll[k].dropna()
        mid.text(last.index[-1].to_timestamp(), last.iloc[-1], f" {last.iloc[-1]:.1f}", va="center", fontsize=8, color=SECONDARY)
    mid.axhline(0, color=MUTED, linewidth=0.8)
    mid.set_ylabel("12 month sum, percent of broad money", fontsize=8, color=SECONDARY)
    mid.legend(loc="upper left", fontsize=8, frameon=False, ncol=3)
    bot.plot(x, m["credit_growth"], color=INK, linewidth=2, label="private credit")
    bot.plot(x, m["deposit_growth"], color=MUTED, linewidth=2, linestyle="--", label="deposits")
    bot.set_ylabel("growth over 12 months, percent", fontsize=8, color=SECONDARY)
    bot.legend(loc="upper right", fontsize=8, frameon=False, ncol=2)
    for ax in (top, mid, bot):
        ax.set_facecolor(SURFACE)
        ax.grid(axis="y", color=GRID, linewidth=0.6)
        ax.tick_params(colors=SECONDARY, labelsize=8)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(GRID)
    fig.text(0.01, 0.005, "Shading: floor (blue) or ceiling (orange) months, interbank rate within 0.5 points of that bound. "
             "Sources: NRB database and CME tables, IMF MFS.", fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    FIGURE.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(FIGURE.with_suffix(f".{ext}"), dpi=200, facecolor=SURFACE)
    plt.close(fig)


def main() -> int:
    m = frame()
    e, f = episodes(m).round(3), fiscal_years(m).round(3)
    e.to_csv(TABLES / "nepal_liquidity_regimes.csv", index=False)
    f.to_csv(TABLES / "nepal_liquidity_fiscal_years.csv")
    chart(m)
    pd.set_option("display.width", 200)
    print(e.to_string(index=False))
    print(f.to_string())
    print(m.groupby("regime")[MEASURES].mean().round(3).to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
