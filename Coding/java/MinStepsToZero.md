# Minimum Steps to Reduce n to 0 (Add or Subtract a Power of Two)

## 1. Problem Understanding

Given a positive integer `n`, each step adds or subtracts any power of two (`2^i`, `i >= 0`). Return the minimum number of steps to reach `0`.

| Input | Output | Explanation |
|---|---|---|
| 14 | 2 | 14 (01110) -> 16 (10000) -> 0 |
| 27 | 3 | 27 (011011) -> 31 (011111) -> 32 (100000) -> 0 |
| 1 | 1 | 1 -> 0 |

- Powers of two are single set bits, so this is a binary-representation problem.
- Reaching `0` means writing `n` as a signed sum of powers of two (`+2^i` or `-2^i`) using as few terms as possible.
- No constraints were given, so assume `n` can be as large as a 32-bit int and use `long` to avoid overflow when adding 1.

## 2. Approach & Intuition

Process `n` from the lowest bit upward:

1. **Lowest bit is 0 (even):** shift right (`n >>= 1`). It costs nothing, since the bit is already clear.
2. **Lowest bit is 1 (odd):** one step must deal with it, either `n - 1` or `n + 1`. Look at the two lowest bits:
   - `...01`: subtract 1. It clears the bit and doesn't create a carry.
   - `...11`: add 1. The carry turns a run of 1s into a single 1 at a higher bit. For example, `0111` becomes `1000`, so 3 bits cost 1 step.

A run of two or more 1s costs that many steps if cleared one by one, but only 2 steps (one add, one subtract) if rounded up: `0111 = 1000 - 1`.

Example: `27 = 11011`. Bits `...11`, so add 1 to get `11100`. Shift twice to get `111`. Add 1 to get `1000`, then shift to `1`. Subtract 1 to reach `0`. That is 3 steps.

## 3. Data Structures

None, only primitive variables. Bit operations (`& 1`, `& 3`, `>>=`) fit because the problem is about binary structure, so no arrays, maps, or recursion are needed.

## 4. Java Implementation

```java
public class MinStepsToZero {

    public static int minSteps(long n) {
        int steps = 0;
        while (n > 0) {
            if ((n & 1) == 0) {
                n >>= 1;              // even: shift for free
            } else if ((n & 3) == 1) {
                n--;                  // ends in 01: subtract
                steps++;
            } else {
                n++;                  // ends in 11: add, carry merges the 1s
                steps++;
            }
        }
        return steps;
    }
}
```

- `n` is a `long` so `n + 1` can't overflow when `n == Integer.MAX_VALUE`.
- `n == 1` ends in `01`, so it subtracts and ends the loop. `n == 3` (`11`) becomes `4`, 2 steps total, the same as the alternative.

## 5. Complexity Analysis

- **Time:** O(log n). Each iteration shifts out the lowest bit or, after +1/-1, shifts it out on the next iteration.
- **Space:** O(1), no auxiliary storage.

## 6. Dry Run: `n = 14` (`1110`)

| n (binary) | Lowest bits | Action | steps |
|---|---|---|---|
| 1110 (14) | `0` | shift | 0 |
| 111 (7) | `11` | add 1 -> 1000 | 1 |
| 1000 (8) | `0` | shift | 1 |
| 100 (4) | `0` | shift | 1 |
| 10 (2) | `0` | shift | 1 |
| 1 (1) | `01` | subtract 1 -> 0 | 2 |

Result: **2**.

## 7. Test Cases & Edge Cases

| Input | Expected | Notes |
|---|---|---|
| 14 | 2 | sample (`16 - 2`) |
| 27 | 3 | sample (`32 - 4 - 1`) |
| 1 | 1 | minimum |
| 2, 8, 1 073 741 824 (`2^30`) | 1 | exact power of two |
| 3 | 2 | `4 - 1` (or `2 + 1`) |
| 5 | 2 | `4 + 1` |
| 7 | 2 | `8 - 1` |
| 15, 1023 | 2 | all 1s: round up, then subtract |
| 2 147 483 647 (`Integer.MAX_VALUE`) | 2 | overflow case; `long` handles `n + 1` |
| 4 611 686 018 427 387 903 (`Long.MAX_VALUE / 2`) | 2 | large `long` input |

Empty or null inputs don't apply. `n = 0` returns `0` (the loop doesn't run).

The greedy was also compared against a brute-force BFS over every power-of-two move for all `n` from 1 to 2000, with 0 mismatches.

## 8. Alternative Approaches

- **BFS or DP over values:** correct but slow and memory-heavy (roughly O(n log n)). Used only to verify the greedy.
- **Memoized recursion:** `f(n) = f(n/2)` if even, otherwise `1 + min(f(n+1), f(n-1))`. It has O(log n) states, but needs a map and recursion for no gain.
- **Non-adjacent form (NAF):** the answer equals the number of non-zero digits in the NAF of `n`. That is mathematically equivalent to the greedy, but harder to explain from scratch, so mention it as the theory behind the greedy.

The selected solution is O(log n) time with O(1) space and about 10 lines of code. The `& 3` rule is the only trick, and it can be derived on the spot.
