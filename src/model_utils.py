#------------------------------------------------------------------------------
# Model helper functions
#------------------------------------------------------------------------------
import warnings

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV

try:
    from sklearn.frozen import FrozenEstimator
except Exception:
    FrozenEstimator = None

from .config import RANDOM_STATE, MODEL_LABEL_MAP, BAND_LABEL_MAP

#------------------------------------------------------------------------------
# Clean model labels for tables and charts
#------------------------------------------------------------------------------
def clean_model_label(model_name):
    return MODEL_LABEL_MAP.get(str(model_name), str(model_name).replace("_", " ").title())

#------------------------------------------------------------------------------
# Build preprocessing for numeric and categorical fields
#------------------------------------------------------------------------------
def make_preprocessor(num_cols, cat_cols, scale_numeric=False):
    num_steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        num_steps.append(("scaler", StandardScaler(with_mean=False)))

    return ColumnTransformer([
        ("num", Pipeline(num_steps), list(num_cols)),
        ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                          ("onehot", OneHotEncoder(handle_unknown="ignore"))]), list(cat_cols))])

#------------------------------------------------------------------------------
# Build the Logistic Regression baseline
#------------------------------------------------------------------------------
def make_logistic_model():
    return LogisticRegression(class_weight="balanced", max_iter=2000, solver="liblinear", random_state=RANDOM_STATE)

#------------------------------------------------------------------------------
# Build the LightGBM model setup
#------------------------------------------------------------------------------
def make_lgbm_model(n_estimators=2000):
    try:
        from lightgbm import LGBMClassifier
    except Exception as exc:
        raise ImportError("lightgbm is required for make_lgbm_model(). Install it with pip install lightgbm.") from exc

    return LGBMClassifier(objective="binary", n_estimators=int(n_estimators), learning_rate=0.03, num_leaves=31,
                          min_child_samples=50, subsample=0.8, colsample_bytree=0.8, class_weight="balanced",
                          random_state=RANDOM_STATE, force_col_wise=True, verbosity=-1)

#------------------------------------------------------------------------------
# Calibrate a fitted model with sigmoid calibration
#------------------------------------------------------------------------------
def calibrate_prefit_model(model, X_val, y_val):
    if FrozenEstimator is not None:
        calibrator = CalibratedClassifierCV(estimator=FrozenEstimator(model), method="sigmoid")
    else:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="The `cv='prefit' option is deprecated.*")
            calibrator = CalibratedClassifierCV(estimator=model, method="sigmoid", cv="prefit")
    calibrator.fit(X_val, y_val)
    return calibrator

#------------------------------------------------------------------------------
# Clean encoded feature names from a fitted preprocessor
#------------------------------------------------------------------------------
def get_clean_feature_names(preprocessor):
    names = preprocessor.get_feature_names_out()
    return [n.replace("num__", "").replace("cat__", "") for n in names]

#------------------------------------------------------------------------------
# Match encoded names back to original fields
#------------------------------------------------------------------------------
def get_original_feature_from_encoded(encoded_feature_name, numeric_cols, categorical_cols):
    if encoded_feature_name in numeric_cols:
        return encoded_feature_name
    for col_name in sorted(categorical_cols, key=len, reverse=True):
        if encoded_feature_name.startswith(f"{col_name}_"):
            return col_name
    return encoded_feature_name

#------------------------------------------------------------------------------
# Define feature groups used for checks
#------------------------------------------------------------------------------
ENGAGEMENT_FEATURES = {"n_events", "n_distinct_event_names", "session_duration_seconds", "engagement_time_msec_sum",
                       "events_per_event_type", "engagement_time_per_event"}
FUNNEL_PREFIXES = ("reached_", "t_view_", "t_cart_", "t_checkout_", "t_shipping_", "t_payment_")
ITEM_KEYWORDS = ("item", "price", "qty", "basket")

#------------------------------------------------------------------------------
# Map features into simple modelling groups
#------------------------------------------------------------------------------
def get_ablation_block(feature_name):
    if feature_name.startswith("channel_") or feature_name.startswith("geo_") or feature_name.startswith("device_"):
        return "contextual"
    if feature_name in ENGAGEMENT_FEATURES:
        return "engagement"
    if feature_name.startswith(FUNNEL_PREFIXES):
        return "funnel"
    if feature_name == "has_item_activity" or any(k in feature_name for k in ITEM_KEYWORDS):
        return "item"
    return "basic_session"

#------------------------------------------------------------------------------
# Map features into report-friendly groups
#------------------------------------------------------------------------------
def get_interpretability_group(feature_name):
    if feature_name.startswith("channel_"):
        return "traffic source / medium"
    if feature_name.startswith("geo_"):
        return "geography"
    if feature_name.startswith("device_"):
        return "device"
    if get_ablation_block(feature_name) == "funnel":
        return "funnel progression"
    if get_ablation_block(feature_name) == "item":
        return "item intensity"
    return "session behaviour"

#------------------------------------------------------------------------------
# Summarise feature groups from model importances
#------------------------------------------------------------------------------
def build_grouped_importance(feature_names, importances, numeric_cols, categorical_cols):
    rows = []
    for feature_name, importance in zip(feature_names, importances):
        original_feature = get_original_feature_from_encoded(feature_name, numeric_cols, categorical_cols)
        group = get_interpretability_group(original_feature)
        rows.append({"encoded_feature": feature_name, "original_feature": original_feature,
                     "feature_group": group, "importance": float(importance)})

    df = pd.DataFrame(rows)
    if len(df) == 0:
        return df

    grouped = df.groupby("feature_group", as_index=False)["importance"].sum()
    total_importance = grouped["importance"].sum()
    grouped["relative_importance"] = grouped["importance"] / total_importance if total_importance > 0 else np.nan
    return grouped.sort_values("relative_importance", ascending=False).reset_index(drop=True)

#------------------------------------------------------------------------------
# Add funnel labels to scored sessions
#------------------------------------------------------------------------------
def add_funnel_path_labels(df):
    df = df.copy()
    stage_scan = [("reached_add_payment_info", "add_payment_info", "after_add_payment_info"),
                  ("reached_add_shipping_info", "add_shipping_info", "after_add_shipping_info"),
                  ("reached_begin_checkout", "begin_checkout", "after_begin_checkout"),
                  ("reached_add_to_cart", "add_to_cart", "after_add_to_cart"),
                  ("reached_view_item", "view_item", "after_view_item")]

    df["last_funnel_stage"] = "none"
    df["dropped_after"] = "none"

    # Scan from latest to earliest funnel stage
    for col, stage, dropped_after in stage_scan:
        if col in df.columns:
            mask = df["last_funnel_stage"].eq("none") & df[col].fillna(0).eq(1)
            df.loc[mask, "last_funnel_stage"] = stage
            df.loc[mask, "dropped_after"] = dropped_after

    return df

#------------------------------------------------------------------------------
# Flag sessions with non-monotonic funnel paths
#------------------------------------------------------------------------------
def get_non_monotonic_funnel_mask(df):
    needed = ["reached_view_item","reached_add_to_cart","reached_begin_checkout",
              "reached_add_shipping_info","reached_add_payment_info"]
    available = [col for col in needed if col in df.columns]
    if len(available) < 2:
        return pd.Series(False, index=df.index)

    mask = pd.Series(False, index=df.index)
    for earlier, later in zip(available[:-1], available[1:]):
        mask = mask | (df[later].fillna(0).astype(int) > df[earlier].fillna(0).astype(int))
    return mask

#------------------------------------------------------------------------------
# Select top candidates within a group
#------------------------------------------------------------------------------
def select_candidates(df, score_col, top_n):
    if len(df) == 0:
        return df.copy()
    out = df.sort_values(score_col, ascending=False).head(int(top_n)).copy()
    out["candidate_rank"] = np.arange(1, len(out) + 1)
    out["priority_score"] = np.linspace(1, 0, len(out)) if len(out) > 1 else 1.0
    return out

#------------------------------------------------------------------------------
# Assign priority bands inside candidate groups
#------------------------------------------------------------------------------
def assign_priority_band(priority_score):
    if priority_score >= 0.80:
        return BAND_LABEL_MAP["very_high"]
    if priority_score >= 0.60:
        return BAND_LABEL_MAP["high"]
    if priority_score >= 0.40:
        return BAND_LABEL_MAP["medium"]
    return BAND_LABEL_MAP["review"]
