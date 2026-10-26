import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from common import INK, SERIES, badge, style, table

st.title("India to Nepal transmission")
badge("estimated")
st.caption("Local projections (decision D032): response of Nepali variables to a 100 basis point RBI repo move, "
           "holding oil, US policy and Indian inflation fixed. Monthly, August 2000 to October 2021; shaded bands "
           "are 95 percent intervals with Newey West errors. Associations conditional on controls, not proof of causation.")

lp = table("local_projections")
names = {"interbank_rate": "Interbank rate, pp", "tbill_91d": "91 day T bill, pp",
         "nepal_cpi_yoy": "CPI inflation, pp", "private_credit_growth": "Private credit growth, pp"}
fig = make_subplots(rows=2, cols=2, subplot_titles=list(names.values()), horizontal_spacing=0.08,
                    vertical_spacing=0.14)
for i, (k, title) in enumerate(names.items()):
    g = lp[lp["outcome"] == k]
    r, c = i // 2 + 1, i % 2 + 1
    fig.add_scatter(x=list(g["horizon"]) + list(g["horizon"][::-1]), y=list(g["ci_high"]) + list(g["ci_low"][::-1]),
                    fill="toself", fillcolor="rgba(42,120,214,0.15)", line=dict(width=0), showlegend=False,
                    hoverinfo="skip", row=r, col=c)
    fig.add_scatter(x=g["horizon"], y=g["coef"], line=dict(color=SERIES[0], width=2), showlegend=False,
                    customdata=g["p_value"], hovertemplate="month %{x}: %{y:.2f} (p %{customdata:.2f})<extra></extra>",
                    row=r, col=c)
    fig.add_hline(y=0, line=dict(color=INK, width=1), row=r, col=c)
fig.update_xaxes(title_text="months after the RBI move", row=2)
st.plotly_chart(style(fig, height=620, hovermode="closest"), use_container_width=True, theme=None)

st.markdown("""
**Reading.** Short rates do not follow India: if they did, the interbank and T bill responses would rise towards plus one. At twelve months full pass through lies outside the interval for the interbank rate. Nepal's open border carries goods and cash, but a largely closed capital account stops banks arbitraging into Indian money markets, which is how a peg and a separate short rate can coexist. The negative point estimates reflect few RBI cycles that happened to coincide with opposite Nepali liquidity cycles, not a negative effect. Inflation is where the peg bites: the CPI response rises to about 1.5 points after two years, consistent with Indian prices arriving through trade at a fixed exchange rate.
""")

st.subheader("Does Nepali liquidity change the response? (H4)")
s = table("local_projections_state")
fig = go.Figure()
for term, colour, fill, label in [("shock_high_liquidity", SERIES[0], "rgba(42,120,214,0.15)", "excess reserves above median"),
                                  ("shock_low_liquidity", SERIES[1], "rgba(235,104,52,0.15)", "below median")]:
    g = s[s["term"] == term]
    fig.add_scatter(x=list(g["horizon"]) + list(g["horizon"][::-1]), y=list(g["ci_high"]) + list(g["ci_low"][::-1]),
                    fill="toself", fillcolor=fill, line=dict(width=0), showlegend=False, hoverinfo="skip")
    fig.add_scatter(x=g["horizon"], y=g["coef"], name=label, line=dict(color=colour, width=2))
fig.add_hline(y=0, line=dict(color=INK, width=1))
st.plotly_chart(style(fig, height=360, title="Interbank response by liquidity state, pp"), use_container_width=True, theme=None)
st.caption("The larger negative response in abundant liquidity supports the coincidence reading above; we do not claim "
           "a liquidity dependent transmission mechanism.")
