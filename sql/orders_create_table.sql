
CREATE OR REPLACE TABLE `ga4-project-490603.ga4_capstone.orders` AS
WITH purchase_events AS (
  SELECT
    user_pseudo_id,
    ga_session_id,
    event_timestamp,
    TIMESTAMP_MICROS(event_timestamp) AS purchase_time,
    DATE(TIMESTAMP_MICROS(event_timestamp)) AS purchase_date,
    DATE_TRUNC(DATE(TIMESTAMP_MICROS(event_timestamp)), WEEK(MONDAY)) AS week_start_date,
    ecommerce.transaction_id AS transaction_id,
    ecommerce.purchase_revenue AS purchase_revenue,
    ecommerce.total_item_quantity AS total_item_quantity,
    ecommerce.tax_value AS tax_value,
    ecommerce.shipping_value AS shipping_value,
    ecommerce.unique_items AS unique_items
  FROM `ga4-project-490603.ga4_capstone.events_base`
  WHERE ga_session_id IS NOT NULL AND event_name = 'purchase'
)
SELECT *
FROM purchase_events
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY user_pseudo_id, ga_session_id, COALESCE(transaction_id, CAST(event_timestamp AS STRING))
  ORDER BY event_timestamp) = 1;
