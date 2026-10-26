import streamlit as st

from common import text

st.title("Methods and limitations")

st.subheader("How overfitting and leakage were controlled")
st.markdown("""
* **Point in time features.** Every input is joined on its publication date with conservative lags; tests assert no feature is dated after its cutoff.
* **Walk forward validation.** Expanding window, models refit at every decision on outcomes already public; a five month embargo for Nepal's overlapping labels.
* **Specifications declared before running** (decision log), so feature choice was never searched on validation results; regularisation strength chosen by an inner walk forward and the one standard error rule.
* **Sealed blind window.** November 2021 to October 2026 stayed sealed until the configuration was frozen with a hash; the unblinding script refuses to run otherwise.
* **Significance.** Block bootstrap intervals, Diebold Mariano tests with the small sample correction, and a circular permutation test.
* **Stability.** Coefficient signs must hold in 80 percent of windows; accuracy reported by three year block; byte identical replication.
""")

st.subheader("Limitations")
st.markdown("""
* 31 blind RBI decisions give wide intervals; the gain over persistence is not statistically significant.
* Data are the latest revised vintages except where release dates were applied; real time vintages were not available for most series.
* IIP covers industry only and swings on base effects, so the growth gap is a weak output gap proxy.
* The repo rate misses non rate tools (MSF, liquidity operations, FX intervention), for example the 2013 rupee defence.
* Nepal's NRB moved too rarely to score its decisions; the interbank rate is used instead, and the NRB website was unavailable during collection.
* Transmission estimates rest on about six RBI cycles; signs can reflect coincident timing.
""")

for title, path in [("Decision log", "docs/decision_log.md"), ("Research protocol", "docs/research_protocol.md"),
                    ("Economic interpretation", "reports/economic_interpretation.md"),
                    ("Blind test results", "reports/blind_test_results.md"),
                    ("Event coding guide", "docs/event_coding_guide.md"),
                    ("Data access", "docs/data_access.md")]:
    with st.expander(title):
        st.markdown(text(path))
