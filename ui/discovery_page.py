from __future__ import annotations

import streamlit as st

from reports.evidence_report import to_html, to_markdown
from ui import state
from utils.helpers import to_json


def render_discovery():
    st.header("Final Discovery Report")
    if state.need_data():
        return
    done = {k: r for k, r in st.session_state["records"].items() if r.evidence_report}
    if not done:
        st.info("Run the Evidence Review for at least one hypothesis first.")
        return
    st.subheader("Summary")
    for r in done.values():
        st.write(f"**{r.id}**: {r.statement} - {r.evidence_report['final_assessment']['label']}")
    rid = st.selectbox("Open report", list(done))
    rec = done[rid]
    md = to_markdown(rec.evidence_report)
    st.markdown(md)
    c = st.columns(3)
    c[0].download_button("Download Markdown", md, f"{rid}_evidence_report.md", "text/markdown")
    c[1].download_button("Download HTML", to_html(rec.evidence_report), f"{rid}_evidence_report.html", "text/html")
    c[2].download_button("Download JSON (all records)", to_json([r.to_dict() for r in done.values()]),
                         "evidence_reports.json", "application/json")
