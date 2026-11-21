from django.test import SimpleTestCase

from planner.fuel import NoStationInReach, plan_fuel_stops


def stations(*rows):
    return [{"name": name, "mile": mile, "price": price} for name, mile, price in rows]


class FuelPlanTests(SimpleTestCase):
    def test_worked_example(self):
        """800 miles, 150-mile tank, 10 mpg, start full: the a-j example worked through by hand."""
        route = stations(
            ("a", 50, 1), ("b", 200, 5), ("c", 300, 7), ("d", 350, 3), ("e", 500, 5),
            ("f", 600, 1), ("g", 650, 6), ("h", 700, 10), ("i", 720, 2), ("j", 770, 1),
        )
        plan = plan_fuel_stops(route, total_miles=800, tank_miles=150, mpg=10)

        self.assertEqual([p["name"] for p in plan], ["a", "b", "d", "e", "f", "i", "j"])
        self.assertEqual([round(p["gallons"], 2) for p in plan], [5, 15, 15, 10, 15, 2, 3])
        self.assertAlmostEqual(sum(p["cost"] for p in plan), 197)

    def test_fills_up_when_nothing_cheaper_is_in_reach(self):
        plan = plan_fuel_stops(stations(("cheap", 100, 2.0), ("dear", 400, 4.0), ("dearer", 700, 5.0)), total_miles=900)
        self.assertEqual(plan[0]["name"], "cheap")
        self.assertAlmostEqual(plan[0]["gallons"], 10)  # arrived with 400 miles left, filled to 500

    def test_short_trip_needs_no_fuel(self):
        self.assertEqual(plan_fuel_stops(stations(("x", 100, 3)), total_miles=400), [])

    def test_gap_longer_than_a_tank_is_an_error(self):
        with self.assertRaises(NoStationInReach):
            plan_fuel_stops(stations(("x", 300, 3)), total_miles=1000)
