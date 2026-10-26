import plotly.graph_objects as go
import streamlit as st

from common import DECISION, INK, SERIES, badge, style
from src.simulation import scenarios as sc

st.title("Scenarios")
badge("simulated")
st.warning("Conditional on your assumptions and on relationships estimated from 2002 to 2026. "
           "These are not forecasts, and they are not causal effects of policy.")


@st.cache_data
def hist():
    return sc.history()


h = hist()
last = h.iloc[-1]
india, nepal = st.tabs(["India: what would the RBI do?", "Nepal: an RBI move and Nepali variables"])

with india:
    st.caption(f"Defaults are the situation at the latest decision ({last['date'].date()}).")
    c = st.columns(4)
    x = {
        "prev_decision": {"cut": -1, "hold": 0, "hike": 1}[c[0].selectbox("Previous decision", ["cut", "hold", "hike"],
                                                                         index=int(last["prev_decision"]) + 1)],
        "repo_level": c[1].number_input("Current repo rate, %", 0.0, 15.0, float(last["repo_level"]), 0.25),
        "anchor": c[2].number_input("Inflation target (anchor), %", 2.0, 10.0, float(last["anchor"]), 0.5),
        "inr_depr_3m": c[3].number_input("Rupee depreciation over 3 months, %", -15.0, 15.0,
                                         float(round(last["inr_depr_3m"], 1)), 0.5),
        "infl": c[0].slider("Latest CPI inflation, %", -2.0, 15.0, float(round(last["infl"], 1)), 0.1),
        "proj_infl": c[1].slider("RBI projected inflation, %", 0.0, 12.0, float(last["proj_infl"]), 0.1),
        "proj_revision": c[2].slider("Revision to that projection, points", -2.0, 2.0, 0.0, 0.1),
        "growth_gap": c[3].slider("IIP growth gap, points", -15.0, 15.0, float(round(last["growth_gap"], 1)), 0.5),
    }
    out = sc.india(x, h)
    if out["extrapolated"]:
        st.error("Outside the historical range: " + ", ".join(out["extrapolated"]) +
                 ". The model is extrapolating; treat the result as unreliable.")
    probs = {k: out[f"p_{k}"] for k in ("cut", "hold", "hike")}
    fig = go.Figure(go.Bar(x=list(probs), y=list(probs.values()), marker_color=[DECISION[k] for k in probs],
                           text=[f"{v:.0%}" for v in probs.values()], textposition="outside"))
    fig.update_yaxes(range=[0, 1.1], tickformat=".0%")
    c = st.columns([2, 1])
    c[0].plotly_chart(style(fig, height=320, title="Learned reaction function: decision probabilities",
                            hovermode="closest"), use_container_width=True, theme=None)
    c[1].metric("Estimated inertial rule", out["rule"], f"{out['rule_change_pp'] * 100:+.0f} bp prescribed")
    c[1].metric("Textbook Taylor rule (normative)", out["taylor"])
    c[1].caption(f"Prescribes {out['taylor_rate']:.2f}% against a current repo of {x['repo_level']:.2f}%.")
    c[1].caption(f"Fitted on {out['n_decisions']} decisions with known outcomes.")

with nepal:
    shock = st.slider("RBI repo change, points (0.25 = 25 bp)", -2.0, 2.0, 1.0, 0.25)
    r = sc.nepal(shock)
    names = {"interbank_rate": "Interbank rate", "tbill_91d": "91 day T bill", "nepal_cpi_yoy": "CPI inflation",
             "private_credit_growth": "Private credit growth"}
    pick = st.segmented_control("Variable", list(names), default="nepal_cpi_yoy", format_func=names.get)
    g = r[r["outcome"] == (pick or "nepal_cpi_yoy")]
    fig = go.Figure()
    fig.add_scatter(x=list(g["horizon"]) + list(g["horizon"][::-1]), y=list(g["ci_high"]) + list(g["ci_low"][::-1]),
                    fill="toself", fillcolor="rgba(42,120,214,0.15)", line=dict(width=0), name="95% band",
                    hoverinfo="skip")
    fig.add_scatter(x=g["horizon"], y=g["response"], line=dict(color=SERIES[0], width=2), name="conditional response")
    fig.add_hline(y=0, line=dict(color=INK, width=1))
    fig.update_xaxes(title_text="months after the RBI move")
    st.plotly_chart(style(fig, height=380, title=f"{names[pick or 'nepal_cpi_yoy']}: change from before the move, points"),
                    use_container_width=True, theme=None)
    st.caption("Scales the local projection estimates linearly with the size of the move; assumes the historical "
               "relationship holds and other drivers stay as they were.")
