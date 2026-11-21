# Lines 1-5 were cut off in the screenshot; assumed to be a docstring and these imports.
from typing import Dict, List, Tuple

# m, n = lengths of the two strings; N = dictionary size; L = average word length.


class EditDistance:
    # Levenshtein distance with a full DP table. Time O(m·n), Space O(m·n)
    def compute(self, source: str, target: str) -> int:
        # BUG FIX 1 (original distance.py lines 8-9): removed the equal-length shortcut. It returned the
        # Hamming distance (substitutions only), which is wrong when a delete + insert is cheaper:
        # "abc" -> "bca" is 2, not 3.
        # Old code:
        #     if len(source) == len(target):
        #         return sum(1 for a, b in zip(source, target) if a != b)

        m = len(source)
        n = len(target)

        dp: List[List[int]] = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if source[i - 1] == target[j - 1]:
                    substitute = dp[i - 1][j - 1]
                else:
                    substitute = dp[i - 1][j - 1] + 1

                insert = dp[i][j - 1] + 1
                delete = dp[i - 1][j] + 1

                dp[i][j] = min(insert, delete, substitute)

        return dp[m][n]

    # NEW: bounded version used by the optimized Checker.suggest.
    # Same distance, but stops once it must exceed max_distance (returns max_distance + 1).
    # Time O(m·n) worst case, usually far less; Space O(n) with two rows.
    def bounded_compute(self, source: str, target: str, max_distance: int) -> int:
        if abs(len(source) - len(target)) > max_distance:  # O(1) reject: each length diff costs an edit
            return max_distance + 1
        prev = list(range(len(target) + 1))
        for i in range(1, len(source) + 1):
            curr = [i] + [0] * len(target)
            for j in range(1, len(target) + 1):
                cost = 0 if source[i - 1] == target[j - 1] else 1
                curr[j] = min(curr[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost)
            if min(curr) > max_distance:  # row minimum never decreases, so the answer can't recover
                return max_distance + 1
            prev = curr
        return min(prev[-1], max_distance + 1)

    # Brute force: compute the distance to every candidate. Time O(N·L² + C log C), Space O(C)
    def closest_words(
        self,
        word: str,
        candidates: Dict[str, int],
        max_distance: int,
    ) -> List[Tuple[str, int, int]]:
        results: List[Tuple[str, int, int]] = []
        for candidate, freq in candidates.items():  # O(N) candidates
            dist = self.compute(word, candidate)  # O(L²) each
            if dist <= max_distance:
                results.append((candidate, dist, freq))
        # BUG FIX 2 (original distance.py line 46): on equal distance, higher frequency must rank first,
        # so sort frequency descending. The word breaks any remaining tie so results are deterministic.
        # Old code:
        #     results.sort(key=lambda x: (x[1], x[2]))
        results.sort(key=lambda x: (x[1], -x[2], x[0]))
        return results
