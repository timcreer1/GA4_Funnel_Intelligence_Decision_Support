#------------------------------------------------------------------------------
# Data quality and leakage check helpers
#------------------------------------------------------------------------------
import numpy as np
import pandas as pd

from .io_utils import require_cols

#------------------------------------------------------------------------------
# Check duplicate keys at the chosen table grain
#------------------------------------------------------------------------------
def check_duplicate_keys(df, key_cols, df_name="table"):
    require_cols(df, key_cols, df_name)
    dup_df = df.groupby(key_cols, dropna=False).size().reset_index(name="row_count")
    dup_df = dup_df[dup_df["row_count"] > 1].copy()
    return {"table": df_name, "key_cols": key_cols, "duplicate_key_groups": int(len(dup_df)),
            "duplicate_rows": int(dup_df["row_count"].sum()) if len(dup_df) else 0}

#------------------------------------------------------------------------------
# Check two session-grain tables align on the same keys
#------------------------------------------------------------------------------
def check_table_alignment(reference_df, check_df, key_cols, reference_name="reference", check_name="check"):
    require_cols(reference_df, key_cols, reference_name)
    require_cols(check_df, key_cols, check_name)

    ref_keys = reference_df[key_cols].drop_duplicates()
    check_keys = check_df[key_cols].drop_duplicates()
    merged = ref_keys.merge(check_keys, on=key_cols, how="outer", indicator=True)

    missing_from_check = int((merged["_merge"] == "left_only").sum())
    extra_in_check = int((merged["_merge"] == "right_only").sum())

    return {"reference_table": reference_name, "check_table": check_name, "key_cols": key_cols,
            "reference_keys": int(len(ref_keys)), "check_keys": int(len(check_keys)),
            "missing_from_check": missing_from_check, "extra_in_check": extra_in_check,
            "aligned_flag": missing_from_check == 0 and extra_in_check == 0}

#------------------------------------------------------------------------------
# Build a table count summary from loaded dataframes
#------------------------------------------------------------------------------
def summarise_loaded_tables(table_map):
    rows = []
    for table_name, df in table_map.items():
        rows.append({"table_name": table_name, "row_count": int(len(df)), "column_count": int(df.shape[1])})
    return pd.DataFrame(rows).sort_values("table_name").reset_index(drop=True)

#------------------------------------------------------------------------------
# Check funnel reach is monotonic across step columns
#------------------------------------------------------------------------------
def check_funnel_monotonic(df, step_cols, df_name="funnel_table"):
    require_cols(df, step_cols, df_name)
    rows = []
    for earlier, later in zip(step_cols[:-1], step_cols[1:]):
        bad_rows = int((pd.to_numeric(df[later], errors="coerce").fillna(0) >
                        pd.to_numeric(df[earlier], errors="coerce").fillna(0)).sum())
        rows.append({"table": df_name, "earlier_step": earlier, "later_step": later,
                     "non_monotonic_rows": bad_rows, "passed": bad_rows == 0})
    return pd.DataFrame(rows)

#------------------------------------------------------------------------------
# Check validation outputs from Notebook 01
#------------------------------------------------------------------------------
def check_pre_purchase_validation(validation_obj):
    if isinstance(validation_obj, pd.DataFrame):
        row = validation_obj.iloc[0].to_dict() if len(validation_obj) else {}
    else:
        row = dict(validation_obj)

    event_mismatches = int(row.get("n_session_event_count_mismatches", 0))
    item_mismatches = int(row.get("n_item_count_mismatches", 0))
    post_purchase_steps = int(row.get("n_post_purchase_funnel_steps", 0))

    return {"session_event_count_mismatches": event_mismatches,
            "item_count_mismatches": item_mismatches,
            "post_purchase_funnel_steps": post_purchase_steps,
            "pre_purchase_validation_passed": event_mismatches == 0 and item_mismatches == 0 and post_purchase_steps == 0}

#------------------------------------------------------------------------------
# Check that model feature columns do not contain obvious leakage terms
#------------------------------------------------------------------------------
def check_feature_leakage_terms(feature_cols):
    blocked_terms = ["purchase", "transaction", "revenue", "order", "value", "tax", "shipping_amount"]
    rows = []
    for col in feature_cols:
        col_lower = str(col).lower()
        matched = [term for term in blocked_terms if term in col_lower]
        if matched:
            rows.append({"feature": col, "matched_terms": ", ".join(matched)})
    return pd.DataFrame(rows)

#------------------------------------------------------------------------------
# Check model inputs have the expected columns
#------------------------------------------------------------------------------
def check_model_input_columns(df, numeric_cols, categorical_cols, target_col=None):
    required_cols = list(numeric_cols) + list(categorical_cols)
    if target_col is not None:
        required_cols = required_cols + [target_col]
    missing = [col for col in required_cols if col not in df.columns]
    return {"expected_columns": int(len(required_cols)), "missing_columns": missing,
            "passed": len(missing) == 0}

#------------------------------------------------------------------------------
# Combine common quality outputs into one dictionary
#------------------------------------------------------------------------------
def build_quality_audit(sessions_df=None, label_df=None, funnel_features_df=None, items_df=None,
                        orders_df=None, key_cols=None):
    key_cols = key_cols or ["user_pseudo_id", "ga_session_id"]
    audit = {}

    if sessions_df is not None:
        audit["sessions_duplicate_check"] = check_duplicate_keys(sessions_df, key_cols, "sessions")
    if label_df is not None and sessions_df is not None:
        audit["session_label_alignment"] = check_table_alignment(sessions_df, label_df, key_cols, "sessions", "session_label")
    if funnel_features_df is not None and sessions_df is not None:
        audit["funnel_features_alignment"] = check_table_alignment(sessions_df, funnel_features_df, key_cols, "sessions", "funnel_features")
    if items_df is not None and sessions_df is not None:
        audit["items_session_alignment"] = check_table_alignment(sessions_df, items_df, key_cols, "sessions", "items_session")
    if orders_df is not None:
        order_key_cols = [col for col in ["transaction_id", "user_pseudo_id", "ga_session_id"] if col in orders_df.columns]
        if order_key_cols:
            audit["orders_duplicate_check"] = check_duplicate_keys(orders_df, order_key_cols, "orders")

    return audit
