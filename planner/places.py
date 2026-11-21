"""Step 1: turn "City, ST" into latitude and longitude, offline, using the US Census town list."""
import csv
import re
from functools import lru_cache

from django.conf import settings

NOT_DRIVABLE = {"AK", "HI", "PR"}  # a truck can't drive there from the mainland
# Words the Census adds after a name: "Kansas City city", "Canton charter township".
SUFFIX = re.compile(r"\s+(city|town|village|cdp|borough|township|charter township|ccd|county|"
                    r"metropolitan government|consolidated government|unified government|urban county)$")


class PlaceNotFound(Exception):
    pass


def normalize(name):
    """'Big Cabin town' and 'Big Cabin' -> 'big cabin'; 'St. Louis' -> 'saint louis'."""
    name = name.lower().replace("(balance)", "").strip()
    for _ in range(3):  # "Kansas City city" -> "kansas city" -> "kansas"
        name = SUFFIX.sub("", name).strip()
    name = re.sub(r"[^a-z0-9 ]", " ", name.replace("-", " "))
    words = {"st": "saint", "ste": "sainte", "ft": "fort", "mt": "mount"}
    return " ".join(words.get(w, w) for w in name.split())


@lru_cache(maxsize=1)
def census_places():
    """{(town, state): (lat, lon)}. Cities and towns win over townships with the same name."""
    places, townships = {}, {}
    with open(settings.DATA_DIR / "us_places.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            target = places if row["kind"] == "place" else townships
            point = (float(row["lat"]), float(row["lon"]))
            target.setdefault((normalize(row["name"]), row["state"]), point)
            # "Nashville-Davidson" is also known as "Nashville".
            target.setdefault((normalize(row["name"].split("-")[0]), row["state"]), point)
    return {**townships, **places}


def find_town(city, state):
    """(lat, lon) for a town, or None. Also tries 'Mc Calla' as 'mccalla'."""
    key = normalize(city)
    joined = re.sub(r"\b(mc|de|la|le|du|van) ", r"\1", key)
    return census_places().get((key, state)) or census_places().get((joined, state))


def find_city(text):
    """'New York, NY' -> (lat, lon)."""
    parts = [p.strip() for p in text.split(",")]
    if len(parts) != 2 or len(parts[1]) != 2:
        raise PlaceNotFound(f'Write the place as "City, ST", for example "Dallas, TX" (got "{text}").')
    city, state = parts[0], parts[1].upper()
    if state in NOT_DRIVABLE:
        raise PlaceNotFound(f'"{text}" is not in the contiguous USA.')
    point = find_town(city, state)
    if point is None:
        raise PlaceNotFound(f'Could not find "{text}".')
    return point
