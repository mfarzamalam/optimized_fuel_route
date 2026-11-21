"""Step 3: find the fuel stations close to the road, and at which mile of the trip they are."""
import csv
from functools import lru_cache

import numpy as np
from django.conf import settings

MAX_MILES_FROM_ROAD = 10
EARTH_RADIUS_MILES = 3958.8


@lru_cache(maxsize=1)
def all_stations():
    """Read data/stations.csv once. A station listed twice keeps its lowest price."""
    cheapest = {}
    with open(settings.DATA_DIR / "stations.csv", newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if not row["lat"]:  # town not found by scripts/build_stations.py (e.g. Canada)
                continue
            station = {
                "name": row["Truckstop Name"].strip(), "address": row["Address"].strip(),
                "city": row["City"].strip(), "state": row["State"].strip(),
                "price": float(row["Retail Price"]), "lat": float(row["lat"]), "lon": float(row["lon"]),
            }
            station_id = row["OPIS Truckstop ID"]
            if station_id not in cheapest or station["price"] < cheapest[station_id]["price"]:
                cheapest[station_id] = station
    return list(cheapest.values())


def distance_miles(lat1, lon1, lat2, lon2):
    """Haversine: distance over the Earth's surface. Works on numpy arrays."""
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 2 * EARTH_RADIUS_MILES * np.arcsin(np.sqrt(a))


def stations_near_route(route):
    # 1. One point for every mile of road.
    lats, lons = np.array(route.lats), np.array(route.lons)
    road_miles = np.concatenate([[0], np.cumsum(distance_miles(lats[:-1], lons[:-1], lats[1:], lons[1:]))])
    count = int(road_miles[-1]) + 2
    lats = np.interp(np.linspace(0, road_miles[-1], count), road_miles, lats)
    lons = np.interp(np.linspace(0, road_miles[-1], count), road_miles, lons)
    mile_markers = np.linspace(0, route.miles, count)  # use OSRM's exact trip length

    # 2. For each station, the closest road point. Skip stations far outside the route's box.
    near = []
    for station in all_stations():
        if not (lats.min() - 0.3 <= station["lat"] <= lats.max() + 0.3
                and lons.min() - 0.3 <= station["lon"] <= lons.max() + 0.3):
            continue
        distances = distance_miles(station["lat"], station["lon"], lats, lons)
        closest = distances.argmin()
        if distances[closest] <= MAX_MILES_FROM_ROAD:
            near.append({**station, "mile": float(mile_markers[closest])})
    return near
