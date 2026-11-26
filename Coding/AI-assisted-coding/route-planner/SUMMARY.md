# Route Planner — Summary

## 1. Problem
`Network` stores stations and connections (travel time, line, optional one-way) and has two bugs. Implement
`Planner.find_route` (fastest route by total time, with a 5-minute penalty per line change) and
`find_route_with_max_transfers`, fast enough for a 60×60 grid in under 2 s. **Pattern:** graph search with weighted
edges, so Dijkstra's algorithm. A ride's price depends on the line you arrived on, so each node is a (station, line) pair.

1. Run main and the tests; uncomment the given tests (baseline: 3 pass, main prints "No route found").
2. Fix the two `Network` bugs and fill in the `????` values (`test_network.py` passes).
3. Implement `find_route` (`test_find_shortest_route` passes: 7 minutes).
4. Optimize: the transfer-limit tests and the large-network timing test pass.

## 2. Bugs
| # | Symptom | Original line | Solution line | Old code → New code |
|---|---|---|---|---|
| 1 | One-way A→B: `get_neighbors("B")` is `["A"]`, expected `[]`; Downtown → Uptown rides the Uptown-only Loop backwards in 6 min, expected 7 | `network.py:33-35` (`add_connection`) | `network.py:40-43` (fix comment at 34) | always add the reverse connection → `if not one_way:` add it |
| 2 | Staying on Red costs 3 + 5 = 8, expected 3; Central → Airport takes 13 min, expected 7 | `network.py:41` (`get_travel_cost`) | `network.py:54` (fix comment at 50) | `if current_line is not None:` → `if current_line is not None and current_line != connection.line:` |

**Bug 1, root cause:** `add_connection` always adds the reverse direction and ignores `one_way`, so riders can go
against a one-way line. Add the reverse connection only when the connection is two-way.

**Bug 2, root cause:** the penalty is for changing lines, but it is charged on every ride after the first, even on
the same line. Charge it only when the new ride's line differs from the current one.

`????` values:
| Original line | Old | New |
|---|---|---|
| `test_network.py:35` | `expected = "????"` | `expected = []` |
| `test_network.py:43` | `expected = "????"` | `expected = 3` |

## 3. Brute force
**Algorithm:** backtracking, which walks every route that never revisits a station and keeps the fastest.

**AI prompt:**
```text
Solve this with backtracking: walk every route that never revisits a station, trying every connection out
of each station, and undo each step after exploring it. Add ride times plus 5 minutes per line change, keep
the fastest route, fewer transfers on a tie, and return None if none fits.
```

**Data structures:**
- list: the stations on the route I'm walking now
- set: the same stations, to check "already on my route" quickly
- tuple: the best minutes, transfers and stations so far

**Approach:** I will start at the first station and try every connection that doesn't revisit a station. I add the
ride time, plus 5 minutes when the line changes. At the end station, I keep the route if it's faster, or as fast with
fewer transfers. A best route never needs a loop, because cutting a loop out never adds time or transfers, so this is
exhaustive. A 5×5 grid takes 25 ms, but 6×6 takes 5.2 s.

```text
def brute_force(start, end, max_transfers):
    best = none
    explore(start, no line, 0 minutes, 0 transfers)
    return best

def explore(station, line, minutes, transfers):
    if station is end:
        if within max_transfers and (minutes, transfers) beats best: best = this route
        return
    for each connection out of station to a station not on the route:
        explore(next, its line, minutes + ride cost, transfers + 1 if the line changed)   # undo after
```
Time **O(P·L)**, space **O(V)** recursion depth. Bottleneck: the number of simple routes grows exponentially.

*Where:* P = simple routes from the start, L = stations on a route, V = stations.

## 4. Optimal
**Algorithm:** Dijkstra's algorithm over (station, line) states, because every ride time and the penalty are never negative; with a limit, the state also carries the transfers used.

**AI prompt (`find_route`):**
```text
Solve this with Dijkstra's algorithm on (station, current line) states, since ride times and the 5-minute
penalty are never negative. Use a min-heap ordered by time, then transfers, skipping stale entries. Return
None for unknown or unreachable stations, zero minutes when start equals end, and match the brute force.
```

**AI prompt (`find_route_with_max_transfers`):**
```text
Extend that Dijkstra's search to (station, line, transfers used) states, so a slower arrival with fewer
transfers is never thrown away, and skip any move that goes over max_transfers. Return None if
max_transfers is negative or no route fits, and match the brute force's time and transfers.
```

**Data structures:**
- min-heap: always hands me the cheapest state to settle next
- dictionary: each state → its cheapest (minutes, transfers) so far
- dictionary: each state → the state it came from, to rebuild the stations

**Approach:** I will settle states from cheapest to most expensive. First, a state is a station plus the line I
arrived on, because the next ride's price depends on that line. Second, the heap hands me the cheapest state, so the
first time I pop the end, nothing can beat it. Third, I skip heap entries that a cheaper visit already replaced.
Fourth, with a transfer limit, I also keep the transfers used in the state, so a slower arrival with fewer transfers
survives. It matches the brute force and solves the 60×60 map in 9 ms.

**Key insight:** the price of the next ride depends on the line you're on, so the node is a station plus a line, not the station alone.

```text
def dijkstra(start, end, max_transfers):
    if start or end is unknown: return none
    heap = [(0 minutes, 0 transfers, start with no line)]
    while heap:
        minutes, transfers, state = pop the cheapest
        if a cheaper cost is already saved for state: skip     # stale entry
        if state's station is end: return route from parent links
        for each connection out of the station:
            add 1 transfer if the line changes; skip if over max_transfers
            next = (destination, connection line, transfers if limited)
            if (new minutes, new transfers) beats next's saved cost: save it, set parent, push
    return none
```
Time **O(E·T log(E·T))** without a limit, **O(E·T·K log(E·T·K))** with one; space O(E·T) and O(E·T·K).

*Where:* E = connections, T = lines reaching one station, K = max_transfers + 1.

## 5. Complexity
| | Time | Space |
|---|---|---|
| Brute force | O(P·L), exponential | O(V) |
| Optimal (Dijkstra's on states) | O(E·T log(E·T)); × K with a transfer limit | O(E·T); × K with a limit |

*Where:* P = simple routes, L = stations on a route, V = stations, E = connections, T = lines per station, K = max_transfers + 1.

Measured (best of 3): grid 4×4 / 5×5 / 6×6: brute force **0.3 ms / 25 ms / 5.2 s**, Dijkstra's **< 0.1 ms**. Large maps,
`find_route` / with at most 3 transfers: 50×50 **6 / 17 ms**, 60×60 **9 / 25 ms** (limit 2 s), 150×150 **61 / 181 ms**,
300×300 **280 / 811 ms**.

## 6. Non-coding answers
- **How does the runtime grow?** Each state is settled once, so a map 4 times bigger takes about 4–5 times longer. A transfer limit splits every state by transfers used, so it runs about 3 times slower.
- **Why not key the search by station only?** It is smaller but wrong. It settles a station on the first cheap arrival and forgets the line, so the coupling map gives 8 minutes instead of 4.
- **What if transfers had different prices, like free same-platform changes?** Pass the two lines to the cost function. Dijkstra's still works as long as no price is negative. Add a `lines` list to `Route` if callers need each leg's line, and keep the old fields.
- **What does the data tell me?** Each row and column of the large maps is one line, so a station has at most 2 lines, and the state count stays about 2 per station. Capping the 150×150 trip at 3 transfers costs only 4 more minutes (1,185 vs 1,181).

## 7. Tests added
**One-line coverage AI prompt**
```text
Review network.py and planner.py against all test files and add any missing tests so that every line, branch and edge case (one-way connections, same-line and first-ride costs, unknown or unreachable stations, start equals end, negative or zero transfer limits, parallel lines, time ties, the line-coupling and transfer-trap maps) is covered at 100% line and branch coverage, add non-functional tests for large input (a 300×300 map under 3 s, Dijkstra's matching the brute force on random small networks) and for concurrent calls from multiple threads, then tell me whether the planner is thread-safe (and what would break it) and what CPU and memory VM I need to run it in production, using measured memory per station and latency per route, all without changing the solution code.
```
Expected answers (measured):
- **Thread-safe:** the search keeps its heap, costs and parent links in locals and only reads the `Network`. 8 threads × 5 limited searches on an 80×80 map gave identical routes (`test_concurrent_routes_are_consistent`). It would break if connections were added during a search. The GIL means threads don't speed up this CPU-bound search, so scale with processes.
- **Sizing:** the `Network` takes about 650 B per station (55 MB for 300×300); a search peaks at about 400 B per station. A 150×150 route takes 61 ms (about 16 routes/s per core); 60×60 takes 9 ms (about 110/s). A **2 vCPU / 2 GB** VM is plenty; cores ≈ target routes/s ÷ per-core rate, memory ≈ workers × (network + about 30 MB runtime).

Uncommented the 4 assert lines in `test_find_shortest_route`, the 3 planner tests and the 2 network tests, and filled
in both `????` values. The original tests alone cover **74%** of the solution (network.py 97%, planner.py 66%); with the
tests added, `./run.sh coverage` reports **100% line and branch coverage** of `network.py` and `planner.py` (28 tests).

**Gaps in the original tests, exposed by our implementation**
- **The trap maps exist but no given test uses them.** A search keyed by station only (8 instead of 4), or by (station, line) under a limit (`None` instead of 14), passes every given test. Covered by P10, P11, X1, X2.
- **The limit tests never change the answer.** They use 0 and −1 on a map whose fastest route already has 0 transfers. Covered by P11, P14, X1.
- **No test checks a route's stations or transfers,** only the endpoints and total time, so a route that reports a time its stations can't achieve would pass. Covered by the route checker in P5, P14, P15, X1.
- **Unknown stations, unreachable ends, start equals end, parallel lines and time ties are never tried** (`planner.py:62`, `planner.py:85`). Covered by P6–P8, P12, P13.
- **`find_route_brute_force` is never called** (`planner.py:105-130`), so nothing proves Dijkstra's finds the best route. Covered by X1, X2.
- **`get_all_stations` is never called** (`network.py:62`). Covered by N5, N6.

Run against the original `network.py`, the new tests catch both bugs (13 tests fail). X1 also caught a real bug in my
own route checker: it ignored the transfer limit, so it rejected a correct 12-minute, 0-transfer route under a limit of 0.

| ID | Area | Scenario | Example → expected | Covering test |
|---|---|---|---|---|
| N1 | `add_connection` | One-way A→B (**Bug 1**) | B's neighbors → `[]` | `test_one_way_neighbors` |
| N2 | `get_travel_cost` | Same line (**Bug 2**) | Red after Red, 3 → 3 | `test_travel_cost_same_line` |
| N3 | `add_connection` | One-way plus a separate two-way line back | A: Express and Local; B: Local only | `test_one_way_keeps_the_forward_direction` |
| N4 | `get_travel_cost` | First ride; line change | 3; 3 + 5 | `test_travel_cost_first_ride_and_line_change` |
| N5 | `Network` | Unknown station; station added twice | `[]`, False; one station | `test_unknown_and_lone_stations` |
| N6 | `add_connection` | One-way still adds both stations | `{A, B}` | `test_one_way_adds_both_stations` |
| P1 | `find_route` | Test map, Central → Airport | 7 | `test_find_shortest_route` |
| P2 | limited | Standard map, max 0 transfers (catches **Bug 1**) | 7 | `test_transfer_limit` |
| P3 | limited | Negative limit | `None` | `test_no_route_within_transfer_limit` |
| P4 | `find_route` | 50×50, 60×60, 50×50 maps | route in < 2 s | `test_efficiency_on_large_network` |
| P5 | `find_route` | Route details | Central, Mall, Stadium, Airport; 0 transfers | `test_test_map_route_details` |
| P6 | both | Start equals end; with limit −1 | `[Park]`, 0, 0; `None` | `test_start_equals_end` |
| P7 | both | Unknown start or end | `None` | `test_unknown_station` |
| P8 | `find_route` | Only against a one-way; island station | `None`; `None` | `test_unreachable` |
| P9 | `find_route` | One-way Loop (**Bug 1**) | Downtown→Uptown 7; Uptown→Downtown 6 | `test_one_way_respected_in_routes` |
| P10 | `find_route` | Line-coupling trap | Start, B, End: 4 | `test_line_coupling_trap` |
| P11 | both | Transfer trap | no limit 13/2; max 2 → 13; max 1 → 14/1; max 0 → `None` | `test_transfer_trap` |
| P12 | `find_route` | Two lines between the same stations | 4, 0 transfers | `test_parallel_lines_between_two_stations` |
| P13 | `find_route` | Time tie | fewer transfers wins: A, D, C | `test_time_tie_prefers_fewer_transfers` |
| P14 | both | 150×150 with and without a limit | 1,181/4; max 3 → 1,185/3, < 2 s | `test_large_network_with_transfer_limit` |
| P15 | both | Every route's numbers match its stations | 4 maps, with and without a limit | `test_given_maps_routes_are_honest` |
| X1 | vs brute force | 1,500 random networks, limits −1 to 3 or none | same (minutes, transfers) or both `None` | `test_dijkstra_matches_brute_force` |
| X2 | brute force | Traps, limits, unknown, start equals end | 4; 13/2; 14/1; `None`; `[A]` | `test_brute_force_edge_cases` |
| X3 | scale | 300×300 map | honest route in < 3 s (measured 0.28 s) | `test_scale_300x300` |
| X4 | threads | 8 threads × 5 limited searches | identical routes | `test_concurrent_routes_are_consistent` |

Not tested: negative travel times (the code doesn't reject them, and Dijkstra's would be silently wrong) and the
brute force on maps larger than about 6×6.

**Coverage AI prompt**
```text
Using only the original tests (uncommented, ???? filled in), network.py and planner.py have 74% line and
branch coverage (network.py 97%, planner.py 66%). Please add tests only for what they miss, then confirm 100%.

Lines and branches never reached:
1. network.py get_all_stations: after add_connection("A", "B", 4, "Express", one_way=True) it is {"A", "B"}.
2. planner.py unknown station: find_route("Central", "Moon") and with max_transfers=3 -> None.
3. planner.py no route: for a one-way A->B, find_route("B", "A") -> None; an island station -> None.
4. planner.py find_route_brute_force (never called): coupling map -> 4 minutes; transfer trap -> 13 minutes
   and 2 transfers, max 1 -> 14 and 1, max 0 or -1 -> None; start equals end -> ["A"].

Behavior the original tests don't check, even where lines are covered:
5. The line-coupling map Start -> End is 4 minutes (Start, B, End), not 8.
6. The transfer-trap map under max_transfers=1 is 14 minutes with 1 transfer, not None.
7. Each route's total_time and transfers equal the best way to ride exactly its stations within the limit.
8. Time ties go to fewer transfers; two lines between the same stations pick the cheaper overall.
9. On 1,000+ random small networks with one-way connections and limits -1 to 3, both planner methods
   match find_route_brute_force's (minutes, transfers), or both return None.

Run: python3 -m coverage run --branch -m unittest <test files>, then coverage report -m for network.py and
planner.py. Line and branch coverage must be 100%. Add tests only; don't change the solution code.
```

## 8. Gotchas
- **Key the search by (station, line), not station.** A station-only search settles B on the cheap Red arrival and returns 8 instead of 4 on the coupling map. Check this line first in the AI's code.
- **With a transfer limit, add the transfers used to the state.** Otherwise the transfer trap returns `None` instead of 14 minutes.
- **No penalty on the first ride or on the same line.** Make sure the AI prices each ride with `get_travel_cost` and the line you arrived on.
- **Put a counter in the heap entries.** On a time and transfer tie, the heap compares the states, and a `None` line next to a string raises `TypeError`.
- **Check the end when it's popped, not when it's pushed, and skip stale entries.** A negative limit returns `None`, even when start equals end.
