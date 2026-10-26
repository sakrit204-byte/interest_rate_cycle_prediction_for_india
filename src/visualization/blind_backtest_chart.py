"""Blind backtest chart (plan section 6.1), static figure for the report.

Top: RBI repo rate as a step line, blind window shaded, a marker at every decision (shape is
the actual decision, fill is the engine's suggestion, a ring marks a mismatch, hollow means
uncertain). Middle: stacked probabilities of cut, hold and hike from the learned reaction
function. Bottom: rate prescribed by the estimated rule and by the textbook Taylor rule
against the actual rate.

Colours: diverging blue (cut) and red (hike) poles with a gray midpoint (hold); validated with
the dataviz palette script. Decision shape repeats the meaning so colour is never alone.

Usage: python -m src.visualization.blind_backtest_chart [train|blind]
Output: reports/figures/backtest_<period>.png and .svg
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

from src.features.build_india_features import BIS_IN, daily_rate
from src.policy.suggestion_engine import config

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "reports" / "tables"
FIGURES = ROOT / "reports" / "figures"
INK, SECONDARY, MUTED, GRID, AXIS, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
COLOUR = {"cut": "#2a78d6", "hold": "#898781", "hike": "#e34948"}
PROB_FILL = {"cut": "#2a78d6", "hold": "#d6d5ce", "hike": "#e34948"}
RULE, TAYLOR = "#6250d6", "#1baf7a"
Y_RANGE = (0, 16)  # bottom panel; textbook rule values outside are labelled
SHAPE = {"cut": "v", "hold": "o", "hike": "^"}


def style(ax) -> None:
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(AXIS)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.yaxis.label.set_color(SECONDARY)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def draw(s: pd.DataFrame, title: str, out: Path) -> None:
    s = s.copy()
    s["date"] = pd.to_datetime(s["date"])
    repo = daily_rate(BIS_IN).loc[s["date"].min() - pd.Timedelta(days=60): s["date"].max() + pd.Timedelta(days=30)]
    blind_start = config()["blind_start"]
    if s["date"].max() < blind_start:  # training chart: nothing from the sealed period
        repo = repo.loc[: blind_start - pd.Timedelta(days=1)]
    fig, axes = plt.subplots(3, 1, figsize=(11, 8.5), sharex=True, height_ratios=[2.2, 1.2, 1.8],
                             facecolor=SURFACE)
    top, mid, bot = axes
    for ax in axes:
        style(ax)
        if repo.index.max() >= blind_start:
            ax.axvspan(blind_start, repo.index.max(), color="#f0efec", zorder=0)
    if repo.index.max() >= blind_start:
        top.text(blind_start, 1.02, "  sealed test period", transform=top.get_xaxis_transform(), color=SECONDARY, fontsize=8)

    top.step(repo.index, repo.values, where="post", color=INK, linewidth=1.6)
    for _, r in s.iterrows():
        sug = r["suggestion"]
        face = "white" if sug == "uncertain" else COLOUR[sug]
        miss = sug != "uncertain" and sug != r["actual"]
        top.scatter(r["date"], r["repo_before"], marker=SHAPE[r["actual"]], s=70, facecolor=face,
                    edgecolor=INK if miss else (MUTED if sug == "uncertain" else SURFACE),
                    linewidth=1.6 if miss else 1.0, zorder=3)
    top.set_ylabel("Repo rate, %")
    top.set_title(title, loc="left", fontsize=11, color=INK)
    handles = [Line2D([], [], marker=SHAPE[k], linestyle="", markerfacecolor=COLOUR[k], markeredgecolor=SURFACE,
                      markersize=8, label=f"suggested {k}") for k in ("cut", "hold", "hike")]
    handles += [Line2D([], [], marker="o", linestyle="", markerfacecolor="white", markeredgecolor=MUTED,
                       markersize=8, label="uncertain"),
                Line2D([], [], marker="o", linestyle="", markerfacecolor="#d6d5ce", markeredgecolor=INK,
                       markeredgewidth=1.6, markersize=8, label="mismatch (ring)")]
    top.legend(handles=handles, loc="lower left", fontsize=8, frameon=False, ncol=3,
               title="shape = actual decision (▲ hike, ● hold, ▼ cut)", title_fontsize=8)

    mid.stackplot(s["date"], s["p_cut"], s["p_hold"], s["p_hike"], step="post", edgecolor=SURFACE, linewidth=0.8,
                  colors=[PROB_FILL[k] for k in ("cut", "hold", "hike")], labels=["P(cut)", "P(hold)", "P(hike)"])
    mid.set_ylim(0, 1)
    mid.set_ylabel("Probability")
    mid.legend(loc="upper left", fontsize=8, frameon=False, ncol=3)

    bot.step(repo.index, repo.values, where="post", color=INK, linewidth=1.6)
    bot.plot(s["date"], s["rule_prescribed_rate"], color=RULE, linewidth=2, marker="o", markersize=3)
    bot.plot(s["date"], s["taylor_rate"], color=TAYLOR, linewidth=2)
    for text, c in (("actual", INK), ("estimated rule", RULE), ("textbook Taylor", TAYLOR)):
        bot.plot([], [], color=c, linewidth=2, label=text)
    lo, hi = Y_RANGE
    bot.set_ylim(lo, hi)
    off = s[(s["taylor_rate"] > hi) | (s["taylor_rate"] < lo)]
    note = ("" if off.empty else "Textbook Taylor values off scale: " + ", ".join(
        f"{pd.Timestamp(d):%b %Y} {v:.0f}%" for d, v in zip(off["date"], off["taylor_rate"])) + " (IIP base effects).\n")
    bot.set_ylabel("Rate, %")
    bot.legend(loc="upper left", fontsize=8, frameon=False, ncol=3)
    fig.text(0.01, 0.005, note + "Sources: RBI decisions (BIS policy rate), MoSPI, RBI statements; model output from "
             "src/policy/suggestion_engine.py. Probabilities refit in real time at each decision.",
             fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.035, 0.97, 1))
    FIGURES.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(out.with_suffix(f".{ext}"), dpi=200, facecolor=SURFACE)
    plt.close(fig)


def main() -> int:
    period = sys.argv[1] if len(sys.argv) > 1 else "train"
    s = pd.read_csv(TABLES / f"suggestions_{period}.csv")
    title = ("RBI decisions and engine suggestions, training period walk forward (not the blind test)"
             if period == "train" else "Blind backtest: RBI decisions from November 2021 against frozen suggestions")
    draw(s, title, FIGURES / f"backtest_{period}")
    print("written", FIGURES / f"backtest_{period}.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
