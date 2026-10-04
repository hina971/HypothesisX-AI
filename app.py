"""HypothesisX AI - run with: streamlit run app.py"""

import streamlit as st

st.set_page_config(
    page_title="HypothesisX AI",
    page_icon="🧠",
    layout="wide",
)

st.markdown(
    """
    <style>

    /* ================================
       GLOBAL
       ================================ */

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* ================================
       ANIMATIONS
       ================================ */

    @keyframes gradientFlow {
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

    @keyframes float {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-8px);
        }
    }

    @keyframes glow {
        0%, 100% {
            box-shadow: 0 0 15px rgba(99,102,241,0.20);
        }
        50% {
            box-shadow: 0 0 35px rgba(236,72,153,0.40);
        }
    }

    @keyframes shine {
        0% {
            left: -120%;
        }
        100% {
            left: 120%;
        }
    }

    @keyframes pulse {
        0%, 100% {
            opacity: 0.75;
        }
        50% {
            opacity: 1;
        }
    }

    /* ================================
       HEADER
       ================================ */

    .hx-header {
        position: relative;
        overflow: hidden;
        text-align: center;
        padding: 42px 25px;
        margin-bottom: 30px;
        border-radius: 28px;

        background: linear-gradient(
            120deg,
            #eef2ff,
            #f5e8ff,
            #fce7f3,
            #e0f2fe,
            #ecfeff
        );

        background-size: 400% 400%;
        animation: gradientFlow 8s ease infinite;

        border: 1px solid rgba(139,92,246,0.25);

        box-shadow:
            0 15px 45px rgba(99,102,241,0.15);
    }

    .hx-header::before {
        content: "";
        position: absolute;
        width: 220px;
        height: 220px;
        border-radius: 50%;
        background: rgba(99,102,241,0.10);
        top: -120px;
        left: -80px;
    }

    .hx-header::after {
        content: "";
        position: absolute;
        width: 180px;
        height: 180px;
        border-radius: 50%;
        background: rgba(236,72,153,0.10);
        bottom: -100px;
        right: -50px;
    }

    .hx-title {
        position: relative;
        z-index: 2;

        font-size: 54px;
        font-weight: 900;
        margin: 0;

        background: linear-gradient(
            90deg,
            #4f46e5,
            #7c3aed,
            #db2777,
            #0891b2,
            #4f46e5
        );

        background-size: 300% auto;

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;

        animation: gradientFlow 5s ease infinite;
    }

    .hx-subtitle {
        position: relative;
        z-index: 2;

        margin-top: 12px;

        font-size: 18px;
        font-weight: 500;

        color: #475569;

        letter-spacing: 0.7px;

        animation: pulse 3s ease-in-out infinite;
    }

    /* ================================
       TEAM HEADING
       ================================ */

    .team-heading {
        text-align: center;

        font-size: 34px;
        font-weight: 900;

        margin-top: 65px;
        margin-bottom: 8px;

        background: linear-gradient(
            90deg,
            #4f46e5,
            #9333ea,
            #db2777,
            #0891b2
        );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .team-subheading {
        text-align: center;

        color: #64748b;

        font-size: 15px;

        margin-bottom: 30px;
    }

    /* ================================
       TEAM GRID
       ================================ */

    .team-grid {
        display: grid;

        grid-template-columns: repeat(3, 1fr);

        gap: 22px;

        max-width: 1000px;

        margin: 0 auto;
    }

    /* ================================
       TEAM CARD
       ================================ */

    .team-card {
        position: relative;

        overflow: hidden;

        text-align: center;

        padding: 30px 18px;

        min-height: 175px;

        border-radius: 24px;

        background: rgba(255,255,255,0.94);

        border: 1px solid rgba(139,92,246,0.20);

        box-shadow:
            0 10px 30px rgba(15,23,42,0.08);

        animation:
            float 4s ease-in-out infinite,
            glow 4s ease-in-out infinite;

        transition:
            transform 0.35s ease,
            box-shadow 0.35s ease;
    }

    .team-card:nth-child(1) {
        border-top: 4px solid #6366f1;
    }

    .team-card:nth-child(2) {
        border-top: 4px solid #8b5cf6;
        animation-delay: 0.3s;
    }

    .team-card:nth-child(3) {
        border-top: 4px solid #ec4899;
        animation-delay: 0.6s;
    }

    .team-card:nth-child(4) {
        border-top: 4px solid #06b6d4;
        animation-delay: 0.9s;
    }

    .team-card:nth-child(5) {
        border-top: 4px solid #f59e0b;
        animation-delay: 1.2s;
    }

    .team-card:nth-child(6) {
        border-top: 4px solid #10b981;
        animation-delay: 1.5s;
    }

    .team-card:hover {
        transform: translateY(-14px) scale(1.04);

        box-shadow:
            0 20px 50px rgba(99,102,241,0.25);
    }

    .team-card::after {
        content: "";

        position: absolute;

        top: 0;
        left: -120%;

        width: 60%;
        height: 100%;

        transform: skewX(-25deg);

        background: linear-gradient(
            90deg,
            transparent,
            rgba(255,255,255,0.55),
            transparent
        );

        animation: shine 4s infinite;
    }

    .member-icon {
        position: relative;
        z-index: 2;

        font-size: 42px;

        margin-bottom: 12px;

        animation: float 3s ease-in-out infinite;
    }

    .member-name {
        position: relative;
        z-index: 2;

        font-size: 20px;

        font-weight: 800;

        color: #1e293b;
    }

    .member-role {
        position: relative;
        z-index: 2;

        margin-top: 7px;

        font-size: 13px;

        font-weight: 700;

        color: #7c3aed;

        text-transform: uppercase;

        letter-spacing: 0.8px;
    }

    /* ================================
       FOOTER
       ================================ */

    .hx-footer {
        position: relative;

        overflow: hidden;

        text-align: center;

        margin-top: 75px;

        padding: 40px 20px;

        border-radius: 28px;

        background: linear-gradient(
            120deg,
            #eef2ff,
            #f5e8ff,
            #fce7f3,
            #e0f2fe
        );

        background-size: 400% 400%;

        animation: gradientFlow 8s ease infinite;

        border: 1px solid rgba(139,92,246,0.25);

        box-shadow:
            0 15px 45px rgba(99,102,241,0.14);
    }

    .footer-title {
        position: relative;
        z-index: 2;

        font-size: 30px;

        font-weight: 900;

        background: linear-gradient(
            90deg,
            #4f46e5,
            #9333ea,
            #db2777,
            #0891b2
        );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .footer-text {
        position: relative;
        z-index: 2;

        margin-top: 8px;

        font-size: 15px;

        color: #475569;
    }

    .footer-tagline {
        position: relative;
        z-index: 2;

        margin-top: 15px;

        font-size: 14px;

        font-weight: 700;

        color: #7c3aed;

        letter-spacing: 1px;
    }

    .footer-copy {
        position: relative;
        z-index: 2;

        margin-top: 20px;

        font-size: 12px;

        color: #94a3b8;
    }

    /* ================================
       MOBILE
       ================================ */

    @media (max-width: 800px) {

        .hx-title {
            font-size: 40px;
        }

        .hx-subtitle {
            font-size: 15px;
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
# IMPORT PROJECT MODULES
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
# INITIALIZE STATE
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
# SELECTED PAGE
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
