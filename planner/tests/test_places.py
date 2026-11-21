from django.test import SimpleTestCase

from planner.places import PlaceNotFound, find_city


class FindCityTests(SimpleTestCase):
    def test_finds_cities_offline(self):
        for text, lat in [("New York, NY", 40.7), ("Kansas City, MO", 39.1), ("St. Louis, MO", 38.6), ("Nashville, TN", 36.2)]:
            self.assertAlmostEqual(find_city(text)[0], lat, places=0, msg=text)

    def test_rejects_bad_input(self):
        for text in ["New York", "Honolulu, HI", "Nowhereville, KS"]:
            with self.assertRaises(PlaceNotFound, msg=text):
                find_city(text)
