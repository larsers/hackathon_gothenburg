# ⚙️ Quest 2B-2 — Upload the DAG

<Objective lane="pipeline">

**🎯 What you'll do.** Copy `pothole-poet/airflow/compose_the_odes.py` and the two SQL files (`01_federate.sql`, `02_enrich.sql`) into your Composer environment's GCS bucket with `gsutil cp`. Then wait ~60 seconds for Airflow to parse the file and surface the new DAG in the UI.

**🤝 Why it matters.** Until the DAG file is in the bucket, Airflow doesn't know `compose_the_odes` exists — the next page (trigger) has nothing to fire. Read the SQL files while you upload them: the two-task structure (federate AlloyDB → BigQuery, then enrich-with-AI) is what you'll demo to your teammates when they ask "wait, where do the poems actually come from?".

</Objective>

> Lane A · 2 of 3. ~3 minutes hands-on (~5 min for Airflow to parse).

<QuickPath>

```bash
# 1. Find the DAGs bucket path
DAGS_BUCKET="$(gcloud composer environments describe the-laureate-bureau \
  --location=europe-west1 \
  --format='value(config.dagGcsPrefix)')"
echo "DAGs bucket: $DAGS_BUCKET"

# 2. Upload DAG + sql/ folder (both needed)
gsutil -m cp -r ~/quest/pothole-poet/airflow/* "$DAGS_BUCKET/"

# 3. Verify upload
gsutil ls "$DAGS_BUCKET/" "$DAGS_BUCKET/sql/"
# ✅ Expect: compose_the_odes.py + sql/01_federate.sql + sql/02_enrich.sql

# 4. Wait 1-5 min, then check Airflow UI shows compose_the_odes (no error pill)
```

</QuickPath>

Apache Airflow doesn't read DAGs from your laptop — it reads them from a directory the scheduler scans on a fixed interval. Managed Composer auto-creates a Cloud Storage bucket for this purpose; anything you put in `<bucket>/dags/` gets parsed and shows up in the Airflow UI.

---

### Step 1 — Find the DAGs bucket path

```bash
DAGS_BUCKET="$(gcloud composer environments describe the-laureate-bureau \
  --location=europe-west1 \
  --format='value(config.dagGcsPrefix)')"
echo "DAGs bucket: $DAGS_BUCKET"
```

✅ **Expect:** `gs://europe-west1-the-laureate-bu-1a2b3c4d-bucket/dags`

<Concept title="Why is the bucket name unpredictable?">

Composer auto-generates the bucket name with a region prefix + the environment name (truncated) + a hash. That makes the name deterministic per environment but not predictable from the env name alone — always look it up via `config.dagGcsPrefix` rather than guessing.

</Concept>

### Step 2 — Upload the DAG + `sql/` folder

`gsutil -m cp -r` is the fastest path. The `-m` parallelises; the `-r` recurses into the `sql/` folder.

```bash
gsutil -m cp -r ~/quest/pothole-poet/airflow/* "$DAGS_BUCKET/"
```

✅ **Expect:** confirmation lines for each file. Lands as:
- `<bucket>/dags/compose_the_odes.py`
- `<bucket>/dags/sql/01_federate.sql`
- `<bucket>/dags/sql/02_enrich.sql`

<Concept title="Why upload the sql/ folder too?">

`compose_the_odes.py` uses `BigQueryInsertJobOperator(query={"query": ..., "useLegacySql": False})` and reads its SQL bodies from sibling paths like `sql/01_federate.sql`. At runtime, those paths resolve relative to the DAG file's location *inside the bucket*.

If you upload only the `.py` file, the DAG parses fine but every task fails on first run with a "no such file" error. Upload the whole `airflow/` directory — DAG + sql/ folder — and the relative paths resolve.

</Concept>

<Cheat title="Or drag and drop in the Console">

From the Composer console: click your environment → **OPEN DAGS FOLDER** → drag the files into the GCS UI. Slower but no terminal needed.

</Cheat>

### Step 3 — Verify the upload

```bash
gsutil ls "$DAGS_BUCKET/"
gsutil ls "$DAGS_BUCKET/sql/"
```

✅ **Expect:** the `dags/` listing shows `compose_the_odes.py`; the `sql/` listing shows both `.sql` files.

### Step 4 — Wait for Airflow to parse, then check the UI

Airflow scans the bucket every ~1 minute. New DAGs show up within ~1-2 min on a quiet system, ~5 min worst case.

Open the Airflow UI: in the Console, your environment page → **OPEN AIRFLOW UI**. Find the **DAGs** tab.

✅ **Expect:** `compose_the_odes` listed alongside the built-in `airflow_monitoring` DAG. No red error pill. No banner at the top of the page.

<Screenshot caption="Airflow DAGs tab showing compose_the_odes parsed and ready to trigger." />

<Gotchas>
- <strong>DAG doesn&rsquo;t appear in the UI after 5 min.</strong> Check the <strong>DAG Errors</strong> banner at the top of the Airflow UI &mdash; it&rsquo;ll show the parse error. Most common: forgot the <code>sql/</code> folder upload, or there&rsquo;s a Python syntax error.
- <strong>DAG appears with red error pill.</strong> Click into it to see the import error. If it says "No such file: <code>sql/01_federate.sql</code>" &mdash; re-run the upload step with the <code>-r</code> flag to include the directory.
- <strong>Wrong bucket path.</strong> The path must come from <code>config.dagGcsPrefix</code> &mdash; don&rsquo;t guess. Composer auto-generates the bucket name with a hash; it&rsquo;s not predictable.
- <strong><code>gsutil</code> errors with <code>access denied</code>.</strong> The Workstation SA needs <code>roles/storage.objectAdmin</code> on the bucket &mdash; pre-bound by the platform; flag a Sherpa if missing.
- <strong>Uploaded files but the timestamps don&rsquo;t update.</strong> <code>gsutil cp</code> is idempotent; if local files haven&rsquo;t changed, the bucket isn&rsquo;t updated. To force re-upload, edit and re-save the DAG file to bump its timestamp, then re-upload.
</Gotchas>

<Shipped>
The DAG is in the bucket and parsed by Airflow. <strong><code>compose_the_odes</code> appears in the Airflow UI, ready to trigger.</strong> Two tasks defined: <code>federate_pothole_reports</code> and <code>ask_the_laureate</code>.
</Shipped>

⚙️ **Q2B-2 done.** DAG uploaded and parsed.

➡️ Next: **Q2B-3 — Trigger the DAG** (sidebar on the left).
