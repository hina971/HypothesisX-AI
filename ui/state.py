"""Streamlit session state: one place that holds the dataset, findings and hypothesis records."""
from __future__ import annotations

import streamlit as st

from agents.hypothesisx_agent import HypothesisXAgent, load_excel
from schemas import RobustnessConfig


def init_state():
    defaults = {"df": None, "date_col": None, "quality": None, "disc_df": None, "conf_df": None,
                "discovery": None, "records": {}, "cfg": RobustnessConfig(), "use_holdout": True,
                "source_name": None}
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def get_agent() -> HypothesisXAgent:
    return HypothesisXAgent(st.session_state["cfg"], st.session_state["use_holdout"])


def load_dataframe(raw, name: str):
    agent = get_agent()
    df, date_col, quality = agent.prepare(raw)
    st.session_state.update(df=df, date_col=date_col, quality=quality, source_name=name,
                            discovery=None, records={}, disc_df=None, conf_df=None)


def load_excel_source(source, name: str):
    load_dataframe(load_excel(source), name)


def testing_df():
    return st.session_state["conf_df"] if st.session_state["conf_df"] is not None else st.session_state["df"]


def need_data() -> bool:
    if st.session_state["df"] is None:
        st.info("Load a dataset first (page: Dataset Upload).")
        return True
    return False


def pick_record(label="Choose a hypothesis"):
    recs = st.session_state["records"]
    if not recs:
        st.info("No hypotheses yet. Create them on the Discovered Patterns or Hypotheses page.")
        return None
    rid = st.selectbox(label, list(recs), format_func=lambda i: f"{i}: {recs[i].statement}")
    return recs[rid]
