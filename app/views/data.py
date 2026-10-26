import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from common import INK, SERIES, badge, csv, style
from src.features.build_india_features import BIS_IN, BIS_US, daily_rate

st.title("Data explorer")
badge("observed")
st.caption("Values as published. Release lags are applied only inside the models, never here.")

country = st.segmented_control("Country", ["India", "Nepal"], default="India")
if country == "Nepal":
    t = csv("data/interim/nepal/nepal_target_monthly.csv")
    t["month"] = pd.PeriodIndex(t["month"], freq="M").to_timestamp()
    fig = go.Figure()
    fig.add_scatter(x=t["month"], y=t["interbank_rate"], name="Interbank rate", line=dict(color=SERIES[3], width=1.5))
    fig.add_scatter(x=t["month"], y=t["interbank_adj"], name="Seasonally adjusted", line=dict(color=INK, width=2))
    st.plotly_chart(style(fig, title="Nepal interbank rate, percent"), use_container_width=True, theme=None)
    f = csv("data/processed/nepal/nepal_features_monthly.csv")
    f["month"] = pd.PeriodIndex(f["month"], freq="M").to_timestamp()
    fig = go.Figure()
    for i, (col, name) in enumerate([("reserves_to_deposits", "Banks' claims on the NRB, % of deposits"),
                                     ("nfa_cb_growth_3m", "NRB net foreign assets, 3 month growth %"),
                                     ("gov_deposit_change_3m", "Government deposits at NRB, 3 month change, % of broad money")]):
        fig.add_scatter(x=f["month"], y=f[col], name=name, line=dict(color=SERIES[i], width=1.8))
    st.plotly_chart(style(fig, title="Liquidity drivers, as known at each forecast origin (two month lag)"),
                    use_container_width=True, theme=None)
    st.markdown("Sources: NRB Quarterly Economic Bulletin table 41 via the Internet Archive (interbank rate); "
                "IMF monetary surveys MFS_CBS, MFS_ODC and MFS_DC (liquidity); IMF CPI. NPR pegged at 1.6 per INR.")
else:
    repo, us = daily_rate(BIS_IN), daily_rate(BIS_US)
    m = csv("data/interim/india/india_macro_monthly.csv")
    m["month"] = pd.PeriodIndex(m["month"], freq="M").to_timestamp()
    fig = go.Figure()
    fig.add_scatter(x=repo.index, y=repo.values, name="RBI repo rate", line=dict(color=INK, shape="hv", width=2))
    fig.add_scatter(x=us.index, y=us.values, name="US policy rate", line=dict(color=SERIES[1], shape="hv", width=2))
    st.plotly_chart(style(fig, title="Policy rates, percent"), use_container_width=True, theme=None)
    fig = go.Figure()
    for i, (col, name) in enumerate([("cpi_yoy", "CPI combined inflation"), ("wpi_yoy", "WPI inflation")]):
        fig.add_scatter(x=m["month"], y=m[col], name=name, line=dict(color=SERIES[i], width=2))
    st.plotly_chart(style(fig, title="Inflation, percent year on year"), use_container_width=True, theme=None)
    fig = go.Figure()
    fig.add_scatter(x=m["month"], y=m["iip_yoy"], name="IIP growth", line=dict(color=SERIES[2], width=1.8))
    st.plotly_chart(style(fig, height=300, title="Industrial production (IIP), percent year on year "
                          "(2020 to 2021 swings are pandemic base effects)"), use_container_width=True, theme=None)
    st.markdown("Sources: RBI policy rate (BIS WS_CBPOL); MoSPI eSankhyiki API (CPI, WPI, IIP); IMF for CPI after "
                "December 2025. Lags used in models: CPI and WPI on the 15th of the next month, IIP two months later.")
