#------------------------------------------------------------------------------
# Model evaluation helper functions
#------------------------------------------------------------------------------
import numpy as np
import pandas as pd

from sklearn.metrics import average_precision_score, roc_auc_score, brier_score_loss, precision_recall_curve

from .config import TOP_FRAC, RANKING_TOP_FRACS, RANKING_TOP_NS

#------------------------------------------------------------------------------
# Calculate main model metrics
#------------------------------------------------------------------------------
def calc_binary_metrics(y_true, y_prob, split_name, model_name, top_frac=TOP_FRAC):
    y_true = np.asarray(y_true).astype(int)
    y_prob = np.asarray(y_prob).astype(float)

    n_obs = len(y_true)
    n_positive = int(y_true.sum())
    prevalence = float(y_true.mean()) if n_obs > 0 else np.nan

    # Keep only the highest scored sessions for top-k metrics
    order = np.argsort(-y_prob)
    k_n = max(1, int(np.ceil(n_obs * top_frac)))
    y_top = y_true[order][:k_n]

    precision_at_k = float(y_top.mean()) if len(y_top) > 0 else np.nan
    recall_at_k = float(y_top.sum() / n_positive) if n_positive > 0 else np.nan
    lift_at_k = float(precision_at_k / prevalence) if prevalence > 0 else np.nan

    return {"split": split_name, "data_split": split_name, "model": model_name,
            "n_obs": int(n_obs), "n_positive": int(n_positive), "prevalence": prevalence,
            "pr_auc": float(average_precision_score(y_true, y_prob)) if n_positive > 0 else np.nan,
            "roc_auc": float(roc_auc_score(y_true, y_prob)) if len(np.unique(y_true)) > 1 else np.nan,
            "brier_score": float(brier_score_loss(y_true, y_prob)),
            "top_frac": float(top_frac), "k_n": int(len(y_top)),
            "precision_at_k": precision_at_k, "recall_at_k": recall_at_k, "lift_at_k": lift_at_k}

#------------------------------------------------------------------------------
# Calculate ranking metrics at review cut-offs
#------------------------------------------------------------------------------
def calc_rank_metrics_at_cutoff(y_true, y_score, split_name, model_name, cutoff_label, top_frac=None, top_n=None):
    y_true = np.asarray(y_true).astype(int)
    y_score = np.asarray(y_score).astype(float)

    n_obs = len(y_true)
    n_positive = int(y_true.sum())
    prevalence = float(y_true.mean()) if n_obs > 0 else np.nan

    order = np.argsort(-y_score)
    y_sorted = y_true[order]

    # Choose either a percent cut-off or fixed row count
    if top_frac is not None:
        k = max(1, int(np.ceil(n_obs * float(top_frac))))
        cutoff_type = "share"
        cutoff_value = float(top_frac)
    elif top_n is not None:
        k = min(n_obs, int(top_n))
        cutoff_type = "count"
        cutoff_value = int(top_n)
    else:
        raise ValueError("Either top_frac or top_n must be provided.")

    y_top = y_sorted[:k]
    precision_at_k = float(y_top.mean()) if len(y_top) > 0 else np.nan
    recall_at_k = float(y_top.sum() / n_positive) if n_positive > 0 else np.nan
    lift_at_k = float(precision_at_k / prevalence) if prevalence > 0 else np.nan

    return {"split": split_name, "data_split": split_name, "model": model_name,
            "cutoff_label": cutoff_label, "cutoff_type": cutoff_type, "cutoff_value": cutoff_value,
            "n_obs": int(n_obs), "n_positive": int(n_positive), "prevalence": prevalence,
            "k_n": int(k), "positives_captured_n": int(y_top.sum()),
            "precision_at_k": precision_at_k, "recall_at_k": recall_at_k, "lift_at_k": lift_at_k}

#------------------------------------------------------------------------------
# Build ranking metrics across models and cut-offs
#------------------------------------------------------------------------------
def build_ranking_cutoff_table(y_true, prediction_dict, split_name, top_fracs=None, top_ns=None):
    rows = []
    for model_name, y_score in prediction_dict.items():
        for top_frac in top_fracs or []:
            label = f"top_{int(top_frac * 100)}pct"
            rows.append(calc_rank_metrics_at_cutoff(y_true, y_score, split_name, model_name, label, top_frac=top_frac))
        for top_n in top_ns or []:
            rows.append(calc_rank_metrics_at_cutoff(y_true, y_score, split_name, model_name, f"top_{top_n}", top_n=top_n))
    return pd.DataFrame(rows)

#------------------------------------------------------------------------------
# Build the standard ranking table used in this project
#------------------------------------------------------------------------------
def build_standard_ranking_cutoff_table(y_true, prediction_dict, split_name):
    return build_ranking_cutoff_table(y_true, prediction_dict, split_name, RANKING_TOP_FRACS, RANKING_TOP_NS)

#------------------------------------------------------------------------------
# Create a precision-recall curve dataframe
#------------------------------------------------------------------------------
def make_pr_curve_df(y_true, y_prob, model_name, split_name):
    precision, recall, thresholds = precision_recall_curve(y_true, y_prob)
    threshold_values = list(thresholds) + [np.nan]
    return pd.DataFrame({"model": model_name, "data_split": split_name,
                         "precision": precision, "recall": recall,
                         "threshold": threshold_values})

#------------------------------------------------------------------------------
# Create a compact model comparison table
#------------------------------------------------------------------------------
def make_model_comparison_table(rows):
    df = pd.DataFrame(rows)
    preferred_cols = ["data_split","model","n_obs","n_positive","prevalence","pr_auc",
                      "roc_auc","brier_score","precision_at_k","recall_at_k","lift_at_k"]
    cols = [col for col in preferred_cols if col in df.columns] + [col for col in df.columns if col not in preferred_cols]
    return df[cols]

#------------------------------------------------------------------------------
# Add readable percent columns for reports
#------------------------------------------------------------------------------
def add_metric_display_cols(df):
    df = df.copy()
    for col in ["prevalence","pr_auc","roc_auc","brier_score","precision_at_k","recall_at_k"]:
        if col in df.columns:
            df[f"{col}_display"] = df[col].map(lambda x: "n/a" if pd.isna(x) else f"{x:.4f}")
    if "lift_at_k" in df.columns:
        df["lift_at_k_display"] = df["lift_at_k"].map(lambda x: "n/a" if pd.isna(x) else f"{x:.2f}")
    return df
