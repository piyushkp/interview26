"""You'll implement this."""

from typing import List

from word_list import WordList

# n = valid words, u = distinct character sets (u <= n), A = alphabet size (26 letters or 10 digits).


class MaxUniqueSolver:
    """Finds the subset of valid words that maximizes total unique characters."""

    def __init__(self, word_list: WordList):
        self.word_list = word_list

    # Optimized: bitmask DFS over words that are still compatible, with an upper-bound prune.
    # Time O(2^u) worst case, far less in practice because each pick removes every overlapping word
    # and branches that can't beat the best are cut; Space O(u·A) for the candidate lists on the stack.
    def solve(self) -> List[str]:
        # CHANGED (original solver.py line 15): implemented. Old code:
        #     return []
        # NEW: everything below.
        bit = {ch: 1 << i for i, ch in enumerate(sorted(self.word_list.alphabet()))}
        word_for_mask = {}  # one word per character set: anagrams like "acts"/"cast" are interchangeable
        for word in self.word_list.valid_words():
            mask = 0
            for ch in self.word_list.char_set(word):
                mask |= bit[ch]
            if mask and mask not in word_for_mask:
                word_for_mask[mask] = word
        # Bigger words first so a good answer is found early and the bound prunes more.
        masks = sorted(word_for_mask, key=lambda m: -bin(m).count("1"))
        alphabet_size = len(bit)
        best = {"count": 0, "masks": []}

        def search(candidates: List[int], used: int, chosen: List[int]) -> None:
            count = bin(used).count("1")
            if count > best["count"]:
                best["count"], best["masks"] = count, list(chosen)
            if best["count"] == alphabet_size:  # can't do better than every character
                return
            reachable = used
            for m in candidates:
                reachable |= m
            if bin(reachable).count("1") <= best["count"]:  # bound: even taking everything left can't win
                return
            for i, m in enumerate(candidates):
                rest = [c for c in candidates[i + 1:] if c & m == 0]  # O(u) filter per pick
                chosen.append(m)
                search(rest, used | m, chosen)
                chosen.pop()
                if best["count"] == alphabet_size:
                    return

        search(masks, 0, [])
        return [word_for_mask[m] for m in best["masks"]]

    # NEW: brute force kept so tests can compare it with the optimized solve.
    # Brute force: try every subset with include/exclude recursion, checking pairwise compatibility.
    # Time O(2^n · n), Space O(n) recursion depth.
    def solve_brute_force(self) -> List[str]:
        words = self.word_list.valid_words()
        best: List[str] = []

        def search(i: int, chosen: List[str]) -> None:
            nonlocal best
            if i == len(words):
                if self.word_list.total_unique_chars(chosen) > self.word_list.total_unique_chars(best):
                    best = list(chosen)
                return
            search(i + 1, chosen)  # exclude words[i]
            if all(self.word_list.are_compatible(words[i], w) for w in chosen):  # O(n) check
                chosen.append(words[i])
                search(i + 1, chosen)  # include words[i]
                chosen.pop()

        search(0, [])
        return best
