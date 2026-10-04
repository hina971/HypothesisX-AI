"""Dataset validation. Nothing is dropped or imputed silently: every action is reported."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd


def validate_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """Return a data-quality report; raises ValueError only if the data is unusable."""
    if df is None or df.empty:
        raise ValueError("The dataset is empty.")
    numeric = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric) < 2:
        raise ValueError("At least two numeric columns are required for relationship testing.")

    n = len(df)
    missing = df.isna().sum()
    issues: List[str] = []
    if n < 100:
        issues.append(f"Small sample (n={n}); estimates will be imprecise.")
    for col, m in missing.items():
        if m / n > 0.2:
            issues.append(f"Column '{col}' has {m / n:.0%} missing values.")
    constant = [c for c in numeric if df[c].nunique(dropna=True) <= 1]
    if constant:
        issues.append(f"Constant numeric column(s) cannot be analysed: {constant}")
    dups = int(df.duplicated().sum())
    if dups:
        issues.append(f"{dups} duplicated row(s).")
    inf_cols = [c for c in numeric if np.isinf(df[c]).any()]
    if inf_cols:
        issues.append(f"Infinite values in {inf_cols}.")

    return {
        "n_rows": n,
        "n_cols": df.shape[1],
        "numeric_columns": [c for c in numeric if c not in constant],
        "datetime_columns": df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist(),
        "missing_by_column": {k: int(v) for k, v in missing.items()},
        "missing_fraction_max": float(missing.max() / n),
        "duplicate_rows": dups,
        "constant_columns": constant,
        "issues": issues,
    }


def complete_cases(df: pd.DataFrame, cols: List[str]) -> tuple[pd.DataFrame, Dict[str, Any]]:
    """Listwise deletion on the columns used by one analysis, with an explicit report."""
    missing_cols = [c for c in cols if c not in df.columns]
    if missing_cols:
        raise KeyError(f"Columns not found in dataset: {missing_cols}")
    sub = df[cols].replace([np.inf, -np.inf], np.nan)
    clean = sub.dropna()
    return clean, {"n_before": len(df), "n_after": len(clean), "n_dropped": len(df) - len(clean),
                   "dropped_fraction": (len(df) - len(clean)) / max(len(df), 1)}


def split_discovery_confirmation(df: pd.DataFrame, seed: int = 42, frac: float = 0.5):
    """Random hold-out split: patterns are mined on one part, tested on the other."""
    disc = df.sample(frac=frac, random_state=seed)
    conf = df.drop(disc.index)
    return disc.sort_index(), conf.sort_index()
