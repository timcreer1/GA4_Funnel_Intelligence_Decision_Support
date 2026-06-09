
CREATE OR REPLACE TABLE `ga4-project-490603.ga4_capstone.fact_funnel_weekly` AS
SELECT
  s.week_start_date,
  s.device_category,
  s.geo_country,
  s.channel_source,
  s.channel_medium,
  s.channel_segment,
  f.funnel_step,
  COUNT(*) AS n_sessions_reaching_step
FROM `ga4-project-490603.ga4_capstone.sessions` s
JOIN `ga4-project-490603.ga4_capstone.funnel_steps` f
  ON s.user_pseudo_id = f.user_pseudo_id AND s.ga_session_id = f.ga_session_id
GROUP BY s.week_start_date, s.device_category, s.geo_country, s.channel_source, s.channel_medium, s.channel_segment, f.funnel_step;
