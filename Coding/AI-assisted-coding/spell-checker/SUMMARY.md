# Spell Checker — Summary

Variables: N = dictionary size, L = word length, d = `max_distance`, k = `max_suggestions`,
N_d = words whose length is within d of the query, C = matches within d.

## 1. Problem
`EditDistance` computes Levenshtein distance (insert, delete, substitute) and has two bugs. Implement
`Checker.suggest(word, max_distance=2, max_suggestions=5)` to return corrections ranked by distance
(low first), then frequency (high first), and make it fast on a 50,000-word dictionary (< 2 s for 10 words).

## 2. Bugs
| # | Symptom | Original line | Solution line | Old code → New code |
|---|---|---|---|---|
| 1 | `compute("abc", "bca")` returns 3, expected 2 | `distance.py:8-9` (`compute`) | `distance.py:10` (fix comment) | `if len(source) == len(target): return sum(1 for a, b in zip(source, target) if a != b)` → removed |
| 2 | `closest_words("rat", …)` returns `mat` first, expected `hat` | `distance.py:46` (`closest_words`) | `distance.py:74` (fix comment at 70) | `key=lambda x: (x[1], x[2])` → `key=lambda x: (x[1], -x[2], x[0])` |

**Bug 1, root cause:** the equal-length shortcut counts mismatched letters (substitutions only), but an
insert + delete can be cheaper: "abc" → "bca" is 2 (delete "a", append "a"), not 3. The DP already handles it, so delete the shortcut.

**Bug 2, root cause:** Python sorts keys ascending, so on equal distance the *rarest* word wins ("mat" 50 beats "hat" 300).
Negate frequency to sort it descending; add the word as a final key for stable ties.

`????` values:
| Original line | Old | New |
|---|---|---|
| `test_distance.py:23` | `# ComputeCase("abc", "bca", "????"),` | `ComputeCase("abc", "bca", 2),` |
| `test_distance.py:57` | `# self.assertEqual(top_result[0][0], "????")` | `self.assertEqual(top_result[0][0], "hat")` (all four are distance 1; hat has the highest frequency) |

## 3. Brute force
**Approach:** The way I approach brute force is to loop over every word in the dictionary and compute its edit distance to the misspelled word, meaning the fewest single-letter inserts, deletes or replacements to turn one into the other. I compute that with dynamic programming, using a 2D table where each cell holds the cost for a prefix of each word. I keep the words that are close enough in a list, sort it by distance, then by frequency (most common first), then alphabetically, and return the top k. It's always correct because it checks every word, but it builds a full table for all 50,000 words, so ten lookups take about 2 seconds.

```text
SUGGEST(WORD, MAX_DISTANCE, K)
    IF K <= 0
        RETURN EMPTY LIST
    RESULTS = EMPTY LIST
    FOR EACH (CANDIDATE, FREQ) IN DICTIONARY
        DIST = EDIT_DISTANCE(WORD, CANDIDATE)                 // full 2D DP table
        IF DIST <= MAX_DISTANCE
            ADD (CANDIDATE, DIST, FREQ) TO RESULTS
    SORT RESULTS BY DIST ASC, FREQ DESC, CANDIDATE A-Z
    RETURN FIRST K CANDIDATES OF RESULTS
```
Time **O(N·L² + C log C)**, space **O(L² + C)**. Bottleneck: the full DP for all N words.

## 4. Optimal
**Approach:** The way I approach the optimal solution is to skip work that can't change the answer. First, I build a dictionary that maps word length to a list of words, once at startup; since every extra or missing letter costs at least one edit, I only look at words whose length is close to the misspelled word. Second, I still use dynamic programming for the distance, but with just two rows instead of the full table, and I stop early as soon as a whole row is already over the limit, because the numbers can only go up from there. Third, I use a min-heap (`heapq.nsmallest`) to grab the top k suggestions instead of sorting every match. The results are the same as brute force, but ten lookups take a few milliseconds instead of 2 seconds.

**Key insight:** each character of length difference costs at least one edit, so only words with length
within d of the query can match; and once every cell in a DP row exceeds d, the distance can't come back down.
```text
BUILD_INDEX(DICTIONARY)                                       // once, in __init__
    FOR EACH WORD IN DICTIONARY
        ADD WORD TO WORDS_BY_LENGTH[LENGTH(WORD)]

SUGGEST(WORD, MAX_DISTANCE, K)
    IF K <= 0
        RETURN EMPTY LIST
    MATCHES = EMPTY LIST
    FOR LEN = MAX(0, LENGTH(WORD) - MAX_DISTANCE) TO LENGTH(WORD) + MAX_DISTANCE
        FOR EACH CANDIDATE IN WORDS_BY_LENGTH[LEN]
            DIST = BOUNDED_EDIT_DISTANCE(WORD, CANDIDATE, MAX_DISTANCE)   // 2 DP rows, stops early
            IF DIST <= MAX_DISTANCE
                ADD (DIST, -FREQ[CANDIDATE], CANDIDATE) TO MATCHES
    RETURN CANDIDATES OF THE K SMALLEST MATCHES                // min-heap
```
Time **O(N_d·L·d)** typical, O(N_d·L²) worst; space **O(N)** index + **O(C + L)** per query.

## 5. Complexity
| | Time per query | Space |
|---|---|---|
| Brute force | O(N·L² + C log C) | O(L² + C) |
| Optimal | O(N_d·L·d + C log k) | O(N) index, O(C + L) per query |

Measured on 10 misspellings: large dictionary (50,084 words) **2.10 s → < 0.01 s**. With 50,000 random
words all of length 5 (length filter can't help) **1.34 s → 0.80 s**. Next step: trie + DP rows.

## 6. Tests added
**One-line coverage AI prompt**
```text
Review distance.py and checker.py against all test files and add any missing tests so that every line, branch and edge case (empty input, ties, limits, boundaries) is covered at 100% line and branch coverage, add non-functional tests for large input (50,000+ words under 2 s, optimized suggest matching the brute force at scale) and for concurrent calls from multiple threads, then tell me whether the solution is thread-safe (and what would break it) and what CPU and memory VM I need to run it in production, using measured memory per word and latency per query, all without changing the solution code.
```
Expected answers (measured):
- **Thread-safe for reads:** `suggest` only reads `dictionary` and `words_by_length` and keeps all state in locals; 8 threads × 250 queries gave identical results (`test_concurrent_suggest_is_consistent`). It breaks if the dictionary is changed while queries run (stale index, "dict changed size" errors), so rebuild a new `Checker` and swap the reference instead. The GIL means threads give no speedup for this CPU-bound work: scale with processes (one worker per core).
- **Sizing:** ~6.5 MB for 50k words (~130 B/word), so 1M words ≈ 130 MB per process; typical query 0.4 ms (~2,400 queries/s per core), worst case 80 ms when all words share a length (~12/s per core). For 50k words, a **2 vCPU / 2 GB** VM is plenty; cores ≈ target QPS ÷ per-core QPS, memory ≈ workers × (index + ~30 MB Python runtime).

Uncommented the given tests (`test_basic_suggestion`, `test_multiple_misspellings`,
`test_large_dictionary_performance`) and filled in the two `????` values. The original tests alone cover **89%** of the solution; with the tests added, every scenario below has a test and
`./run.sh coverage` reports **100% line and branch coverage** of `distance.py` and `checker.py` (14 tests).

**Gaps in the original tests, exposed by our implementation**
- **`bounded_compute` had no tests at all.** It's new, and its three exits (length gap, early exit, final cap) can each be wrong while `suggest` still looks fine. The missing cap was a real bug in my first version, caught only by E16/E18.
- **No tie on equal frequency.** The original ties ("rat") all have different frequencies, so a broken alphabetical tie-break in `closest_words` or in the heap tuple `(dist, -freq, word)` would pass. Covered by E11, E20.
- **No short query.** No original query is shorter than `max_distance`, so the `max(0, len(word) - d)` clamp in the length range is never exercised. Covered by E26.
- **No limit edge cases.** `max_suggestions` is never 0, negative or larger than the number of matches, so the new `<= 0` guards and the heap's `k > C` case are untested. Covered by E22, E23, E29.
- **Weak assertions on the optimized path.** `test_multiple_misspellings` and `test_large_dictionary_performance` only check "not empty", so an optimization that returned wrong or misordered words would still pass. Covered by E30 (optimized == brute force on random dictionaries).
- **No `d = 0`, exact match, empty dictionary or empty query.** These hit boundaries of the length index and the DP. Covered by E17, E21, E24, E25.

**Edge-case scenarios**
| ID | Area | Scenario | Example → expected | Test |
|---|---|---|---|---|
| E1 | compute | Both strings empty | `("", "")` → 0 | `test_compute` |
| E2 | compute | One string empty | `("abc", "")`, `("", "abc")` → 3 | `test_compute`, `test_compute_edge_cases` |
| E3 | compute | One substitution | `("cat", "bat")` → 1 | `test_compute` |
| E4 | compute | Identical strings | `("same", "same")` → 0 | `test_compute_edge_cases` |
| E5 | compute | Insert only / delete only | `("ca", "cat")`, `("cart", "cat")` → 1 | `test_compute_edge_cases` |
| E6 | compute | Same length, insert + delete is cheaper (**Bug 1**) | `("abc", "bca")` → 2 | `test_compute` |
| E7 | compute | Adjacent swap costs 2 (no transposition) | `("teh", "the")` → 2 | `test_compute_edge_cases` |
| E8 | compute | Nothing in common | `("abc", "xyz")` → 3 | `test_compute_edge_cases` |
| E9 | compute | Case-sensitive | `("Cat", "cat")` → 1 | `test_compute_edge_cases` |
| E10 | closest_words | Same distance → higher frequency first (**Bug 2**) | `"rat"` → `hat` first | `test_closest_words` |
| E11 | closest_words | Same distance and frequency → alphabetical | `{hat:5, bat:5}` → `[bat, hat]` | `test_closest_words_edge_cases` |
| E12 | closest_words | Distance == max kept, > max dropped | `"cat"`, d=1: `cart` kept, `carts` dropped | `test_closest_words_edge_cases` |
| E13 | closest_words | No match / empty candidates | → `[]` | `test_closest_words_edge_cases` |
| E14 | bounded_compute | Length gap > d (skips the DP) | `("a", "abcd", 2)` → 3 | `test_bounded_compute_edge_cases` |
| E15 | bounded_compute | Early exit when a whole row is > d | `("aaaa", "bbbb", 1)` → 2 | `test_bounded_compute_edge_cases` |
| E16 | bounded_compute | No early exit, result still capped at d + 1 | `("bac", "ccccb", 2)` → 3 | `test_bounded_compute_edge_cases` |
| E17 | bounded_compute | d = 0; empty strings | `("cat","cat",0)` → 0, `("cat","bat",0)` → 1, `("","",0)` → 0 | `test_bounded_compute_edge_cases` |
| E18 | bounded_compute | Matches `min(compute, d + 1)` | 3,000 random pairs, d = 0..4 | `test_bounded_compute_matches_compute` |
| E19 | suggest | Misspelling → most likely word | `"teh"` → `the` first | `test_basic_suggestion` |
| E20 | suggest | Ranking: distance, then frequency desc, then a-z | `"cat"` → `[cat, cart, bat, hat]` | `test_ranking_limits_and_edge_cases` |
| E21 | suggest | Exact match ranks first | `"cat"` → `cat` first | `test_ranking_limits_and_edge_cases` |
| E22 | suggest | Limit k, and k > number of matches | k=2 → `[cat, cart]`; k=100 → all 4 | `test_ranking_limits_and_edge_cases` |
| E23 | suggest | k = 0 or negative | → `[]` | `test_ranking_limits_and_edge_cases` |
| E24 | suggest | d = 0 (exact only) | → `[cat]` | `test_ranking_limits_and_edge_cases` |
| E25 | suggest | No match, empty dictionary, empty query | → `[]` | `test_ranking_limits_and_edge_cases` |
| E26 | suggest | Short query: `len - d` < 0 clamps to 0 | `"a"`, d=2 → `[a, an, cat]` | `test_short_query_clamps_length_range` |
| E27 | suggest | Several misspellings all get suggestions | `helo, thier, hourse, knwo` | `test_multiple_misspellings` |
| E28 | suggest | 10 lookups on 50,084 words < 2 s | measured < 0.01 s | `test_large_dictionary_performance` |
| E29 | suggest_brute_force | k = 0 or negative | → `[]` | `test_brute_force_non_positive_limit` |
| E30 | suggest | Optimized == brute force | 30 random dictionaries × 20 queries × 4 (d, k) | `test_suggest_matches_brute_force` |
| E31 | suggest | Concurrent calls from 8 threads return identical results | 50,084 words, 8 × 250 queries | `test_concurrent_suggest_is_consistent` |

Not tested (by design): the dictionary changing after `Checker` is built (the length index would be stale).

**Coverage AI prompt** (only what the original tests miss)
```text
The original tests, uncommented and with the ???? values filled in, cover 89% of the solution
(checker.py 79%, distance.py 95%). Please add tests only for what they miss, then confirm 100%.
Lines and branches the original tests never reach:
1. checker.py suggest, max_suggestions <= 0 guard: suggest("cat", max_suggestions=0) and -1 -> [].
2. checker.py suggest_brute_force (new method, never called): k <= 0 -> [], and it must return the same
   list as suggest on random dictionaries and queries for several (max_distance, max_suggestions).
3. distance.py bounded_compute, length-gap early return (suggest pre-filters by length, so only a direct
   call reaches it): bounded_compute("a", "abcd", 2) -> 3.
4. distance.py closest_words, a candidate farther than max_distance is dropped:
   closest_words("cat", {"cart": 1, "carts": 1}, 1) -> [("cart", 1, 1)].
Behavior the original tests don't check, even where lines are covered:
5. bounded_compute caps at max_distance + 1 without the early exit: ("bac", "ccccb", 2) -> 3; early exit:
   ("aaaa", "bbbb", 1) -> 2; and it equals min(compute, max_distance + 1) on random pairs.
6. Ties on equal frequency go alphabetical: closest_words("rat", {"hat": 5, "bat": 5}, 1) -> bat, hat;
   suggest("cat") on {cat:10, bat:30, hat:30, cart:99, dog:5} -> [cat, cart, bat, hat].
7. Short query clamps the length range at 0: suggest("a", max_distance=2) on {a:1, an:2, cat:3, cart:4}
   -> [a, an, cat]. Also max_suggestions larger than the matches returns all of them.
Run: python3 -m coverage run --branch -m unittest <test files>, then coverage report -m for distance.py and
checker.py. Line and branch coverage must be 100%. Add tests only; don't change the solution code.
```

## 7. Gotchas
- Ties: frequency **descending** (`-freq`); AI assistants often sort it ascending.
- `bounded_compute` must cap its return at `d + 1` even when the early exit doesn't fire.
- `range(len - d, len + d + 1)`: the upper bound is exclusive, and clamp the lower bound at 0.
- The length index goes stale if the dictionary changes after `Checker` is built.
- Check by hand: "teh" → "the" is distance **2** (no transposition in Levenshtein), and an exact match ranks first.
