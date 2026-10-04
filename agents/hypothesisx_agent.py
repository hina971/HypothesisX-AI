"""HypothesisX single agent: discover -> hypothesise -> test -> validate -> stress-test -> review evidence."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from agents.evidence_agent import EvidenceAgent
from agents.robustness_agent import RobustnessAgent
from analysis.discovery import TIME_COL, add_time_index, discover
from analysis.ml_validation import cross_validate_relationship
from analysis.preprocessing import split_discovery_confirmation, validate_dataset
from analysis.statistical_tests import test_relationship
from schemas import HypothesisRecord, RobustnessConfig

PER_KIND = {"correlation": 3, "nonlinear": 2, "trend": 2, "interaction": 2}


def load_excel(source, sheet=0) -> pd.DataFrame:
    """Read an .xlsx/.xls file (path or uploaded buffer). Raises a clear error on failure."""
    try:
        return pd.read_excel(source, sheet_name=sheet)
    except Exception as exc:
        raise ValueError(f"Could not read the Excel file: {exc}") from exc


def detect_date_col(df: pd.DataFrame) -> Optional[str]:
    for c in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[c]):
            return c
    for c in df.columns:
        if any(k in str(c).lower() for k in ("date", "time", "day")) and df[c].dtype == object:
            try:
                pd.to_datetime(df[c])
                return c
            except Exception:
                continue
    return None


class HypothesisXAgent:
    def __init__(self, cfg: Optional[RobustnessConfig] = None, use_holdout: bool = True):
        self.cfg = cfg or RobustnessConfig()
        self.use_holdout = use_holdout
        self.robustness = RobustnessAgent(self.cfg)
        self.evidence = EvidenceAgent(self.cfg)

    def prepare(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[str], Dict[str, Any]]:
        quality = validate_dataset(df)
        date_col = detect_date_col(df)
        if date_col:
            df = df.copy(); df[date_col] = pd.to_datetime(df[date_col])
        return add_time_index(df, date_col), date_col, quality

    def explore(self, df: pd.DataFrame, date_col: Optional[str]):
        """Return (discovery_df, testing_df, discovery_result)."""
        if self.use_holdout and len(df) >= 200:
            disc, conf = split_discovery_confirmation(df, self.cfg.seed)
        else:
            disc = conf = df
        result = discover(disc, date_col, self.cfg.seed, self.cfg.alpha)
        result["holdout"] = bool(self.use_holdout and len(df) >= 200)
        return disc, conf, result

    def make_hypotheses(self, findings: List[Dict], holdout: bool, quality: Dict, start: int = 1) -> List[HypothesisRecord]:
        recs, taken = [], {k: 0 for k in PER_KIND}
        for f in findings:
            k = f["kind"]
            if k not in PER_KIND or not f.get("x") or taken[k] >= PER_KIND[k]:
                continue
            taken[k] += 1
            recs.append(HypothesisRecord(
                id=f"H{start + len(recs)}", statement=f["suggested_hypothesis"],
                variables={"x": f["x"], "y": f["y"], "controls": f["controls"]},
                origin={"finding_id": f["id"], "kind": k, "why_interesting": f["why_interesting"],
                        "metrics": f["metrics"], "caveat": f["caveat"], "holdout": holdout},
                data_quality={"issues": quality.get("issues", [])}))
        return recs

    def analyze(self, rec: HypothesisRecord, df: pd.DataFrame, date_col: Optional[str],
                stages=("stats", "ml", "robustness", "evidence")) -> HypothesisRecord:
        v = rec.variables
        if "stats" in stages:
            rec.statistical_results = test_relationship(df, v["x"], v["y"], v.get("controls", []),
                                                        self.cfg.alpha, date_col)
        if "ml" in stages:
            rec.ml_results = cross_validate_relationship(df, v["x"], v["y"], v.get("controls", []), self.cfg.seed)
        if "robustness" in stages:
            self.robustness.run(rec, df, date_col)
        if "evidence" in stages:
            self.evidence.review(rec)
        return rec

    def run_all(self, df_raw: pd.DataFrame) -> Dict[str, Any]:
        df, date_col, quality = self.prepare(df_raw)
        disc, conf, found = self.explore(df, date_col)
        recs = self.make_hypotheses(found["findings"], found["holdout"], quality)
        for r in recs:
            self.analyze(r, conf, date_col)
        return {"quality": quality, "date_col": date_col, "discovery": found, "records": recs}
