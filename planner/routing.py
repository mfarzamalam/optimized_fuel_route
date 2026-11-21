"""Step 2: one call to OSRM, a free routing API, for the road from A to B."""
from dataclasses import dataclass
from functools import lru_cache

import requests

OSRM_URL = "https://router.project-osrm.org"
METERS_PER_MILE = 1609.344


class RoutingError(Exception):
    pass


@dataclass
class Route:
    lats: list
    lons: list
    miles: float


@lru_cache(maxsize=256)  # the same trip twice makes only one call
def get_route(start, finish):
    """start and finish are (lat, lon). OSRM wants lon,lat."""
    url = f"{OSRM_URL}/route/v1/driving/{start[1]},{start[0]};{finish[1]},{finish[0]}"
    try:
        body = requests.get(url, params={"overview": "full", "geometries": "geojson"}, timeout=20).json()
    except (requests.RequestException, ValueError) as exc:
        raise RoutingError(f"The routing service failed: {exc}") from exc
    if body.get("code") != "Ok":
        raise RoutingError(f"No driving route found ({body.get('code')}).")

    route = body["routes"][0]
    points = route["geometry"]["coordinates"]  # [lon, lat] pairs
    return Route(
        lats=[p[1] for p in points],
        lons=[p[0] for p in points],
        miles=route["distance"] / METERS_PER_MILE,
    )
