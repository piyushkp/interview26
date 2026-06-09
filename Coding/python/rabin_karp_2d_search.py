"""Rabin-Karp style 2D pattern search.

Port of java/RabinKarp2DSearch.java (original package code.ds).

Given a 2D grid of characters, search for the occurrence of a 2D pattern using a
rolling hash (the 2D analogue of Rabin-Karp).

NOTE: The reference rolling-hash shift logic (and the author's extra "-1" loop
bound in search) is buggy, so the rolling hash never equals the pattern hash even
where a real match exists. This is ported faithfully; the demo therefore reports
"pattern not found" even though the pattern is present (verified separately with
check()).
"""

from __future__ import annotations

from typing import List, Optional

MODULUS = 2147483647  # Integer.MAX_VALUE, which happens to be prime.
RADIX = 256           # Alphabet radix (assumes ASCII characters).


class RabinKarp2DSearch:
    def __init__(self, pattern: List[str]):
        self.pattern = pattern
        self.height = len(pattern)
        self.width = len(pattern[0])
        # factors[i] == RADIX^i mod MODULUS (used when shifting the window).
        self.factors = [0] * ((self.height - 1) + (self.width - 1) + 1)
        self.factors[0] = 1
        for i in range(1, len(self.factors)):
            self.factors[i] = (RADIX * self.factors[i - 1]) % MODULUS
        self.pattern_hash = self.hash(pattern)

    def check(self, text: List[str], i: int, j: int) -> bool:
        """True if the pattern matches text with its top-left corner at (i, j)."""
        x, y = i, j
        for a in range(self.height):
            for b in range(self.width):
                if text[x][y] != self.pattern[a][b]:
                    return False
                y += 1
            x += 1
            y = j
        return True

    def get_factors(self) -> List[int]:
        return self.factors

    def hash(self, data: List[str]) -> int:
        """Compute (from scratch) the hash of the upper-left height x width block."""
        result = 0
        for i in range(self.height):
            row_hash = 0
            for j in range(self.width):
                row_hash = (RADIX * row_hash + ord(data[i][j])) % MODULUS
            result = (RADIX * result + row_hash) % MODULUS
        return result

    def search(self, text: List[str]) -> Optional[List[int]]:
        """Return [i, j] of a match, or None. (Faithful to the buggy reference.)"""
        row_start_hash = self.hash(text)
        h = row_start_hash
        # Java: for (i = 0; i <= text.length - height - 1; i++)  (author's -1).
        for i in range(0, len(text) - self.height - 1 + 1):
            if h == self.pattern_hash and self.check(text, i, 0):
                return [i, 0]
            for j in range(0, len(text[0]) - self.width):
                h = self.shift_right(h, text, i, j)
                if h == self.pattern_hash and self.check(text, i, j + 1):
                    return [i, j + 1]
            row_start_hash = self.shift_down(row_start_hash, text, i)
            h = row_start_hash
        return None

    def shift_down(self, h: int, text: List[str], i: int) -> int:
        """Given the hash of the block at (i, j), return the hash at (i + 1, j)."""
        # Hash of row i.
        x_i = 0
        for j in range(self.width):
            x_i = (RADIX * x_i + ord(text[i][j])) % MODULUS
        # Shift row i out of the block hash.
        h = (h + MODULUS - self.factors[self.width - 1] * x_i) % MODULUS
        # Add the hash of row i + height to the block hash.
        x = 0
        for j in range(self.width):
            x = (RADIX * x + ord(text[i + self.height][j])) % MODULUS
        h = (h * RADIX + x) % MODULUS
        return h

    def shift_right(self, h: int, text: List[str], i: int, j: int) -> int:
        """Given the hash of the block at (i, j), return the hash at (i, j + 1)."""
        result = h
        degree = self.height + self.width - 2  # exponent to keep track of.

        # Subtract the first column.
        x_i = 0
        for offset in range(self.height):
            x_i = (x_i + (ord(text[i + offset][j]) * self.factors[degree])) % MODULUS
            degree -= 1

        result = (result + MODULUS - x_i) % MODULUS
        # Multiply by RADIX.
        result *= RADIX

        x = 0
        for k in range(self.height):
            x = (RADIX * x + ord(text[i + k][j + self.width])) % MODULUS
        result = (result + x) % MODULUS
        return result


if __name__ == "__main__":
    text = [
        "1234567890",
        "0987654321",
        "1111111111",
        "1111111111",
        "2222222222",
    ]
    pattern = [
        "876543",
        "111111",
        "111111",
    ]
    searcher = RabinKarp2DSearch(pattern)
    result = searcher.search(text)
    if result is None:
        print("pattern not found")
    else:
        print(f"pattern found at row {result[0]}, col {result[1]}")
    # The pattern actually occurs at (1, 2); check() confirms it directly even
    # though the buggy rolling hash in search() never finds it.
    print("direct check(text, 1, 2):", searcher.check(text, 1, 2))
