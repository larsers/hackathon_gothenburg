-- test_federation.sql — Smoke test for the AlloyDB → BigQuery federation.
-- Run in BigQuery Studio after setup_alloydb_connection.sh succeeds.

-- 1. Can we reach AlloyDB at all? Should return 5000.
-- Note: cast UUID to TEXT — BigQuery doesn't support PostgreSQL UUID natively.
SELECT count(*) AS row_count
FROM EXTERNAL_QUERY(
  'projects/${PROJECT_ID}/locations/europe-west1/connections/alloydb_archive',
  'SELECT id::TEXT AS id FROM pothole_reports'
);

-- 2. Sample a few rows to confirm columns + content look sane.
SELECT *
FROM EXTERNAL_QUERY(
  'projects/${PROJECT_ID}/locations/europe-west1/connections/alloydb_archive',
  'SELECT neighbourhood, severity_iron_marks, reporter_mood, reporter_quote
   FROM pothole_reports
   ORDER BY random()
   LIMIT 5'
);
