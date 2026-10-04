"""HypothesisX AI - run with: streamlit run app.py"""

import streamlit as st

st.set_page_config(
    page_title="HypothesisX AI",
    page_icon="🧠",
    layout="wide"
)


# ============================================================
# STYLISH HYPOXESISX AI HEADER + TEAM UI
# ============================================================

st.markdown(
    """
    <style>

    /* ================= HEADER ================= */

    .hx-header {
        text-align: center;
        padding: 32px 20px 28px 20px;
        margin-bottom: 25px;
        border-radius: 24px;
        background: linear-gradient(
            135deg,
            rgba(99,102,241,0.15),
            rgba(168,85,247,0.15),
            rgba(236,72,153,0.12),
            rgba(6,182,212,0.12)
        );
        border: 1px solid rgba(139,92,246,0.25);
        box-shadow: 0 10px 35px rgba(99,102,241,0.12);
    }

    .hx-title {
        font-size: 52px;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(
            90deg,
            #6366f1,
            #8b5cf6,
            #ec4899,
            #06b6d4,
            #6366f1
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 300% 300%;
        animation: gradientMove 5s ease infinite;
    }

    .hx-subtitle {
        font-size: 17px;
        margin-top: 10px;
        color: #64748b;
        letter-spacing: 1px;
    }

    @keyframes gradientMove {
        0% {
            background-position: 0% 50%;
        }

        50% {
            background-position: 100% 50%;
        }

        100% {
            background-position: 0% 50%;
        }
    }


    /* ================= TEAM ================= */

    .team-heading {
        text-align: center;
        font-size: 30px;
        font-weight: 800;
        margin-top: 55px;
        margin-bottom: 8px;
    }

    .team-subheading {
        text-align: center;
        color: #64748b;
        margin-bottom: 28px;
        font-size: 15px;
    }

    .team-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 18px;
        max-width: 950px;
        margin: auto;
    }


    /* ================= TEAM CARDS ================= */

    .team-card {
        position: relative;
        padding: 23px 15px;
        text-align: center;
        border-radius: 20px;
        background: rgba(255,255,255,0.78);
        border: 1px solid rgba(139,92,246,0.18);
        box-shadow: 0 8px 25px rgba(15,23,42,0.08);
        transition: all 0.35s ease;
        animation: cardFloat 3.5s ease-in-out infinite;
        overflow: hidden;
    }

    .team-card:nth-child(2) {
        animation-delay: 0.25s;
    }

    .team-card:nth-child(3) {
        animation-delay: 0.50s;
    }

    .team-card:nth-child(4) {
        animation-delay: 0.75s;
    }

    .team-card:nth-child(5) {
        animation-delay: 1.00s;
    }

    .team-card:nth-child(6) {
        animation-delay: 1.25s;
    }

    .team-card:hover {
        transform: translateY(-10px) scale(1.03);
        box-shadow: 0 18px 40px rgba(99,102,241,0.22);
        border-color: rgba(139,92,246,0.45);
    }

    .team-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 3px;
        background: linear-gradient(
            90deg,
            #6366f1,
            #8b5cf6,
            #ec4899,
            #06b6d4
        );
        animation: shine 3s linear infinite;
    }

    @keyframes shine {
        0% {
            left: -100%;
        }

        100% {
            left: 100%;
        }
    }

    @keyframes cardFloat {
        0%, 100% {
            transform: translateY(0px);
        }

        50% {
            transform: translateY(-5px);
        }
    }

    .member-icon {
        font-size: 30px;
        margin-bottom: 8px;
    }

    .member-name {
        font-size: 17px;
        font-weight: 700;
        color: #1e293b;
    }

    .member-role {
        margin-top: 5px;
        font-size: 13px;
        color: #8b5cf6;
        font-weight: 600;
    }


    /* ================= FOOTER ================= */

    .hx-footer {
        text-align: center;
        margin-top: 55px;
        padding: 28px 15px;
        border-radius: 22px;
        background: linear-gradient(
            135deg,
            rgba(99,102,241,0.10),
            rgba(236,72,153,0.10)
        );
        border-top: 1px solid rgba(139,92,246,0.18);
    }

    .footer-title {
        font-size: 22px;
        font-weight: 800;
        color: #6366f1;
    }

    .footer-text {
        color: #64748b;
        font-size: 14px;
        margin-top: 6px;
    }


    /* ================= MOBILE ================= */

    @media (max-width: 700px) {

        .hx-title {
            font-size: 38px;
        }

        .team-grid {
            grid-template-columns: 1fr;
        }

    }

    </style>


    <!-- HEADER -->

    <div class="hx-header">

        <div class="hx-title">
            🧠 HypothesisX AI
        </div>

        <div class="hx-subtitle">
            Intelligent Hypothesis Generation & Scientific Reasoning
        </div>

    </div>

    """,
    unsafe_allow_html=True
)


# ============================================================
# YOUR EXISTING IMPORTS
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
# APP STATE
# ============================================================

state.init_state()

choice = st.sidebar.radio(
    "Navigate",
    list(PAGES)
)


# ============================================================
# SETTINGS
# ============================================================

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
# RUN SELECTED PAGE
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
        Developed by Hina Ramzan & Team
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


    <!-- FOOTER -->

    <div class="hx-footer">

        <div class="footer-title">
            🧠 HypothesisX AI
        </div>

        <div class="footer-text">
            Developed by Hina Ramzan & Team
        </div>

        <div class="footer-text">
            Intelligent • Scientific • Data-Driven
        </div>

    </div>
    """,
    unsafe_allow_html=True
)
