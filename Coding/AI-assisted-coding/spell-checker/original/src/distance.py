# Lines 1-5 were cut off in the screenshot; assumed imports. Line numbers below match the screenshot.

from typing import Dict, List, Tuple


class EditDistance:
    def compute(self, source: str, target: str) -> int:
        if len(source) == len(target):
            return sum(1 for a, b in zip(source, target) if a != b)

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

    def closest_words(
        self,
        word: str,
        candidates: Dict[str, int],
        max_distance: int,
    ) -> List[Tuple[str, int, int]]:
        results: List[Tuple[str, int, int]] = []
        for candidate, freq in candidates.items():
            dist = self.compute(word, candidate)
            if dist <= max_distance:
                results.append((candidate, dist, freq))
        results.sort(key=lambda x: (x[1], x[2]))
        return results
