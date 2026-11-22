"""Read this first."""

from typing import Dict, List, Set


class WordList:
    def __init__(self, words: List[str], alphabet: str):
        self._words = words
        self._alphabet = set(alphabet)
        self._char_sets: Dict[str, Set[str]] = {}
        self._valid: List[str] = []
        self._build()

    def _build(self) -> None:
        for word in self._words:
            if self._is_in_alphabet(word) and self._has_unique_chars(word):
                self._valid.append(word)
                self._char_sets[word] = set(word)

    def _is_in_alphabet(self, word: str) -> bool:
        return all(ch in self._alphabet for ch in word)

    def _has_unique_chars(self, word: str) -> bool:
        # BUG FIX 1 (original word_list.py line 25): the loop started at index 1, so the first character
        # was never added to `seen` and a word repeating it ("aba", "sts") passed as valid.
        # Old code:
        #     for i in range(1, len(word)):
        seen: Set[str] = set()
        for i in range(len(word)):
            if word[i] in seen:
                return False
            seen.add(word[i])
        return True

    def valid_words(self) -> List[str]:
        return list(self._valid)

    def are_compatible(self, word_a: str, word_b: str) -> bool:
        chars_a = self._char_sets.get(word_a, set())
        chars_b = self._char_sets.get(word_b, set())
        shared = chars_a & chars_b
        # BUG FIX 2 (original word_list.py line 38): compatible words must share no characters, but this
        # allowed one shared character ("abc" and "cde" share "c").
        # Old code:
        #     return len(shared) <= 1
        return len(shared) == 0

    def char_set(self, word: str) -> Set[str]:
        return set(self._char_sets.get(word, set()))

    def total_unique_chars(self, words: List[str]) -> int:
        combined: Set[str] = set()
        for w in words:
            combined |= self._char_sets.get(w, set())
        return len(combined)

    def alphabet(self) -> Set[str]:
        return set(self._alphabet)
