"""Statistical evidence for one candidate relationship (stand-in for the Statistical Testing agent)."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

import numpy as np
import pandas as pd
from scipy import stats

from analysis.preprocessing import complete_cases
from utils.helpers import to_native


def direction_of(v: Optional[float], eps: float = 1e-12) -> str:
    if v is None or not np.isfinite(v):
        return "undetermined"
    return "positive" if v > eps else "negative" if v < -eps else "none"


def ols_fit(X, y, alpha: float = 0.05) -> Dict[str, Any]:
    """Plain OLS with an intercept. X has no intercept column. Index 0 of the returned arrays
    is the intercept; index 1 is the first predictor."""
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    if X.ndim == 1:
        X = X[:, None]
    n = len(y)
    Xd = np.column_stack([np.ones(n), X])
    k = Xd.shape[1]
    dof = n - k
    if dof <= 2:
        raise ValueError(f"Too few observations (n={n}) for {k} parameters.")
    beta, *_ = np.linalg.lstsq(Xd, y, rcond=None)
    resid = y - Xd @ beta
    rss = float(resid @ resid)
    tss = float(((y - y.mean()) ** 2).sum())
    if tss == 0:
        raise ValueError("The outcome variable has zero variance.")
    cov = (rss / dof) * np.linalg.pinv(Xd.T @ Xd)
    se = np.sqrt(np.clip(np.diag(cov), 0, None))
    with np.errstate(divide="ignore", invalid="ignore"):
        t = beta / se
    p = 2 * stats.t.sf(np.abs(t), dof)
    tcrit = stats.t.ppf(1 - alpha / 2, dof)
    return {"n": n, "dof": dof, "beta": beta, "se": se, "t": t, "p": p,
            "ci_low": beta - tcrit * se, "ci_high": beta + tcrit * se,
            "r2": 1 - rss / tss, "resid": resid}


def predictor_summary(fit: Dict[str, Any], x: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
    """Summary of the main predictor (first column of X) from an ols_fit result."""
    coef = float(fit["beta"][1])
    t = float(fit["t"][1])
    sx, sy = float(np.std(x, ddof=1)), float(np.std(y, ddof=1))
    return {
        "coef": coef, "se": float(fit["se"][1]), "p_value": float(fit["p"][1]),
        "ci_low": float(fit["ci_low"][1]), "ci_high": float(fit["ci_high"][1]),
        "std_beta": coef * sx / sy if sy > 0 else None,
        "partial_r2": t ** 2 / (t ** 2 + fit["dof"]),
        "r2": float(fit["r2"]), "n": int(fit["n"]), "direction": direction_of(coef),
    }


def variance_inflation(X: np.ndarray) -> List[float]:
    X = np.asarray(X, float)
    if X.ndim == 1 or X.shape[1] < 2:
        return [1.0]
    out = []
    for j in range(X.shape[1]):
        others = np.delete(X, j, axis=1)
        try:
            r2 = ols_fit(others, X[:, j])["r2"]
            out.append(float(1 / (1 - r2)) if r2 < 1 else float("inf"))
        except ValueError:
            out.append(float("nan"))
    return out


def effect_size_label(std_beta: Optional[float]) -> str:
    if std_beta is None:
        return "undetermined"
    a = abs(std_beta)
    return "negligible" if a < 0.1 else "small" if a < 0.3 else "moderate" if a < 0.5 else "large"


def test_relationship(df: pd.DataFrame, x: str, y: str, controls: Sequence[str] = (),
                      alpha: float = 0.05, date_col: Optional[str] = None) -> Dict[str, Any]:
    """Correlation + adjusted OLS + assumption checks. Failures are returned, never hidden."""
    controls = list(controls)
    cols = [x, y] + controls
    try:
        d, report = complete_cases(df, cols + ([date_col] if date_col else []))
        if date_col:
            d = d.sort_values(date_col)
        d = d[cols].astype(float)
        xv, yv = d[x].values, d[y].values
        pr, pp = stats.pearsonr(xv, yv)
        sr, sp = stats.spearmanr(xv, yv)
        X = d[[x] + controls].values
        fit = ols_fit(X, yv, alpha)
        main = predictor_summary(fit, xv, yv)

        notes: List[str] = []
        resid = fit["resid"]
        norm_p = float(stats.normaltest(resid).pvalue) if len(resid) >= 8 else None
        if norm_p is not None and norm_p < alpha:
            notes.append("Residuals deviate from normality; p-values and CIs are approximate "
                         "(bootstrap CIs are reported under robustness).")
        dw = float(np.sum(np.diff(resid) ** 2) / np.sum(resid ** 2))
        if date_col and (dw < 1.5 or dw > 2.5):
            notes.append(f"Durbin-Watson = {dw:.2f}: residuals are serially correlated, so "
                         "standard errors are likely too small for time-ordered data.")
        vifs = variance_inflation(X)
        if max(vifs) > 5:
            notes.append(f"High multicollinearity (max VIF = {max(vifs):.1f}); coefficient "
                         "estimates may be unstable.")
        if report["dropped_fraction"] > 0.05:
            notes.append(f"{report['n_dropped']} rows dropped for missing values.")

        return to_native({
            "test": "pearson_spearman_ols", "variables": {"x": x, "y": y, "controls": controls},
            "n": len(d), "missing_handling": report,
            "pearson": {"r": pr, "p_value": pp}, "spearman": {"rho": sr, "p_value": sp},
            "ols": main, "effect_size_label": effect_size_label(main["std_beta"]),
            "assumptions": {"residual_normality_p": norm_p,
                            "durbin_watson": dw if date_col else None,
                            "max_vif": max(vifs), "notes": notes},
            "alpha": alpha, "error": None,
        })
    except Exception as exc:  # reported to the user, not swallowed
        return {"test": "pearson_spearman_ols", "variables": {"x": x, "y": y, "controls": controls},
                "error": f"{type(exc).__name__}: {exc}"}
