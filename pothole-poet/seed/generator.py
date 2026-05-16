#!/usr/bin/env python3
"""Generate seed data for Quest #1 — The Pothole Poet.

Outputs (both in this directory):
    citizens.json          — 3,000 Göteborg citizens with home neighbourhood + tone.
                              Source of truth for citizen identities; consumed by both
                              this generator (to populate citizen_id on reports) AND by
                              the BigQuery analyst playground seeder
                              (platform/terraform/modules/garage/bq_seed/seed.py).
    pothole_reports.csv    — 5,000 synthetic citizen pothole reports, each with a
                              citizen_id pointing into citizens.json (with ~10% NULLs
                              for anonymous reports).

The CSV is uploaded to gs://{project_id}-seed/ and imported into AlloyDB by
Lane B (AlloyDB Lead) during Quest 2A. citizens.json is loaded into BigQuery at
per-Garage Terraform apply time.

Run:
    pip install -r requirements.txt
    python generator.py
"""

import csv
import json
import random
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from faker import Faker

# Each neighbourhood gets a personality. The biases here are what make the
# Gemini-composed poems texture differently per neighbourhood — without them,
# every poem reads the same.

NEIGHBOURHOODS = [
    {
        "name": "Hisingen",
        "count": 800,
        "moods": ["vengeful"] * 4 + ["frustrated"] * 2 + ["resigned"] * 1,
        "weather": ["slask"] * 3 + ["dimma"] * 2 + ["regn"] * 2 + ["snö"] * 1,
        "severity_weights": [5, 10, 25, 35, 25],
        "swallowed": [
            "hubcap", "lost mitten", "Volvo emblem", "muffler bracket",
            "industrial bolt", "factory ID badge", None,
        ],
        "lat_range": (57.690, 57.720),
        "lng_range": (11.850, 11.950),
    },
    {
        "name": "Frölunda",
        "count": 700,
        "moods": ["philosophical"] * 3 + ["resigned"] * 3 + ["lagom"] * 1,
        "weather": ["snö"] * 3 + ["slask"] * 2 + ["regn"] * 2,
        "severity_weights": [2, 5, 13, 35, 45],
        # Frölunda potholes are craters; they swallow nothing because nothing escapes.
        "swallowed": [None] * 8 + ["entire shopping bag", "a smaller pothole"],
        "lat_range": (57.650, 57.670),
        "lng_range": (11.930, 11.970),
    },
    {
        "name": "Kortedala",
        "count": 600,
        "moods": ["frustrated"] * 4 + ["vengeful"] * 2 + ["resigned"] * 1,
        "weather": ["snö"] * 4 + ["slask"] * 3 + ["regn"] * 1,
        "severity_weights": [5, 15, 30, 30, 20],
        "swallowed": ["apartment key", "tram ticket", "bicycle pedal", "dog leash", "1980s coin", None],
        "lat_range": (57.760, 57.780),
        "lng_range": (12.040, 12.070),
    },
    {
        "name": "Haga",
        "count": 550,
        "moods": ["amused"] * 4 + ["philosophical"] * 2 + ["lagom"] * 1,
        "weather": ["regn"] * 4 + ["sol"] * 2 + ["dimma"] * 1,
        "severity_weights": [25, 35, 25, 12, 3],
        "swallowed": [
            "cinnamon bun", "tourist postcard", "vintage camera strap",
            "second-hand cup", "wedding confetti", None,
        ],
        "lat_range": (57.700, 57.710),
        "lng_range": (11.950, 11.970),
    },
    {
        "name": "Centrum",
        "count": 500,
        "moods": ["resigned"] * 4 + ["frustrated"] * 2 + ["amused"] * 1,
        "weather": ["regn"] * 5 + ["dimma"] * 2 + ["sol"] * 1,
        "severity_weights": [15, 25, 30, 20, 10],
        "swallowed": ["umbrella", "office lanyard", "lunch deal flyer", "tram pass", "press card", None],
        "lat_range": (57.700, 57.715),
        "lng_range": (11.960, 11.985),
    },
    {
        "name": "Annedal",
        "count": 400,
        "moods": ["frustrated"] * 3 + ["philosophical"] * 2 + ["lagom"] * 2,
        "weather": ["regn"] * 4 + ["sol"] * 2 + ["dimma"] * 1,
        "severity_weights": [10, 25, 35, 20, 10],
        "swallowed": ["bicycle bell", "student textbook", "philosophy notes", "thesis chapter", None],
        "lat_range": (57.690, 57.700),
        "lng_range": (11.945, 11.970),
    },
    {
        "name": "Gamlestaden",
        "count": 400,
        "moods": ["vengeful"] * 3 + ["frustrated"] * 3 + ["philosophical"] * 1,
        "weather": ["slask"] * 3 + ["snö"] * 2 + ["regn"] * 2 + ["dimma"] * 1,
        "severity_weights": [5, 15, 30, 30, 20],
        "swallowed": ["tram token", "factory whistle", "century-old nail", "shipyard rivet", None],
        "lat_range": (57.720, 57.735),
        "lng_range": (11.990, 12.020),
    },
    {
        "name": "Linné",
        "count": 350,
        "moods": ["philosophical"] * 4 + ["lagom"] * 2 + ["amused"] * 1,
        "weather": ["regn"] * 4 + ["sol"] * 2 + ["dimma"] * 1,
        "severity_weights": [20, 30, 30, 15, 5],
        "swallowed": ["second-hand book", "natural-wine cork", "vintage scarf", "vinyl 7-inch", None],
        "lat_range": (57.690, 57.700),
        "lng_range": (11.940, 11.962),
    },
    {
        "name": "Majorna",
        "count": 300,
        "moods": ["lagom"] * 4 + ["philosophical"] * 2 + ["amused"] * 1,
        "weather": ["regn"] * 4 + ["sol"] * 2 + ["dimma"] * 1,
        "severity_weights": [15, 30, 35, 15, 5],
        "swallowed": ["sourdough loaf", "vinyl record", "vintage tote", "oat milk carton", "linen napkin", None],
        "lat_range": (57.692, 57.702),
        "lng_range": (11.918, 11.948),
    },
    {
        "name": "Örgryte",
        "count": 200,
        "moods": ["lagom"] * 3 + ["resigned"] * 2 + ["amused"] * 2,
        "weather": ["sol"] * 4 + ["regn"] * 2 + ["dimma"] * 1,
        "severity_weights": [30, 35, 20, 10, 5],
        "swallowed": ["golf ball", "tennis ball", "garden glove", "dog biscuit", None],
        "lat_range": (57.695, 57.715),
        "lng_range": (11.990, 12.020),
    },
    {
        "name": "Vasastan",
        "count": 100,
        "moods": ["resigned"] * 3 + ["lagom"] * 2 + ["philosophical"] * 2,
        "weather": ["sol"] * 3 + ["regn"] * 3 + ["dimma"] * 1,
        "severity_weights": [40, 35, 15, 7, 3],
        "swallowed": ["cufflink", "old money receipt", "monogrammed scarf", "antique brass key", None],
        "lat_range": (57.694, 57.702),
        "lng_range": (11.962, 11.982),
    },
    {
        "name": "Lorensberg",
        "count": 100,
        "moods": ["philosophical"] * 3 + ["amused"] * 2 + ["lagom"] * 2,
        "weather": ["sol"] * 3 + ["regn"] * 3 + ["dimma"] * 1,
        "severity_weights": [30, 35, 25, 8, 2],
        "swallowed": ["theatre ticket", "opera programme", "concert hall pin", "festival wristband", None],
        "lat_range": (57.696, 57.703),
        "lng_range": (11.972, 11.990),
    },
]


# Citizens — character archetypes. Tones are visible to the analyst (a column
# in the citizens table they can group by); occupations are flavour. Names are
# Faker(sv_SE)-generated for proper Swedish texture.

OCCUPATIONS = [
    "lärare", "sjuksköterska", "ingenjör", "programmerare", "spårvägsförare",
    "bibliotekarie", "journalist", "konstnär", "musiker", "kock",
    "pensionerad", "student", "egenföretagare", "hantverkare", "polis",
    "arkitekt", "frisör", "trädgårdsmästare", "fastighetsskötare", "barnmorska",
    "ekonom", "filosof", "sjökapten", "jurist", "hovmästare",
    "busschaufför", "psykolog", "veterinär", "renhållningsarbetare", "stadsplanerare",
]

TONES = [
    "concerned civic", "chaotic poet", "retired engineer with grievances",
    "twelve-year-old with a Strava account", "amateur urbanist", "weekend cyclist",
    "unhinged Volvo enthusiast", "philosophical postal worker", "diaspora returnee",
    "tram-pass moralist", "amateur weather hobbyist", "calm but noting things",
]

# Total citizens, distributed across neighbourhoods proportionally to report counts.
CITIZENS_TOTAL = 3000

# Probability that a report is fully anonymous (no citizen_id).
ANON_RATE = 0.10

# Of the non-anonymous reports, probability that the reporter is a local
# (home_neighbourhood == report.neighbourhood) vs. a visitor from elsewhere.
LOCAL_REPORTER_RATE = 0.70


def load_quotes(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def generate_citizens(fake: Faker) -> list[dict]:
    """Generate CITIZENS_TOTAL citizens, distributed across neighbourhoods
    proportionally to that neighbourhood's report count. Each citizen gets a
    propensity_score (1-5) used to weight reporter selection — most are 1
    (occasional reporters), a few are 5 (power users)."""
    total_reports = sum(nb["count"] for nb in NEIGHBOURHOODS)
    citizens: list[dict] = []
    counter = 0
    for nb in NEIGHBOURHOODS:
        share = round(CITIZENS_TOTAL * nb["count"] / total_reports)
        for _ in range(share):
            counter += 1
            first_seen = date.today() - timedelta(days=random.randint(30, 1825))
            citizens.append({
                "citizen_id": f"cit-{counter:05d}",
                "full_name": fake.name(),
                "home_neighbourhood": nb["name"],
                "occupation": random.choice(OCCUPATIONS),
                "tone": random.choice(TONES),
                "first_seen_date": first_seen.isoformat(),
                # Propensity: heavy power-law. ~70% are score 1, ~5% are score 5.
                "propensity_score": random.choices([1, 2, 3, 4, 5],
                                                   weights=[70, 15, 7, 3, 5], k=1)[0],
            })
    return citizens


def index_citizens(citizens: list[dict]) -> tuple[dict[str, list[dict]], list[dict]]:
    """Index citizens by home_neighbourhood for fast local-vs-visitor selection."""
    by_neighbourhood: dict[str, list[dict]] = {}
    for c in citizens:
        by_neighbourhood.setdefault(c["home_neighbourhood"], []).append(c)
    return by_neighbourhood, citizens


def pick_citizen_id(neighbourhood: str,
                    by_neighbourhood: dict[str, list[dict]],
                    all_citizens: list[dict]) -> str | None:
    """Return a citizen_id (or None for anonymous), weighted by propensity_score
    and biased toward locals."""
    if random.random() < ANON_RATE:
        return None
    pool = (by_neighbourhood.get(neighbourhood, [])
            if random.random() < LOCAL_REPORTER_RATE
            else all_citizens)
    if not pool:
        return None
    weights = [c["propensity_score"] for c in pool]
    return random.choices(pool, weights=weights, k=1)[0]["citizen_id"]


def random_timestamp_in_last_90_days() -> datetime:
    """TZ-aware timestamp biased toward winter and toward morning rush."""
    now = datetime.now(timezone.utc)
    days_ago = random.choices(
        range(90),
        # Mild winter bias — events further back (more winter-y) are more likely.
        weights=[1.0 + 0.5 * (i / 90) for i in range(90)],
        k=1,
    )[0]
    base = now - timedelta(days=days_ago)
    hour = random.choices(
        range(24),
        weights=[1, 1, 1, 1, 1, 2, 5, 8, 7, 5, 3, 3, 3, 3, 2, 2, 3, 3, 2, 2, 1, 1, 1, 1],
        k=1,
    )[0]
    return base.replace(
        hour=hour,
        minute=random.randint(0, 59),
        second=random.randint(0, 59),
        microsecond=0,
    )


def generate_row(nb: dict, quotes: list[str],
                 by_neighbourhood: dict[str, list[dict]],
                 all_citizens: list[dict]) -> dict:
    severity = random.choices(range(1, 6), weights=nb["severity_weights"], k=1)[0]
    citizen_id = pick_citizen_id(nb["name"], by_neighbourhood, all_citizens)
    return {
        "id": str(uuid.uuid4()),
        "reported_at": random_timestamp_in_last_90_days().isoformat(),
        "neighbourhood": nb["name"],
        "latitude": round(random.uniform(*nb["lat_range"]), 6),
        "longitude": round(random.uniform(*nb["lng_range"]), 6),
        "severity_iron_marks": severity,
        "weather": random.choice(nb["weather"]),
        "reporter_mood": random.choice(nb["moods"]),
        "swallowed_object": random.choice(nb["swallowed"]) or "",
        "reporter_quote": random.choice(quotes),
        "citizen_id": citizen_id or "",
    }


def main() -> None:
    here = Path(__file__).parent
    quotes = load_quotes(here / "citizen_quotes.txt")
    if len(quotes) < 50:
        raise SystemExit(f"Expected 100+ citizen quotes; got {len(quotes)}.")
    print(f"Loaded {len(quotes)} citizen quotes.")

    fake = Faker("sv_SE")
    Faker.seed(20260508)
    citizens = generate_citizens(fake)
    citizens_path = here / "citizens.json"
    citizens_path.write_text(json.dumps(citizens, ensure_ascii=False, indent=2),
                             encoding="utf-8")
    print(f"Wrote {len(citizens)} citizens to {citizens_path}")

    by_neighbourhood, all_citizens = index_citizens(citizens)

    rows: list[dict] = []
    for nb in NEIGHBOURHOODS:
        for _ in range(nb["count"]):
            rows.append(generate_row(nb, quotes, by_neighbourhood, all_citizens))
    random.shuffle(rows)

    out = here / "pothole_reports.csv"
    fieldnames = [
        "id", "reported_at", "neighbourhood", "latitude", "longitude",
        "severity_iron_marks", "weather", "reporter_mood", "swallowed_object",
        "reporter_quote", "citizen_id",
    ]
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {out}")
    print()
    counts: dict[str, int] = {nb["name"]: 0 for nb in NEIGHBOURHOODS}
    anon = 0
    for r in rows:
        counts[r["neighbourhood"]] += 1
        if not r["citizen_id"]:
            anon += 1
    print("Distribution by neighbourhood:")
    for name, count in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {name:<14} {count}")
    print(f"\nAnonymous reports: {anon} ({100*anon/len(rows):.1f}%)")


if __name__ == "__main__":
    random.seed(20260508)  # deterministic for reproducible output across runs
    main()
