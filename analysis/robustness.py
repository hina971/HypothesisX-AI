"""Robustness tests. Each function re-estimates the main coefficient under a different analytical
condition and compares it with the original estimate. Stability is decided by explicit rules
(config.tolerance, direction, significance), never by a hidden score."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import HuberRegressor
from sklearn.model_selection import RepeatedKFold

from analysis.statistical_tests import direction_of, ols_fit, predictor_summary
from schemas import RobustnessConfig, RobustnessResult
from utils.helpers import fmt, to_native


class Ctx:
    """Prepared analysis context: complete cases for the variables of one hypothesis."""
    def __init__(self, df, x, y, controls, cfg, date_col=None):
        self.x, self.y, self.controls, self.cfg = x, y, list(controls), cfg
        cols = [x, y] + self.controls + ([date_col] if date_col and date_col not in (x, y) else [])
        d = df[cols].replace([np.inf, -np.inf], np.nan).dropna()
        self.date = d[date_col] if date_col and date_col in d else None
        self.d = d[[x, y] + self.controls].astype(float)
        self.rng = np.random.default_rng(cfg.seed)
        self.orig = self.fit(self.d)

    def fit(self, d, controls=None):
        controls = self.controls if controls is None else controls
        X = d[[self.x] + list(controls)].values
        return predictor_summary(ols_fit(X, d[self.y].values, self.cfg.alpha), d[self.x].values, d[self.y].values)


def _orig_view(o):
    return {k: o[k] for k in ("coef", "p_value", "ci_low", "ci_high", "std_beta", "r2", "n", "direction")}


def classify(orig, mod, cfg, comparable_scale=True):
    """Return (stability, changed, reasons) comparing a modified estimate with the original."""
    reasons, changed = [], False
    if mod["direction"] != orig["direction"]:
        return "unstable", True, ["direction of the relationship reversed"]
    if comparable_scale and orig["coef"] != 0:
        rel = abs(mod["coef"] - orig["coef"]) / abs(orig["coef"])
        if rel > cfg.tolerance:
            changed = True
            reasons.append(f"coefficient moved {rel:.0%} (tolerance {cfg.tolerance:.0%})")
    o_sig = orig["p_value"] is not None and orig["p_value"] < cfg.alpha
    m_sig = mod.get("p_value") is not None and mod["p_value"] < cfg.alpha
    if mod.get("p_value") is not None and o_sig != m_sig:
        changed = True
        reasons.append("statistical significance " + ("was lost" if o_sig else "appeared"))
    return ("moderately_sensitive" if changed else "stable"), changed, reasons


def _describe(orig, mod, stability, reasons, extra=""):
    rel = (mod["coef"] - orig["coef"]) / abs(orig["coef"]) if orig["coef"] else float("nan")
    s = (f"Coefficient changed from {fmt(orig['coef'])} to {fmt(mod['coef'])} ({rel:+.1%}); "
         f"direction {mod['direction']} (original {orig['direction']}); p-value {fmt(orig['p_value'])} -> "
         f"{fmt(mod.get('p_value'))}. ")
    if stability == "stable":
        s += "The relationship remained reasonably stable. "
    else:
        s += "Why it matters: " + "; ".join(reasons) + ". "
    return s + extra


def _result(ctx, test, method, config, mod, stability, changed, interp, performance=None):
    return RobustnessResult(
        test=test, method=method, configuration=config, original_result=_orig_view(ctx.orig),
        modified_result=to_native(mod), stability=stability, changed_materially=changed,
        interpretation=interp, coefficient=mod.get("coef"), p_value=mod.get("p_value"),
        ci_low=mod.get("ci_low"), ci_high=mod.get("ci_high"), effect_size=mod.get("std_beta"),
        model_performance=to_native(performance or {}), direction=mod.get("direction"))


def _single(ctx, test, method, config, mod, comparable=True, extra="", performance=None):
    st, ch, rs = classify(ctx.orig, mod, ctx.cfg, comparable)
    return _result(ctx, test, method, config, mod, st, ch, _describe(ctx.orig, mod, st, rs, extra), performance)


def _distribution_result(ctx, test, method, config, coefs, extra_mod=None, performance=None, extra=""):
    coefs = np.asarray(coefs)
    o = ctx.orig
    med = float(np.median(coefs))
    sign_share = float(np.mean(np.sign(coefs) == np.sign(o["coef"])))
    lo, hi = np.percentile(coefs, [2.5, 97.5])
    rel = abs(med - o["coef"]) / abs(o["coef"]) if o["coef"] else np.inf
    excl0 = (lo > 0) or (hi < 0)
    o_sig = o["p_value"] < ctx.cfg.alpha
    mod = {"coef": med, "ci_low": float(lo), "ci_high": float(hi), "direction": direction_of(med),
           "std_beta": None, "p_value": float(2 * min(np.mean(coefs > 0), np.mean(coefs <= 0))),
           "sign_consistency": sign_share, "distribution": coefs[:1000].round(6).tolist()}
    mod.update(extra_mod or {})
    reasons = []
    if sign_share < 0.8:
        st = "unstable"; reasons.append(f"sign agreed in only {sign_share:.0%} of re-estimates")
    elif sign_share < 0.95 or rel > ctx.cfg.tolerance or (excl0 != o_sig):
        st = "moderately_sensitive"
        if sign_share < 0.95: reasons.append(f"sign agreed in {sign_share:.0%} of re-estimates")
        if rel > ctx.cfg.tolerance: reasons.append(f"median coefficient moved {rel:.0%}")
        if excl0 != o_sig: reasons.append("the 95% interval " + ("now includes" if o_sig else "now excludes") + " zero")
    else:
        st = "stable"
    changed = st != "stable"
    interp = (f"Across {len(coefs)} re-estimates the median coefficient was {fmt(med)} "
              f"(95% range {fmt(lo)} to {fmt(hi)}) vs original {fmt(o['coef'])}; the sign matched in "
              f"{sign_share:.0%}. " + ("The relationship remained reasonably stable. " if st == "stable"
              else "Why it matters: " + "; ".join(reasons) + ". ") + extra)
    return _result(ctx, test, method, config, mod, st, changed, interp, performance)


# ---------------------------------------------------------------------- tests
def bootstrap_test(ctx) -> List[RobustnessResult]:
    n, B = len(ctx.d), ctx.cfg.n_boot
    X = ctx.d[[ctx.x] + ctx.controls].values
    y = ctx.d[ctx.y].values
    coefs = []
    for _ in range(B):
        i = ctx.rng.integers(0, n, n)
        try:
            coefs.append(ols_fit(X[i], y[i])["beta"][1])
        except ValueError:
            continue
    return [_distribution_result(ctx, "bootstrap", "Nonparametric bootstrap (rows resampled with replacement)",
                                 {"n_resamples": len(coefs), "sample_size": n, "seed": ctx.cfg.seed}, coefs,
                                 extra="Bootstrap interval does not rely on normal residuals.")]


def split_half_test(ctx) -> List[RobustnessResult]:
    n, S = len(ctx.d), ctx.cfg.n_splits
    X = ctx.d[[ctx.x] + ctx.controls].values
    y = ctx.d[ctx.y].values
    coefs, sig = [], []
    for _ in range(S):
        i = ctx.rng.permutation(n)[: n // 2]
        f = ols_fit(X[i], y[i])
        coefs.append(f["beta"][1]); sig.append(f["p"][1] < ctx.cfg.alpha)
    return [_distribution_result(ctx, "random_subsamples", "Repeated random half-samples",
                                 {"n_subsamples": S, "sample_size": n // 2, "seed": ctx.cfg.seed}, coefs,
                                 extra_mod={"share_significant": float(np.mean(sig))},
                                 extra=f"Half-samples had less power; {np.mean(sig):.0%} were individually significant.")]


def temporal_split_test(ctx) -> List[RobustnessResult]:
    if ctx.date is None:
        return []
    d = ctx.d.loc[ctx.date.sort_values().index]
    h = len(d) // 2
    out = []
    for name, part in (("first_half", d.iloc[:h]), ("second_half", d.iloc[h:])):
        mod = ctx.fit(part)
        out.append(_single(ctx, f"temporal_split_{name}", "Re-fit on one half of the time range",
                           {"sample_size": len(part), "period": name}, mod,
                           extra="Different periods can reveal drift or seasonality."))
    return out


def cv_stability_test(ctx) -> List[RobustnessResult]:
    X = ctx.d[[ctx.x] + ctx.controls].values
    y = ctx.d[ctx.y].values
    cv = RepeatedKFold(n_splits=5, n_repeats=2, random_state=ctx.cfg.seed)
    coefs, oof = [], []
    for tr, te in cv.split(X):
        f = ols_fit(X[tr], y[tr])
        coefs.append(f["beta"][1])
        pred = np.column_stack([np.ones(len(te)), X[te]]) @ f["beta"]
        oof.append(1 - ((y[te] - pred) ** 2).sum() / ((y[te] - y[te].mean()) ** 2).sum())
    perf = {"in_sample_r2": ctx.orig["r2"], "out_of_fold_r2_mean": float(np.mean(oof)),
            "out_of_fold_r2_sd": float(np.std(oof, ddof=1))}
    return [_distribution_result(ctx, "cross_validation", "Coefficient across 2x repeated 5-fold training sets",
                                 {"folds": len(coefs), "seed": ctx.cfg.seed}, coefs, performance=perf,
                                 extra=f"Out-of-fold R2 = {perf['out_of_fold_r2_mean']:.3f} vs in-sample "
                                       f"{perf['in_sample_r2']:.3f}.")]


def outlier_test(ctx) -> List[RobustnessResult]:
    d, cfg = ctx.d, ctx.cfg
    z = np.abs(stats.zscore(d[[ctx.x, ctx.y]].values, axis=0))
    keep = (z < cfg.outlier_z).all(axis=1)
    out = []
    if keep.all():
        mod = dict(_orig_view(ctx.orig))
        out.append(_result(ctx, "outlier_removal", f"Remove rows with |z| >= {cfg.outlier_z}",
                           {"rows_removed": 0}, mod, "stable", False,
                           f"No observations exceeded |z| >= {cfg.outlier_z}, so removal changes nothing."))
    else:
        mod = ctx.fit(d[keep])
        out.append(_single(ctx, "outlier_removal", f"Remove rows with |z| >= {cfg.outlier_z} on x or y",
                           {"rows_removed": int((~keep).sum()), "sample_size": int(keep.sum())}, mod))
    lo, hi = cfg.winsor_pct, 1 - cfg.winsor_pct
    w = d.copy()
    for c in (ctx.x, ctx.y):
        w[c] = w[c].clip(d[c].quantile(lo), d[c].quantile(hi))
    out.append(_single(ctx, "winsorization", f"Clip x and y at the {lo:.0%}/{hi:.0%} percentiles",
                       {"percentiles": [lo, hi]}, ctx.fit(w)))
    return out


def alternative_model_test(ctx) -> List[RobustnessResult]:
    d = ctx.d
    X = d[[ctx.x] + ctx.controls].values
    y = d[ctx.y].values
    sd = X.std(axis=0, ddof=1); mu = X.mean(axis=0)
    hub = HuberRegressor(epsilon=1.35, max_iter=500).fit((X - mu) / sd, y)
    coef = float(hub.coef_[0] / sd[0])
    mod = {"coef": coef, "p_value": None, "ci_low": None, "ci_high": None,
           "direction": direction_of(coef), "std_beta": coef * sd[0] / y.std(ddof=1)}
    out = [_single(ctx, "alternative_model_huber", "Huber robust regression (down-weights extreme residuals)",
                   {"epsilon": 1.35}, mod, extra="No p-value is available for this estimator.")]
    ranked = d.rank()
    out.append(_single(ctx, "alternative_method_rank_regression", "OLS on ranks (monotonic, outlier-resistant)",
                       {"transform": "rank"}, ctx.fit(ranked), comparable=False,
                       extra="Coefficient is on a rank scale, so only direction and significance are compared."))
    return out


def feature_variation_test(ctx, df_full: pd.DataFrame) -> List[RobustnessResult]:
    out = []
    for c in ctx.controls:
        rest = [k for k in ctx.controls if k != c]
        out.append(_single(ctx, f"feature_variation_drop_{c}", f"Drop control '{c}'",
                           {"controls": rest}, ctx.fit(ctx.d, rest)))
    cand = [c for c in df_full.select_dtypes(include=[np.number]).columns
            if c not in [ctx.x, ctx.y] + ctx.controls and df_full[c].nunique() > 1]
    if cand:
        sub = df_full.loc[ctx.d.index, cand]
        score = sub.apply(lambda s: max(abs(s.corr(ctx.d[ctx.x], method="spearman")),
                                        abs(s.corr(ctx.d[ctx.y], method="spearman")))).fillna(0)
        for c in score.sort_values(ascending=False).index[: ctx.cfg.max_candidate_features]:
            dd = ctx.d.copy(); dd[c] = df_full.loc[ctx.d.index, c].astype(float)
            if dd[c].isna().any():
                continue
            mod = ctx.fit(dd, ctx.controls + [c])
            res = _single(ctx, f"feature_variation_add_{c}", f"Add candidate control '{c}'",
                          {"controls": ctx.controls + [c]}, mod,
                          extra="A change can reflect confounding, mediation or collinearity; this test "
                                "alone cannot tell which.")
            out.append(res)
    return out


ALL_TESTS = ("bootstrap", "random_subsamples", "temporal", "cross_validation", "outliers",
             "alternative_models", "feature_variation")
