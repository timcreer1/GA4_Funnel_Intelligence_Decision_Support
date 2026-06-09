#------------------------------------------------------------------------------
# Core project config
#------------------------------------------------------------------------------
from pathlib import Path
import os

#------------------------------------------------------------------------------
# BigQuery settings
#------------------------------------------------------------------------------
BQ_PROJECT_ID = os.getenv("BQ_PROJECT_ID", "ga4-project-490603")
BQ_DATASET_ID = os.getenv("BQ_DATASET_ID", "ga4_capstone")
GA4_PUBLIC_DATASET_TABLE = "bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*"
BQ_LOCATION = "US"

#------------------------------------------------------------------------------
# Drive and project paths
#------------------------------------------------------------------------------
CAPSTONE_DIR = Path(os.getenv("CAPSTONE_DIR", "/content/drive/MyDrive/Capstone_Project"))
DATA_DIR = CAPSTONE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = CAPSTONE_DIR / "outputs"
SQL_DIR = OUTPUT_DIR / "sql"
DQ_DIR = OUTPUT_DIR / "data_quality"
REPORTS_DIR = CAPSTONE_DIR / "reports"
PBI_LATEST_DIR = CAPSTONE_DIR / "powerbi_extracts" / "latest"
SCORING_DIR = OUTPUT_DIR / "scoring"

#------------------------------------------------------------------------------
# Date window
#------------------------------------------------------------------------------
START_DATE = "20201101"
END_DATE = "20210228"

#------------------------------------------------------------------------------
# BigQuery table names
#------------------------------------------------------------------------------
EVENTS_BASE_TABLE = f"{BQ_PROJECT_ID}.{BQ_DATASET_ID}.events_base"
SESSIONS_TABLE = f"{BQ_PROJECT_ID}.{BQ_DATASET_ID}.sessions"
FUNNEL_STEPS_TABLE = f"{BQ_PROJECT_ID}.{BQ_DATASET_ID}.funnel_steps"
SESSION_LABEL_TABLE = f"{BQ_PROJECT_ID}.{BQ_DATASET_ID}.session_label"
FUNNEL_FEATURES_TABLE = f"{BQ_PROJECT_ID}.{BQ_DATASET_ID}.funnel_features"
ITEMS_SESSION_TABLE = f"{BQ_PROJECT_ID}.{BQ_DATASET_ID}.items_session"
ORDERS_TABLE = f"{BQ_PROJECT_ID}.{BQ_DATASET_ID}.orders"
FACT_SESSIONS_WEEKLY_TABLE = f"{BQ_PROJECT_ID}.{BQ_DATASET_ID}.fact_sessions_weekly"
FACT_FUNNEL_WEEKLY_TABLE = f"{BQ_PROJECT_ID}.{BQ_DATASET_ID}.fact_funnel_weekly"

#------------------------------------------------------------------------------
# Saved file paths
#------------------------------------------------------------------------------
RUN_METADATA_PATH = OUTPUT_DIR / "run_metadata.json"
EVENTS_QUALITY_PATH = DQ_DIR / "events_base_quality.json"
GOLD_SANITY_PATH = DQ_DIR / "gold_tables_sanity.json"
PRE_PURCHASE_VALIDATION_PATH = DQ_DIR / "pre_purchase_feature_validation.json"
TABLE_DICTIONARY_PATH = DQ_DIR / "table_dictionary.csv"

FACT_SESSIONS_PATH = PBI_LATEST_DIR / "fact_sessions_weekly.csv"
FACT_FUNNEL_PATH = PBI_LATEST_DIR / "fact_funnel_weekly.csv"
FUNNEL_WEEKLY_PATH = PBI_LATEST_DIR / "funnel_weekly_rates.csv"
SEGMENT_STEP_PATH = PBI_LATEST_DIR / "segment_step_metrics_weekly.csv"
TOP_ISSUES_PATH = PBI_LATEST_DIR / "top_issues_weekly.csv"
MODEL_COMPARISON_PATH = PBI_LATEST_DIR / "model_comparison_metrics.csv"
RANKING_CUTOFF_PATH = PBI_LATEST_DIR / "ranking_cutoff_metrics.csv"
GROUPED_IMPORTANCE_PATH = PBI_LATEST_DIR / "grouped_model_importance.csv"
COMBINED_CANDIDATES_PATH = PBI_LATEST_DIR / "combined_priority_candidates.csv"
WEEKLY_DECISION_SUMMARY_PATH = PBI_LATEST_DIR / "weekly_decision_summary.csv"

SESSIONS_PATH = PROCESSED_DIR / "sessions.parquet"
FUNNEL_FEATURES_PATH = PROCESSED_DIR / "funnel_features.parquet"
ITEMS_SESSION_PATH = PROCESSED_DIR / "items_session.parquet"
SESSION_LABEL_PATH = PROCESSED_DIR / "session_label.parquet"

#------------------------------------------------------------------------------
# Funnel settings
#------------------------------------------------------------------------------
FUNNEL_STEPS = ["view_item","add_to_cart","begin_checkout","add_shipping_info","add_payment_info","purchase"]
DASHBOARD_FUNNEL_STEPS = ["view_item","add_to_cart","begin_checkout","add_payment_info","purchase"]
FUNNEL_PAIRS = list(zip(FUNNEL_STEPS[:-1], FUNNEL_STEPS[1:]))

STEP_LABELS = {"view_item": "product view", "add_to_cart": "cart", "begin_checkout": "checkout",
               "add_shipping_info": "shipping", "add_payment_info": "payment", "purchase": "purchase"}

STEP_DISPLAY_LABELS = {"view_item": "Product view", "add_to_cart": "Add to cart", "begin_checkout": "Begin checkout",
                       "add_shipping_info": "Add shipping", "add_payment_info": "Add payment", "purchase": "Purchase"}

#------------------------------------------------------------------------------
# Issue ranking settings
#------------------------------------------------------------------------------
MIN_EARLIER_STEP_SESSIONS = 100
TOP_ISSUES_PER_WEEK = 3
ISSUE_IMPACT_WEIGHT = 0.70
ISSUE_SEVERITY_WEIGHT = 0.30

#------------------------------------------------------------------------------
# Model settings
#------------------------------------------------------------------------------
RANDOM_STATE = 42
TARGET_COL = "y_purchase"
TOP_FRAC = 0.05
RANKING_TOP_FRACS = [0.01, 0.02, 0.05]
RANKING_TOP_NS = [100, 250]

BROWSE_INTERVENTION_TOP_N = 50
CART_INTERVENTION_TOP_N = 50
LATE_RECOVERY_TOP_N = 100

NUMERIC_FEATURES = ["ga_session_number","session_duration_seconds","n_events","n_distinct_event_names",
                    "engagement_time_msec_sum","session_engaged_flag_max","events_per_event_type",
                    "engagement_time_per_event","reached_view_item","reached_add_to_cart",
                    "reached_begin_checkout","reached_add_shipping_info","reached_add_payment_info",
                    "t_view_to_cart_sec","t_cart_to_checkout_sec","t_checkout_to_shipping_sec",
                    "t_shipping_to_payment_sec","n_item_rows","n_distinct_item_id",
                    "n_distinct_item_category","avg_item_price","max_item_price","qty_sum",
                    "has_item_activity","item_rows_per_distinct_item"]

CATEGORICAL_FEATURES = ["device_category","device_os","device_browser","geo_country","geo_region",
                        "channel_source","channel_medium","channel_segment"]

FEATURE_GROUPS = {"session behaviour": ["ga_session_number","session_duration_seconds","n_events",
                                        "n_distinct_event_names","engagement_time_msec_sum",
                                        "session_engaged_flag_max","events_per_event_type",
                                        "engagement_time_per_event"],
                  "item intensity": ["n_item_rows","n_distinct_item_id","n_distinct_item_category",
                                     "avg_item_price","max_item_price","qty_sum",
                                     "has_item_activity","item_rows_per_distinct_item"],
                  "funnel progression": ["reached_view_item","reached_add_to_cart","reached_begin_checkout",
                                         "reached_add_shipping_info","reached_add_payment_info",
                                         "t_view_to_cart_sec","t_cart_to_checkout_sec",
                                         "t_checkout_to_shipping_sec","t_shipping_to_payment_sec"],
                  "device": ["device_category","device_os","device_browser"],
                  "geography": ["geo_country","geo_region"],
                  "traffic source / medium": ["channel_source","channel_medium","channel_segment"]}

MODEL_LABEL_MAP = {"logistic_regression": "Logistic regression baseline",
                   "lightgbm_raw": "LightGBM raw score",
                   "lightgbm_calibrated": "LightGBM calibrated likelihood"}

INTERVENTION_LABEL_MAP = {"browse_intervention": "Browse drop-off review",
                          "cart_intervention": "Cart drop-off review",
                          "late_recovery": "Late checkout recovery"}

BAND_LABEL_MAP = {"very_high": "Very high within group", "high": "High within group",
                  "medium": "Medium within group", "review": "Review"}

#------------------------------------------------------------------------------
# Create the standard project folders
#------------------------------------------------------------------------------
def make_project_dirs():
    paths = [CAPSTONE_DIR, DATA_DIR, PROCESSED_DIR, OUTPUT_DIR, SQL_DIR, DQ_DIR,
             REPORTS_DIR, PBI_LATEST_DIR, SCORING_DIR]
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)
    return paths
