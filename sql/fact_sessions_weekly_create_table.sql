
CREATE OR REPLACE TABLE `ga4-project-490603.ga4_capstone.fact_sessions_weekly` AS
SELECT
  s.week_start_date,
  s.device_category,
  s.geo_country,
  s.channel_source,
  s.channel_medium,
  s.channel_segment,
  COUNT(*) AS n_sessions,
  SUM(COALESCE(l.y_purchase, 0)) AS n_purchases,
  SAFE_DIVIDE(SUM(COALESCE(l.y_purchase, 0)), COUNT(*)) AS purchase_rate,
  AVG(s.session_duration_seconds) AS avg_session_duration_sec,
  AVG(s.engagement_time_msec_sum) AS avg_engagement_time_msec
FROM `ga4-project-490603.ga4_capstone.sessions` s
LEFT JOIN `ga4-project-490603.ga4_capstone.session_label` l
  ON s.user_pseudo_id = l.user_pseudo_id AND s.ga_session_id = l.ga_session_id
GROUP BY s.week_start_date, s.device_category, s.geo_country, s.channel_source, s.channel_medium, s.channel_segment;
