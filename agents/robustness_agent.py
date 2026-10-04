"""Robustness Testing Agent: runs every applicable robustness test for one hypothesis."""
from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd

from analysis import robustness as R
from schemas import HypothesisRecord, RobustnessConfig, RobustnessResult
from utils.helpers import to_native


def _not_assessable(test: str, reason: str) -> RobustnessResult:
    return RobustnessResult(test=test, method="n/a", configuration={}, original_result={},
                            modified_result={}, stability="not_assessable", changed_materially=None,
                            interpretation=f"Test could not be completed: {reason}")


class RobustnessAgent:
    def __init__(self, cfg: Optional[RobustnessConfig] = None):
        self.cfg = cfg or RobustnessConfig()

    def run(self, record: HypothesisRecord, df: pd.DataFrame, date_col: Optional[str] = None) -> List[Dict]:
        v = record.variables
        try:
            ctx = R.Ctx(df, v["x"], v["y"], v.get("controls", []), self.cfg, date_col)
        except Exception as exc:
            res = [_not_assessable("all_tests", f"{type(exc).__name__}: {exc}")]
            record.robustness_results = [r.to_dict() for r in res]
            return record.robustness_results
        steps = {
            "bootstrap": R.bootstrap_test, "random_subsamples": R.split_half_test,
            "temporal_split": R.temporal_split_test, "cross_validation": R.cv_stability_test,
            "outlier_sensitivity": R.outlier_test, "alternative_models": R.alternative_model_test,
            "feature_variation": lambda c: R.feature_variation_test(c, df),
        }
        results: List[RobustnessResult] = []
        for name, fn in steps.items():
            try:
                results.extend(fn(ctx))
            except Exception as exc:  # never silently skipped
                results.append(_not_assessable(name, f"{type(exc).__name__}: {exc}"))
        record.robustness_results = [to_native(r.to_dict()) for r in results]
        return record.robustness_results

    @staticmethod
    def summary(results: List[Dict]) -> Dict[str, int]:
        c = {"total": len(results), "stable": 0, "moderately_sensitive": 0, "unstable": 0, "not_assessable": 0}
        for r in results:
            c[r["stability"]] += 1
        c["sensitive"] = c["moderately_sensitive"] + c["unstable"]
        return c
