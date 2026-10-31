import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from common import DECISION, INK, MUTED, SERIES, badge, style, table
from src.features.build_india_features import BIS_IN, daily_rate

NAMES = {"premium_persists": "Premium persists (Brent about 112)", "escalation": "Escalation in the Gulf (about 135)",
         "de_escalation": "Easing tensions (about 92)", "ai_bust": "AI bust, world slowdown (about 90)",
         "stagflation": "Stagflation (about 125)"}

st.title("Next two years: December 2026 to October 2028")
badge("simulated")
st.caption("Decisions D050, D057 and D058. The frozen India model, chained through the next 12 RBI meetings. The first "
           "three meetings use news based scenario inputs; after April 2027 the inputs follow assumptions declared "
           "before the run. A conditional outlook, not a forecast.")

t = table("india_outlook_2y_20261031", parse_dates=["meeting"])
name = st.segmented_control("Scenario", list(NAMES), default="premium_persists", format_func=NAMES.get) or "premium_persists"
g = t[t["scenario"] == name]
repo = daily_rate(BIS_IN).loc["2022-01-01":]

fig = go.Figure()
fig.add_scatter(x=repo.index, y=repo.values, name="RBI repo, actual", line=dict(color=INK, shape="hv", width=2))
fig.add_scatter(x=list(g["meeting"]) + list(g["meeting"][::-1]), y=list(g["repo_p90"]) + list(g["repo_p10"][::-1]),
                fill="toself", fillcolor="rgba(235,104,52,0.15)", line=dict(width=0), name="10 to 90 percent range",
                hoverinfo="skip")
fig.add_scatter(x=g["meeting"], y=g["expected_repo_after"], name="RBI repo, expected", mode="lines+markers",
                line=dict(color=SERIES[1], width=2.5))
fig.add_scatter(x=g["meeting"], y=g["nrb_bank_rate_mid"], name="NRB bank rate implied (0.49 response)",
                mode="lines+markers", line=dict(color=SERIES[0], width=2, dash="dot"))
fig.update_yaxes(title_text="percent", range=[3.5, 7])
st.plotly_chart(style(fig, height=430, title="Repo rate path and the implied NRB bank rate"), use_container_width=True,
                theme=None)

c = st.columns(4)
peak = g.loc[g["expected_repo_after"].idxmax()]
end = g.iloc[-1]
c[0].metric("Expected peak", f"{peak['expected_repo_after']:.2f}", f"at {peak['meeting']:%B %Y}", delta_color="off")
c[1].metric("Expected repo, October 2028", f"{end['expected_repo_after']:.2f}",
            f"range {end['repo_p10']:.2f} to {end['repo_p90']:.2f}", delta_color="off")
c[2].metric("NRB bank rate at the peak", f"{peak['nrb_bank_rate_mid']:.2f}",
            f"range {peak['nrb_bank_rate_low']:.2f} to {peak['nrb_bank_rate_high']:.2f}", delta_color="off")
c[3].metric("NRB bank rate, October 2028", f"{end['nrb_bank_rate_mid']:.2f}", "today 5.75", delta_color="off")

fig = go.Figure()
for k in ("cut", "hold", "hike"):
    fig.add_bar(x=g["meeting"], y=g[f"p_{k}"], name=f"P({k})", marker_color=DECISION[k])
fig.update_yaxes(range=[0, 1], tickformat=".0%")
st.plotly_chart(style(fig, height=320, title="Probability of a cut, a hold and a hike at each meeting (they add to 100 percent)",
                      barmode="stack"), use_container_width=True, theme=None)

st.subheader("All scenarios")
show = t.assign(scenario=t["scenario"].map(NAMES), meeting=t["meeting"].dt.strftime("%b %Y"))
show = show.pivot(index="meeting", columns="scenario", values="expected_repo_after")
show = show.loc[pd.unique(t["meeting"].dt.strftime("%b %Y"))]
st.dataframe(show.round(2), use_container_width=True)
st.caption("Expected repo rate after each meeting under each scenario.")

st.markdown("""
**Reading.** In every scenario the model's hiking cycle peaks by April 2027 at an expected 5.7 to 5.8 percent, one or two hikes above today. From June 2027 a cut becomes more likely than a hike: the oil shock drops out of twelve month inflation a year after it began, inflation returns towards its recent average of 4.7 percent, and the RBI's own earlier hikes have cooled prices. By October 2028 the expected repo is back near 5.25, but the range is wide, 4.25 to 6.25, because each meeting adds uncertainty. The scenarios look alike after a year because the assumptions, not the news, drive that part of the path.

**Nepal.** If the NRB keeps responding at the 0.49 measured since 2016, its bank rate rises from 5.75 to about 5.95 to 6.0 at the RBI's peak and drifts back towards 5.75 by late 2028. Through the peg, Nepal's inflation should follow India's path down from 2027.

**Assumptions after April 2027** (D057): inflation converges to 4.7 and the growth gap to zero, halving the distance every two meetings; the oil effect leaves twelve month inflation from December 2027; the AI bust's demand effect fades; the rupee weakens 1 percent a quarter; the RBI projects the path two meetings ahead; and each point of repo above 5.50 lowers inflation by 0.4 point, an assumed policy feedback.
""")
