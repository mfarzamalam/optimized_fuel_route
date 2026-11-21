"""Run once: add lat and lon columns to data/stations.csv, in the same file.

    python scripts/build_stations.py

Each station gets its town's coordinates from data/us_places.csv. Rows that already
have coordinates are left as they are; towns not found (for example in Canada) stay empty.
"""
import csv
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fuelroute.settings")

import django  # noqa: E402

django.setup()
from planner.places import find_town  # noqa: E402

STATIONS = ROOT / "data/stations.csv"


def main():
    with open(STATIONS, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames + [c for c in ("lat", "lon") if c not in reader.fieldnames]
        rows = list(reader)

    for row in rows:
        if not row.get("lat"):
            point = find_town(row["City"].strip(), row["State"].strip())
            row["lat"], row["lon"] = point or ("", "")

    with open(STATIONS, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    found = sum(1 for row in rows if row["lat"])
    print(f"{found} of {len(rows)} rows in {STATIONS.name} have coordinates")


if __name__ == "__main__":
    main()
