import plotly.express as px
import streamlit as st

from common import SERIES, badge, csv, style, table

st.title("Political and policy events")
badge("observed")
st.caption("98 events, each with a source. Features join on the announcement date, never the event date.")
e = csv("data/events/political_events.csv", parse_dates=["event_date", "announcement_date"])
country = st.segmented_control("Country", ["India", "Nepal"], default="India") or "India"
d = e[e["country"] == country].copy()
d["type"] = d["event_type"].str.replace("_", " ")
fig = px.scatter(d, x="event_date", y="type", hover_name="description",
                 hover_data={"announcement_date": "|%d %b %Y", "event_date": "|%d %b %Y", "type": False},
                 color_discrete_sequence=[SERIES[0]])
fig.update_traces(marker=dict(size=10, line=dict(width=1.5, color="#fcfcfb")))
st.plotly_chart(style(fig, height=420, title=f"{country}: events by type", hovermode="closest"),
                use_container_width=True, theme=None)
st.dataframe(d[["event_date", "announcement_date", "event_type", "description", "verified", "source_url", "note"]],
             hide_index=True, use_container_width=True,
             column_config={"source_url": st.column_config.LinkColumn("source"),
                            "event_date": st.column_config.DateColumn(format="YYYY-MM-DD"),
                            "announcement_date": st.column_config.DateColumn(format="YYYY-MM-DD")})

st.subheader("Do events improve forecasts? (H2)")
dm = table("ablation_political_dm")
st.dataframe(dm.round(3), hide_index=True, use_container_width=True)
st.caption("Negative statistic means the model with events had lower log loss. Neither difference is significant.")
