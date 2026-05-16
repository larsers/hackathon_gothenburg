"""compose_the_odes — the Pothole Poet's hourly composition cycle.

Two tasks:
  1. federate_pothole_reports — pull raw events from AlloyDB into a BigQuery
     staging table via Lakehouse federation.
  2. ask_the_laureate — aggregate per neighbourhood and ask Gemini 3 Flash
     (via BigQuery's AI.GENERATE) to compose a three-line ode for each.

Runs hourly. Tag a manual run from the DAGs UI to test.
"""

import datetime
import os
from pathlib import Path

from airflow import models
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator

# In Composer Gen 3, this DAG is uploaded to /home/airflow/gcs/dags/, and the
# sql/ folder uploaded alongside it ends up at /home/airflow/gcs/dags/sql/.
SQL_DIR = Path(__file__).parent / "sql"


def _read_sql(name: str) -> str:
    """Read a SQL file from the sql/ folder shipped beside this DAG."""
    text = (SQL_DIR / name).read_text(encoding="utf-8")
    project_id = (
        os.environ.get("GCP_PROJECT")
        or os.environ.get("GOOGLE_CLOUD_PROJECT")
        or os.environ.get("CLOUD_ML_PROJECT_ID")
    )
    if not project_id:
        raise RuntimeError(
            "Composer should expose the project ID via GCP_PROJECT or "
            "GOOGLE_CLOUD_PROJECT env vars; neither was set."
        )
    return text.replace("${PROJECT_ID}", project_id)


with models.DAG(
    dag_id="compose_the_odes",
    description=(
        "Federate pothole reports from AlloyDB into BigQuery and ask Gemini "
        "to compose a three-line poem for each Gothenburg neighbourhood."
    ),
    start_date=datetime.datetime(2026, 5, 1),
    schedule="@hourly",
    catchup=False,
    max_active_runs=1,
    tags=["pothole-poet", "quest-1"],
    default_args={
        "owner": "the-laureate-bureau",
        "retries": 1,
        "retry_delay": datetime.timedelta(minutes=2),
    },
) as dag:

    federate_pothole_reports = BigQueryInsertJobOperator(
        task_id="federate_pothole_reports",
        configuration={
            "query": {
                "query": _read_sql("01_federate.sql"),
                "useLegacySql": False,
            }
        },
    )

    ask_the_laureate = BigQueryInsertJobOperator(
        task_id="ask_the_laureate",
        configuration={
            "query": {
                "query": _read_sql("02_enrich.sql"),
                "useLegacySql": False,
            }
        },
    )

    federate_pothole_reports >> ask_the_laureate
