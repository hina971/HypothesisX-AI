"""End-to-end driver: discovery -> hypotheses -> stats -> ML -> robustness -> evidence.
The statistical/ML stages are stand-ins so this agent works alone; swap in teammates' agents later."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd

from agents.evidence_agent import EvidenceAgent
from agents.robustness_agent import RobustnessAgent
from analysis.discovery import add_time_index, discover
from analysis.ml_validation import cross_validate_relationship
from analysis.preprocessing import split_discovery_confirmation, validate_dataset
from analysis.statistical_tests import test_relationship
from schemas import HypothesisRecord, RobustnessConfig

TESTABLE = ("correlation", "nonlinear", "trend", "interaction")


def hypotheses_from_findings(findings: List[Dict[str, Any]], same_data: bool, max_n: int = 10) -> List[HypothesisRecord]:
    recs = []
    for f in findings:
        if f["kind"] in TESTABLE and f.get("x") and f.get("y"):
            recs.append(HypothesisRecord(
                id=f"H{len(recs) + 1}", statement=f["suggested_hypothesis"],
                variables={"x": f["x"], "y": f["y"], "controls": f.get("controls", [])},
                origin={"finding_id": f["id"], "kind": f["kind"], "why": f["why_interesting"],
                        "metrics": f["metrics"], "discovered_on_same_data": same_data}))
        if len(recs) >= max_n:
            break
    return recs


def run_stages(record, df, cfg, date_col=None, dataset_issues=None, stages=("stats", "ml", "robustness", "evidence")):
    v = record.variables
    if "stats" in stages:
        record.statistical_results = test_relationship(df, v["x"], v["y"], v.get("controls", []), cfg.alpha, date_col)
    if "ml" in stages:
        record.ml_results = cross_validate_relationship(df, v["x"], v["y"], v.get("controls", []), cfg.seed)
    if "robustness" in stages:
        RobustnessAgent(cfg).run(record, df, date_col)
    if "evidence" in stages:
        EvidenceAgent(cfg).review(record, dataset_issues)
    return record


def run_full(df: pd.DataFrame, date_col: Optional[str] = None, cfg: Optional[RobustnessConfig] = None,
             holdout: bool = True, max_hypotheses: int = 10) -> Dict[str, Any]:
    cfg = cfg or RobustnessConfig()
    quality = validate_dataset(df)
    if holdout and len(df) >= 200:
        disc, conf = split_discovery_confirmation(df, cfg.seed)
    else:
        disc, conf, holdout = df, df, False
    findings = discover(disc, date_col, cfg.seed, cfg.alpha)
    test_df = add_time_index(conf, date_col)
    records = hypotheses_from_findings(findings["findings"], same_data=not holdout, max_n=max_hypotheses)
    for r in records:
        run_stages(r, test_df, cfg, date_col, quality["issues"])
    return {"quality": quality, "discovery": findings, "records": records, "holdout": holdout,
            "test_df": test_df}
