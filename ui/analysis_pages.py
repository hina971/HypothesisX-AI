from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from schemas import HypothesisRecord
from ui import state
from utils.helpers import fmt

KIND_HELP = {
    "correlation": "Two variables move together (monotonic).",
    "nonlinear": "One variable carries information about another, but not in a straight line.",
    "association": "A numeric or categorical outcome differs between groups.",
    "trend": "A variable drifts over time.",
    "cluster": "Observations separate into groups.",
    "anomaly": "Unusual observations.",
    "interaction": "The effect of one variable depends on another.",
}


def render_patterns():
    st.header("Discovered Patterns")
    if state.need_data():
        return
    if st.button("Search for patterns"):
        with st.spinner("Scanning correlations, associations, trends, clusters, anomalies, non-linear "
                        "relationships and interactions..."):
            agent = state.get_agent()
            disc, conf, found = agent.explore(st.session_state["df"], st.session_state["date_col"])
            st.session_state.update(disc_df=disc if found["holdout"] else None,
                                    conf_df=conf if found["holdout"] else None, discovery=found)
    found = st.session_state["discovery"]
    if not found:
        return
    if found["holdout"]:
        st.info("Patterns were found on a random half of the rows; hypotheses are tested on the other half.")
    for name, msg in found["errors"].items():
        st.error(f"Detector '{name}' failed: {msg}")
    st.write("Findings by type:", found["counts"])
    kinds = sorted({f["kind"] for f in found["findings"]})
    pick = st.multiselect("Show types", kinds, default=kinds)
    for f in found["findings"]:
        if f["kind"] not in pick:
            continue
        with st.expander(f"{f['id']} [{f['kind']}] {f['title']}"):
            st.write(f["why_interesting"])
            st.caption(KIND_HELP.get(f["kind"], ""))
            st.json(f["metrics"])
            if f["caveat"]:
                st.warning(f["caveat"])
            if f["suggested_hypothesis"]:
                st.write("Candidate hypothesis: " + f["suggested_hypothesis"])
                if st.button("Create hypothesis", key=f"mk_{f['id']}"):
                    rid = f"H{len(st.session_state['records']) + 1}"
                    st.session_state["records"][rid] = HypothesisRecord(
                        id=rid, statement=f["suggested_hypothesis"],
                        variables={"x": f["x"], "y": f["y"], "controls": f["controls"]},
                        origin={"finding_id": f["id"], "kind": f["kind"], "why_interesting": f["why_interesting"],
                                "metrics": f["metrics"], "caveat": f["caveat"], "holdout": found["holdout"]},
                        data_quality={"issues": st.session_state["quality"]["issues"]})
                    st.success(f"Created {rid}")


def render_hypotheses():
    st.header("Hypotheses")
    if state.need_data():
        return
    agent = state.get_agent()
    found = st.session_state["discovery"]
    if found and st.button("Auto-create hypotheses from top findings"):
        recs = agent.make_hypotheses(found["findings"], found["holdout"], st.session_state["quality"],
                                     start=len(st.session_state["records"]) + 1)
        for r in recs:
            st.session_state["records"][r.id] = r
    with st.expander("Add your own hypothesis"):
        num = [c for c in st.session_state["df"].select_dtypes("number").columns]
        x = st.selectbox("Predictor (X)", num, key="hx")
        y = st.selectbox("Outcome (Y)", num, index=min(1, len(num) - 1), key="hy")
        ctrl = st.multiselect("Controls", [c for c in num if c not in (x, y)], key="hc")
        if st.button("Add") and x != y:
            rid = f"H{len(st.session_state['records']) + 1}"
            st.session_state["records"][rid] = HypothesisRecord(
                id=rid, statement=f"{x} is associated with {y}", variables={"x": x, "y": y, "controls": ctrl},
                origin={"kind": "user", "why_interesting": "Proposed by the user."},
                data_quality={"issues": st.session_state["quality"]["issues"]})
    recs = st.session_state["records"]
    for r in recs.values():
        st.write(f"**{r.id}** {r.statement}  (X={r.variables['x']}, Y={r.variables['y']}, "
                 f"controls={r.variables['controls'] or 'none'})")
        if r.origin.get("why_interesting"):
            st.caption("Why discovered: " + r.origin["why_interesting"])
    if recs and st.button("Run full analysis on all hypotheses"):
        bar = st.progress(0.0)
        for i, r in enumerate(recs.values(), 1):
            agent.analyze(r, state.testing_df(), st.session_state["date_col"])
            bar.progress(i / len(recs))
        st.success("Done. See the Statistical, ML, Robustness and Evidence pages.")


def _run_button(label, stage):
    rec = st.session_state.get("_rec")
    if st.button(label):
        with st.spinner("Running..."):
            state.get_agent().analyze(rec, state.testing_df(), st.session_state["date_col"], stages=(stage,))


def render_statistical():
    st.header("Statistical Testing")
    if state.need_data():
        return
    rec = state.pick_record()
    if rec is None:
        return
    st.session_state["_rec"] = rec
    _run_button("Run statistical test", "stats")
    s = rec.statistical_results
    if not s:
        return
    if s.get("error"):
        st.error("Test failed: " + s["error"])
        return
    o = s["ols"]
    c = st.columns(4)
    c[0].metric("Coefficient", fmt(o["coef"]))
    c[1].metric("p-value", fmt(o["p_value"]))
    c[2].metric("Std. effect", fmt(o["std_beta"]), s["effect_size_label"])
    c[3].metric("n", s["n"])
    st.write(f"95% CI: {fmt(o['ci_low'])} to {fmt(o['ci_high'])}. Pearson r = {fmt(s['pearson']['r'])}, "
             f"Spearman rho = {fmt(s['spearman']['rho'])}.")
    for n in s["assumptions"]["notes"]:
        st.warning(n)
    st.caption("A significant p-value shows the association is unlikely to be pure chance under the model's "
               "assumptions. It does not show causation or practical importance.")


def render_ml():
    st.header("ML / DL Validation")
    if state.need_data():
        return
    rec = state.pick_record()
    if rec is None:
        return
    st.session_state["_rec"] = rec
    _run_button("Run cross-validated models", "ml")
    m = rec.ml_results
    if not m:
        return
    if m.get("error"):
        st.error("Validation failed: " + m["error"])
        return
    st.write(f"Baseline: {m['baseline']}. Validation: {m['cv']}.")
    rows = [{"model": k, "baseline R2": v["baseline_r2_mean"], "full R2": v["full_r2_mean"],
             "gain": v["delta_r2"], "folds improved": v["share_folds_improved"]} for k, v in m["models"].items()]
    st.dataframe(pd.DataFrame(rows))
    fig = go.Figure()
    for k, v in m["models"].items():
        fig.add_trace(go.Box(y=v["fold_scores_full"], name=f"{k} (with X)"))
        fig.add_trace(go.Box(y=v["fold_scores_baseline"], name=f"{k} (baseline)"))
    fig.update_layout(yaxis_title="held-out R2")
    st.plotly_chart(fig)
    st.caption("This is predictive evidence. It is separate from, and does not replace, the statistical test.")
