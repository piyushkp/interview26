"""Tests for Checker. Outlines for optional tests, maybe useful after Checker is functioning.
"""

import os
import sys

# NEW: lets this file run directly (python3 test_x.py); run.sh's PYTHONPATH still takes priority.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "solution", "src"))
import unittest
import time

from checker import Checker
from dictionary import get_test_dictionary, get_large_dictionary


class CheckerTest(unittest.TestCase):

    def test_basic_suggestion(self) -> None:
        checker = Checker(get_test_dictionary())
        suggestions = checker.suggest("teh", max_suggestions=3)
        # UNCOMMENTED (original test_checker.py lines 16-17).
        self.assertGreater(len(suggestions), 0)
        self.assertEqual(suggestions[0], "the")

    # UNCOMMENTED (original test_checker.py lines 19-24).
    def test_multiple_misspellings(self) -> None:
        checker = Checker(get_test_dictionary())
        words = ["helo", "thier", "hourse", "knwo"]
        for word in words:
            suggestions = checker.suggest(word, max_suggestions=3)
            self.assertGreater(len(suggestions), 0, f"no suggestions for '{word}'")

    # UNCOMMENTED (original test_checker.py lines 26-35).
    def test_large_dictionary_performance(self) -> None:
        checker = Checker(get_large_dictionary())
        misspelled = ["teh", "helo", "thier", "hourse", "knwo",
                      "abotu", "thign", "peple", "knowl", "herat"]
        start = time.time()
        for word in misspelled:
            suggestions = checker.suggest(word, max_suggestions=5)
            self.assertGreater(len(suggestions), 0, f"no suggestions for '{word}'")
        elapsed = time.time() - start
        self.assertLess(elapsed, 2.0, f"took {elapsed:.1f}s, expected under 2s")

    # NEW: edge cases E20-E25 (not in the original tests).
    def test_ranking_limits_and_edge_cases(self) -> None:
        checker = Checker({"cat": 10, "bat": 30, "hat": 30, "cart": 99, "dog": 5})
        self.assertEqual(checker.suggest("cat"), ["cat", "cart", "bat", "hat"])  # distance, then freq desc, then a-z
        self.assertEqual(checker.suggest("cat", max_suggestions=2), ["cat", "cart"])
        self.assertEqual(checker.suggest("cat", max_distance=0), ["cat"])
        self.assertEqual(checker.suggest("zzzzzz"), [])
        self.assertEqual(checker.suggest("cat", max_suggestions=0), [])
        self.assertEqual(Checker({}).suggest("cat"), [])
        self.assertEqual(checker.suggest(""), [])  # every word is 3+ edits from ""
        self.assertEqual(checker.suggest("cat", max_suggestions=-1), [])  # negative limit
        self.assertEqual(checker.suggest("cat", max_suggestions=100), ["cat", "cart", "bat", "hat"])  # k > matches

    # NEW: edge case E26 (not in the original tests).
    def test_short_query_clamps_length_range(self) -> None:
        # len("a") - max_distance is negative; the length range must start at 0, not wrap or crash.
        checker = Checker({"a": 1, "an": 2, "cat": 3, "cart": 4})
        self.assertEqual(checker.suggest("a", max_distance=2), ["a", "an", "cat"])


if __name__ == "__main__":
    unittest.main()
