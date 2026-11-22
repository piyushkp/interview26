"""Tests for MaxUniqueSolver."""

import os
import sys

# NEW: lets this file run directly (python3 test_x.py); run.sh's PYTHONPATH still takes priority.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "solution", "src"))
import unittest
import time
from typing import List, Set

from solver import MaxUniqueSolver
from word_list import WordList
from words import get_small_words, get_months, get_primes, get_wordle_words, get_large_words


class SolverTest(unittest.TestCase):

    def _validate_solution(self, wl: WordList, result: List[str]) -> None:
        valid = set(wl.valid_words())
        used_chars: Set[str] = set()
        for word in result:
            self.assertIn(word, valid, f"'{word}' is not a valid word")
            chars = wl.char_set(word)
            overlap = used_chars & chars
            self.assertEqual(len(overlap), 0, f"'{word}' shares chars {overlap} with prior words")
            used_chars |= chars

    # ===== Phase 2: Implement Solver =====

    # UNCOMMENTED (original test_solver.py lines 26-31).
    def test_trivial(self) -> None:
        wl = WordList(["abc", "def"], alphabet="abcdef")
        solver = MaxUniqueSolver(wl)
        result = solver.solve()
        self._validate_solution(wl, result)
        self.assertEqual(wl.total_unique_chars(result), 6)

    # UNCOMMENTED (original test_solver.py lines 33-38).
    def test_overlap(self) -> None:
        wl = WordList(["abc", "cde", "fgh"], alphabet="abcdefgh")
        solver = MaxUniqueSolver(wl)
        result = solver.solve()
        self._validate_solution(wl, result)
        self.assertEqual(wl.total_unique_chars(result), 6)

    # UNCOMMENTED (original test_solver.py lines 40-46).
    def test_small_words(self) -> None:
        words, alphabet = get_small_words()
        wl = WordList(words, alphabet)
        solver = MaxUniqueSolver(wl)
        result = solver.solve()
        self._validate_solution(wl, result)
        self.assertGreaterEqual(wl.total_unique_chars(result), 9)

    # UNCOMMENTED (original test_solver.py lines 48-54).
    def test_months(self) -> None:
        words, alphabet = get_months()
        wl = WordList(words, alphabet)
        solver = MaxUniqueSolver(wl)
        result = solver.solve()
        self._validate_solution(wl, result)
        self.assertEqual(wl.total_unique_chars(result), 12)

    # UNCOMMENTED (original test_solver.py lines 56-62).
    def test_primes(self) -> None:
        words, alphabet = get_primes()
        wl = WordList(words, alphabet)
        solver = MaxUniqueSolver(wl)
        result = solver.solve()
        self._validate_solution(wl, result)
        self.assertEqual(wl.total_unique_chars(result), 9)

    # ===== Phase 3: Optimize =====

    # UNCOMMENTED (original test_solver.py lines 66-75).
    def test_wordle_words(self) -> None:
        words, alphabet = get_wordle_words()
        wl = WordList(words, alphabet)
        solver = MaxUniqueSolver(wl)
        start = time.time()
        result = solver.solve()
        elapsed = time.time() - start
        self._validate_solution(wl, result)
        self.assertGreaterEqual(wl.total_unique_chars(result), 20)
        self.assertLess(elapsed, 1.0, f"took {elapsed:.1f}s, expected under 1s")

    # UNCOMMENTED (original test_solver.py lines 77-86).
    def test_large_words(self) -> None:
        words, alphabet = get_large_words()
        wl = WordList(words, alphabet)
        solver = MaxUniqueSolver(wl)
        start = time.time()
        result = solver.solve()
        elapsed = time.time() - start
        self._validate_solution(wl, result)
        self.assertGreaterEqual(wl.total_unique_chars(result), 20)
        self.assertLess(elapsed, 3.0, f"took {elapsed:.1f}s, expected under 3s")


    # ===== NEW: edge cases S1-S8 (not in the original tests) =====

    def _assert_best(self, words: List[str], alphabet: str, expected: int) -> List[str]:
        wl = WordList(words, alphabet)
        result = MaxUniqueSolver(wl).solve()
        self._validate_solution(wl, result)
        self.assertEqual(wl.total_unique_chars(result), expected)
        return result

    def test_empty_and_no_valid_words(self) -> None:
        self.assertEqual(self._assert_best([], "abc", 0), [])
        self.assertEqual(self._assert_best(["aa", "xyz"], "abc", 0), [])
        self.assertEqual(self._assert_best([""], "abc", 0), [])  # empty word adds nothing

    def test_single_word_and_all_overlapping(self) -> None:
        self.assertEqual(self._assert_best(["abc"], "abc", 3), ["abc"])
        self.assertEqual(self._assert_best(["ab", "abc", "bc"], "abc", 3), ["abc"])

    def test_greedy_longest_first_is_wrong(self) -> None:
        # Taking the longest word "abcd" blocks everything else (4); the best is aef + bgh + cd (8).
        result = self._assert_best(["abcd", "aef", "bgh", "cd"], "abcdefgh", 8)
        self.assertEqual(sorted(result), ["aef", "bgh", "cd"])

    def test_duplicates_and_anagrams_pick_one(self) -> None:
        result = self._assert_best(["abc", "cab", "abc", "de"], "abcde", 5)
        self.assertEqual(len(result), 2)

    def test_full_alphabet_stops_early(self) -> None:
        words = ["abcdefghijklm", "nopqrstuvwxyz", "ab", "yz"]
        self._assert_best(words, "abcdefghijklmnopqrstuvwxyz", 26)


if __name__ == "__main__":
    unittest.main()
