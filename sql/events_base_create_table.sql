
CREATE OR REPLACE TABLE `ga4-project-490603.ga4_capstone.events_base` AS
SELECT
  event_date,
  event_timestamp,
  TIMESTAMP_MICROS(event_timestamp) AS event_time,
  event_name,
  SAFE_CAST(user_pseudo_id AS STRING) AS user_pseudo_id,
  user_id,

  -- Sessionisation fields
  (SELECT ep.value.int_value FROM UNNEST(event_params) ep WHERE ep.key = 'ga_session_id') AS ga_session_id,
  (SELECT ep.value.int_value FROM UNNEST(event_params) ep WHERE ep.key = 'ga_session_number') AS ga_session_number,
  COALESCE(
    (SELECT ep.value.int_value FROM UNNEST(event_params) ep WHERE ep.key = 'session_engaged'),
    SAFE_CAST((SELECT ep.value.string_value FROM UNNEST(event_params) ep WHERE ep.key = 'session_engaged') AS INT64)
  ) AS session_engaged_flag,
  (SELECT ep.value.int_value FROM UNNEST(event_params) ep WHERE ep.key = 'engagement_time_msec') AS engagement_time_msec,

  -- Page context
  (SELECT ep.value.string_value FROM UNNEST(event_params) ep WHERE ep.key = 'page_location') AS page_location,
  (SELECT ep.value.string_value FROM UNNEST(event_params) ep WHERE ep.key = 'page_referrer') AS page_referrer,
  (SELECT ep.value.string_value FROM UNNEST(event_params) ep WHERE ep.key = 'page_title') AS page_title,
  event_dimensions.hostname AS hostname,

  -- Event-level acquisition fields
  (SELECT ep.value.string_value FROM UNNEST(event_params) ep WHERE ep.key = 'source') AS ep_source,
  (SELECT ep.value.string_value FROM UNNEST(event_params) ep WHERE ep.key = 'medium') AS ep_medium,
  (SELECT ep.value.string_value FROM UNNEST(event_params) ep WHERE ep.key = 'campaign') AS ep_campaign,
  (SELECT ep.value.string_value FROM UNNEST(event_params) ep WHERE ep.key = 'term') AS ep_term,
  (SELECT ep.value.string_value FROM UNNEST(event_params) ep WHERE ep.key = 'content') AS ep_content,

  -- Device and geo fields
  device.category AS device_category,
  device.operating_system AS device_os,
  device.web_info.browser AS device_browser,
  geo.country AS geo_country,
  geo.region AS geo_region,
  geo.city AS geo_city,

  -- First acquisition traffic-source fields
  traffic_source.source AS traffic_source_source,
  traffic_source.medium AS traffic_source_medium,
  traffic_source.name AS traffic_source_name,

  -- Ecommerce and item fields
  ecommerce,
  items,
  platform,
  stream_id
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210228';
