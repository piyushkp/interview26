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
            # FILLED IN (original test_distance.py line 23). Old: # ComputeCase("abc", "bca", "????"),
            ComputeCase("abc", "bca", 2),  # catches Bug 1: the Hamming shortcut returned 3
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

        # FILLED IN (original test_distance.py lines 52-57; was commented out with "????").
        # Catches Bug 2: all are distance 1, so the most frequent ("hat") must come first, not "mat".
        top_result = ed.closest_words(
            "rat",
            {"bat": 200, "hat": 300, "mat": 50, "cat": 100},
            max_distance=1,
        )
        self.assertEqual(top_result[0][0], "hat")


    # NEW: edge cases E2, E4, E5, E7, E8, E9 (not in the original tests).
    def test_compute_edge_cases(self) -> None:
        ed = EditDistance()
        cases = [
            ("", "abc", 3),       # E2 empty source
            ("same", "same", 0),  # E4 identical
            ("ca", "cat", 1),     # E6 insert only
            ("cart", "cat", 1),   # E7 delete only
            ("teh", "the", 2),    # E9 adjacent swap costs 2 (no transposition)
            ("abc", "xyz", 3),    # E10 nothing in common
            ("Cat", "cat", 1),    # E11 case-sensitive
        ]
        for source, target, expected in cases:
            self.assertEqual(ed.compute(source, target), expected, (source, target))

    # NEW: edge cases E11, E12, E13 (not in the original tests).
    def test_closest_words_edge_cases(self) -> None:
        ed = EditDistance()
        # E13 same distance and frequency -> alphabetical
        self.assertEqual([w for w, _, _ in ed.closest_words("rat", {"hat": 5, "bat": 5}, 1)], ["bat", "hat"])
        # E14 distance == max_distance is kept, distance > max_distance is dropped
        self.assertEqual(ed.closest_words("cat", {"cart": 1, "carts": 1}, 1), [("cart", 1, 1)])
        # E15 nothing within range
        self.assertEqual(ed.closest_words("cat", {"zzzzz": 1}, 1), [])
        # E16 empty candidates
        self.assertEqual(ed.closest_words("cat", {}, 2), [])


if __name__ == "__main__":
    unittest.main()
