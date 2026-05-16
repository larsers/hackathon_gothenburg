#!/usr/bin/env bash
# setup_alloydb_connection.sh — Lane C runs this to create the BigQuery →
# AlloyDB federation connection (`alloydb_archive`).
#
# Run from your Cloud Workstation terminal AFTER Lane B's AlloyDB cluster
# is READY and you know its primary instance ID.
#
# AlloyDB uses BigQuery's connector framework (--connector_configuration with
# connector_id "google-alloydb"), NOT the legacy --connection_type=CLOUD_SQL
# (which only accepts CloudSQL instance names and rejects AlloyDB paths).

set -euo pipefail

PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${REGION:-europe-west1}"
ALLOYDB_CLUSTER="${ALLOYDB_CLUSTER:-pothole-archive}"
ALLOYDB_INSTANCE="${ALLOYDB_INSTANCE:-pothole-archive-primary}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-buildwithgemini2026}"
DB_NAME="${DB_NAME:-postgres}"

INSTANCE_PATH="projects/${PROJECT_ID}/locations/${REGION}/clusters/${ALLOYDB_CLUSTER}/instances/${ALLOYDB_INSTANCE}"

echo "==> Creating BigQuery connection 'alloydb_archive' → ${INSTANCE_PATH}"

CONFIG=$(cat <<JSON
{
  "connector_id": "google-alloydb",
  "asset": {
    "database": "${DB_NAME}",
    "google_cloud_resource": "//alloydb.googleapis.com/${INSTANCE_PATH}"
  },
  "authentication": {
    "username_password": {
      "username": "${DB_USER}",
      "password": {
        "plaintext": "${DB_PASSWORD}"
      }
    }
  }
}
JSON
)

# Idempotent: swallow "Already Exists" on re-run.
LOG=$(mktemp)
if bq mk --connection \
     --location="${REGION}" \
     --project_id="${PROJECT_ID}" \
     --connector_configuration="${CONFIG}" \
     alloydb_archive 2>&1 | tee "${LOG}"; then
  :
elif grep -q -E "Already Exists|already exists" "${LOG}"; then
  echo "(connection alloydb_archive already exists — leaving it in place)"
else
  cat "${LOG}" >&2
  exit 1
fi

echo
echo "✅ Connection ready. Verify with:"
echo "    bq show --connection --location=${REGION} --project_id=${PROJECT_ID} alloydb_archive"
echo
echo "Next: run bigquery/test_federation.sql in BigQuery Studio to confirm the federation works."
