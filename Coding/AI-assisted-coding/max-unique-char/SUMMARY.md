# Max Unique Characters — Summary

Variables: n = valid words, u = distinct character sets (u ≤ n), A = alphabet size (26 letters or 10 digits),
L = word length.

## 1. Problem
`WordList` filters words to those in the alphabet with no repeated characters, and has two bugs. Implement
`MaxUniqueSolver.solve()` to pick words that share no characters and maximize the total unique characters,
fast enough for 250 Wordle words (< 1 s) and 300 mixed words (< 3 s).

## 2. Bugs
| # | Symptom | Original line | Solution line | Old code → New code |
|---|---|---|---|---|
| 1 | `"aba"`, `"sts"` counted as valid | `word_list.py:25` (`_has_unique_chars`) | `word_list.py:29` (fix comment at 24) | `for i in range(1, len(word)):` → `for i in range(len(word)):` |
| 2 | `are_compatible("abc", "cde")` is `True` | `word_list.py:38` (`are_compatible`) | `word_list.py:46` (fix comment at 42) | `return len(shared) <= 1` → `return len(shared) == 0` |

**Bug 1, root cause:** the loop starts at index 1, so the first character is never added to `seen` and a
repeat of it goes unnoticed ("aba"). Start at 0.

**Bug 2, root cause:** words are compatible only if they share no characters, but `<= 1` allows one
shared character ("abc" and "cde" share "c"). Use `== 0`.

`????` values:
| Original line | Old | New |
|---|---|---|
| `test_word_list.py:43` | `self.assertEqual(len(valid), ????)` | `self.assertEqual(len(valid), 2)` (abc, pqr) |
| `test_word_list.py:47` | `self.assertEqual(wl.are_compatible("abc", "cde"), ????)` | `... , False)` (they share "c") |

**Setup issue (not a code bug):** the data file was saved as `data/words_month.txt`, but `words.py` loads
`words_months.txt`, so `main.py` and `test_months` crash with `FileNotFoundError`. In `solution/data` it is named
`words_months.txt`; `words.py` is unchanged.

## 3. Brute force
**Approach:** The way I approach brute force is with recursion (backtracking): I go through the list of valid words one at a time, and for each word I try two options, skip it or take it. I only take a word if it shares no letters with the words already picked, and I keep the picked words in a simple list. When I reach the end of the list, I count the unique letters and remember the best list I've seen. This always finds the right answer because it tries every possible combination, but the number of combinations doubles with each word, so it's O(2^n) and 300 words take about 48 seconds.

```text
SOLVE(WORDS)
    BEST = EMPTY LIST
    BACKTRACK(WORDS, 0, EMPTY LIST)
    RETURN BEST

BACKTRACK(WORDS, INDEX, PICKED)
    IF INDEX == LENGTH(WORDS)
        IF UNIQUE_CHARS(PICKED) > UNIQUE_CHARS(BEST)
            BEST = PICKED
        RETURN
    BACKTRACK(WORDS, INDEX + 1, PICKED)                       // skip the word
    IF WORDS[INDEX] SHARES NO LETTER WITH ANY WORD IN PICKED
        BACKTRACK(WORDS, INDEX + 1, PICKED + WORDS[INDEX])    // take the word
```
Time **O(2^n · n·L)** worst case, space **O(n)** recursion. Bottleneck: it re-explores every combination,
including ones that can't beat the best found.

## 4. Optimal
**Approach:** The way I approach the optimal solution is still recursion (DFS with backtracking), but with three tricks. First, I store each word as a bitmask, an integer where each bit stands for one letter, so checking if two words share a letter is one `&` operation, and I use a dictionary from bitmask to word so duplicate words and anagrams are kept only once. Second, every time I pick a word, I pass down only the words that don't clash with it, so the list of choices gets smaller with each pick, and I try longer words first so I find a good answer early. Third, I prune: if the letters still available can't beat my best score, I stop going down that path, and I stop completely once every letter is used. It gives the same answer as brute force, in about 0.1 seconds instead of 48.

**Key insight:** if even taking every remaining compatible character can't beat the best, the branch is dead;
and once all A characters are used, nothing can beat it.
```text
SOLVE(WORDS)
    MASKS = BITMASK OF EACH WORD, ONE PER DISTINCT MASK      // bit i = letter i
    SORT MASKS BY NUMBER OF 1 BITS, LARGEST FIRST
    BEST = EMPTY LIST
    DFS(MASKS, 0, EMPTY LIST)
    RETURN WORDS FOR BEST

DFS(CHOICES, USED, PICKED)
    IF BITS(USED) > BITS(BEST)                                // BITS = number of 1 bits = letters used
        BEST = PICKED
    IF BITS(USED OR ALL CHOICES) <= BITS(BEST)                // prune: can't beat best
        RETURN
    FOR EACH MASK M IN CHOICES
        REST = MASKS AFTER M IN CHOICES WHERE (MASK AND M) == 0   // no shared letters
        DFS(REST, USED OR M, PICKED + M)
```
Time **O(2^u)** worst case, far less in practice (each pick removes every overlapping word, depth ≤ A);
space **O(u·A)** for the candidate lists on the stack.

## 5. Complexity
| | Time | Space |
|---|---|---|
| Brute force | O(2^n · n·L) | O(n) |
| Optimal | O(2^u) worst, pruned in practice | O(u·A) |

Measured: Wordle (250 words) **0.30 s → 5 ms**; large list (300 words) **47.6 s → 105 ms** (the test limit is 3 s);
10,000 random words **38 ms**. Both always return the same total.

## 6. Tests added
**One-line coverage AI prompt**
```text
Review word_list.py and solver.py against all test files and add any missing tests so that every line, branch and edge case (empty input, invalid words, duplicates, ties, boundaries) is covered at 100% line and branch coverage, add non-functional tests for large input (10,000+ words under 1 s, optimized solve matching the brute force) and for concurrent calls from multiple threads, then tell me whether the solution is thread-safe (and what would break it) and what CPU and memory VM I need to run it in production, using measured memory and latency per solve, all without changing the solution code.
```
Expected answers (measured):
- **Thread-safe:** `solve` keeps all state (bitmasks, best, candidate lists) in locals and only reads `WordList`, which has no public way to change after construction; 8 threads solving the 300-word list got identical results (`test_concurrent_solve_is_consistent`). The GIL means threads don't speed up this CPU-bound search, so scale with processes.
- **Sizing:** `WordList` for 300 words ≈ 143 KB; `solve` peaks at 0.8 MB for 10,000 words. One solve takes 5–105 ms on these lists (~10–200 solves/s per core). A **1–2 vCPU / 1 GB** VM is plenty; the risk is CPU, not memory, because the worst case is exponential when no combination reaches all A characters. Cache results per word list, and set a time limit if inputs are untrusted.

Uncommented all 9 given tests and filled in the two `????` values. The original tests alone cover **84%** of the
solution; with the tests added, `./run.sh coverage` reports **100% line and branch coverage** of
`word_list.py` and `solver.py` (27 tests).

**Gaps in the original tests, exposed by our implementation**
- **`solve_brute_force` is never called** (`solver.py:62-78`), so nothing proves the optimized search finds the
  true maximum. Covered by S9 (optimized == brute force on 300 random lists).
- **Large lists only assert `>= 20`**, but the true maximum for the 300-word list is 22, so a search that stops at
  20 or 21 (e.g. an over-aggressive prune) would still pass. Covered by S9 (exact match with the brute force). Plain
  greedy longest-first does fail the originals (Wordle 10, large 17), but S3 pins that down on a tiny input.
- **No empty input, no valid words, or empty word**, which exercise the `mask == 0` skip and the `[]` result. Covered by S1.
- **Duplicates and anagrams are never asserted**: the dedupe-by-bitmask path runs on the data files but no test checks
  only one is picked. Covered by S4.
- **No scale beyond 300 words and no concurrency.** Covered by S10, S11.

**Edge-case scenarios**
| ID | Area | Scenario | Example → expected | Test |
|---|---|---|---|---|
| W1 | valid_words | Repeat of the first character (**Bug 1**) | `aba`, `sts` → filtered; 2 valid | `test_valid_words_first_char_repeat` |
| W2 | valid_words | Repeat in the middle or at the end | `abcc`, `abcb`, `abca` → filtered | `test_unique_chars_edge_cases` |
| W3 | valid_words | Character outside the alphabet; case-sensitive | `xyz`, `Abc` → filtered | `test_valid_words_filters_out_of_alphabet`, `test_unique_chars_edge_cases` |
| W4 | valid_words | Single character, empty word, duplicates kept | `["a", "", "abc", "abc"]` | `test_unique_chars_edge_cases` |
| W5 | valid_words | Empty word list | → `[]` | `test_unique_chars_edge_cases` |
| W6 | are_compatible | One shared character (**Bug 2**) | `abc`, `cde` → False | `test_compatible_single_shared_char` |
| W7 | are_compatible | Same word; unknown or invalid word | `abc`,`abc` → False; `abc`,`zzz` → True | `test_compatibility_and_char_set_edge_cases` |
| W8 | char_set | Returns a copy; unknown word | mutating result doesn't change it; `zzz` → `set()` | `test_compatibility_and_char_set_edge_cases` |
| W9 | total_unique_chars | Empty list; duplicates; unknown words | `[]` → 0; `[abc, abc, zzz]` → 3 | `test_compatibility_and_char_set_edge_cases` |
| S1 | solve | Empty list, no valid words, only `""` | → `[]` | `test_empty_and_no_valid_words` |
| S2 | solve | Single word; every word overlaps | → the single longest word | `test_single_word_and_all_overlapping` |
| S3 | solve | Greedy longest-first is wrong | `abcd, aef, bgh, cd` → `aef, bgh, cd` (8) | `test_greedy_longest_first_is_wrong` |
| S4 | solve | Duplicates and anagrams: pick one | `abc, cab, abc, de` → 2 words, 5 chars | `test_duplicates_and_anagrams_pick_one` |
| S5 | solve | All A characters reached: early stop | → 26 | `test_full_alphabet_stops_early` |
| S6 | solve | Given small cases | trivial 6, overlap 6, small ≥ 9, months 12 | `test_trivial`, `test_overlap`, `test_small_words`, `test_months` |
| S7 | solve | Digit alphabet | primes → 9 | `test_primes` |
| S8 | solve | Given performance limits | Wordle ≥ 20 in < 1 s; large ≥ 20 in < 3 s | `test_wordle_words`, `test_large_words` |
| S9 | solve | Optimized == brute force, result is valid | 300 random lists, alphabets 3–12 | `test_solve_matches_brute_force` |
| S10 | solve | Scale: 10,000 random words | 26 in < 1 s | `test_scale_10000_words` |
| S11 | solve | 8 threads on one `WordList` | identical results | `test_concurrent_solve_is_consistent` |
| S12 | solve_brute_force | Empty list; greedy trap | `[]`; 8 | `test_brute_force_edge_cases` |

Not tested (by design): a list where no combination reaches A and n is in the thousands; that's the exponential
worst case, handled operationally with caching or a time limit.

**Coverage AI prompt** (only what the original tests miss)
```text
The original tests, uncommented and with the ???? values filled in, cover 84% of the solution
(word_list.py 100%, solver.py 74%). Please add tests only for what they miss, then confirm 100%.
Lines the original tests never reach:
1. solver.py solve_brute_force (lines 62-78, never called): [] for an empty list, 8 for
   ["abcd", "aef", "bgh", "cd"] with alphabet "abcdefgh", and the same total as solve() on many random lists.
Behavior the original tests don't check, even where lines are covered:
2. solve returns the true maximum, not just ">= 20": ["abcd", "aef", "bgh", "cd"] -> aef, bgh, cd (8).
3. Empty list, no valid words (["aa", "xyz"], alphabet "abc") and [""] -> [].
4. Duplicates and anagrams: ["abc", "cab", "abc", "de"] -> 2 words, 5 characters.
5. WordList: repeats in the middle/end ("abcc", "abca") are invalid; "Abc" is invalid for alphabet "abc";
   are_compatible(w, w) is False; unknown words are compatible and have an empty char_set; char_set returns a copy.
6. Non-functional: 10,000 random words solve in < 1 s; 8 threads solving one WordList get identical results.
Run: python3 -m coverage run --branch -m unittest <test files>, then coverage report -m for word_list.py and
solver.py. Line and branch coverage must be 100%. Add tests only; don't change the solution code.
```

## 7. Gotchas
- Use `== 0` shared characters, not `<= 1`; and start the uniqueness loop at index 0.
- The original large-list test only checks `>= 20` while the optimum is 22; verify against the brute force, not just the threshold.
- Greedy "longest word first" is wrong (S3); the search must backtrack.
- Deduplicate by character set (anagrams) or the search repeats identical branches.
- Check by hand: the prune uses `<=` (can't *beat* best), and `rest` filters only `candidates[i+1:]` so each
  combination is tried once.
- The data file name mismatch (`words_month.txt` vs `words_months.txt`) crashes `main.py` before any solver code runs.
