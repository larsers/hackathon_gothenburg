# ⚙️ Quest 2B-3 — Trigger the DAG

<Objective lane="pipeline">

**🎯 What you'll do.** Trigger the `compose_the_odes` DAG manually from the Airflow UI (or one gcloud command) and watch both tasks finish (~30 sec for federation, ~1-2 min for the AI enrichment call). Verify BigQuery now has 12 rows in `pothole_laureate.neighbourhood_odes` — one Gemini-composed three-line ode per Göteborg neighbourhood.

**🤝 Why it matters.** This is the moment the **whole pipeline lights up for the first time**. The Data Engineer's federation finally gets used, their table finally gets read, Gemini finally gets called, and BigQuery finally has poems. After this page, the App Dev / Guardian can flip Streamlit's `TIER` env to `SILVER` and the audience sees real AI verse instead of placeholder text. **You are the persona that earns Silver.**

</Objective>

> Lane A · 3 of 3. ~3 minutes hands-on.

<QuickPath>

```bash
# 1. Trigger the DAG (returns immediately; runs ~1-2 min in background)
gcloud composer environments run the-laureate-bureau \
  --location=europe-west1 \
  dags trigger -- compose_the_odes

# 2. Wait ~2 min, then verify in BigQuery
bq query --use_legacy_sql=false \
  'SELECT count(*) AS n FROM `pothole_laureate.neighbourhood_odes`'
# ✅ Expect: n=12

bq query --use_legacy_sql=false --format=prettyjson \
  'SELECT neighbourhood, ode FROM `pothole_laureate.neighbourhood_odes` ORDER BY pothole_count DESC LIMIT 1'
# ✅ Expect: a real three-line poem (probably about Hisingen)
```

</QuickPath>

DAG is in the bucket, parsed, sitting ready in the Airflow UI. Now we trigger it manually (don't wait for the scheduled run) and watch the AI moment unfold.

---

### Step 1 — Trigger the DAG

In the Airflow UI, click into `compose_the_odes`, then click the **Trigger DAG** button (top-right ▶ play icon). Confirm in the dialog.

✅ **Expect:** The DAG run appears in the Grid view with a yellow ⏳ "running" status.

<Cheat title="Or trigger from the CLI">

```bash
gcloud composer environments run the-laureate-bureau \
  --location=europe-west1 \
  dags trigger -- compose_the_odes
```

The CLI returns immediately; check the UI for status.

</Cheat>

### Step 2 — Watch the run go green (~1-2 min)

In the Grid view, both tasks should turn green:

- `federate_pothole_reports` (~30 sec) — pulls AlloyDB rows into BigQuery via the federation connection.
- `ask_the_laureate` (~30-60 sec) — Gemini composes 12 odes via `AI.GENERATE`.

✅ **Expect:** Two green squares in the Grid view. If either goes red, click into it and read the logs (gotchas at the bottom of this page).

<Screenshot caption="Successful DAG run with both tasks green in the Airflow Grid view." />

<Concept title="The AI moment">

`ask_the_laureate` is the task where everything you've built becomes real. It runs a single BigQuery `INSERT INTO ... SELECT` that:

1. Aggregates the 5,000 federated reports per neighbourhood (group by, count, avg severity, dominant weather/mood).
2. Calls `AI.GENERATE` against a Gemini 3 Flash endpoint with a per-neighbourhood prompt that reads back actual citizen quotes and asks for a three-line poem in the Laureate's voice.
3. Writes the result row to `pothole_laureate.neighbourhood_odes`.

12 LLM calls, one per neighbourhood, all in a single BigQuery statement via `AI.GENERATE`. Takes ~30-60 seconds total.

</Concept>

### Step 3 — Read at least one of the odes out loud

In BigQuery Studio:

```sql
SELECT neighbourhood, ode
FROM `pothole_laureate.neighbourhood_odes`
ORDER BY pothole_count DESC
LIMIT 3;
```

✅ **Expect:** Three rows, each with a real Gemini-composed three-line poem about a Gothenburg neighbourhood. Hisingen first, then Frölunda, then Kortedala.

If the poem mentions cinnamon buns, weather, Eurovision, or Carl, you've made the Laureate proud.

### Step 4 — Verify the full set

```sql
SELECT count(*) FROM `pothole_laureate.neighbourhood_odes`;
```

✅ **Expect:** `12` (one per neighbourhood)

```sql
SELECT neighbourhood, dominant_weather, dominant_mood, composed_at
FROM `pothole_laureate.neighbourhood_odes`
ORDER BY composed_at DESC
LIMIT 5;
```

✅ **Expect:** 5 rows with recent `composed_at` timestamps and real values for `dominant_weather` and `dominant_mood`.

<Gotchas>
- <strong><code>federate_pothole_reports</code> fails: <code>connection alloydb_archive not found</code>.</strong> The Data Engineer&rsquo;s BigQuery sub-lane (Q2C-2) hasn&rsquo;t created the federation connection yet. Wait for them, then re-trigger.
- <strong><code>ask_the_laureate</code> fails on <code>AI.GENERATE</code> with <code>permission denied</code>.</strong> The <code>gemini</code> connection&rsquo;s service account is missing <code>roles/aiplatform.user</code>. Should be pre-bound by the platform &mdash; flag a Sherpa.
- <strong><code>gemini-3-flash</code> not found error.</strong> Gemini 3 is global-endpoint only. The DAG SQL uses the full URL <code>https://aiplatform.googleapis.com/v1/projects/&lt;project&gt;/locations/global/publishers/google/models/gemini-3-flash-preview</code> &mdash; if you edited it and dropped the URL form, restore it.
- <strong>DAG ran green but <code>neighbourhood_odes</code> shows 0 rows.</strong> The federation cache may be stale (the staging table was empty). Re-trigger the DAG.
- <strong>Odes appear as raw JSON, not poetry.</strong> The <code>AI.GENERATE</code> response wasn&rsquo;t unwrapped &mdash; check that <code>02_enrich.sql</code> reads <code>.result</code> off the AI.GENERATE call.
- <strong>Trigger button greyed out.</strong> The DAG is paused. Click the toggle next to the DAG name in the DAGs list to unpause.
</Gotchas>

<Shipped>
The orchestration layer is fully live. <strong>The <code>compose_the_odes</code> DAG ran green end-to-end, and 12 Gemini-composed odes now sit in <code>pothole_laureate.neighbourhood_odes</code>.</strong> The App Dev / Guardian can now flip Streamlit to Silver tier.
</Shipped>

⚙️ **Lane A done.** Tell the App Dev / Guardian:

> *"DAG is green. `pothole_laureate.neighbourhood_odes` has 12 rows. Swap the data source."*

➡️ Next: **Quest 3 — Wire the Pipeline** (sidebar on the left). The team converges; you celebrate with them.
