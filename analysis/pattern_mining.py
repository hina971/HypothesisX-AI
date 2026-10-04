"""Pattern mining stand-in: rank-correlation scan with false-discovery-rate control."""
from __future__ import annotations

from itertools import combinations
from typing import List, Sequence

import numpy as np
import pandas as pd
from scipy import stats


def benjamini_hochberg(p: np.ndarray) -> np.ndarray:
    p = np.asarray(p, float)
    n = len(p)
    order = np.argsort(p)
    ranked = p[order] * n / (np.arange(n) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(n)
    out[order] = np.clip(ranked, 0, 1)
    return out


def mine_patterns(df: pd.DataFrame, columns: Sequence[str], alpha: float = 0.05,
                  min_abs_rho: float = 0.2, derived_threshold: float = 0.95) -> pd.DataFrame:
    rows: List[dict] = []
    for a, b in combinations(columns, 2):
        d = df[[a, b]].dropna()
        if len(d) < 10 or d[a].nunique() < 3 or d[b].nunique() < 3:
            continue
        rho, p = stats.spearmanr(d[a], d[b])
        rows.append({"x": a, "y": b, "n": len(d), "spearman_rho": rho, "p_value": p})
    if not rows:
        return pd.DataFrame(columns=["x", "y", "n", "spearman_rho", "p_value", "fdr_q", "note"])
    res = pd.DataFrame(rows)
    res["fdr_q"] = benjamini_hochberg(res["p_value"].values)
    res["note"] = np.where(res["spearman_rho"].abs() >= derived_threshold,
                           "Very strong: check whether one variable is derived from the other",
                           "")
    res = res[(res["fdr_q"] < alpha) & (res["spearman_rho"].abs() >= min_abs_rho)]
    return res.sort_values("spearman_rho", key=lambda s: -s.abs()).reset_index(drop=True)
