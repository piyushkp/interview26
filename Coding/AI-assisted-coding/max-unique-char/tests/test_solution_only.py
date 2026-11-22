# NEW FILE: not in the original. Tests the solution-only method (solve_brute_force), scale and concurrency.
"""Solution-only checks: optimized solve must agree with the brute force, scale, and be thread-safe."""

import random
import string
import threading
import time
import unittest

from solver import MaxUniqueSolver
from word_list import WordList
from words import get_large_words


class SolutionOnlyTest(unittest.TestCase):
    def test_solve_matches_brute_force(self) -> None:
        rng = random.Random(7)
        for _ in range(300):
            alphabet = string.ascii_lowercase[: rng.randint(3, 12)]
            words = ["".join(rng.choices(alphabet, k=rng.randint(0, 5))) for _ in range(rng.randint(0, 14))]
            wl = WordList(words, alphabet)
            solver = MaxUniqueSolver(wl)
            optimized = solver.solve()
            brute = solver.solve_brute_force()
            self.assertEqual(wl.total_unique_chars(optimized), wl.total_unique_chars(brute), words)
            used = set()
            for word in optimized:
                self.assertTrue(used.isdisjoint(wl.char_set(word)), (words, optimized))
                used |= wl.char_set(word)

    def test_brute_force_edge_cases(self) -> None:
        self.assertEqual(MaxUniqueSolver(WordList([], "abc")).solve_brute_force(), [])
        wl = WordList(["abcd", "aef", "bgh", "cd"], "abcdefgh")
        self.assertEqual(wl.total_unique_chars(MaxUniqueSolver(wl).solve_brute_force()), 8)

    def test_scale_10000_words(self) -> None:
        rng = random.Random(5)
        words = ["".join(rng.sample(string.ascii_lowercase, rng.randint(2, 6))) for _ in range(10000)]
        wl = WordList(words, string.ascii_lowercase)
        start = time.time()
        result = MaxUniqueSolver(wl).solve()
        elapsed = time.time() - start
        self.assertEqual(wl.total_unique_chars(result), 26)
        self.assertLess(elapsed, 1.0, f"took {elapsed:.2f}s")

    def test_concurrent_solve_is_consistent(self) -> None:
        words, alphabet = get_large_words()
        wl = WordList(words, alphabet)
        expected = MaxUniqueSolver(wl).solve()
        results = []

        def worker() -> None:
            results.append(MaxUniqueSolver(wl).solve())

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(results, [expected] * 8)


if __name__ == "__main__":
    unittest.main()
