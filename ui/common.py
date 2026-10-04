"""Shared UI helpers: session state, guards, small widgets."""
from __future__ import annotations

from typing import List, Optional

import pandas as pd
import streamlit as st

from schemas import Project

STAB_COLORS = {"stable": "#16a34a", "moderately_sensitive": "#f59e0b", "sensitive": "#dc2626", "not_assessable": "#9ca3af"}
STAB_NAMES = {"stable": "Stable", "moderately_sensitive": "Moderately sensitive", "sensitive": "Sensitive",
              "not_assessable": "Not assessable"}
STAB_ICON = {"stable": "🟢", "moderately_sensitive": "🟡", "sensitive": "🔴", "not_assessable": "⚪"}

CAUSALITY_BANNER = ("**Association ≠ causation.** HypothesisX reports evidence-supported *hypotheses*. "
                    "Nothing here establishes that one variable causes another.")


def get_project() -> Project:
    if "project" not in st.session_state:
        st.session_state["project"] = Project()
    return st.session_state["project"]


def need_dataset() -> bool:
    p = get_project()
    if p.df is None:
        st.info("No dataset loaded yet. Go to **Dataset Upload** to load your data or the sample weather dataset.")
        return False
    return True


def need_hypotheses() -> bool:
    if not need_dataset():
        return False
    if not get_project().records:
        st.info("No hypotheses yet. Go to **Discovered Patterns** and **Hypotheses** to create some.")
        return False
    return True


def hyp_selector(key: str, label: str = "Hypothesis") -> Optional[str]:
    p = get_project()
    ids = list(p.records.keys())
    if not ids:
        return None
    fmt = {i: f"{i}: {p.records[i].hypothesis.statement}" for i in ids}
    return st.selectbox(label, ids, format_func=lambda i: fmt[i], key=key)


def show_plot(fig) -> None:
    st.plotly_chart(fig, use_container_width=True)


def show_df(df: pd.DataFrame) -> None:
    st.dataframe(df, use_container_width=True, hide_index=True)


def causality_banner() -> None:
    st.warning(CAUSALITY_BANNER)


def pipeline_status(rec) -> dict:
    return {"Statistics": bool(rec.statistical), "ML/DL": bool(rec.ml),
            "Robustness": bool(rec.robustness), "Evidence": bool(rec.evidence_report)}


def tick(b: bool) -> str:
    return "✅" if b else "—"
