# NEW FILE: not in the original. Tests the new solution-only methods (bounded_compute, suggest_brute_force).
"""Solution-only checks: the optimized code must agree with the brute force on random inputs."""

import os
import sys

# NEW: lets this file run directly (python3 test_x.py); run.sh's PYTHONPATH still takes priority.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "solution", "src"))
import random
import string
import threading
import unittest

from checker import Checker
from distance import EditDistance


class SolutionOnlyTest(unittest.TestCase):
    def test_bounded_compute_matches_compute(self) -> None:
        ed = EditDistance()
        rng = random.Random(1)
        for _ in range(3000):
            a = "".join(rng.choices("abc", k=rng.randint(0, 6)))
            b = "".join(rng.choices("abc", k=rng.randint(0, 6)))
            d = rng.randint(0, 4)
            expected = min(ed.compute(a, b), d + 1)
            self.assertEqual(ed.bounded_compute(a, b, d), expected, (a, b, d))

    def test_suggest_matches_brute_force(self) -> None:
        rng = random.Random(2)
        for _ in range(30):
            words = {"".join(rng.choices("abcde", k=rng.randint(1, 7))): rng.randint(1, 20) for _ in range(300)}
            checker = Checker(words)
            for _ in range(20):
                query = "".join(rng.choices("abcde", k=rng.randint(1, 7)))
                for d, k in [(0, 3), (1, 5), (2, 5), (3, 10)]:
                    self.assertEqual(checker.suggest(query, d, k), checker.suggest_brute_force(query, d, k), (query, d, k))


    def test_bounded_compute_edge_cases(self) -> None:
        ed = EditDistance()
        self.assertEqual(ed.bounded_compute("a", "abcd", 2), 3)     # E17 length gap > d, skips the DP
        self.assertEqual(ed.bounded_compute("aaaa", "bbbb", 1), 2)  # E18 early exit when a row passes d
        self.assertEqual(ed.bounded_compute("bac", "ccccb", 2), 3)  # E19 no early exit, result still capped
        self.assertEqual(ed.bounded_compute("cat", "cat", 0), 0)    # E20 d = 0, identical
        self.assertEqual(ed.bounded_compute("cat", "bat", 0), 1)    # E20 d = 0, one edit
        self.assertEqual(ed.bounded_compute("", "", 0), 0)          # E21 empty strings

    def test_brute_force_non_positive_limit(self) -> None:
        checker = Checker({"cat": 1})
        self.assertEqual(checker.suggest_brute_force("cat", max_suggestions=0), [])   # E32
        self.assertEqual(checker.suggest_brute_force("cat", max_suggestions=-1), [])


    # NEW: non-functional, concurrency. suggest only reads shared state, so parallel calls must agree.
    def test_concurrent_suggest_is_consistent(self) -> None:
        from dictionary import get_large_dictionary
        checker = Checker(get_large_dictionary())
        words = ["teh", "helo", "thier", "hourse", "knwo"]
        expected = {w: checker.suggest(w) for w in words}
        mismatches = []

        def worker() -> None:
            for _ in range(50):
                for w in words:
                    if checker.suggest(w) != expected[w]:
                        mismatches.append(w)

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(mismatches, [])


if __name__ == "__main__":
    unittest.main()
