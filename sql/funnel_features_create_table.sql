
CREATE OR REPLACE TABLE `ga4-project-490603.ga4_capstone.funnel_features` AS
WITH first_purchase AS (
  SELECT user_pseudo_id, ga_session_id, MIN(event_timestamp) AS first_purchase_ts
  FROM `ga4-project-490603.ga4_capstone.events_base`
  WHERE ga_session_id IS NOT NULL AND event_name = 'purchase'
  GROUP BY user_pseudo_id, ga_session_id
),
pre_purchase_steps AS (
  SELECT
    e.user_pseudo_id,
    e.ga_session_id,
    e.event_name,
    MIN(e.event_timestamp) AS first_step_ts
  FROM `ga4-project-490603.ga4_capstone.events_base` e
  LEFT JOIN first_purchase p
    ON e.user_pseudo_id = p.user_pseudo_id AND e.ga_session_id = p.ga_session_id
  WHERE e.ga_session_id IS NOT NULL
    AND e.event_name IN ('view_item','add_to_cart','begin_checkout','add_shipping_info','add_payment_info')
    AND (p.first_purchase_ts IS NULL OR e.event_timestamp < p.first_purchase_ts)
  GROUP BY e.user_pseudo_id, e.ga_session_id, e.event_name
),
step_pivot AS (
  SELECT
    user_pseudo_id,
    ga_session_id,
    MAX(CASE WHEN event_name = 'view_item' THEN first_step_ts END) AS view_item_ts,
    MAX(CASE WHEN event_name = 'add_to_cart' THEN first_step_ts END) AS add_to_cart_ts,
    MAX(CASE WHEN event_name = 'begin_checkout' THEN first_step_ts END) AS begin_checkout_ts,
    MAX(CASE WHEN event_name = 'add_shipping_info' THEN first_step_ts END) AS add_shipping_info_ts,
    MAX(CASE WHEN event_name = 'add_payment_info' THEN first_step_ts END) AS add_payment_info_ts
  FROM pre_purchase_steps
  GROUP BY user_pseudo_id, ga_session_id
)
SELECT
  s.user_pseudo_id,
  s.ga_session_id,
  IF(p.view_item_ts IS NULL, 0, 1) AS reached_view_item,
  IF(p.add_to_cart_ts IS NULL, 0, 1) AS reached_add_to_cart,
  IF(p.begin_checkout_ts IS NULL, 0, 1) AS reached_begin_checkout,
  IF(p.add_shipping_info_ts IS NULL, 0, 1) AS reached_add_shipping_info,
  IF(p.add_payment_info_ts IS NULL, 0, 1) AS reached_add_payment_info,
  IF(fp.first_purchase_ts IS NULL, 0, 1) AS reached_purchase,
  CASE WHEN p.view_item_ts IS NOT NULL AND p.add_to_cart_ts IS NOT NULL AND p.add_to_cart_ts >= p.view_item_ts THEN SAFE_DIVIDE(p.add_to_cart_ts - p.view_item_ts, 1000000.0) END AS t_view_to_cart_sec,
  CASE WHEN p.add_to_cart_ts IS NOT NULL AND p.begin_checkout_ts IS NOT NULL AND p.begin_checkout_ts >= p.add_to_cart_ts THEN SAFE_DIVIDE(p.begin_checkout_ts - p.add_to_cart_ts, 1000000.0) END AS t_cart_to_checkout_sec,
  CASE WHEN p.begin_checkout_ts IS NOT NULL AND p.add_shipping_info_ts IS NOT NULL AND p.add_shipping_info_ts >= p.begin_checkout_ts THEN SAFE_DIVIDE(p.add_shipping_info_ts - p.begin_checkout_ts, 1000000.0) END AS t_checkout_to_shipping_sec,
  CASE WHEN p.add_shipping_info_ts IS NOT NULL AND p.add_payment_info_ts IS NOT NULL AND p.add_payment_info_ts >= p.add_shipping_info_ts THEN SAFE_DIVIDE(p.add_payment_info_ts - p.add_shipping_info_ts, 1000000.0) END AS t_shipping_to_payment_sec,
  CAST(NULL AS FLOAT64) AS t_payment_to_purchase_sec
FROM `ga4-project-490603.ga4_capstone.sessions` s
LEFT JOIN step_pivot p
  ON s.user_pseudo_id = p.user_pseudo_id AND s.ga_session_id = p.ga_session_id
LEFT JOIN first_purchase fp
  ON s.user_pseudo_id = fp.user_pseudo_id AND s.ga_session_id = fp.ga_session_id;
