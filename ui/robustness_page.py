from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from agents.robustness_agent import RobustnessAgent
from ui import state

COLORS = {"stable": "#2e7d32", "moderately_sensitive": "#f9a825", "unstable": "#c62828", "not_assessable": "#757575"}


def _table(rs):
    rows = []
    for r in rs:
        o = r["original_result"] or {}
        rel = None
        if r["coefficient"] is not None and o.get("coef"):
            rel = (r["coefficient"] - o["coef"]) / abs(o["coef"])
        rows.append({"test": r["test"], "method": r["method"], "coefficient": r["coefficient"],
                     "change vs original": rel, "p-value": r["p_value"], "CI low": r["ci_low"],
                     "CI high": r["ci_high"], "effect size": r["effect_size"], "direction": r["direction"],
                     "stability": r["stability"], "changed materially": r["changed_materially"]})
    return pd.DataFrame(rows)


def render_robustness():
    st.header("Robustness Testing")
    st.caption("Does the relationship survive different samples, outlier handling, models and added variables? "
               "Each test explains what changed instead of giving a good/bad score.")
    if state.need_data():
        return
    rec = state.pick_record()
    if rec is None:
        return
    if st.button("Run robustness tests"):
        if not rec.statistical_results:
            state.get_agent().analyze(rec, state.testing_df(), st.session_state["date_col"], stages=("stats",))
        with st.spinner("Running bootstrap, subsamples, cross-validation, outliers, alternative models..."):
            state.get_agent().analyze(rec, state.testing_df(), st.session_state["date_col"], stages=("robustness",))
    rs = rec.robustness_results
    if not rs:
        return
    c = RobustnessAgent.summary(rs)
    m = st.columns(4)
    m[0].metric("Tests run", c["total"])
    m[1].metric("Stable", c["stable"])
    m[2].metric("Sensitive", c["sensitive"])
    m[3].metric("Not assessable", c["not_assessable"])

    tab = _table(rs)
    ok = [r for r in rs if r["coefficient"] is not None]
    tabs = st.tabs(["Test-by-test", "Coefficients", "P-values", "Model performance", "Distributions"])
    with tabs[0]:
        st.dataframe(tab)
        for r in rs:
            with st.expander(f"{r['test']}: {r['stability']}"):
                st.write(r["interpretation"])
                st.json(r["configuration"])
    with tabs[1]:
        orig = rs[0]["original_result"].get("coef") if rs[0]["original_result"] else None
        fig = go.Figure()
        for r in reversed(ok):
            err = None
            if r["ci_low"] is not None and r["ci_high"] is not None:
                err = dict(type="data", symmetric=False, array=[r["ci_high"] - r["coefficient"]],
                           arrayminus=[r["coefficient"] - r["ci_low"]])
            fig.add_trace(go.Scatter(x=[r["coefficient"]], y=[r["test"]], mode="markers", error_x=err,
                                     marker=dict(size=9, color=COLORS[r["stability"]]), showlegend=False))
        fig.add_vline(x=0, line_dash="dot")
        if orig is not None:
            fig.add_vline(x=orig, line_color="black", annotation_text="original")
        fig.update_layout(height=max(350, 28 * len(ok)), xaxis_title="coefficient (95% interval where available)")
        st.plotly_chart(fig)
        st.caption("Colour: green stable, amber moderately sensitive, red unstable. The rank-regression estimate is on "
                   "a different scale; only its direction and significance are compared.")
    with tabs[2]:
        p = tab.dropna(subset=["p-value"])
        st.plotly_chart(go.Figure(go.Bar(x=p["test"], y=p["p-value"])).update_layout(
            yaxis_type="log", yaxis_title="p-value (log scale)"))
        st.caption("Bootstrap and subsample p-values are approximate resampling values, not model-based.")
    with tabs[3]:
        perf = [{"test": r["test"], **r["model_performance"]} for r in rs if r["model_performance"]]
        st.dataframe(pd.DataFrame(perf)) if perf else st.write("No performance metrics recorded.")
    with tabs[4]:
        for r in rs:
            dist = (r["modified_result"] or {}).get("distribution")
            if dist:
                f = go.Figure(go.Histogram(x=dist, nbinsx=40))
                if r["original_result"]:
                    f.add_vline(x=r["original_result"]["coef"], line_color="black")
                f.add_vline(x=0, line_dash="dot")
                f.update_layout(title=r["test"], xaxis_title="coefficient")
                st.plotly_chart(f)
