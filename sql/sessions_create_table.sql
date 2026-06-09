
CREATE OR REPLACE TABLE `ga4-project-490603.ga4_capstone.sessions` AS
WITH base AS (
  SELECT
    user_pseudo_id, ga_session_id, ga_session_number, event_timestamp, event_name,
    engagement_time_msec, session_engaged_flag,
    device_category, device_os, device_browser, geo_country, geo_region, geo_city,
    ep_source, ep_medium, ep_campaign, ep_term,
    traffic_source_source, traffic_source_medium, traffic_source_name,
    CONCAT(user_pseudo_id, '-', CAST(ga_session_id AS STRING)) AS user_session_key
  FROM `ga4-project-490603.ga4_capstone.events_base`
  WHERE ga_session_id IS NOT NULL
),
first_purchase AS (
  SELECT user_session_key, MIN(event_timestamp) AS first_purchase_ts
  FROM base
  WHERE event_name = 'purchase'
  GROUP BY user_session_key
),
labelled AS (
  SELECT
    b.*,
    p.first_purchase_ts,
    p.first_purchase_ts IS NULL OR b.event_timestamp < p.first_purchase_ts AS is_model_event
  FROM base b
  LEFT JOIN first_purchase p
    ON b.user_session_key = p.user_session_key
),
session_rollup AS (
  SELECT
    user_pseudo_id,
    ga_session_id,
    user_session_key,
    ARRAY_AGG(ga_session_number IGNORE NULLS ORDER BY event_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)] AS ga_session_number,

    MIN(event_timestamp) AS full_session_start_ts,
    MIN(IF(is_model_event, event_timestamp, NULL)) AS feature_start_ts,
    MAX(IF(is_model_event, event_timestamp, NULL)) AS feature_end_ts,

    COUNTIF(is_model_event) AS n_events,
    COUNT(DISTINCT IF(is_model_event, event_name, NULL)) AS n_distinct_event_names,
    SUM(IF(is_model_event, COALESCE(engagement_time_msec, 0), 0)) AS engagement_time_msec_sum,
    MAX(IF(is_model_event, COALESCE(session_engaged_flag, 0), 0)) AS session_engaged_flag_max,

    ARRAY_AGG(device_category IGNORE NULLS ORDER BY event_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)] AS device_category,
    ARRAY_AGG(device_os IGNORE NULLS ORDER BY event_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)] AS device_os,
    ARRAY_AGG(device_browser IGNORE NULLS ORDER BY event_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)] AS device_browser,
    ARRAY_AGG(geo_country IGNORE NULLS ORDER BY event_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)] AS geo_country,
    ARRAY_AGG(geo_region IGNORE NULLS ORDER BY event_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)] AS geo_region,
    ARRAY_AGG(geo_city IGNORE NULLS ORDER BY event_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)] AS geo_city,

    COALESCE(
      ARRAY_AGG(NULLIF(TRIM(ep_source), '') IGNORE NULLS ORDER BY event_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)],
      ARRAY_AGG(NULLIF(TRIM(traffic_source_source), '') IGNORE NULLS ORDER BY event_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)]
    ) AS channel_source_raw,

    COALESCE(
      ARRAY_AGG(NULLIF(TRIM(ep_medium), '') IGNORE NULLS ORDER BY event_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)],
      ARRAY_AGG(NULLIF(TRIM(traffic_source_medium), '') IGNORE NULLS ORDER BY event_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)]
    ) AS channel_medium_raw,

    COALESCE(
      ARRAY_AGG(NULLIF(TRIM(ep_campaign), '') IGNORE NULLS ORDER BY event_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)],
      ARRAY_AGG(NULLIF(TRIM(traffic_source_name), '') IGNORE NULLS ORDER BY event_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)]
    ) AS channel_campaign_raw,

    ARRAY_AGG(NULLIF(TRIM(ep_term), '') IGNORE NULLS ORDER BY event_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)] AS channel_term
  FROM labelled
  GROUP BY user_pseudo_id, ga_session_id, user_session_key
)
SELECT
  user_pseudo_id,
  ga_session_id,
  user_session_key,
  ga_session_number,
  COALESCE(feature_start_ts, full_session_start_ts) AS session_start_ts,
  COALESCE(feature_end_ts, feature_start_ts, full_session_start_ts) AS session_end_ts,
  TIMESTAMP_MICROS(COALESCE(feature_start_ts, full_session_start_ts)) AS session_start_time,
  TIMESTAMP_MICROS(COALESCE(feature_end_ts, feature_start_ts, full_session_start_ts)) AS session_end_time,
  DATE(TIMESTAMP_MICROS(full_session_start_ts)) AS session_date,
  DATE_TRUNC(DATE(TIMESTAMP_MICROS(full_session_start_ts)), WEEK(MONDAY)) AS week_start_date,
  CASE
    WHEN feature_start_ts IS NULL OR feature_end_ts IS NULL THEN 0
    ELSE SAFE_DIVIDE(feature_end_ts - feature_start_ts, 1000000.0)
  END AS session_duration_seconds,
  n_events,
  n_distinct_event_names,
  engagement_time_msec_sum,
  session_engaged_flag_max,
  COALESCE(device_category, '(not set)') AS device_category,
  device_os,
  device_browser,
  COALESCE(geo_country, '(not set)') AS geo_country,
  geo_region,
  geo_city,
  COALESCE(channel_source_raw, '(not set)') AS channel_source,
  COALESCE(channel_medium_raw, '(not set)') AS channel_medium,
  COALESCE(channel_campaign_raw, '(not set)') AS channel_campaign,
  CONCAT(COALESCE(channel_source_raw, '(not set)'), ' / ', COALESCE(channel_medium_raw, '(not set)')) AS channel_segment,
  channel_term
FROM session_rollup;
