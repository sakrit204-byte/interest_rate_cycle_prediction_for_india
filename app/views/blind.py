import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from common import DECISION, INK, PROB_FILL, RULE, TAYLOR, badge, metrics_view, style, table, text
from src.features.build_india_features import BIS_IN, daily_rate

BLIND_START = pd.Timestamp("2021-11-01")
SHAPE = {"cut": "triangle-down", "hold": "circle", "hike": "triangle-up"}

st.title("Blind backtest")
badge("predicted")
st.caption("Configuration frozen on 26 October 2026 (SHA256 b8122750...) and only then unsealed. Every model is "
           "the frozen specification, refit in real time at each decision; nothing was retuned.")

context = st.toggle("Show the training period walk forward as context", value=True)
s = table("suggestions_blind", parse_dates=["date"])
if context:
    s = pd.concat([table("suggestions_train", parse_dates=["date"]), s], ignore_index=True)
repo = daily_rate(BIS_IN).loc[s["date"].min() - pd.Timedelta(days=60):]

fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.45, 0.25, 0.30], vertical_spacing=0.04)
fig.add_scatter(x=repo.index, y=repo.values, name="Repo rate", line=dict(color=INK, shape="hv", width=2),
                row=1, col=1)
for sug in ["cut", "hold", "hike", "uncertain"]:
    g = s[s["suggestion"] == sug]
    miss = (g["suggestion"] != g["actual"]) & (sug != "uncertain")
    fig.add_scatter(x=g["date"], y=g["repo_before"], mode="markers", name=f"suggested {sug}",
                    marker=dict(symbol=[SHAPE[a] for a in g["actual"]], size=12,
                                color="#ffffff" if sug == "uncertain" else DECISION[sug],
                                line=dict(color=[INK if m else ("#898781" if sug == "uncertain" else "#fcfcfb")
                                                 for m in miss], width=[2.5 if m else 1 for m in miss])),
                    customdata=g[["actual", "p_cut", "p_hold", "p_hike", "reasons"]],
                    hovertemplate="actual %{customdata[0]}<br>P(cut) %{customdata[1]:.2f}, P(hold) %{customdata[2]:.2f}, "
                                  "P(hike) %{customdata[3]:.2f}<br>%{customdata[4]}<extra>suggested " + sug + "</extra>",
                    row=1, col=1)
for k in ["cut", "hold", "hike"]:
    fig.add_scatter(x=s["date"], y=s[f"p_{k}"], name=f"P({k})", stackgroup="p", line=dict(width=0.5, color="#fcfcfb",
                    shape="hv"), fillcolor=PROB_FILL[k], showlegend=True, row=2, col=1)
fig.add_scatter(x=repo.index, y=repo.values, name="actual", line=dict(color=INK, shape="hv", width=2),
                showlegend=False, row=3, col=1)
fig.add_scatter(x=s["date"], y=s["rule_prescribed_rate"], name="estimated rule", line=dict(color=RULE, width=2),
                row=3, col=1)
fig.add_scatter(x=s["date"], y=s["taylor_rate"].clip(-2, 16), name="textbook Taylor (clipped to -2..16)",
                line=dict(color=TAYLOR, width=2), row=3, col=1)
fig.add_vrect(x0=BLIND_START, x1=repo.index.max(), fillcolor="#f0efec", line_width=0, layer="below")
fig.add_annotation(x=BLIND_START, y=1, yref="y domain", xanchor="left", yanchor="top", showarrow=False,
                   text=" sealed test period", font=dict(size=11, color="#52514e"), row=1, col=1)
fig.update_yaxes(title_text="Repo, %", row=1, col=1)
fig.update_yaxes(title_text="Probability", range=[0, 1], row=2, col=1)
fig.update_yaxes(title_text="Rate, %", row=3, col=1)
st.plotly_chart(style(fig, height=820), use_container_width=True, theme=None)
st.caption("Marker shape is the actual decision (triangle up hike, circle hold, triangle down cut); fill is the "
           "engine's suggestion; a dark ring marks a mismatch; hollow means uncertain (classifier and estimated rule "
           "disagree, or top probability below 0.5).")

st.subheader("India: 31 decisions, December 2021 to October 2026")
st.dataframe(metrics_view(table("blind_india_metrics")), hide_index=True, use_container_width=True)
c = st.columns(2)
c[0].markdown("**Diebold Mariano tests on log loss**")
c[0].dataframe(table("blind_india_dm").round(3), hide_index=True, use_container_width=True)
c[1].markdown("**Suggestion sources against actual decisions**")
c[1].dataframe(table("suggestions_blind_agreement").round(3), hide_index=True, use_container_width=True)
b = table("suggestions_blind")
c = st.columns(2)
c[0].markdown("**Confusion matrix, learned reaction function** (rows actual, columns predicted)")
c[0].dataframe(pd.crosstab(b["actual"], b["classifier"]), use_container_width=True)
c[1].markdown("**Turning points** (negative: called early; positive: late; blank: never called)")
c[1].dataframe(table("blind_turning_points").pivot(index="date", columns="source", values="lag_decisions"),
               use_container_width=True)

st.subheader("Nepal: 57 months, interbank direction three months ahead")
st.dataframe(metrics_view(table("blind_nepal_metrics")), hide_index=True, use_container_width=True)
st.dataframe(table("blind_nepal_dm").round(3), hide_index=True, use_container_width=True)
st.caption("First row is the transmission test: the liquidity model with against without the RBI repo change.")
with st.expander("Full economic reading (reports/blind_test_results.md)"):
    st.markdown(text("reports/blind_test_results.md"))
