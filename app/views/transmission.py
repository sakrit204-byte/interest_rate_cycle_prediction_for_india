import pandas as pd
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
**Reading.** Market rates do not follow India: if they did, the interbank and T bill responses would rise towards plus one. At twelve months full pass through lies outside the interval for the interbank rate. Nepal's open border carries goods and cash, but a largely closed capital account stops banks arbitraging into Indian money markets, which is how a peg and a separate short rate can coexist. The negative point estimates reflect few RBI cycles that happened to coincide with opposite Nepali liquidity cycles, not a negative effect. Inflation does not respond measurably to the RBI's own moves (0.9 points after two years, not significant); the peg carries India's prices into Nepal, and the policy rate reaches Nepal only through the NRB's own decisions (next section).
""")

st.subheader("Through India's cycles: market rate against the NRB's policy rate")
badge("estimated")
st.caption("Decisions D053, D055 and D056. Cycle table: change from the month before the RBI's first move to three "
           "months after its last, in percentage points; same way means more than 0.1 point in the RBI's direction. "
           "Test: monthly OLS of the 6 month change in each Nepali rate on the RBI's 6 month change three months "
           "earlier, separately before and during the NRB corridor (from August 2016), Newey West errors, declared "
           "before it was run.")
cyc = table("peg_cycles")
cyc = cyc[cyc["complete"]]
left, right = st.columns([3, 2])
with left:
    shown = pd.DataFrame({
        "RBI cycle": cyc["direction"].str.capitalize() + " " + cyc["first_move"].str[:4] + " to " + cyc["last_move"].str[:4],
        "RBI change": cyc["rbi_change"], "Nepal interbank": cyc["interbank_change"],
        "followed": cyc["interbank_same_direction"].map({True: "same way", False: "no"}),
        "NRB bank rate": cyc["nrb_bank_rate_change"],
        "followed ": cyc["nrb_bank_rate_same_direction"].map({True: "same way", False: "no"})})
    st.dataframe(shown, hide_index=True, use_container_width=True)
with right:
    pr = table("peg_policy_response").set_index("outcome")
    for k, label in (("nrb_bank_rate", "NRB bank rate"), ("interbank", "Interbank rate")):
        r = pr.loc[k]
        st.metric(f"{label}: response per RBI point, corridor years", f"{r['corridor']:.2f} (p {r['corridor_p']:.3f})",
                  f"before corridor {r['before_corridor']:.2f} (p {r['before_p']:.2f})", delta_color="off",
                  help=f"95 percent interval {r['corridor_ci_low']:.2f} to {r['corridor_ci_high']:.2f}, p {r['corridor_p']:.3f}")
st.markdown("""
**Reading.** Two results belong together. Nepal's market rate followed the RBI in only 6 of 12 cycles since 2001, a coin flip, and the monthly test finds no response of it in either period: the peg alone does not import India's interest rate, because capital controls stop arbitrage and remittances bought at the peg keep the interbank rate on its own liquidity path. The NRB's own policy rate is different. Before the corridor it did not respond (0.02), but since August 2016 it has moved about 0.49 point per point of RBI move (95 percent interval 0.14 to 0.85, p 0.007), and the last three RBI cycles all fit. India's interest rate cycle therefore reaches Nepal through the NRB's decision, at about half the RBI's move. Applied to the outlook, a cycle ending at 5.75 to 6.00 implies an NRB move of about 0.25 to 0.37 point; this is an implication, not a model forecast.
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
