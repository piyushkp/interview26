"""Tests for WordList."""

import unittest

from word_list import WordList


class WordListTest(unittest.TestCase):

    def test_valid_words_filters_duplicates(self) -> None:
        wl = WordList(["abc", "abbc", "def", "pqr"], alphabet="abcdefpqr")
        valid = wl.valid_words()
        self.assertEqual(len(valid), 3)

    def test_valid_words_filters_out_of_alphabet(self) -> None:
        wl = WordList(["abc", "xyz", "def"], alphabet="abcdef")
        valid = wl.valid_words()
        self.assertEqual(len(valid), 2)

    def test_compatible_disjoint_words(self) -> None:
        wl = WordList(["abc", "def"], alphabet="abcdef")
        self.assertTrue(wl.are_compatible("abc", "def"))

    def test_incompatible_many_shared(self) -> None:
        wl = WordList(["abc", "abd"], alphabet="abcd")
        self.assertFalse(wl.are_compatible("abc", "abd"))

    def test_char_set(self) -> None:
        wl = WordList(["abc"], alphabet="abc")
        self.assertEqual(wl.char_set("abc"), {"a", "b", "c"})

    def test_total_unique_chars(self) -> None:
        wl = WordList(["abc", "def", "ghi"], alphabet="abcdefghi")
        self.assertEqual(wl.total_unique_chars(["abc", "def"]), 6)

    def test_alphabet(self) -> None:
        wl = WordList([], alphabet="abcdef")
        self.assertEqual(wl.alphabet(), set("abcdef"))

    # UNCOMMENTED (original test_word_list.py lines 40-43).
    def test_valid_words_first_char_repeat(self) -> None:
        wl = WordList(["abc", "aba", "sts", "pqr"], alphabet="abcdefghijklmnopqrst")
        valid = wl.valid_words()
        # FILLED IN (original test_word_list.py line 43). Old: self.assertEqual(len(valid), ????)
        self.assertEqual(len(valid), 2)  # catches Bug 1: "aba" and "sts" repeat their first character

    # UNCOMMENTED (original test_word_list.py lines 45-47).
    def test_compatible_single_shared_char(self) -> None:
        wl = WordList(["abc", "cde"], alphabet="abcde")
        # FILLED IN (original test_word_list.py line 47). Old: self.assertEqual(wl.are_compatible("abc", "cde"), ????)
        self.assertEqual(wl.are_compatible("abc", "cde"), False)  # catches Bug 2: they share "c"

    # NEW: edge cases W1-W7 (not in the original tests).
    def test_unique_chars_edge_cases(self) -> None:
        wl = WordList(["abca", "abcc", "abcb", "a", "", "abc", "abc"], alphabet="abc")
        # repeat at the end or middle is invalid; single char, empty word and duplicates are kept
        self.assertEqual(wl.valid_words(), ["a", "", "abc", "abc"])
        self.assertEqual(WordList([], alphabet="abc").valid_words(), [])
        self.assertEqual(WordList(["Abc"], alphabet="abc").valid_words(), [])  # case-sensitive alphabet

    # NEW: edge cases W8-W11 (not in the original tests).
    def test_compatibility_and_char_set_edge_cases(self) -> None:
        wl = WordList(["abc", "def", "aba"], alphabet="abcdef")
        self.assertFalse(wl.are_compatible("abc", "abc"))  # a word overlaps itself
        self.assertTrue(wl.are_compatible("abc", "zzz"))  # unknown word has no characters
        self.assertTrue(wl.are_compatible("abc", "aba"))  # invalid word is treated as unknown
        self.assertEqual(wl.total_unique_chars([]), 0)
        self.assertEqual(wl.total_unique_chars(["abc", "abc", "zzz"]), 3)
        chars = wl.char_set("abc")
        chars.add("z")
        self.assertEqual(wl.char_set("abc"), {"a", "b", "c"})  # returns a copy
        self.assertEqual(wl.char_set("zzz"), set())


if __name__ == "__main__":
    unittest.main()
