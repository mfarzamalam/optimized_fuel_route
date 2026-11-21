# Fuel Route Planner

A Django API. Give it a start and a finish in the USA; it returns the cheapest places to
buy fuel on the way and the total fuel cost.

- The truck goes 500 miles on a full tank and does 10 miles per gallon. It starts full.
- Fuel prices come from `data/stations.csv`, the price file provided with the brief.
- The road comes from [OSRM](https://project-osrm.org), a free routing API: **one call per request**.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

Open <http://localhost:8000/api/route/?start=New%20York,%20NY&finish=Los%20Angeles,%20CA>

Run the tests with `python manage.py test`.

## The answer

```json
{
  "start": "New York, NY",
  "finish": "Los Angeles, CA",
  "distance_miles": 2810.5,
  "number_of_stops": 17,
  "fuel_stops": [
    {"name": "SHEETZ #639", "address": "I-80 Exit 223", "city": "Youngstown", "state": "OH",
     "mile": 396.5, "price_per_gallon": 3.059, "gallons": 6.17, "cost": 18.87}
  ],
  "total_gallons": 231.05,
  "total_fuel_cost": 698.63
}
```

Errors return `{"error": "..."}`: 400 for a bad or unknown city, 422 when a stretch of road
has no station within 500 miles, 502 when OSRM fails.

## How it works: four steps

| Step | What happens | File |
|---|---|---|
| 1. Find the cities | "Dallas, TX" → latitude/longitude, from the US Census town list. Offline, no API call. | `planner/places.py` |
| 2. Get the road | **One** call to OSRM returns the road's points and its length. | `planner/routing.py` |
| 3. Stations near the road | Put a point on every mile of road. For each station, find the closest point; keep it if it is within 10 miles. That point's mile is the station's place on the trip. | `planner/stations.py` |
| 4. Cheapest stops | At each station, look 500 miles ahead. **Cheaper station in reach?** Buy just enough to get there. **Nothing cheaper?** Fill the tank and go to the cheapest one in reach. | `planner/fuel.py` |

`planner/views.py` runs the four steps and returns the JSON.

**Why step 4 is the cheapest:** every gallon is bought at the lowest price the truck can
reach before it runs out.

## The data

Two files, both read into memory:

- `data/stations.csv`: the stations and their prices (the file provided with the brief).
- `data/us_places.csv`: US towns with their coordinates (the US Census list).

The price file came with a city and state but no coordinates.
`scripts/build_stations.py` was run once to add `lat` and `lon` columns to that same file,
using each station's town from `us_places.csv`. Canadian stations get no coordinates and are
skipped; a station listed twice keeps its lowest price.

6,622 US stations have coordinates. A station sits at the centre of its town, not at its
exact exit, so "10 miles from the road" is approximate.
