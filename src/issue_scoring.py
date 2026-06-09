#------------------------------------------------------------------------------
# Funnel and segment issue scoring helpers
#------------------------------------------------------------------------------
import re

import numpy as np
import pandas as pd

from .config import FUNNEL_STEPS, FUNNEL_PAIRS, STEP_LABELS, MIN_EARLIER_STEP_SESSIONS
from .config import TOP_ISSUES_PER_WEEK, ISSUE_IMPACT_WEIGHT, ISSUE_SEVERITY_WEIGHT
from .io_utils import safe_divide, weighted_mean, require_cols

#------------------------------------------------------------------------------
# Percentile-style rank used in issue scoring
#------------------------------------------------------------------------------
def pct_rank(series):
    if len(series) == 0:
        return series
    if series.nunique(dropna=False) <= 1:
        return pd.Series(np.ones(len(series)), index=series.index)
    return series.rank(pct=True, method="average")

#------------------------------------------------------------------------------
# Clean raw and previously formatted channel labels for dashboard tables
#------------------------------------------------------------------------------
def clean_channel_segment(value):
    raw_value = "(not set) / (not set)" if pd.isna(value) else str(value).strip()
    value_lower = raw_value.lower().strip()

    label_map = {"(direct) / (none)": "Direct traffic",
                 "(direct) / organic": "Direct organic traffic",
                 "(direct) / referral": "Direct referral traffic",
                 "(not set) / (not set)": "Unknown traffic",
                 "(data deleted) / (data deleted)": "Unknown traffic",
                 "(data deleted) / organic": "Unknown organic traffic",
                 "(data deleted) / referral": "Unknown referral traffic",
                 "<other> / <other>": "Other channels",
                 "<other> / organic": "Other organic traffic",
                 "<other> / referral": "Other referral traffic",
                 "google / organic": "Google organic traffic",
                 "google / cpc": "Google paid search traffic",
                 "google / referral": "Google referral traffic",
                 "google / email": "Google email traffic",
                 "shop.googlemerchandisestore.com / referral": "Google Merch Store referral traffic",
                 "googlemerchandisestore.com / referral": "Google Merch Store referral traffic",
                 "your.googlemerchandisestore.com / referral": "Google Merch Store referral traffic",
                 "analytics.google.com / referral": "Google Analytics referral traffic",
                 "support.google.com / referral": "Google support referral traffic",
                 "sites.google.com / referral": "Google sites referral traffic",
                 "mail.google.com / referral": "Google Mail referral traffic",
                 "docs.google.com / referral": "Google Docs referral traffic",
                 "creatoracademy.youtube.com / referral": "YouTube Creator Academy referral traffic",
                 "youtube.com / referral": "YouTube referral traffic",
                 "m.youtube.com / referral": "YouTube referral traffic",
                 "reddit.com / referral": "Reddit referral traffic",
                 "amp.reddit.com / referral": "Reddit referral traffic",
                 "quora.com / referral": "Quora referral traffic",
                 "pinterest.com / referral": "Pinterest referral traffic",
                 "theverge.com / referral": "The Verge referral traffic",
                 "qiita.com / referral": "Qiita referral traffic",
                 "udemy.com / referral": "Udemy referral traffic",
                 "qwiklabs.com / referral": "Qwiklabs referral traffic",
                 "run.qwiklabs.com / referral": "Qwiklabs referral traffic",
                 "perksatwork.com / referral": "Perks at Work referral traffic",
                 "yandex.ru / referral": "Yandex referral traffic",
                 "yandex.kz / referral": "Yandex referral traffic",
                 "yahoo / organic": "Yahoo organic traffic",
                 "baidu / organic": "Baidu organic traffic",
                 "bing / organic": "Bing organic traffic",
                 "t.co / referral": "Twitter/X referral traffic",
                 "web.skype.com / referral": "Skype referral traffic",
                 "coursera.org / referral": "Coursera referral traffic",
                 "facebook.com / referral": "Facebook referral traffic",
                 "m.facebook.com / referral": "Facebook referral traffic",
                 "l.facebook.com / referral": "Facebook referral traffic"}

    if value_lower in label_map:
        return label_map[value_lower]

    # Catch noisy technical labels before title casing
    if "safeframe" in value_lower or "googlesyndication" in value_lower:
        return "Google ad frame referral traffic"
    if "doubleclick" in value_lower or "2mdn.net" in value_lower:
        return "Google ad network referral traffic"
    if "googleusercontent" in value_lower:
        return "Google hosted referral traffic"
    if "appspot.com" in value_lower:
        return "Google hosted app referral traffic"

    if "search.yahoo.com" in value_lower:
        return "Yahoo search traffic"
    if "search.aol.com" in value_lower:
        return "AOL search referral traffic"
    if "ask.com" in value_lower:
        return "Ask search referral traffic"
    if "startpage.com" in value_lower:
        return "Startpage search referral traffic"

    has_long_hash = re.search(r"[a-f0-9]{24,}", value_lower) is not None
    is_long_technical = len(value_lower) > 55 or value_lower.count(".") >= 3
    if has_long_hash or is_long_technical:
        if "referral" in value_lower:
            return "Other technical referral traffic"
        if "organic" in value_lower:
            return "Other technical organic traffic"
        return "Other technical traffic"

    # Clean regular source / medium values
    if " / " in raw_value:
        source, medium = raw_value.split(" / ", 1)
        source_clean = source.strip().lower()
        medium_clean = medium.strip().lower()

        if source_clean in ["<other>", "other"]:
            return "Other channels" if medium_clean in ["<other>", "other", "(data deleted)"] else f"Other {medium_clean} traffic"
        if source_clean in ["(not set)", "(data deleted)", "data deleted"]:
            return "Unknown traffic" if medium_clean in ["(not set)", "(none)", "(data deleted)"] else f"Unknown {medium_clean} traffic"
        if medium_clean in ["(not set)", "(none)", "(data deleted)", "<other>"]:
            return f"{source_clean.replace('_', ' ').replace('-', ' ').title()} traffic"

        source_display = source_clean.replace("www.", "").replace("_", " ").replace("-", " ")
        source_display = source_display.replace(".com", "").replace(".org", "").replace(".net", "").replace(".ru", "")
        source_display = source_display.title().replace("Youtube", "YouTube").replace("T.Co", "Twitter/X")
        return f"{source_display} {medium_clean} traffic"

    return raw_value.replace("_", " ").replace("-", " ").title()

#------------------------------------------------------------------------------
# Convert segment values into short display labels
#------------------------------------------------------------------------------
def format_segment_label(segment_type, segment_value):
    value = str(segment_value).strip()
    if segment_type == "device_category":
        return f"{value.title()} users"
    if segment_type == "geo_country":
        return "Unknown country users" if value in ["(not set)", "not set", "nan", "None"] else f"{value} users"
    if segment_type == "channel_segment":
        return clean_channel_segment(value)
    return value

#------------------------------------------------------------------------------
# Build readable issue labels
#------------------------------------------------------------------------------
def format_issue_label(row):
    segment_label = row.get("segment_value_clean", row.get("segment_value_display", row.get("segment_value", "")))
    step_from = STEP_LABELS.get(row["step_from"], row["step_from"])
    step_to = STEP_LABELS.get(row["step_to"], row["step_to"])
    return f"{segment_label}: {step_from} to {step_to} drop-off"

#------------------------------------------------------------------------------
# Aggregate weekly sessions to a selected grouping level
#------------------------------------------------------------------------------
def aggregate_sessions_weekly(df, group_cols):
    require_cols(df, group_cols + ["n_sessions","n_purchases"], "fact_sessions_weekly")
    rows = []
    for keys, group in df.groupby(group_cols, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        n_sessions = int(group["n_sessions"].sum())
        n_purchases = int(group["n_purchases"].sum())
        row = dict(zip(group_cols, keys))
        row.update({"n_sessions": n_sessions, "n_purchases": n_purchases,
                    "purchase_rate": n_purchases / n_sessions if n_sessions > 0 else np.nan})
        if "avg_session_duration_sec" in group.columns:
            row["avg_session_duration_sec"] = weighted_mean(group["avg_session_duration_sec"], group["n_sessions"])
        if "avg_engagement_time_msec" in group.columns:
            row["avg_engagement_time_msec"] = weighted_mean(group["avg_engagement_time_msec"], group["n_sessions"])
        rows.append(row)
    return pd.DataFrame(rows)

#------------------------------------------------------------------------------
# Aggregate weekly funnel rows to a selected grouping level
#------------------------------------------------------------------------------
def aggregate_funnel_weekly(df, group_cols):
    require_cols(df, group_cols + ["funnel_step","n_sessions_reaching_step"], "fact_funnel_weekly")
    return df.groupby(group_cols + ["funnel_step"], dropna=False, as_index=False)["n_sessions_reaching_step"].sum()

#------------------------------------------------------------------------------
# Convert long funnel rows into wide weekly rows
#------------------------------------------------------------------------------
def pivot_funnel_steps(funnel_df, index_cols, value_col="n_sessions_reaching_step"):
    require_cols(funnel_df, index_cols + ["funnel_step", value_col], "funnel_df")
    wide_df = funnel_df.pivot_table(index=index_cols, columns="funnel_step", values=value_col,
                                    aggfunc="sum", fill_value=0).reset_index()
    wide_df.columns.name = None
    for step in FUNNEL_STEPS:
        if step not in wide_df.columns:
            wide_df[step] = 0
    return wide_df

#------------------------------------------------------------------------------
# Build segment-step metrics from wide segment and baseline tables
#------------------------------------------------------------------------------
def build_segment_step_metrics(segment_base_weekly, baseline_weekly, segment_cols=None,
                               funnel_pairs=None, min_sessions=MIN_EARLIER_STEP_SESSIONS):
    segment_cols = segment_cols or ["week_start_date","segment_type","segment_value"]
    funnel_pairs = funnel_pairs or FUNNEL_PAIRS
    require_cols(segment_base_weekly, segment_cols + FUNNEL_STEPS, "segment_base_weekly")
    require_cols(baseline_weekly, ["week_start_date"] + FUNNEL_STEPS, "baseline_weekly")

    base_lookup = baseline_weekly.set_index("week_start_date")
    rows = []

    # Calculate one row per segment-week-transition
    for _, row in segment_base_weekly.iterrows():
        week = row["week_start_date"]
        if week not in base_lookup.index:
            continue
        baseline = base_lookup.loc[week]
        if isinstance(baseline, pd.DataFrame):
            baseline = baseline.iloc[0]

        for step_from, step_to in funnel_pairs:
            earlier_count = float(row.get(step_from, 0))
            later_count = float(row.get(step_to, 0))
            baseline_earlier = float(baseline.get(step_from, 0))
            baseline_later = float(baseline.get(step_to, 0))

            current_conv = later_count / earlier_count if earlier_count > 0 else np.nan
            baseline_conv = baseline_later / baseline_earlier if baseline_earlier > 0 else np.nan
            conversion_gap = baseline_conv - current_conv if pd.notna(current_conv) and pd.notna(baseline_conv) else np.nan

            downstream_rate = float(baseline.get("purchase", 0)) / baseline_later if baseline_later > 0 else np.nan
            lost_next_step_sessions = max(conversion_gap * earlier_count, 0) if pd.notna(conversion_gap) else np.nan
            estimated_lost_purchases = lost_next_step_sessions * downstream_rate if pd.notna(downstream_rate) else np.nan

            out = {col: row[col] for col in segment_cols}
            out.update({"step_from": step_from, "step_to": step_to, "earlier_step_sessions": int(earlier_count),
                        "later_step_sessions": int(later_count), "baseline_earlier_step_sessions": int(baseline_earlier),
                        "baseline_later_step_sessions": int(baseline_later), "current_step_conversion": current_conv,
                        "baseline_step_conversion": baseline_conv, "conversion_gap": conversion_gap,
                        "downstream_purchase_rate": downstream_rate, "lost_next_step_sessions": lost_next_step_sessions,
                        "estimated_lost_purchases": estimated_lost_purchases,
                        "nonstandard_path_flag": bool(later_count > earlier_count)})
            rows.append(out)

    metrics_df = pd.DataFrame(rows)
    if len(metrics_df) == 0:
        return metrics_df

    metrics_df["qualifies_min_volume_flag"] = metrics_df["earlier_step_sessions"] >= int(min_sessions)
    metrics_df["under_baseline_flag"] = metrics_df["conversion_gap"] > 0
    metrics_df["issue_candidate_flag"] = (metrics_df["qualifies_min_volume_flag"] &
                                          metrics_df["under_baseline_flag"] &
                                          (~metrics_df["nonstandard_path_flag"]))

    metrics_df["segment_value_raw"] = metrics_df["segment_value"]
    metrics_df["segment_value_display"] = metrics_df.apply(
        lambda r: clean_channel_segment(r["segment_value"]) if r["segment_type"] == "channel_segment" else str(r["segment_value"]), axis=1)
    metrics_df["segment_value_clean"] = metrics_df["segment_value_display"]
    return metrics_df.sort_values(["week_start_date","segment_type","segment_value","step_from"]).reset_index(drop=True)

#------------------------------------------------------------------------------
# Rank weekly top issues from segment-step metrics
#------------------------------------------------------------------------------
def rank_top_issues(segment_step_metrics_weekly, top_n=TOP_ISSUES_PER_WEEK):
    df = segment_step_metrics_weekly[segment_step_metrics_weekly["issue_candidate_flag"]].copy()
    if len(df) == 0:
        return df

    df["impact_rank"] = df.groupby("week_start_date")["estimated_lost_purchases"].transform(lambda s: pct_rank(s.fillna(0)))
    df["severity_rank"] = df.groupby("week_start_date")["conversion_gap"].transform(lambda s: pct_rank(s.fillna(0)))
    df["issue_score"] = ISSUE_IMPACT_WEIGHT * df["impact_rank"] + ISSUE_SEVERITY_WEIGHT * df["severity_rank"]
    df["issue_label"] = df.apply(format_issue_label, axis=1)

    df = df.sort_values(["week_start_date","issue_score","estimated_lost_purchases"], ascending=[True, False, False]).reset_index(drop=True)
    df["issue_rank_within_week"] = df.groupby("week_start_date").cumcount() + 1
    return df.groupby("week_start_date", group_keys=False).head(int(top_n)).reset_index(drop=True)

#------------------------------------------------------------------------------
# Assign simple priority labels for dashboard actions
#------------------------------------------------------------------------------
def assign_issue_priority(rank):
    if int(rank) == 1:
        return "high"
    if int(rank) == 2:
        return "medium"
    return "review"
