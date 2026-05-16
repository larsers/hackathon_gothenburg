# 🛠 Quest 1 — Workstation Warm-up

<Objective lane="all">

**🎯 What you'll do.** Open your Cloud Workstation, clone the Quest repo into `~/quest`, run a few sanity checks, and pick which **Persona** (Data Engineer / Pipeline-author / Infra-Admin / App Dev / Guardian) you'll own for the build sprint. ~10 minutes, all four of you doing the same thing in parallel.

**🤝 Why it matters.** Every codelab from Q2 onward assumes you're sitting in a Workstation terminal with the repo at `~/quest` and `gcloud` pointed at your Garage's project. Persona assignment locks in here too — once Q2 starts you're working *solo* for ~30 minutes, so pick now while the team's still in the same room.

</Objective>

> ~10 minutes. Everyone in the Garage.

You've just walked in. Before anyone splits into lanes, the whole team gets their Cloud Workstation open, the Quest repo cloned, a few sanity checks done, and roles picked.

---

## 🌐 Open these tabs (all in your laptop's Chrome — the workstation has no browser)

Use **incognito** so it picks up the right Google identity.

1. **Cloud Workstation IDE** — link on your workbench card. Looks like:
   `https://<workstation>.cloudworkstations.dev`
2. **GCP Console** — `https://console.cloud.google.com/?project=<your-project-id>`

Your **garage_id** and **project_id** are on the workbench card. For the dry-run, garage_id is `test` and project_id is `dev5-495618`.

---

## 1. Why we're doing this

**Cloud Workstations is a Linux container running on a Compute Engine VM in your Garage's GCP project**, with two surfaces you'll use today: a **Code-OSS based IDE** (with the Cloud Code extension pre-installed) and an **integrated Linux terminal**. You access both through a single tab in your laptop's Chrome.

**There is no browser inside the workstation.** Every time a codelab tells you to "open the GCP Console" or "open a URL", that happens in another tab on **your laptop**, not inside the workstation.

So you'll always have at least two tabs open in your laptop's Chrome:
- **Tab 1:** Cloud Workstation IDE — for editing files, running `gcloud`, `psql`, `gsutil`, `bq`.
- **Tab 2..N:** GCP Console — one tab per product (AlloyDB / Apache Airflow / BigQuery / Kubernetes Engine) for the click-paths.

A few things worth knowing up front:
- Your home directory (`/home/user`) lives on a **persistent disk** that survives workstation stops. If you step away and the workstation idles out, your edits and your cloned repo are still there when you restart it.
- Workstations **idle out** after ~2 hours without interaction. Just clicking around in the IDE counts as interaction; the long Composer wait won't trigger this. If you walk away to lunch, just click the workstation URL again to relaunch.
- The workstation's URL on your workbench card looks like `<workstation>.<cluster>.cloudworkstations.dev` — that's the format. If it asks "Start workstation?", click yes.

The Quest content lives in a public GitHub repo. Your first job is to clone it onto the workstation so every command in the upcoming codelabs has the files it needs.

## 2. What it looks like when done

A VS Code window in your laptop's browser tab, with the Quest repo file tree on the left and a terminal at the bottom. Like this:

```
~/quest$ ls
LICENSE  pothole-poet  README.md
~/quest$ gcloud config get-value project
dev5-495618
```

<Screenshot caption="Cloud Workstation IDE on first load — file tree on the left, terminal on the bottom." />

## 3. 💻 Open the IDE and a terminal

Click the workstation link from your workbench card. If it asks, click **Start workstation** and wait ~20 seconds for the VS Code window to load.

Then open the integrated terminal: **Terminal → New Terminal**, or press <kbd>Ctrl</kbd>+<kbd>`</kbd>.

## 4. 💻 Clone the Quest repo into `~/quest`

The workstation comes up empty. Pull the Quest repo into your home directory at `~/quest` — every codelab references files from that path.

*Hints:*
- The repo is public, no auth needed.
- Use `git clone` with the repo URL and the destination path as the second argument.

<Cheat title="Show the clone command">

```bash
git clone https://github.com/larsers/hackathon_gothenburg.git ~/quest
cd ~/quest
ls
```

You should see `LICENSE`, `pothole-poet/`, and `README.md`.

</Cheat>

## 5. 💻 Verify your environment is sane

Run a few commands in the terminal to confirm the workstation is wired to your Garage's GCP project and has the tools the codelabs assume.

*What to check:*
- Active gcloud account (likely the workstation runner SA).
- Default project matches your `project_id`.
- `bq`, `gsutil`, `kubectl`, and `python3` are on PATH.
- `psql` is on PATH — Lane B (AlloyDB) needs it to seed the database. The default Workstation image does not ship it; install it now so the lane doesn't stall later.

<Cheat title="Show the verify + install commands">

```bash
gcloud auth list
gcloud config get-value project
bq --version | head -1 && gsutil --version | head -1 && kubectl version --client 2>/dev/null | head -1 && python3 --version

# Install the PostgreSQL client (needed by Lane B in Q2A-3 for `psql \copy`).
# The Workstation image doesn't ship it — install once, persists on the home PD.
if ! command -v psql >/dev/null; then
  sudo apt-get update -qq && sudo apt-get install -y postgresql-client
fi
psql --version
```

✅ You should see an active SA, your project_id, and version strings for `bq`, `gsutil`, `kubectl`, Python 3, and `psql` (PostgreSQL 16). If anything is missing, flag a Sherpa.

</Cheat>

## 6. 🌐 Find your way around the GCP Console

Open the GCP Console tab on your laptop's Chrome (`https://console.cloud.google.com/?project=<your-project-id>`). Three landmarks to know before Q2:

- **Project selector** — top-left, next to the Google Cloud logo. Shows your current project name. **Confirm it matches your `project_id`** before clicking anything; lots of "this isn't working" stories trace back to having the wrong project selected.
- **Search bar** — top centre (also <kbd>/</kbd>). The fastest way to jump to any product. Type *"AlloyDB"* / *"Apache Airflow"* / *"BigQuery"* / *"Kubernetes Engine"* and pick the matching result. Faster than the hamburger menu.
- **☰ Hamburger menu** — top-left of the page. The full product catalog organised by category. Pin frequently-used products here so they appear at the top.

You can also see a small **Cloud Shell** icon (top-right, looks like `>_`). It opens a terminal *inside the Console*. We don't use it today — your **Workstation terminal** is where everything happens.

<Concept title="Why is the project selector such a big deal?">

Every GCP resource (database, bucket, service, dataset) lives inside exactly one **project**. Every API call you make is scoped to whichever project is currently selected. If your console tab is on the *wrong* project, you'll get permission-denied errors, missing-resource errors, or — worst — you'll create your AlloyDB cluster in someone else's Garage and not realise it. Always glance at the project selector before clicking.

</Concept>

## 7. Skim the Quest README

Open `pothole-poet/README.md` in the IDE (left-side file tree → click). Skim the story, the lane table, and the tier ladder. Two minutes.

<Cheat title="Show two power-tips for the IDE">

These aren't required, but they make life nicer:

- **Multiple terminals.** Press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>5</kbd> (or click the **Split** icon in the terminal tab list) to split into two side-by-side terminals. Useful when one is running `psql` interactively and you want a free shell for `gsutil`.
- **Drag files in.** You can drag files from your laptop's Finder/Explorer onto the Code-OSS file tree to upload them to `/home/user/`. Right-click a file in the tree → **Download** to pull it back.
- **Install the PWA** for better keyboard shortcuts. The browser eats some shortcuts (<kbd>Cmd</kbd>+<kbd>W</kbd>, <kbd>Cmd</kbd>+<kbd>T</kbd>) that the IDE wants. Click the install icon in your laptop Chrome's address bar; the workstation reopens as a desktop-style app where the IDE owns those keys.

</Cheat>

## 8. Decide your lanes (~3 min, all together)

Look at your team. Pick one role each — then open that lane's codelab page from the sidebar on the left.

| Lane | Role | What they own | Sidebar page |
|---|---|---|---|
| A | **Airflow Lead** | Managed Service for Apache Airflow + the DAG | Q2B · Airflow Lead |
| B | **AlloyDB Lead** | AlloyDB cluster + schema + seed | Q2A · AlloyDB Lead |
| C | **BigQuery Lead** | BigQuery dataset + AlloyDB federation | Q2C · BigQuery Lead |
| D | **GKE / App Lead** | Streamlit app + GKE Autopilot + Gateway | Q2D-1 → Q2D-5 · GKE / App Lead (5 pages) |

**Smaller Garage?**
- **3 people:** collapse C + D. BigQuery Lead finishes BQ work, then drops into Streamlit.
- **2 people:** you're a **Bronze Garage**. One person provisions; the other ships Streamlit on the bundled CSV. Skip the rest. The Foreman will confirm.

## 9. Final check before you split

Each person should now have:
- ✅ Cloud Workstation IDE open in their laptop's Chrome
- ✅ The Quest repo cloned at `~/quest`
- ✅ A lane (write it on a sticky note if helpful)
- ✅ Their next codelab page open in another tab on the **hub**

When the room confirms — **the build sprint begins.**

🚦 Go to your lane.

<Gotchas>
- <strong>Workstation won&rsquo;t start / spins forever.</strong> Refresh the workbench card and click <strong>Start workstation</strong> again. If still stuck after 60 seconds, flag a Sherpa &mdash; they&rsquo;ll re-issue your card.
- <strong><code>gcloud config get-value project</code> shows the wrong project.</strong> Run <code>gcloud config set project &lt;your-project-id&gt;</code> using the project_id on your workbench card.
- <strong><code>git clone</code> says &ldquo;Repository not found&rdquo;.</strong> Double-check the URL spelling. The repo is public &mdash; no auth is needed.
- <strong>You see <code>quests/</code> instead of <code>pothole-poet/</code> at the repo root.</strong> You may have cloned an older snapshot &mdash; <code>cd ~ &amp;&amp; rm -rf quest &amp;&amp; git clone &hellip; ~/quest</code> to start fresh.
- <strong>Trying to open a URL from the workstation terminal does nothing.</strong> Expected &mdash; the workstation has no browser. Copy the URL and paste it into a fresh tab in your laptop&rsquo;s Chrome.
</Gotchas>

<Shipped>
Every Garage member has their Cloud Workstation open in their laptop&rsquo;s Chrome, the Quest repo cloned at <code>~/quest</code>, and a chosen Lane on a sticky note. <strong>You&rsquo;re ready for the build sprint.</strong>
</Shipped>
