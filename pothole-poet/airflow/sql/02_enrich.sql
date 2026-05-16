-- 02_enrich.sql — The Pothole Poet Laureate composes one ode per neighbourhood.
--
-- We aggregate first (12 neighbourhoods, not 5,000 events) so AI.GENERATE
-- runs 12 times instead of 5,000. Fast (~30s) and cheap.
--
-- TEAM: this is the file to edit during Quest 5 (Theme It). Change the
-- Laureate's voice — pirate captain? IKEA assembly manual? ABBA chorus? —
-- by editing the prompt below. Re-upload the file. Re-trigger the DAG.

CREATE OR REPLACE TABLE `pothole_laureate.neighbourhood_odes`
CLUSTER BY neighbourhood
AS
WITH neighbourhood_stats AS (
  SELECT
    neighbourhood,
    COUNT(*)                                            AS pothole_count,
    ROUND(AVG(severity_iron_marks), 2)                  AS avg_severity,
    APPROX_TOP_COUNT(weather, 1)[OFFSET(0)].value       AS dominant_weather,
    APPROX_TOP_COUNT(reporter_mood, 1)[OFFSET(0)].value AS dominant_mood,
    ARRAY_AGG(reporter_quote IGNORE NULLS ORDER BY RAND() LIMIT 5)   AS sample_quotes,
    ARRAY_AGG(swallowed_object IGNORE NULLS ORDER BY RAND() LIMIT 5) AS sample_swallowed,
    AVG(latitude)                                       AS centroid_lat,
    AVG(longitude)                                      AS centroid_lng
  FROM `pothole_laureate.pothole_reports_raw`
  GROUP BY neighbourhood
)
SELECT
  neighbourhood,
  pothole_count,
  avg_severity,
  dominant_weather,
  dominant_mood,
  sample_quotes,
  sample_swallowed,
  centroid_lat,
  centroid_lng,
  AI.GENERATE(
    prompt => (
      'You are the Göteborg Pothole Poet Laureate. ',
      'Compose a single three-line poem in the voice of a melancholic Swedish bureaucrat ',
      'about the neighbourhood of ', neighbourhood, '. ',
      'Facts to honour: ', CAST(pothole_count AS STRING), ' potholes reported, ',
      'average severity ', CAST(avg_severity AS STRING), ' iron marks out of 5, ',
      'mostly during ', dominant_weather, ', by citizens who feel ', dominant_mood, '. ',
      'Citizen quotes (use one if it fits): ', ARRAY_TO_STRING(sample_quotes, ' | '), '. ',
      'Allegedly swallowed: ', IFNULL(ARRAY_TO_STRING(sample_swallowed, ', '), 'nothing — these are pure craters'), '. ',
      'Output only the poem. No title. No commentary. No quotation marks.'
    ),
    endpoint      => 'https://aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/global/publishers/google/models/gemini-3-flash-preview',
    connection_id => '${PROJECT_ID}.europe-west1.gemini',
    model_params  => JSON '{"generation_config": {"thinking_config": {"thinking_level": "LOW"}}}'
  ).result AS ode,
  CURRENT_TIMESTAMP() AS composed_at
FROM neighbourhood_stats;
