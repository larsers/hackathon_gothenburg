-- 01_federate.sql — Pull raw pothole reports from AlloyDB into BigQuery.
--
-- Uses BigQuery EXTERNAL_QUERY against the cloud resource connection
-- 'alloydb_archive' that Lane C (Surveyor) created during Quest 2C.
--
-- Materialises into pothole_laureate.pothole_reports_raw, which the next
-- task (ask_the_laureate) reads and aggregates.
--
-- The docs for AI.GENERATE explicitly recommend materialising the source
-- rows into a separate table BEFORE the AI call — that's why this is a
-- two-step DAG rather than one big query.

CREATE OR REPLACE TABLE `pothole_laureate.pothole_reports_raw`
PARTITION BY DATE(reported_at)
CLUSTER BY neighbourhood
AS
SELECT
  id,
  reported_at,
  neighbourhood,
  latitude,
  longitude,
  severity_iron_marks,
  weather,
  reporter_mood,
  swallowed_object,
  reporter_quote,
  citizen_id
FROM EXTERNAL_QUERY(
  'projects/${PROJECT_ID}/locations/europe-west1/connections/alloydb_archive',
  '''
    SELECT id::TEXT AS id, reported_at, neighbourhood, latitude, longitude,
           severity_iron_marks, weather, reporter_mood,
           NULLIF(swallowed_object, '') AS swallowed_object,
           reporter_quote,
           NULLIF(citizen_id, '') AS citizen_id
    FROM pothole_reports
  '''
);
