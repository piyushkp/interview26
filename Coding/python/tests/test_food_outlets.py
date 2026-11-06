import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from food_outlets import getRelevantFoodOutlets


def make_get(pages, calls=None):
    def get(url):
        if calls is not None:
            calls.append(url)
        return pages[int(url.rsplit("=", 1)[1])]
    return get


def outlet(name, cost):
    return {"name": name, "estimated_cost": cost}


class FoodOutletsTest(unittest.TestCase):
    def test_multi_page_order_and_boundary(self):
        pages = {
            1: {"total_pages": 2, "data": [outlet("A", 40), outlet("B", 90)]},
            2: {"total_pages": 2, "data": [outlet("C", 50), outlet("D", 51)]},
        }
        calls = []
        self.assertEqual(getRelevantFoodOutlets("Denver", 50, make_get(pages, calls)),
                         ["A", "C"])
        self.assertEqual(len(calls), 2)
        self.assertIn("city=Denver&page=1", calls[0])

    def test_none_match(self):
        pages = {1: {"total_pages": 1, "data": [outlet("A", 100)]}}
        self.assertEqual(getRelevantFoodOutlets("X", 10, make_get(pages)), [])

    def test_empty_data(self):
        pages = {1: {"total_pages": 1, "data": []}}
        self.assertEqual(getRelevantFoodOutlets("X", 10, make_get(pages)), [])

    def test_zero_pages_makes_single_call(self):
        calls = []
        pages = {1: {"total_pages": 0, "data": []}}
        self.assertEqual(getRelevantFoodOutlets("X", 10, make_get(pages, calls)), [])
        self.assertEqual(len(calls), 1)

    def test_city_with_space_is_encoded(self):
        calls = []
        pages = {1: {"total_pages": 1, "data": []}}
        getRelevantFoodOutlets("New York", 10, make_get(pages, calls))
        self.assertIn("city=New%20York&page=1", calls[0])


if __name__ == "__main__":
    unittest.main()
