
CREATE OR REPLACE TABLE `ga4-project-490603.ga4_capstone.funnel_steps` AS
WITH base AS (
  SELECT
    user_pseudo_id,
    ga_session_id,
    CONCAT(user_pseudo_id, '-', CAST(ga_session_id AS STRING)) AS user_session_key,
    event_name,
    event_timestamp
  FROM `ga4-project-490603.ga4_capstone.events_base`
  WHERE ga_session_id IS NOT NULL
    AND event_name IN ('view_item','add_to_cart','begin_checkout','add_shipping_info','add_payment_info','purchase')
),
first_purchase AS (
  SELECT user_session_key, MIN(event_timestamp) AS first_purchase_ts
  FROM base
  WHERE event_name = 'purchase'
  GROUP BY user_session_key
),
safe_steps AS (
  SELECT b.*
  FROM base b
  LEFT JOIN first_purchase p
    ON b.user_session_key = p.user_session_key
  WHERE p.first_purchase_ts IS NULL
     OR b.event_timestamp < p.first_purchase_ts
     OR (b.event_name = 'purchase' AND b.event_timestamp = p.first_purchase_ts)
)
SELECT
  user_pseudo_id,
  ga_session_id,
  event_name AS funnel_step,
  MIN(event_timestamp) AS first_step_ts,
  TIMESTAMP_MICROS(MIN(event_timestamp)) AS first_step_time,
  DATE(TIMESTAMP_MICROS(MIN(event_timestamp))) AS first_step_date
FROM safe_steps
GROUP BY user_pseudo_id, ga_session_id, funnel_step;
