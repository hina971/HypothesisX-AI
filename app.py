```python
"""HypothesisX AI - run with: streamlit run app.py"""

import streamlit as st

st.set_page_config(
    page_title="HypothesisX AI",
    page_icon="🧠",
    layout="wide"
)


# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- MAIN HEADER ---------- */

    .hx-header {
        text-align: center;
        padding: 28px 20px;
        margin-bottom: 25px;
        border-radius: 22px;
        background: linear-gradient(
            135deg,
            rgba(99, 102, 241, 0.14),
            rgba(168, 85, 247, 0.14),
            rgba(236, 72, 153, 0.12)
        );
        border: 1px solid rgba(139, 92, 246, 0.25);
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.10);
    }

    .hx-title {
        font-size: 48px;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(
            90deg,
            #6366f1,
            #8b5cf6,
            #ec4899,
            #06b6d4
        );
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientMove 5s ease infinite;
    }

    .hx-subtitle {
        font-size: 17px;
        margin-top: 8px;
        color: #64748b;
        letter-spacing: 0.5px;
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


    /* ---------- TEAM HEADING ---------- */

    .team-heading {
        text-align: center;
        font-size: 30px;
        font-weight: 800;
        margin-top: 60px;
        margin-bottom: 6px;
    }

    .team-subheading {
        text-align: center;
        color: #64748b;
        font-size: 15px;
        margin-bottom: 25px;
    }


    /* ---------- TEAM GRID ---------- */

    .team-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 18px;
        max-width: 950px;
        margin: 0 auto;
    }


    /* ---------- TEAM CARD ---------- */

    .team-card {
        position: relative;
        text-align: center;
        padding: 24px 15px;
        border-radius: 20px;
        background: linear-gradient(
            145deg,
            rgba(255,255,255,0.95),
            rgba(248,250,252,0.90)
        );
        border: 1px solid rgba(139,92,246,0.20);
        box-shadow: 0 8px 25px rgba(15,23,42,0.08);
        overflow: hidden;
        transition: all 0.35s ease;
        animation: floatingCard 3.5s ease-in-out infinite;
    }

    .team-card:nth-child(2) {
        animation-delay: 0.3s;
    }

    .team-card:nth-child(3) {
        animation-delay: 0.6s;
    }

    .team-card:nth-child(4) {
        animation-delay: 0.9s;
    }

    .team-card:nth-child(5) {
        animation-delay: 1.2s;
    }

    .team-card:nth-child(6) {
        animation-delay: 1.5s;
    }

    .team-card:hover {
        transform: translateY(-10px) scale(1.03);
        box-shadow: 0 18px 40px rgba(99,102,241,0.20);
        border-color: rgba(139,92,246,0.50);
    }

    .team-card::before {
        content: "";
        position: absolute;
        left: -100%;
        top: 0;
        width: 100%;
        height: 4px;
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
        from {
            left: -100%;
        }

        to {
            left: 100%;
        }
    }

    @keyframes floatingCard {
        0%, 100% {
            transform: translateY(0);
        }

        50% {
            transform: translateY(-5px);
        }
    }

    .member-icon {
        font-size: 32px;
        margin-bottom: 8px;
    }

    .member-name {
        font-size: 18px;
        font-weight: 700;
        color: #1e293b;
    }

    .member-role {
        margin-top: 5px;
        font-size: 13px;
        font-weight: 600;
        color: #8b5cf6;
    }


    /* ---------- FOOTER ---------- */

    .hx-footer {
        text-align: center;
        margin-top: 55px;
        padding: 25px;
        border-radius: 20px;
        background: linear-gradient(
            135deg,
            rgba(99,102,241,0.10),
            rgba(236,72,153,0.10)
        );
        border-top: 1px solid rgba(139,92,246,0.20);
    }

    .footer-title {
        font-size: 22px;
        font-weight: 800;
        color: #6366f1;
    }

    .footer-text {
        margin-top: 6px;
        font-size: 14px;
        color: #64748b;
    }


    /* ---------- MOBILE ---------- */

    @media (max-width: 700px) {

        .hx-title {
            font-size: 36px;
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
            Intelligent Hypothesis Generation & Scientific Reasoning
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# EXISTING APP IMPORTS
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
            Developed by Hina Ramzan &amp; Team
        </div>

        <div class="footer-text">
            Intelligent • Scientific • Data-Driven
        </div>

    </div>
    """,
    unsafe_allow_html=True
)
```
