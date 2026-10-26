import streamlit as st

from common import csv, text

st.title("Variable ledger")
st.caption("Every variable considered, used or left out, and why. Source: data/source_registry/variable_registry.csv.")
v = csv("data/source_registry/variable_registry.csv")
c = st.columns(3)
country = c[0].multiselect("Country", sorted(v["country"].dropna().unique()))
status = c[1].multiselect("Status", sorted(v["status"].dropna().unique()))
q = c[2].text_input("Search")
f = v
if country:
    f = f[f["country"].isin(country)]
if status:
    f = f[f["status"].isin(status)]
if q:
    f = f[f.astype(str).apply(lambda r: q.lower() in " ".join(r).lower(), axis=1)]
st.write(f"{len(f)} of {len(v)} variables")
st.dataframe(f[["variable_id", "country", "family", "variable", "proposed_role", "status", "reason",
                "source_institution", "publication_lag_note"]], hide_index=True, use_container_width=True)
st.subheader("Count by status")
st.dataframe(v.groupby(["country", "status"]).size().unstack(fill_value=0), use_container_width=True)
with st.expander("Change history and reasons (docs/variable_log.md)"):
    st.markdown(text("docs/variable_log.md"))
