"""Dataset Upload and Data Exploration pages."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from agents import pipeline as P
from analysis.preprocessing import DatasetValidationError, numeric_columns
from ui.common import get_project, need_dataset, show_df, show_plot


def render_upload() -> None:
    st.header("Dataset Upload")
    p = get_project()
    st.write("Upload a CSV or Excel file with at least two numeric columns (≥ 30 rows). "
             "Missing values are never imputed silently: each analysis drops incomplete rows and reports how many.")
    up = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx", "xls"], key="upload_file")
    c1, c2 = st.columns(2)
    use_sample = c1.button("Use sample weather dataset", key="use_sample")
    if up is not None and c2.button("Load uploaded file", key="load_upload"):
        try:
            df = P.read_table(up, up.name)
            P.load_into_project(p, df, up.name)
            st.success(f"Loaded {up.name}.")
        except (DatasetValidationError, ValueError) as e:
            st.error(f"Could not load dataset: {e}")
        except Exception as e:
            st.error(f"Unexpected error reading the file: {type(e).__name__}: {e}")
    if use_sample:
        try:
            P.load_into_project(p, pd.read_excel(P.SAMPLE_PATH), "simulated_weather.xlsx")
            st.success("Loaded the sample dataset (simulated weather, 1,000 daily rows).")
        except Exception as e:
            st.error(f"Could not load the sample dataset: {type(e).__name__}: {e}")

    if p.df is None:
        return
    v = p.validation
    st.subheader(f"Current dataset: {p.dataset_name}")
    c = st.columns(4)
    c[0].metric("Rows", f"{v['n_rows']:,}")
    c[1].metric("Columns", v["n_cols"])
    c[2].metric("Numeric columns", len(v["numeric_columns"]))
    c[3].metric("Time column", v["time_column"] or "none")
    if "simulated" in p.dataset_name.lower():
        st.info("The file name suggests this dataset is **simulated**. Relationships reflect how it was generated, "
                "not necessarily real-world phenomena.")
    for w in v["warnings"]:
        st.warning(w)
    if not v["warnings"]:
        st.success("No data-quality warnings.")
    st.dataframe(p.df.head(20), use_container_width=True)


def render_exploration() -> None:
    st.header("Data Exploration")
    if not need_dataset():
        return
    p = get_project()
    df, tc = p.df, p.time_col
    num = numeric_columns(df, exclude=[tc] if tc else [])

    t1, t2, t3, t4 = st.tabs(["Summary", "Distributions", "Correlations", "Over time"])
    with t1:
        desc = df[num].describe().T
        desc["missing"] = df[num].isna().sum()
        desc["skew"] = df[num].skew()
        st.dataframe(desc.round(3), use_container_width=True)
    with t2:
        col = st.selectbox("Variable", num, key="explore_hist_col")
        fig = go.Figure(go.Histogram(x=df[col].dropna(), nbinsx=40, marker_color="#2563eb"))
        fig.update_layout(title=f"Distribution of {col}", xaxis_title=col, yaxis_title="Count", bargap=0.05)
        show_plot(fig)
        zeros = float((df[col] == 0).mean() * 100)
        if zeros > 50:
            st.warning(f"{zeros:.0f}% of '{col}' values are zero (zero-inflated).")
    with t3:
        method = st.radio("Method", ["spearman", "pearson"], horizontal=True, key="explore_corr_method")
        cm = df[num].corr(method=method)
        fig = go.Figure(go.Heatmap(z=cm.values, x=cm.columns, y=cm.index, zmin=-1, zmax=1, colorscale="RdBu",
                                   text=cm.round(2).values, texttemplate="%{text}"))
        fig.update_layout(title=f"{method.title()} correlation matrix", height=600)
        show_plot(fig)
        st.caption("Correlation shows association only; it cannot show which variable influences which.")
    with t4:
        if not tc:
            st.info("No time column was detected.")
        else:
            cols = st.multiselect("Variables", num, default=num[:1], key="explore_ts_cols")
            fig = go.Figure()
            for c in cols:
                fig.add_trace(go.Scatter(x=df[tc], y=df[c], mode="lines", name=c))
            fig.update_layout(title="Variables over time", xaxis_title=tc)
            show_plot(fig)
