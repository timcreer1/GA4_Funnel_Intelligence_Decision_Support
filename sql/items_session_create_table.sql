
CREATE OR REPLACE TABLE `ga4-project-490603.ga4_capstone.items_session` AS
WITH first_purchase AS (
  SELECT user_pseudo_id, ga_session_id, MIN(event_timestamp) AS first_purchase_ts
  FROM `ga4-project-490603.ga4_capstone.events_base`
  WHERE ga_session_id IS NOT NULL AND event_name = 'purchase'
  GROUP BY user_pseudo_id, ga_session_id
),
item_rows AS (
  SELECT
    e.user_pseudo_id,
    e.ga_session_id,
    e.event_timestamp,
    i.item_id,
    i.item_name,
    i.item_brand,
    i.item_category,
    SAFE_CAST(i.price AS FLOAT64) AS item_price,
    COALESCE(i.quantity, 1) AS quantity
  FROM `ga4-project-490603.ga4_capstone.events_base` e
  LEFT JOIN first_purchase p
    ON e.user_pseudo_id = p.user_pseudo_id AND e.ga_session_id = p.ga_session_id
  CROSS JOIN UNNEST(e.items) AS i
  WHERE e.ga_session_id IS NOT NULL
    AND ARRAY_LENGTH(e.items) > 0
    AND (p.first_purchase_ts IS NULL OR e.event_timestamp < p.first_purchase_ts)
),
item_agg AS (
  SELECT
    user_pseudo_id,
    ga_session_id,
    COUNT(*) AS n_item_rows,
    COUNT(DISTINCT COALESCE(item_id, item_name, item_category)) AS n_distinct_item_id,
    COUNT(DISTINCT item_category) AS n_distinct_item_category,
    AVG(item_price) AS avg_item_price,
    MAX(item_price) AS max_item_price,
    SUM(COALESCE(quantity, 1)) AS qty_sum,
    ARRAY_AGG(item_brand IGNORE NULLS ORDER BY event_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)] AS example_brand,
    ARRAY_AGG(item_category IGNORE NULLS ORDER BY event_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)] AS example_category
  FROM item_rows
  GROUP BY user_pseudo_id, ga_session_id
)
SELECT
  s.user_pseudo_id,
  s.ga_session_id,
  COALESCE(a.n_item_rows, 0) AS n_item_rows,
  COALESCE(a.n_distinct_item_id, 0) AS n_distinct_item_id,
  COALESCE(a.n_distinct_item_category, 0) AS n_distinct_item_category,
  COALESCE(a.avg_item_price, 0.0) AS avg_item_price,
  COALESCE(a.max_item_price, 0.0) AS max_item_price,
  COALESCE(a.qty_sum, 0) AS qty_sum,
  a.example_brand,
  a.example_category
FROM `ga4-project-490603.ga4_capstone.sessions` s
LEFT JOIN item_agg a
  ON s.user_pseudo_id = a.user_pseudo_id AND s.ga_session_id = a.ga_session_id;
