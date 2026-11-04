import os
import sys
import unittest
from unittest.mock import patch

import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from medical_records_filter import fetch_all, filter_records

CONDITIONS = [("age", ">=", 18), ("status", "==", "active")]


class FakeResponse:
    def __init__(self, records):
        self.records = records

    def raise_for_status(self):
        pass

    def json(self):
        return {"records": self.records}


def fake_get(data):
    return lambda url, params, timeout: FakeResponse(data[(params["page"] - 1) * 10:params["page"] * 10])


def rec(record_id, patient, timestamp, weight=None, age=40, status="active"):
    record = {"id": record_id, "patient_id": patient, "timestamp": timestamp,
              "age": age, "status": status}
    if weight is not None:
        record["weight"] = weight
    return record


def ids(records, conditions=CONDITIONS):
    return [r["id"] for r in filter_records(records, conditions)]


DATA = [
    rec(1, "A", "2024-01-01", 70),
    rec(2, "A", "2024-03-01", "80"),   # string weight, arrives before id 3
    rec(3, "A", "2024-02-01", 72),
    rec(4, "B", "2024-01-01", 60, age=30),
    rec(5, "B", "2024-02-01", 60, age=30),
    rec(6, "B", "2024-03-01", age=30),  # missing weight
    rec(7, "C", "2024-01-01", 50, age="55"),
    rec(8, "C", "2024-02-01", 90, age="55", status="inactive"),
    rec(9, "C", "2024-03-01", "heavy", age="55"),
    rec(10, "D", "2024-01-05", 100, age=10),
    rec(11, "D", "2024-01-09", 200, age=10),
    rec(12, "E", "2024-01-01", 50, age="34"),
    rec(13, "E", "2024-01-02", 70, age="34"),
]


class Tests(unittest.TestCase):
    def test_fetch_all_stops_on_empty_page(self):
        for total in (23, 20, 0):
            data = [{"id": i} for i in range(total)]
            self.assertEqual(fetch_all("url", get=fake_get(data)), data)

    def test_fetch_all_guard_against_endless_loop(self):
        with self.assertRaises(RuntimeError):
            fetch_all("url", get=lambda url, params, timeout: FakeResponse([{"id": 1}]), max_pages=5)

    @patch("medical_records_filter.time.sleep")
    def test_fetch_all_retries_then_succeeds(self, _sleep):
        calls = []

        def flaky_get(url, params, timeout):
            calls.append(params["page"])
            if len(calls) == 1:
                raise requests.ConnectionError()
            return FakeResponse([{"id": 1}] if params["page"] == 1 else [])

        self.assertEqual(fetch_all("url", get=flaky_get), [{"id": 1}])
        self.assertEqual(calls, [1, 1, 2])

    @patch("medical_records_filter.time.sleep")
    def test_fetch_all_raises_after_retries(self, _sleep):
        def broken_get(url, params, timeout):
            raise requests.ConnectionError()

        with self.assertRaises(requests.ConnectionError):
            fetch_all("url", get=broken_get)

    def test_bad_condition_values_never_match(self):
        def second_visit(age):
            return [rec(1, "P", "2024-01-01", 50), rec(2, "P", "2024-02-01", 100, age=age)]

        self.assertEqual(ids(second_visit("34")), [2])
        for bad in (None, "n/a", [40]):
            self.assertEqual(ids(second_visit(bad)), [])
        missing = second_visit(40)
        del missing[1]["age"]
        self.assertEqual(ids(missing), [])

    def test_weight_and_conditions(self):
        self.assertEqual(ids(DATA), [2, 13])

    def test_weight_only(self):
        self.assertEqual(ids(DATA, []), [2, 8, 11, 13])

    def test_returns_full_record(self):
        self.assertIs(filter_records(DATA, CONDITIONS)[0], DATA[1])

    def test_empty(self):
        self.assertEqual(filter_records([], CONDITIONS), [])


if __name__ == "__main__":
    unittest.main()
