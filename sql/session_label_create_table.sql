
CREATE OR REPLACE TABLE `ga4-project-490603.ga4_capstone.session_label` AS
SELECT
  s.user_pseudo_id,
  s.ga_session_id,
  IF(COUNTIF(f.funnel_step = 'purchase') > 0, 1, 0) AS y_purchase
FROM `ga4-project-490603.ga4_capstone.sessions` s
LEFT JOIN `ga4-project-490603.ga4_capstone.funnel_steps` f
  ON s.user_pseudo_id = f.user_pseudo_id AND s.ga_session_id = f.ga_session_id
GROUP BY s.user_pseudo_id, s.ga_session_id;
