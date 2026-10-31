import streamlit as st

from common import LABEL, table

st.title("RateCycle India Nepal")
st.caption("Predicting RBI and NRB policy cycles and India to Nepal transmission under the NPR/INR peg. "
           "Macroeconomics course project; all data free and official; every number traceable to reports/tables.")

bi = table("blind_india_metrics").set_index("model")
bn = table("blind_nepal_metrics").set_index("model")
sa = table("suggestions_blind_agreement").set_index("source")
st.subheader("Blind test, November 2021 to October 2026 (sealed until the configuration was frozen)")
c = st.columns(4)
c[0].metric("RBI decisions called correctly", f"{sa.at['classifier', 'hit_rate_all']:.0%}",
            help="Economic ordered probit, refit in real time, 31 decisions")
c[1].metric("Balanced accuracy, India", f"{bi.at['ordered_probit_economic', 'balanced_accuracy']:.2f}",
            f"{bi.at['ordered_probit_economic', 'balanced_accuracy'] - bi.at['persistence', 'balanced_accuracy']:+.2f} vs persistence")
c[2].metric("Balanced accuracy, Nepal", f"{bn.at['ordered_probit_liquidity', 'balanced_accuracy']:.2f}",
            f"{bn.at['ordered_probit_liquidity', 'balanced_accuracy'] - bn.at['persistence', 'balanced_accuracy']:+.2f} vs persistence")
c[3].metric("Textbook Taylor rule hit rate", f"{sa.at['taylor', 'hit_rate_all']:.0%}", help="Normative reference only")

st.subheader("What we found")
st.markdown("""
* **The RBI is inertial and forecast targeting.** It moves on revisions to its own inflation projection and on the gap from its nominal anchor; the previous decision is the strongest single predictor. The reaction function learned on 2002 to 2021 called 77 percent of decisions from 2022 to 2026.
* **Turning points are the hard part.** The model calls each new cycle one meeting late, in training and out of sample: the signature of interest rate smoothing.
* **Under the peg, Nepal's interbank rate is a liquidity price.** Reserve inflows lower it and government deposits at the NRB raise it. It followed the RBI in only 6 of 12 cycles, a coin flip. India's cycle reaches Nepal instead through prices, which the peg imports, and through the NRB's own policy rate, which since the 2016 corridor moves about 0.5 point per RBI point (p 0.007, decision D056).
* **Political events add nothing** beyond the fiscal and liquidity variables already in the models.
""")

st.subheader("Research questions and status")
st.table({
    "Question": ["RQ1 Predict RBI and NRB decisions", "RQ2 Political events", "RQ3 RBI stance for Nepal",
                 "RQ4 Peg and transmission", "RQ5 Regime differences", "RQ6 Policy scenarios"],
    "Status": ["Done: blind test run", "Done: no added value (H2 not rejected)",
               "Done: no significant gain (H3 not supported)",
               "Done: market rate a coin flip; NRB rate 0.5 per RBI point since 2016; prices follow",
               "Partly: stability by block and liquidity states", "Done: conditional scenario page"],
})

st.subheader("How to read labels")
for label, colour in LABEL.values():
    st.markdown(f"<span style='color:{colour}'>&#9632;</span> **{label}**", unsafe_allow_html=True)
