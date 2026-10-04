"""Pattern discovery: correlations, associations, trends, clusters, anomalies,
non-linear relationships and feature interactions.

Every detector returns "findings": dicts that say what was found, how strong it is, why it
might matter, and (where testable) a candidate hypothesis. Findings are LEADS, not conclusions.
"""
from __future__ import annotations

from itertools import combinations
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.feature_selection import mutual_info_regression
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from analysis.pattern_mining import benjamini_hochberg, mine_patterns
from analysis.statistical_tests import ols_fit
from utils.helpers import to_native

TIME_COL = "time_index"


def add_time_index(df: pd.DataFrame, date_col: Optional[str]) -> pd.DataFrame:
    """Adds a numeric 'days since start' column so trends can be tested like any other predictor."""
    out = df.copy()
    if date_col and date_col in out.columns:
        t = pd.to_datetime(out[date_col], errors="coerce")
        out[TIME_COL] = (t - t.min()).dt.total_seconds() / 86400.0
    return out


def _finding(kind, title, columns, metrics, why, hypothesis=None, x=None, y=None, controls=None,
             caveat=""):
    return {"kind": kind, "title": title, "columns": list(columns), "metrics": metrics,
            "why_interesting": why, "suggested_hypothesis": hypothesis, "x": x, "y": y,
            "controls": list(controls or []), "caveat": caveat}


def _dir(r):
    return "higher" if r > 0 else "lower"


# ---------------------------------------------------------------- correlations
def find_correlations(df, cols, alpha=0.05) -> List[Dict]:
    pats = mine_patterns(df, cols, alpha=alpha, min_abs_rho=0.2)
    out = []
    for _, r in pats.iterrows():
        pear = df[[r.x, r.y]].dropna().corr().iloc[0, 1]
        out.append(_finding(
            "correlation", f"{r.x} ~ {r.y}", [r.x, r.y],
            {"spearman_rho": r.spearman_rho, "pearson_r": pear, "fdr_q": r.fdr_q, "n": r.n},
            f"Monotonic association (rho={r.spearman_rho:.2f}, FDR q={r.fdr_q:.3g}) that survives "
            "multiple-testing control.",
            f"Higher {r.x} is associated with {_dir(r.spearman_rho)} {r.y}.", r.x, r.y,
            caveat=r.note or "Association only; confounding or reverse direction not excluded."))
    return out


# ------------------------------------------------------------- non-linear (MI)
def find_nonlinear(df, cols, seed=42, n_perm=200, alpha=0.05, top=12) -> List[Dict]:
    rng = np.random.default_rng(seed)
    cand = []
    for a, b in combinations(cols, 2):
        d = df[[a, b]].dropna()
        if len(d) < 50:
            continue
        mi = mutual_info_regression(d[[a]].values, d[b].values, random_state=seed)[0]
        rho = abs(stats.spearmanr(d[a], d[b])[0])
        pear = abs(stats.pearsonr(d[a], d[b])[0])
        cand.append((a, b, mi, rho, pear, d))
    # Non-linear leads: information content is high while linear/monotonic signal is weak.
    cand = [c for c in cand if c[2] >= 0.05 and c[3] < 0.3 and c[4] < 0.3]
    cand.sort(key=lambda c: -c[2])
    out, pvals = [], []
    for a, b, mi, rho, pear, d in cand[:top]:
        null = np.array([mutual_info_regression(d[[a]].values, rng.permutation(d[b].values),
                                                random_state=seed)[0] for _ in range(n_perm)])
        pvals.append((1 + (null >= mi).sum()) / (n_perm + 1))
        out.append((a, b, mi, rho, pear, len(d)))
    if not out:
        return []
    q = benjamini_hochberg(np.array(pvals))
    res = []
    for (a, b, mi, rho, pear, n), p, qq in zip(out, pvals, q):
        if qq < alpha:
            res.append(_finding(
                "nonlinear", f"{a} -> {b} (non-linear)", [a, b],
                {"mutual_information": mi, "spearman_abs": rho, "pearson_abs": pear,
                 "perm_p": p, "fdr_q": qq, "n": n},
                f"{a} carries information about {b} (MI={mi:.3f}, permutation FDR q={qq:.3g}) "
                f"although the linear/monotonic signal is weak (|rho|={rho:.2f}).",
                f"{b} depends on {a} through a non-linear (e.g. threshold or U-shaped) relationship.",
                a, b, caveat="Linear tests will understate this; inspect the scatter plot and "
                             "compare random-forest vs linear performance."))
    return res


# -------------------------------------------------------------- associations
def find_associations(df, numeric_cols, alpha=0.05, max_levels=12) -> List[Dict]:
    cat = [c for c in df.columns if (df[c].dtype == object or str(df[c].dtype) == "category"
                                     or (df[c].dtype != float and c in numeric_cols and df[c].nunique() <= 6
                                         and df[c].nunique() < len(df) * 0.05))
           and 2 <= df[c].nunique() <= max_levels]
    raw = []
    for c in cat:
        for n in numeric_cols:
            if n == c:
                continue
            d = df[[c, n]].dropna()
            groups = [g[n].values for _, g in d.groupby(c) if len(g) >= 5]
            if len(groups) < 2:
                continue
            h, p = stats.kruskal(*groups)
            eps2 = max(0.0, (h - len(groups) + 1) / (len(d) - len(groups)))
            raw.append(("cat-num", c, n, p, eps2, len(d)))
    for a, b in combinations(cat, 2):
        d = df[[a, b]].dropna()
        tab = pd.crosstab(d[a], d[b])
        if tab.shape[0] < 2 or tab.shape[1] < 2:
            continue
        chi2, p, _, _ = stats.chi2_contingency(tab)
        v = np.sqrt(chi2 / (len(d) * (min(tab.shape) - 1)))
        raw.append(("cat-cat", a, b, p, v, len(d)))
    if not raw:
        return []
    q = benjamini_hochberg(np.array([r[3] for r in raw]))
    out = []
    for (typ, a, b, p, eff, n), qq in zip(raw, q):
        if qq < alpha and eff >= 0.06:
            out.append(_finding(
                "association", f"{a} <-> {b}", [a, b],
                {"test": "Kruskal-Wallis" if typ == "cat-num" else "chi-square",
                 "effect_size": eff, "fdr_q": qq, "n": n},
                f"{b} differs across groups of {a} (effect size {eff:.2f}, FDR q={qq:.3g}).",
                f"{b} varies systematically between categories of {a}.",
                caveat="Group differences do not show why the groups differ."))
    return out


# ---------------------------------------------------------------------- trends
def find_trends(df, cols, date_col, alpha=0.05, min_abs_tau=0.05) -> List[Dict]:
    if not date_col or TIME_COL not in df.columns:
        return []
    raw = []
    for c in cols:
        if c == TIME_COL:
            continue
        d = df[[TIME_COL, c]].dropna()
        if len(d) < 30:
            continue
        tau, p = stats.kendalltau(d[TIME_COL], d[c])
        slope = stats.theilslopes(d[c], d[TIME_COL])[0]
        raw.append((c, tau, p, slope * 365.25, len(d)))
    if not raw:
        return []
    q = benjamini_hochberg(np.array([r[2] for r in raw]))
    return [_finding(
        "trend", f"{c} over time", [c, TIME_COL],
        {"kendall_tau": tau, "p_value": p, "fdr_q": qq, "theil_sen_slope_per_year": slope, "n": n},
        f"Monotonic drift over time (tau={tau:.2f}, about {slope:+.3g} units/year, FDR q={qq:.3g}).",
        f"{c} shows a {'rising' if tau > 0 else 'falling'} trend over the observation period.",
        TIME_COL, c,
        caveat="Seasonality and autocorrelation can create apparent trends; compare full years.")
        for (c, tau, p, slope, n), qq in zip(raw, q) if qq < alpha and abs(tau) >= min_abs_tau]


# -------------------------------------------------------------------- clusters
def find_clusters(df, cols, seed=42, min_silhouette=0.25) -> List[Dict]:
    d = df[cols].dropna()
    if len(d) < 60 or len(cols) < 2:
        return []
    Z = StandardScaler().fit_transform(d.values)
    best = None
    for k in range(2, 7):
        lab = KMeans(n_clusters=k, n_init=10, random_state=seed).fit_predict(Z)
        s = silhouette_score(Z, lab, sample_size=min(len(Z), 2000), random_state=seed)
        if best is None or s > best[0]:
            best = (s, k, lab)
    s, k, lab = best
    if s < min_silhouette:
        return [_finding("cluster", "No clear cluster structure", cols,
                         {"best_k": k, "silhouette": s, "n": len(d)},
                         f"Best silhouette was {s:.2f} (k={k}), below {min_silhouette}: the data look "
                         "like one continuous cloud rather than separate groups.", caveat="Negative result.")]
    prof = pd.DataFrame(Z, columns=cols).assign(cl=lab).groupby("cl").mean()
    spread = (prof.max() - prof.min()).sort_values(ascending=False)
    drivers = spread.index[:3].tolist()
    return [_finding("cluster", f"{k} clusters found", cols,
                     {"best_k": k, "silhouette": s, "driving_variables": drivers, "n": len(d),
                      "cluster_sizes": pd.Series(lab).value_counts().sort_index().tolist()},
                     f"K-means finds {k} groups (silhouette={s:.2f}) separated mainly by {drivers}.",
                     f"Observations fall into {k} regimes distinguished by {', '.join(drivers)}.",
                     caveat="Clusters depend on scaling and algorithm; validate with another method.")]


# ------------------------------------------------------------------- anomalies
def find_anomalies(df, cols, seed=42, contamination=0.02) -> List[Dict]:
    d = df[cols].dropna()
    if len(d) < 60:
        return []
    iso = IsolationForest(contamination=contamination, random_state=seed).fit(d.values)
    flag = iso.predict(d.values) == -1
    z = (d - d.mean()) / d.std(ddof=0)
    drivers = z[flag].abs().median().sort_values(ascending=False).index[:3].tolist()
    idx = d.index[flag].tolist()
    return [_finding("anomaly", f"{int(flag.sum())} anomalous rows", cols,
                     {"n_anomalies": int(flag.sum()), "contamination": contamination,
                      "most_deviant_variables": drivers, "row_index_sample": idx[:20]},
                     f"{int(flag.sum())} rows ({flag.mean():.1%}) are multivariate outliers, "
                     f"mainly unusual in {drivers}.",
                     None, caveat="Contamination rate is a setting, not a finding: the count is "
                                  "approximately contamination x n. Inspect the rows for errors or events.")]


# ---------------------------------------------------------------- interactions
def find_interactions(df, cols, alpha=0.05, top_pred=4, min_delta_r2=0.01) -> List[Dict]:
    raw = []
    for y in cols:
        others = [c for c in cols if c != y]
        d0 = df[[y] + others].dropna()
        if len(d0) < 100:
            continue
        rho = d0.corr(method="spearman")[y].drop(y).abs().sort_values(ascending=False)
        preds = rho.index[:top_pred].tolist()
        for a, b in combinations(preds, 2):
            d = df[[y, a, b]].dropna()
            za, zb = stats.zscore(d[a]), stats.zscore(d[b])
            yv = d[y].values
            try:
                red = ols_fit(np.column_stack([za, zb]), yv)
                full = ols_fit(np.column_stack([za, zb, za * zb]), yv)
            except ValueError:
                continue
            dr2 = full["r2"] - red["r2"]
            F = dr2 / ((1 - full["r2"]) / full["dof"])
            p = stats.f.sf(F, 1, full["dof"])
            raw.append((y, a, b, dr2, p, float(full["beta"][3]), len(d)))
    if not raw:
        return []
    q = benjamini_hochberg(np.array([r[4] for r in raw]))
    return [_finding(
        "interaction", f"{a} x {b} -> {y}", [a, b, y],
        {"delta_r2": dr2, "interaction_coef_std": coef, "p_value": p, "fdr_q": qq, "n": n},
        f"The effect of {a} on {y} depends on {b} (adds {dr2:.1%} explained variance, FDR q={qq:.3g}).",
        f"The relationship between {a} and {y} is moderated by {b}.", a, y, [b],
        caveat="Tested over many predictor pairs; confirm on new data before trusting.")
        for (y, a, b, dr2, p, coef, n), qq in zip(raw, q) if qq < alpha and dr2 >= min_delta_r2]


# ------------------------------------------------------------------ entrypoint
def discover(df: pd.DataFrame, date_col: Optional[str] = None, seed: int = 42,
             alpha: float = 0.05) -> Dict[str, Any]:
    """Run every detector. Detectors that fail are reported, not hidden."""
    d = add_time_index(df, date_col)
    cols = [c for c in df.select_dtypes(include=[np.number]).columns
            if df[c].nunique() > 1 and c != TIME_COL]
    detectors = {
        "correlations": lambda: find_correlations(d, cols, alpha),
        "nonlinear": lambda: find_nonlinear(d, cols, seed, alpha=alpha),
        "associations": lambda: find_associations(d, cols, alpha),
        "trends": lambda: find_trends(d, cols, date_col, alpha),
        "clusters": lambda: find_clusters(d, cols, seed),
        "anomalies": lambda: find_anomalies(d, cols, seed),
        "interactions": lambda: find_interactions(d, cols, alpha),
    }
    findings, errors = [], {}
    for name, fn in detectors.items():
        try:
            findings.extend(fn())
        except Exception as exc:
            errors[name] = f"{type(exc).__name__}: {exc}"
    corr_pairs = {frozenset(f["columns"]) for f in findings if f["kind"] == "correlation"}
    findings = [f for f in findings if not (f["kind"] == "nonlinear" and frozenset(f["columns"]) in corr_pairs)]
    for i, f in enumerate(findings, 1):
        f["id"] = f"F{i}"
    counts = pd.Series([f["kind"] for f in findings]).value_counts().to_dict() if findings else {}
    return to_native({"findings": findings, "counts": counts, "errors": errors,
                      "n_rows": len(df), "columns_used": cols})
