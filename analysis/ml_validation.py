"""ML evidence: does adding the predictor improve out-of-sample prediction? (stand-in agent)"""
from __future__ import annotations

from typing import Any, Dict, Sequence

import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import RepeatedKFold, cross_val_score

from analysis.preprocessing import complete_cases
from utils.helpers import to_native


def cross_validate_relationship(df: pd.DataFrame, x: str, y: str, controls: Sequence[str] = (),
                                seed: int = 42, n_splits: int = 5, n_repeats: int = 2) -> Dict[str, Any]:
    """Compare held-out R2 of a baseline (controls only) vs full model (controls + x)."""
    controls = list(controls)
    try:
        d, _ = complete_cases(df, [x, y] + controls)
        d = d.astype(float)
        if len(d) < n_splits * 10:
            raise ValueError(f"Too few rows (n={len(d)}) for {n_splits}-fold validation.")
        cv = RepeatedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=seed)
        yv = d[y].values
        models = {
            "linear_regression": lambda: LinearRegression(),
            "random_forest": lambda: RandomForestRegressor(
                n_estimators=150, min_samples_leaf=5, random_state=seed, n_jobs=-1),
        }
        out: Dict[str, Any] = {}
        for name, make in models.items():
            full = cross_val_score(make(), d[[x] + controls].values, yv, cv=cv, scoring="r2")
            if controls:
                base = cross_val_score(make(), d[controls].values, yv, cv=cv, scoring="r2")
            else:
                base = cross_val_score(DummyRegressor(), d[[x]].values, yv, cv=cv, scoring="r2")
            diff = full - base
            out[name] = {
                "baseline_r2_mean": base.mean(), "full_r2_mean": full.mean(),
                "full_r2_sd": full.std(ddof=1), "delta_r2": diff.mean(),
                "share_folds_improved": float((diff > 0).mean()),
                "fold_scores_full": full, "fold_scores_baseline": base,
            }
        return to_native({"n": len(d), "cv": f"{n_repeats}x repeated {n_splits}-fold",
                          "baseline": "controls only" if controls else "mean-only (no predictors)",
                          "models": out, "seed": seed, "error": None})
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}
