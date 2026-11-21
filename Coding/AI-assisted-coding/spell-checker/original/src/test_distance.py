"""Tests for EditDistance. All of this is just boilerplate to make test cases compact and
understandable."""

import unittest
from typing import List

from distance import EditDistance


class ComputeCase:
    def __init__(self, source: str, target: str, expected: int):
        self.source = source
        self.target = target
        self.expected = expected


class EditDistanceTest(unittest.TestCase):
    def test_compute(self) -> None:
        all_cases = [
            ComputeCase("", "", 0),
            ComputeCase("abc", "", 3),
            ComputeCase("cat", "bat", 1),
            # ComputeCase("abc", "bca", "????"),
        ]

        ed = EditDistance()
        failures: List[str] = []
        for tc in all_cases:
            actual = ed.compute(tc.source, tc.target)
            if actual != tc.expected:
                failures.append(
                    f"compute('{tc.source}', '{tc.target}') = {actual}, "
                    f"expected {tc.expected}"
                )

        if failures:
            self.fail(
                "\n=== TEST CASE FAILURES ===\n" + "\n".join(failures) + "\n=== END ==="
            )

    def test_closest_words(self) -> None:
        ed = EditDistance()

        results = ed.closest_words(
            "ca",
            {"cat": 500, "catch": 200, "dog": 100},
            max_distance=3,
        )
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0], ("cat", 1, 500))

        # top_result = ed.closest_words(
        #     "rat",
        #     {"bat": 200, "hat": 300, "mat": 50, "cat": 100},
        #     max_distance=1,
        # )
        # self.assertEqual(top_result[0][0], "????")


if __name__ == "__main__":
    unittest.main()
