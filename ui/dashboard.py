from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ui import state

SAMPLE = Path(__file__).resolve().parent.parent / "data" / "simulated_weather.xlsx"


def render_dashboard():
    st.title("HypothesisX AI")
    st.caption("Find patterns in your data, turn them into hypotheses, stress-test them and review the evidence. "
               "Results are evidence-supported hypotheses, not proven causes.")
    recs = list(st.session_state["records"].values())
    c = st.columns(4)
    df = st.session_state["df"]
    c[0].metric("Rows", 0 if df is None else len(df))
    c[1].metric("Findings", 0 if not st.session_state["discovery"] else len(st.session_state["discovery"]["findings"]))
    c[2].metric("Hypotheses", len(recs))
    c[3].metric("Robustness-tested", sum(bool(r.robustness_results) for r in recs))
    if recs:
        rows = [{"Hypothesis": r.id, "Statement": r.statement,
                 "Evidence": (r.evidence_report or {}).get("final_assessment", {}).get("label", "not reviewed")}
                for r in recs]
        st.dataframe(pd.DataFrame(rows))
    st.markdown("**Workflow:** 1 Upload -> 2 Explore -> 3 Mine patterns -> 4 Hypotheses -> "
                "5 Statistical + ML tests -> 6 Robustness -> 7 Evidence -> 8 Final report")


def render_upload():
    st.header("Dataset Upload")
    up = st.file_uploader("Excel file (.xlsx / .xls)", type=["xlsx", "xls"])
    if up is not None and st.button("Load uploaded file"):
        try:
            state.load_excel_source(up, up.name)
        except Exception as exc:
            st.error(str(exc))
    if SAMPLE.exists() and st.button("Load bundled weather sample"):
        state.load_excel_source(SAMPLE, SAMPLE.name)
    st.checkbox("Use hold-out confirmation (find patterns on one random half, test on the other)",
                key="use_holdout")
    if st.session_state["df"] is not None:
        q = st.session_state["quality"]
        st.success(f"Loaded {st.session_state['source_name']}: {q['n_rows']} rows, {q['n_cols']} columns. "
                   f"Date column: {st.session_state['date_col'] or 'none detected'}.")
        for issue in q["issues"]:
            st.warning(issue)
        st.dataframe(st.session_state["df"].head(20))


def render_exploration():
    st.header("Data Exploration")
    if state.need_data():
        return
    df = st.session_state["df"]
    num = [c for c in df.select_dtypes(include=[np.number]).columns if c != "time_index"]
    st.subheader("Summary statistics")
    st.dataframe(df[num].describe().T)
    miss = df.isna().sum()
    st.caption("Missing values: " + (", ".join(f"{k}={v}" for k, v in miss.items() if v) or "none"))
    st.subheader("Correlation matrix (Spearman)")
    st.plotly_chart(px.imshow(df[num].corr(method="spearman"), zmin=-1, zmax=1,
                              color_continuous_scale="RdBu_r", aspect="auto"))
    a, b = st.columns(2)
    x = a.selectbox("X variable", num, index=0)
    y = b.selectbox("Y variable", num, index=min(1, len(num) - 1))
    d = df[[x, y]].dropna()
    fig = go.Figure(go.Scatter(x=d[x], y=d[y], mode="markers", marker=dict(opacity=0.5), name="data"))
    if len(d) > 2 and x != y:
        m, c0 = np.polyfit(d[x], d[y], 1)
        xs = np.linspace(d[x].min(), d[x].max(), 50)
        fig.add_trace(go.Scatter(x=xs, y=m * xs + c0, mode="lines", name="linear fit"))
    fig.update_layout(xaxis_title=x, yaxis_title=y)
    st.plotly_chart(fig)
    st.plotly_chart(px.histogram(df, x=x, nbins=40, title=f"Distribution of {x}"))
