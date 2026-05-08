"""
Shared statistical utility functions for Korea Discount study.

Functions:
    winsorize(arr, lower=0.01, upper=0.01) -> np.ndarray
    cohens_kappa(rater1, rater2, labels=None) -> tuple[float, float]
    robust_se(model) -> pd.Series
"""

import numpy as np
import pandas as pd
from scipy.stats.mstats import winsorize as _winsorize
from statsmodels.stats.inter_rater import cohens_kappa as _cohens_kappa


def winsorize(arr, lower=0.01, upper=0.01):
    """
    Winsorize array at lower/upper quantile limits.

    Args:
        arr: array-like (pd.Series or np.ndarray); NaN values are propagated.
        lower: lower quantile limit (default 0.01 = 1st percentile)
        upper: upper quantile limit (default 0.01 = 99th percentile)

    Returns:
        np.ndarray with tails clipped. Plain numpy array, not MaskedArray.

    Example:
        winsorize(df["pbr"], lower=0.01, upper=0.01)
    """
    values = np.asarray(arr, dtype=float)
    result = values.copy()
    valid_mask = ~np.isnan(values)
    if valid_mask.any():
        result[valid_mask] = np.asarray(
            _winsorize(values[valid_mask], limits=[lower, upper]),
            dtype=float,
        )
    return result


def cohens_kappa(rater1, rater2, labels=None):
    """
    Compute Cohen's Kappa inter-rater reliability.

    Args:
        rater1: list/array of integer codes (e.g. [0, 1, 2, 1, 0])
        rater2: list/array of integer codes (same length as rater1)
        labels: list of unique codes; if None, inferred from union of rater1 + rater2

    Returns:
        tuple (kappa: float, p_value: float)

    Example:
        kappa, p = cohens_kappa(coder_a_codes, coder_b_codes, labels=[0, 1, 2])
        print(f"kappa = {kappa:.3f} (p = {p:.4f})")
    """
    rater1 = list(rater1)
    rater2 = list(rater2)
    if len(rater1) != len(rater2):
        raise ValueError("rater1 and rater2 must have the same length.")

    if labels is None:
        labels = sorted(set(rater1) | set(rater2))
    idx = {value: i for i, value in enumerate(labels)}
    table = np.zeros((len(labels), len(labels)), dtype=int)
    for a, b in zip(rater1, rater2):
        if a not in idx or b not in idx:
            raise ValueError("labels must include every rating in rater1 and rater2.")
        table[idx[a]][idx[b]] += 1

    result = _cohens_kappa(table)
    return float(result.kappa), float(result.pvalue_two_sided)


def robust_se(model):
    """
    Extract HC3 robust standard errors from a fitted statsmodels model.

    Args:
        model: statsmodels RegressionResultsWrapper fitted with cov_type="HC3",
            e.g. model.fit(cov_type="HC3")

    Returns:
        pd.Series of robust standard errors indexed by parameter name.

    Example:
        result = smf.logit("complied ~ pbr + roe", data=df).fit(cov_type="HC3")
        se = robust_se(result)
    """
    bse = model.bse
    if isinstance(bse, pd.Series):
        return bse

    index = None
    params = getattr(model, "params", None)
    if isinstance(params, pd.Series):
        index = params.index
    return pd.Series(bse, index=index)
