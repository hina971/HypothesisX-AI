"""HypothesisX AI - run with:  streamlit run app.py"""
import streamlit as st

st.set_page_config(page_title="HypothesisX AI", layout="wide")

from ui import state
from ui.analysis_pages import (render_hypotheses, render_ml, render_patterns, render_statistical)
from ui.dashboard import render_dashboard, render_exploration, render_upload
from ui.discovery_page import render_discovery
from ui.evidence_page import render_evidence
from ui.robustness_page import render_robustness

PAGES = {
    "Dashboard": render_dashboard, "Dataset Upload": render_upload, "Data Exploration": render_exploration,
    "Discovered Patterns": render_patterns, "Hypotheses": render_hypotheses,
    "Statistical Testing": render_statistical, "ML/DL Validation": render_ml,
    "Robustness Testing": render_robustness, "Evidence Review": render_evidence,
    "Final Discovery Report": render_discovery,
}

state.init_state()
choice = st.sidebar.radio("Navigate", list(PAGES))
with st.sidebar.expander("Settings"):
    cfg = st.session_state["cfg"]
    cfg.alpha = st.number_input("Significance level (alpha)", 0.001, 0.2, cfg.alpha, 0.01)
    cfg.tolerance = st.slider("Stability tolerance (relative coefficient change)", 0.05, 0.75, cfg.tolerance)
    cfg.n_boot = st.select_slider("Bootstrap resamples", [200, 500, 1000, 2000], cfg.n_boot)
    cfg.seed = int(st.number_input("Random seed", 0, 99999, cfg.seed))
PAGES[choice]()
