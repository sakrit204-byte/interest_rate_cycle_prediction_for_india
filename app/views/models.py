import plotly.graph_objects as go
import streamlit as st

from common import INK, MUTED, SERIES, badge, metrics_view, style, table

st.title("Models on the training period")
badge("predicted")
st.caption("Walk forward, expanding window: each decision or month is predicted only from information public "
           "before it. Training period ends 31 October 2021; nothing here uses the blind window.")

india, nepal, stability = st.tabs(["India (RBI)", "Nepal (interbank)", "Stability and replication"])

with india:
    st.subheader("Reaction function: what moves the RBI")
    badge("estimated")
    rf = table("india_reaction_function_economic")
    rf = rf.sort_values("ame_p_hike_pp")
    fig = go.Figure(go.Bar(x=rf["ame_p_hike_pp"], y=rf["meaning"].fillna(rf["variable"]), orientation="h",
                           marker=dict(color=[SERIES[0] if p < 0.1 else MUTED for p in rf["p_value"]]),
                           customdata=rf["p_value"], hovertemplate="%{x:.1f} pp, p = %{customdata:.3f}<extra></extra>"))
    st.plotly_chart(style(fig, height=320, title="Effect on P(hike) of a one unit rise, percentage points "
                          "(blue: p below 0.10)", hovermode="closest"), use_container_width=True, theme=None)
    st.markdown("Ordered probit on 115 decisions, 2002 to 2021. Smoothing (previous decision) and news in the RBI's "
                "own inflation projection dominate; the realized gap from the regime's nominal anchor matters at the "
                "margin. The projected gap has a negative sign because RBI projections are conditional on its own "
                "planned policy.")
    st.subheader("Three model generations, each declared before it was run")
    for name, label in [("walk_forward_train_metrics", "Model 1: realized inflation (80 decisions)"),
                        ("walk_forward_train_projection_metrics", "Model 2: adds hand coded RBI projections (75)"),
                        ("walk_forward_train_econ_metrics", "Model 3: gaps from the nominal anchor (75)")]:
        st.markdown(f"**{label}**")
        st.dataframe(metrics_view(table(name)), hide_index=True, use_container_width=True)
    st.markdown("**Permutation test** (labels shifted in time 96 ways): is the skill real?")
    st.dataframe(table("permutation_test").round(3), hide_index=True, use_container_width=True)
    st.markdown("**Diebold Mariano tests, model 3**")
    st.dataframe(table("walk_forward_train_econ_dm").round(3), hide_index=True, use_container_width=True)

with nepal:
    st.markdown("Target: direction of the seasonally adjusted interbank rate over three months "
                "(down, flat or up, deadband 0.5 points).")
    st.markdown("**Model 1: policy style variables (179 months)**")
    st.dataframe(metrics_view(table("nepal_walk_forward_train_metrics")), hide_index=True, use_container_width=True)
    st.markdown("**Model 2: liquidity under the peg (157 months)**")
    st.dataframe(metrics_view(table("nepal_walk_forward_train_liquidity_metrics")), hide_index=True,
                 use_container_width=True)
    st.markdown("**Diebold Mariano tests. First row: the transmission test (with against without the India repo).**")
    st.dataframe(table("nepal_walk_forward_train_liquidity_dm").round(3), hide_index=True, use_container_width=True)
    sf = table("nepal_seasonal_factors")
    fig = go.Figure(go.Bar(x=sf.iloc[:, 0], y=sf.iloc[:, 1], marker_color=SERIES[0]))
    st.plotly_chart(style(fig, height=280, title="Seasonal effect on the interbank rate by calendar month, points",
                          hovermode="closest"), use_container_width=True, theme=None)

with stability:
    st.markdown("A learned relationship counts only if its sign holds in at least 80 percent of walk forward "
                "windows (decision D031).")
    st.dataframe(table("stability_coefficients").round(3), hide_index=True, use_container_width=True)
    b = table("stability_accuracy_by_block")
    for country in ("india", "nepal"):
        g = b[b["country"] == country]
        fig = go.Figure()
        fig.add_bar(x=g["block"], y=g["model_bal_acc"], name="Primary model", marker_color=SERIES[0])
        fig.add_bar(x=g["block"], y=g["benchmark_bal_acc"], name="Persistence", marker_color=MUTED)
        fig.add_hline(y=1 / 3, line=dict(color=INK, dash="dot", width=1), annotation_text="chance")
        st.plotly_chart(style(fig, height=300, title=f"{country.title()}: balanced accuracy by three year block",
                              barmode="group", bargap=0.3, bargroupgap=0.08), use_container_width=True, theme=None)
    st.markdown("**Replication**: rebuilding features and predictions from the raw files gives byte identical "
                "outputs. Check with `python -m src.validation.stability --check`.")
    st.dataframe(table("reproducibility_hashes"), hide_index=True, use_container_width=True)
