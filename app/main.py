"""RateCycle India Nepal dashboard. Run locally: streamlit run app/main.py"""

import streamlit as st

st.set_page_config(page_title="RateCycle India Nepal", layout="wide")

pages = [
    st.Page("views/overview.py", title="Overview", default=True),
    st.Page("views/data.py", title="Data explorer"),
    st.Page("views/variables.py", title="Variable ledger"),
    st.Page("views/events.py", title="Political events"),
    st.Page("views/models.py", title="Models (training period)"),
    st.Page("views/blind.py", title="Blind backtest"),
    st.Page("views/transmission.py", title="India to Nepal transmission"),
    st.Page("views/scenarios.py", title="Scenarios"),
    st.Page("views/outlook.py", title="Next two years"),
    st.Page("views/methods.py", title="Methods and limitations"),
]
st.navigation(pages).run()
