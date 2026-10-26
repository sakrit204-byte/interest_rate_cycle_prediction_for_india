"""Shared paths, cached loaders, palette and labels for the dashboard."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TABLES = ROOT / "reports" / "tables"

# palette validated with the dataviz script: blue and red poles, gray midpoint for hold
INK, SECONDARY, MUTED, GRID = "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
DECISION = {"cut": "#2a78d6", "hold": "#898781", "hike": "#e34948"}
PROB_FILL = {"cut": "#2a78d6", "hold": "#d6d5ce", "hike": "#e34948"}
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#6250d6"]
RULE, TAYLOR = "#6250d6", "#1baf7a"
LABEL = {
    "observed": ("Observed", "#0ca30c"),
    "predicted": ("Predicted, real time out of sample", "#2a78d6"),
    "estimated": ("Estimated from history", "#6250d6"),
    "simulated": ("Simulated, conditional on assumptions", "#ec835a"),
}


@st.cache_data
def table(name: str, **kw) -> pd.DataFrame:
    return pd.read_csv(TABLES / f"{name}.csv", **kw)


@st.cache_data
def csv(rel: str, **kw) -> pd.DataFrame:
    return pd.read_csv(ROOT / rel, **kw)


@st.cache_data
def text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def badge(kind: str) -> None:
    label, colour = LABEL[kind]
    st.markdown(f"<span style='border:1px solid {colour};color:{colour};border-radius:4px;"
                f"padding:1px 8px;font-size:0.8rem'>{label}</span>", unsafe_allow_html=True)


def style(fig: go.Figure, height: int = 380, hovermode: str = "x unified", **kw) -> go.Figure:
    # with a title, the legend goes under the plot so the two never collide
    legend = (dict(orientation="h", yanchor="top", y=-0.12, x=0) if "title" in kw
              else dict(orientation="h", yanchor="bottom", y=1.02, x=0))
    if "title" in kw:
        kw["title"] = dict(text=kw["title"], x=0, xanchor="left", font=dict(size=15, color=INK))
    fig.update_layout(height=height, margin=dict(l=50, r=20, t=50, b=70 if "title" in kw else 40),
                      plot_bgcolor="#fcfcfb", paper_bgcolor="#fcfcfb",
                      font=dict(color=SECONDARY, family="system-ui, Segoe UI, sans-serif", size=12),
                      hovermode=hovermode, legend=legend, **kw)
    fig.update_xaxes(showgrid=False, linecolor="#c3c2b7", automargin=True)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor="#c3c2b7", automargin=True)
    return fig


def metrics_view(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in ["model", "n", "accuracy", "balanced_accuracy", "bal_acc_ci_low", "bal_acc_ci_high",
                        "macro_f1", "cohen_kappa", "log_loss", "brier"] if c in df]
    return df[cols].round(3)
