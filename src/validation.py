"""
Statistical Validation & Predictive Modeling Module
===================================================
Empirical hypothesis testing and logistic classification validating the
Kinetic Translation Deficit (KTD) metric against traditional Combine velocity.

Author: NFL Big Data Bowl 2027 Research Team
License: MIT
"""

from typing import Dict, Tuple
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import cross_val_predict


def run_statistical_hypothesis_tests(df: pd.DataFrame) -> Dict[str, float]:
    """
    Executes parametric and non-parametric correlation tests between KTD and game performance.

    Args:
        df (pd.DataFrame): Master dataset with KTD scores and game metrics.

    Returns:
        Dict[str, float]: Statistical metrics (Spearman, Pearson, p-values).
    """
    active = df[df["routes_run_count"] >= 5].copy()

    # Spearman rank correlation (non-parametric monotonic relationship)
    spearman_corr, spearman_p = stats.spearmanr(active["KTD_Score"], active["avg_separation"])
    pearson_corr, pearson_p = stats.pearsonr(active["KTD_Score"], active["avg_separation"])

    # Benchmark: Traditional combine speed correlation
    trad_corr, trad_p = stats.spearmanr(active["combine_top_speed"], active["avg_separation"])

    return {
        "ktd_spearman_corr": round(spearman_corr, 4),
        "ktd_spearman_pvalue": spearman_p,
        "ktd_pearson_corr": round(pearson_corr, 4),
        "trad_spearman_corr": round(trad_corr, 4),
    }


def evaluate_draft_tier_classification(df: pd.DataFrame) -> Dict[str, float]:
    """
    Evaluates out-of-fold ROC-AUC discriminative performance of KTD vs. Traditional Speed.

    Target: Predicting above-median in-game route separation (Elite Separators).

    Args:
        df (pd.DataFrame): Filtered prospect evaluation records.

    Returns:
        Dict[str, float]: Cross-validated ROC-AUC and Accuracy scores.
    """
    active = df[df["routes_run_count"] >= 5].copy()
    median_sep = active["avg_separation"].median()
    active["is_elite"] = (active["avg_separation"] >= median_sep).astype(int)

    X_ktd = active[["KTD_Score", "combine_speed_retention"]]
    X_trad = active[["combine_top_speed"]]
    y = active["is_elite"]

    # 5-Fold Cross-Validation Predictions
    clf_ktd = LogisticRegression(random_state=42)
    clf_trad = LogisticRegression(random_state=42)

    prob_ktd = cross_val_predict(clf_ktd, X_ktd, y, cv=5, method="predict_proba")[:, 1]
    prob_trad = cross_val_predict(clf_trad, X_trad, y, cv=5, method="predict_proba")[:, 1]

    auc_ktd = roc_auc_score(y, prob_ktd)
    auc_trad = roc_auc_score(y, prob_trad)

    return {
        "ktd_roc_auc": round(auc_ktd, 3),
        "trad_roc_auc": round(auc_trad, 3),
        "relative_predictive_lift_pct": round(((auc_ktd - auc_trad) / auc_trad) * 100, 1),
    }


def assign_strategic_draft_tiers(row: pd.Series) -> str:
    """
    Categorizes prospects into actionable front-office decision tiers.

    Args:
        row (pd.Series): Prospect record containing KTD_Score.

    Returns:
        str: Strategic draft classification tier.
    """
    score = row["KTD_Score"]
    if score <= 1.40:
        return "Tier 1: High-Translation Value (Steal Potential)"
    elif score <= 2.00:
        return "Tier 2: Baseline Operational Translator"
    return "Tier 3: Track-Speed Trap (High Bust Risk)"
