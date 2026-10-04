"""Evidence Reviewer: assembles the full evidence chain and states a cautious, rule-based assessment.
No arbitrary confidence score is produced; every label comes with the explicit rules that triggered it."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from agents.robustness_agent import RobustnessAgent
from schemas import HypothesisRecord, RobustnessConfig
from utils.helpers import fmt, to_native

CAUSALITY = ("Association is not causation. These results describe statistical relationships in "
             "observational data; no causal design (randomisation, instrument, natural experiment, "
             "or explicit causal identification) has been implemented.")

LABELS = {
    "supports": "Evidence supports the hypothesis, but causality is not established.",
    "mixed": "Evidence is mixed; the hypothesis is neither clearly supported nor clearly refuted.",
    "limited": "Evidence is limited.",
    "investigate": "Further investigation is required before the hypothesis can be relied on.",
}


class EvidenceAgent:
    def __init__(self, cfg: Optional[RobustnessConfig] = None):
        self.cfg = cfg or RobustnessConfig()

    # --------------------------------------------------------------- sections
    def _statistical(self, s: Dict) -> Dict[str, Any]:
        if not s or s.get("error"):
            return {"available": False, "supported": None,
                    "summary": [f"Statistical test unavailable: {(s or {}).get('error', 'not run')}"], "data": s or {}}
        o, a = s["ols"], self.cfg.alpha
        supported = bool(o["p_value"] < a and (o["ci_low"] > 0 or o["ci_high"] < 0)
                         and abs(o["std_beta"] or 0) >= self.cfg.min_std_beta)
        lines = [
            f"Adjusted coefficient {fmt(o['coef'])} (95% CI {fmt(o['ci_low'])} to {fmt(o['ci_high'])}), "
            f"p = {fmt(o['p_value'])}, n = {o['n']}, direction: {o['direction']}.",
            f"Standardised effect {fmt(o['std_beta'])} ({s['effect_size_label']}); partial R2 = {fmt(o['partial_r2'])}.",
            f"Pearson r = {fmt(s['pearson']['r'])}, Spearman rho = {fmt(s['spearman']['rho'])}.",
        ]
        if not supported:
            lines.append("Criteria for statistical support (p < alpha, CI excludes 0, non-negligible effect) "
                         "were not all met.")
        return {"available": True, "supported": supported, "summary": lines, "data": s}

    def _ml(self, m: Dict) -> Dict[str, Any]:
        if not m or m.get("error"):
            return {"available": False, "supported": None,
                    "summary": [f"ML validation unavailable: {(m or {}).get('error', 'not run')}"], "data": m or {}}
        lines, ok = [], []
        for name, r in m["models"].items():
            good = r["delta_r2"] >= self.cfg.min_delta_r2 and r["share_folds_improved"] >= 0.8
            ok.append(good)
            lines.append(f"{name}: held-out R2 {fmt(r['baseline_r2_mean'])} -> {fmt(r['full_r2_mean'])} "
                         f"(gain {fmt(r['delta_r2'])}; improved in {r['share_folds_improved']:.0%} of folds).")
        lin, rf = m["models"]["linear_regression"], m["models"]["random_forest"]
        if rf["delta_r2"] - lin["delta_r2"] > 0.02:
            lines.append("The random forest gains noticeably more than the linear model, which hints at a "
                         "non-linear component.")
        lines.append(f"Baseline: {m['baseline']}; validation: {m['cv']}. This is predictive evidence, "
                     "distinct from the statistical test above.")
        return {"available": True, "supported": any(ok), "summary": lines, "data": m}

    def _robustness(self, rs: List[Dict]) -> Dict[str, Any]:
        if not rs:
            return {"available": False, "supported": None, "summary": ["Robustness testing not run."], "data": []}
        c = RobustnessAgent.summary(rs)
        assessable = c["total"] - c["not_assessable"]
        lines = [f"{c['total']} tests: {c['stable']} stable, {c['moderately_sensitive']} moderately sensitive, "
                 f"{c['unstable']} unstable, {c['not_assessable']} not assessable."]
        for r in rs:
            if r["stability"] in ("moderately_sensitive", "unstable"):
                lines.append(f"[{r['test']}] {r['interpretation'].strip()}")
            if r["stability"] == "not_assessable":
                lines.append(f"[{r['test']}] {r['interpretation']}")
        supported = None if assessable == 0 else bool(c["stable"] / assessable >= 0.75 and c["unstable"] == 0)
        return {"available": True, "supported": supported, "summary": lines, "counts": c, "data": rs}

    def _alternatives(self, rec: HypothesisRecord) -> Dict[str, Any]:
        found, dominant = [], False
        for r in rec.robustness_results:
            if r["test"].startswith("feature_variation_add_") and r["stability"] != "stable":
                col = r["test"].replace("feature_variation_add_", "")
                lost = (r["original_result"].get("p_value", 1) < self.cfg.alpha
                        and (r["p_value"] or 0) >= self.cfg.alpha)
                flipped = r["stability"] == "unstable"
                dominant = dominant or lost or flipped
                found.append({"source": "data-driven (feature variation)", "variable": col,
                              "explanation": f"Adding '{col}' changes the estimate; '{col}' may confound or mediate "
                                             f"the relationship. {r['interpretation'].strip()}",
                              "could_explain_away": bool(lost or flipped)})
        for a in rec.alternative_explanations:
            found.append({"source": "alternative-explanation agent", **a})
        generic = ["Unmeasured confounders may drive both variables.",
                   "The direction of influence could be reversed or bidirectional.",
                   "Selection, measurement error or a shared seasonal pattern could create the association."]
        lines = [f"{f.get('variable', 'Other')}: {f['explanation']}" for f in found] or \
                ["No tested candidate variable materially changed the estimate."]
        return {"available": True, "supported": None, "dominant": dominant, "summary": lines + generic,
                "data": found}

    def _quality(self, rec: HypothesisRecord) -> Dict[str, Any]:
        issues: List[str] = list(rec.data_quality.get("issues", []))
        s = rec.statistical_results
        if s and not s.get("error"):
            issues += s["assumptions"]["notes"]
            if s["n"] < 100:
                issues.append(f"Small analysis sample (n = {s['n']}).")
        kind = rec.origin.get("kind")
        if kind == "nonlinear":
            issues.append("Linear tests understate non-linear relationships; the random-forest-vs-linear gain "
                          "is the more relevant indicator.")
        if kind == "interaction":
            issues.append("This pipeline tests the main effect with the moderator as a control; the interaction "
                          "term itself was tested at discovery only.")
        if rec.origin.get("holdout"):
            issues.append("Pattern discovered on one random half of the data and tested on the other half. "
                          "Rows from a time series are not independent, so the split is not a fully independent test.")
        else:
            issues.append("Pattern discovered and tested on the same data; p-values are optimistic. "
                          "Confirm on new data.")
        return {"available": True, "supported": None, "summary": issues, "data": rec.data_quality}

    def _uncertainty(self, rec: HypothesisRecord) -> List[str]:
        out = []
        s = rec.statistical_results
        if s and not s.get("error"):
            o = s["ols"]
            out.append(f"Parametric 95% CI for the coefficient: {fmt(o['ci_low'])} to {fmt(o['ci_high'])}.")
        for r in rec.robustness_results:
            if r["test"] == "bootstrap" and r["stability"] != "not_assessable":
                out.append(f"Bootstrap 95% interval: {fmt(r['ci_low'])} to {fmt(r['ci_high'])}.")
            if r["test"] == "cross_validation" and r["model_performance"]:
                out.append(f"Out-of-fold R2 = {fmt(r['model_performance']['out_of_fold_r2_mean'])} "
                           f"(sd {fmt(r['model_performance']['out_of_fold_r2_sd'])}).")
        out.append("Model-specification uncertainty: results depend on the chosen controls and linear form.")
        return out

    # ------------------------------------------------------------------ main
    def review(self, rec: HypothesisRecord) -> Dict[str, Any]:
        stat, ml = self._statistical(rec.statistical_results), self._ml(rec.ml_results)
        rob, alt = self._robustness(rec.robustness_results), self._alternatives(rec)
        qual = self._quality(rec)

        criteria = {"statistical": stat["supported"], "ml_validation": ml["supported"],
                    "robustness": rob["supported"]}
        reasons = [f"{k}: {'met' if v else 'not met' if v is False else 'not available'}"
                   for k, v in criteria.items()]
        flipped = any(r["stability"] == "unstable" and not r["test"].startswith("feature_variation")
                      for r in rec.robustness_results)
        if criteria["statistical"] is None:
            key = "limited"
        elif alt["dominant"] or flipped:
            key = "investigate"
            reasons.append("a robustness test reversed the direction, or adding a variable removed the effect")
        elif all(v is True for v in criteria.values()):
            key = "supports"
        elif sum(v is True for v in criteria.values()) >= 2:
            key = "mixed"
        else:
            key = "limited"
        if key == "supports" and rec.statistical_results.get("n", 0) < 100:
            key = "mixed"; reasons.append("sample is small")

        nxt = []
        if key != "supports":
            nxt.append("Collect or obtain an independent dataset and re-test the same hypothesis.")
        for f in alt["data"]:
            if f.get("could_explain_away"):
                nxt.append(f"Investigate '{f.get('variable')}' as a confounder or mediator (e.g. stratify, model explicitly).")
        if criteria["ml_validation"] is False:
            nxt.append("Predictive gain was small: check whether the relationship matters in practice.")
        nxt.append("Design a study capable of causal inference (experiment, natural experiment, or causal model) "
                   "if a causal claim is the goal.")

        report = {
            "hypothesis": {"id": rec.id, "statement": rec.statement, "variables": rec.variables,
                           "why_discovered": rec.origin.get("why_interesting", ""),
                           "origin_kind": rec.origin.get("kind", "")},
            "statistical_evidence": stat, "ml_evidence": ml, "robustness_evidence": rob,
            "alternative_explanations": alt, "data_limitations": qual,
            "uncertainty": {"summary": self._uncertainty(rec)},
            "final_assessment": {"key": key, "label": LABELS[key], "criteria": criteria, "reasons": reasons,
                                 "thresholds": {"alpha": self.cfg.alpha, "min_std_beta": self.cfg.min_std_beta,
                                                "min_delta_r2": self.cfg.min_delta_r2,
                                                "stable_fraction_required": 0.75,
                                                "tolerance": self.cfg.tolerance}},
            "recommended_next_investigation": nxt,
            "causality_statement": CAUSALITY if not rec.causal_design else "A causal design was flagged; verify it.",
        }
        rec.evidence_report = to_native(report)
        return rec.evidence_report
