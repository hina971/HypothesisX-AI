from __future__ import annotations

import streamlit as st

from ui import state

STATUS_FN = {"supports": st.success, "mixed": st.warning, "limited": st.warning, "investigate": st.error}


def render_evidence():
    st.header("Evidence Review")
    if state.need_data():
        return
    rec = state.pick_record()
    if rec is None:
        return
    if st.button("Build evidence report (runs missing stages)"):
        stages = [s for s, has in (("stats", rec.statistical_results), ("ml", rec.ml_results),
                                   ("robustness", rec.robustness_results)) if not has] + ["evidence"]
        with st.spinner("Collecting evidence..."):
            state.get_agent().analyze(rec, state.testing_df(), st.session_state["date_col"], stages=tuple(stages))
    rep = rec.evidence_report
    if not rep:
        return
    fa = rep["final_assessment"]
    st.subheader("Evidence status")
    STATUS_FN[fa["key"]](fa["label"])
    st.caption("Why: " + "; ".join(fa["reasons"]))
    tabs = st.tabs(["Statistical", "ML/DL", "Robustness", "Alternatives", "Data quality", "Uncertainty"])
    for t, key in zip(tabs, ["statistical_evidence", "ml_evidence", "robustness_evidence",
                             "alternative_explanations", "data_limitations", "uncertainty"]):
        with t:
            for line in rep[key]["summary"]:
                st.write("- " + line)
    st.info(rep["causality_statement"])
    st.subheader("Recommended next investigation")
    for n in rep["recommended_next_investigation"]:
        st.write("- " + n)
    with st.expander("Thresholds used for this assessment"):
        st.json(fa["thresholds"])
