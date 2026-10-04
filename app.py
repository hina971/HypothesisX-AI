"""HypothesisX AI - run with: streamlit run app.py"""

import streamlit as st

st.set_page_config(
    page_title="HypothesisX AI",
    page_icon="🧠",
    layout="wide"
)


# ============================================================
# UI STYLING
# ============================================================

st.markdown(
    """
    <style>

    /* MAIN HEADER */
    .hx-header {
        padding: 30px;
        margin-bottom: 30px;
        border-radius: 22px;
        text-align: center;
        background: linear-gradient(
            120deg,
            #eef2ff,
            #f5e8ff,
            #fce7f3,
            #e0f7fa
        );
        border: 1px solid #ddd6fe;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.12);
    }

    .hx-title {
        font-size: 44px;
        font-weight: 900;
        color: #4f46e5;
        margin-bottom: 8px;
    }

    .hx-subtitle {
        font-size: 17px;
        color: #475569;
        font-weight: 500;
    }


    /* TEAM SECTION */
    .team-heading {
        margin-top: 55px;
        text-align: center;
        font-size: 30px;
        font-weight: 900;
        color: #6366f1;
    }

    .team-subheading {
        text-align: center;
        color: #64748b;
        margin-top: 6px;
        margin-bottom: 25px;
        font-size: 15px;
    }

    .team-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 18px;
        max-width: 1000px;
        margin: 0 auto;
    }

    .team-card {
        text-align: center;
        padding: 25px 15px;
        border-radius: 20px;
        background: #ffffff;
        border: 1px solid #ddd6fe;
        box-shadow: 0 8px 25px rgba(15, 23, 42, 0.08);
    }

    .member-icon {
        font-size: 34px;
        margin-bottom: 8px;
    }

    .member-name {
        font-size: 18px;
        font-weight: 800;
        color: #1e293b;
    }

    .member-role {
        margin-top: 5px;
        font-size: 13px;
        font-weight: 700;
        color: #7c3aed;
    }


    /* FOOTER */
    .hx-footer {
        margin-top: 60px;
        padding: 30px 20px;
        text-align: center;
        border-radius: 22px;
        background: linear-gradient(
            120deg,
            #eef2ff,
            #f5e8ff,
            #fce7f3,
            #e0f7fa
        );
        border: 1px solid #ddd6fe;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.10);
    }

    .footer-title {
        font-size: 25px;
        font-weight: 900;
        color: #6366f1;
    }

    .footer-text {
        margin-top: 7px;
        color: #475569;
        font-size: 14px;
    }

    .footer-tagline {
        margin-top: 12px;
        font-size: 14px;
        font-weight: 700;
        color: #8b5cf6;
    }

    .footer-copy {
        margin-top: 12px;
        font-size: 12px;
        color: #94a3b8;
    }


    /* MOBILE */
    @media (max-width: 700px) {

        .hx-title {
            font-size: 34px;
        }

        .hx-subtitle {
            font-size: 14px;
        }

        .team-grid {
            grid-template-columns: 1fr;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hx-header">
        <div class="hx-title">
            🧠 HypothesisX AI
        </div>

        <div class="hx-subtitle">
            Intelligent Hypothesis Generation &amp; Scientific Reasoning
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


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
# TEAM SECTION
# ============================================================

st.markdown(
    """
    <div class="team-heading">
        👥 Meet the Team
    </div>

    <div class="team-subheading">
        Developed by Hina Ramzan &amp; Team
    </div>

    <div class="team-grid">

        <div class="team-card">
            <div class="member-icon">👑</div>
            <div class="member-name">Hina Ramzan</div>
            <div class="member-role">Team Leader</div>
        </div>

        <div class="team-card">
            <div class="member-icon">💡</div>
            <div class="member-name">Fayaz Ali</div>
            <div class="member-role">Team Member</div>
        </div>

        <div class="team-card">
            <div class="member-icon">🔬</div>
            <div class="member-name">Moin Afzal</div>
            <div class="member-role">Team Member</div>
        </div>

        <div class="team-card">
            <div class="member-icon">⚡</div>
            <div class="member-name">Shabab Ali</div>
            <div class="member-role">Team Member</div>
        </div>

        <div class="team-card">
            <div class="member-icon">🚀</div>
            <div class="member-name">Arbab Ali</div>
            <div class="member-role">Team Member</div>
        </div>

        <div class="team-card">
            <div class="member-icon">🧠</div>
            <div class="member-name">Absar Ahmed</div>
            <div class="member-role">Team Member</div>
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="hx-footer">

        <div class="footer-title">
            🧠 HypothesisX AI
        </div>

        <div class="footer-text">
            Developed by <strong>Hina Ramzan &amp; Team</strong>
        </div>

        <div class="footer-tagline">
            ✦ Intelligent • Scientific • Data-Driven ✦
        </div>

        <div class="footer-copy">
            © 2026 HypothesisX AI • Scientific Discovery Platform
        </div>

    </div>
    """,
    unsafe_allow_html=True
)
