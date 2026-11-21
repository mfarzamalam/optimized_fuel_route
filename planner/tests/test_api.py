from unittest import mock

from django.test import SimpleTestCase

from planner.routing import Route

FAKE_STATIONS = [
    {"name": "Stop 1", "address": "I-70", "city": "Town", "state": "KS", "price": 3.20, "lat": 40.0, "lon": -96.0},
    {"name": "Stop 2", "address": "I-70", "city": "Town", "state": "KS", "price": 2.80, "lat": 40.0, "lon": -94.0},
    {"name": "Stop 3", "address": "I-70", "city": "Town", "state": "KS", "price": 3.50, "lat": 40.0, "lon": -91.0},
    {"name": "Far away", "address": "", "city": "Town", "state": "KS", "price": 1.00, "lat": 41.0, "lon": -95.0},
]


def fake_route(start, finish):
    """A straight road along latitude 40, 632 miles long, instead of calling OSRM."""
    lons = [-100 + 12 * i / 100 for i in range(101)]
    return Route(lats=[40.0] * 101, lons=lons, miles=632.0)


@mock.patch("planner.views.get_route", side_effect=fake_route)
@mock.patch("planner.stations.all_stations", return_value=FAKE_STATIONS)
class RouteApiTests(SimpleTestCase):
    def test_plans_the_trip(self, _stations, routing):
        resp = self.client.get("/api/route/", {"start": "Goodland, KS", "finish": "Peoria, IL"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        routing.assert_called_once()  # one call to the routing API
        self.assertEqual(data["distance_miles"], 632.0)
        # Full tank reaches Stop 2 (cheapest near the road; "Far away" is 69 miles off it).
        self.assertEqual([s["name"] for s in data["fuel_stops"]], ["Stop 2"])
        self.assertEqual(data["number_of_stops"], 1)
        stop = data["fuel_stops"][0]
        self.assertAlmostEqual(stop["gallons"], (632 - stop["mile"]) / 10 - (500 - stop["mile"]) / 10, places=1)
        self.assertEqual(data["total_fuel_cost"], stop["cost"])

    def test_missing_input(self, *_):
        self.assertEqual(self.client.get("/api/route/", {"start": "Goodland, KS"}).status_code, 400)

    def test_unknown_city(self, *_):
        self.assertEqual(self.client.get("/api/route/", {"start": "Nowhereville, KS", "finish": "Peoria, IL"}).status_code, 400)

    def test_no_station_in_reach(self, stations, _routing):
        stations.return_value = []
        self.assertEqual(self.client.get("/api/route/", {"start": "Goodland, KS", "finish": "Peoria, IL"}).status_code, 422)
