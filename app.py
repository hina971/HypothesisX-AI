"""HypothesisX AI - run with: streamlit run app.py"""

import streamlit as st

st.set_page_config(
    page_title="HypothesisX AI",
    page_icon="🧠",
    layout="wide"
)

# ============================================================
# HEADER
# ============================================================

st.title("🧠 HypothesisX AI")
st.subheader("Intelligent Hypothesis Generation & Scientific Reasoning")

st.write(
    "Find patterns in your data, turn them into hypotheses, "
    "stress-test them and review the evidence. "
    "Results are evidence-supported hypotheses, not proven causes."
)

st.divider()


# ============================================================
# IMPORT EXISTING PROJECT
# ============================================================

from ui import state

from ui.analysis_pages import (
    render_hypotheses,
    render_ml,
    render_patterns,
    render_statistical
)

from ui.dashboard import (
    render_dashboard,
    render_exploration,
    render_upload
)

from ui.discovery_page import render_discovery
from ui.evidence_page import render_evidence
from ui.robustness_page import render_robustness


# ============================================================
# PAGES
# ============================================================

PAGES = {
    "Dashboard": render_dashboard,
    "Dataset Upload": render_upload,
    "Data Exploration": render_exploration,
    "Discovered Patterns": render_patterns,
    "Hypotheses": render_hypotheses,
    "Statistical Testing": render_statistical,
    "ML/DL Validation": render_ml,
    "Robustness Testing": render_robustness,
    "Evidence Review": render_evidence,
    "Final Discovery Report": render_discovery,
}


# ============================================================
# STATE
# ============================================================

state.init_state()


# ============================================================
# SIDEBAR
# ============================================================

choice = st.sidebar.radio(
    "Navigate",
    list(PAGES)
)

with st.sidebar.expander("Settings"):

    cfg = st.session_state["cfg"]

    cfg.alpha = st.number_input(
        "Significance level (alpha)",
        0.001,
        0.2,
        cfg.alpha,
        0.01
    )

    cfg.tolerance = st.slider(
        "Stability tolerance (relative coefficient change)",
        0.05,
        0.75,
        cfg.tolerance
    )

    cfg.n_boot = st.select_slider(
        "Bootstrap resamples",
        [200, 500, 1000, 2000],
        cfg.n_boot
    )

    cfg.seed = int(
        st.number_input(
            "Random seed",
            0,
            99999,
            cfg.seed
        )
    )


# ============================================================
# SHOW SELECTED PAGE
# ============================================================

PAGES[choice]()


# ============================================================
# TEAM
# ============================================================

st.divider()

st.header("👥 Meet the Team")
st.write("Developed by Hina Ramzan & Team")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("👑 Hina Ramzan")
    st.caption("Team Leader")

with col2:
    st.subheader("💡 Fayaz Ali")
    st.caption("Team Member")

with col3:
    st.subheader("🔬 Moin Afzal")
    st.caption("Team Member")


col4, col5, col6 = st.columns(3)

with col4:
    st.subheader("⚡ Shabab Ali")
    st.caption("Team Member")

with col5:
    st.subheader("🚀 Arbab Ali")
    st.caption("Team Member")

with col6:
    st.subheader("🧠 Absar Ahmed")
    st.caption("Team Member")


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption("🧠 HypothesisX AI")
st.caption("Developed by Hina Ramzan & Team")
st.caption("✦ Intelligent • Scientific • Data-Driven ✦")
st.caption("© 2026 HypothesisX AI • Scientific Discovery Platform")
