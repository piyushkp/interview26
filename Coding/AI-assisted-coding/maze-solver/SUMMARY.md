# Maze Solver — Summary

## 1. Problem
`Maze` models a grid of walls `#`, open cells `.`, a start `S`, an end `E` and one-way cells `>` / `<`, and has two
bugs. Implement `Solver.solve()` to return a path of positions from S to E (or `None`), fast enough for a 150×150 maze
in under 1 s. **Pattern:** graph search. Each walkable cell is a node, each legal move is an edge, every move costs one step.

1. Run main and the tests; uncomment the given tests (baseline: 6 pass).
2. Fix the two `Maze` bugs and fill in the `????` values (`test_maze.py` passes).
3. Implement `solve()` (simple, directional and anywhere-start tests pass).
4. Optimize: the medium, large and huge timing tests pass.

## 2. Bugs
| # | Symptom | Original line | Solution line | Old code → New code |
|---|---|---|---|---|
| 1 | `Maze(["#S..E#", ...])` raises `ValueError: No S found`, expected start `(0, 1)` | `maze.py:31` (`_find_cell`) | `maze.py:37` (fix comment at 33) | `for r in range(1, self._rows):` → `for r in range(self._rows):` |
| 2 | Blocked maze returns a 7-cell path that walks right into `<`, expected `None` | `maze.py:69` (`is_valid_move`) | `maze.py:82-87` (fix comment at 77) | `return True` → check the move's direction against `>` / `<` on both the cell left and the cell entered, then `return True` |

**Bug 1, root cause:** the scan starts at row 1, so an S or E in the top row is never found and the constructor
raises. Start the scan at row 0.

**Bug 2, root cause:** `is_valid_move` takes `from_pos` but never uses it, so one-way cells act like open floor.
A `>` cell may only be entered and left moving right, a `<` cell only moving left.

`????` values:
| Original line | Old | New |
|---|---|---|
| `test_maze.py:82` | `expected = "????"` | `expected = "*"` (one value is checked against both S and E, so the path is drawn over both) |
| `test_maze.py:93` | `expected = "????"` | `expected = Position(0, 1)` |
| `test_solver.py:57` | `expected_length = "????"` | `expected_length = 9` |
| `test_solver.py:63` | `expected = "????"` | `expected = None` (the only way down crosses `<` moving right) |
| `test_solver.py:72` | `expected_length = "????"` | `expected_length = 5` |

## 3. Brute force
**Algorithm:** backtracking, which walks every path that never repeats a cell and keeps the shortest.

**AI prompt:**
```text
Solve this with backtracking: from the start, walk every simple path using get_neighbors, so one-way cells
are respected, and undo each step after exploring it. Keep the shortest path that reaches the end, or
return None if none does.
```

**Data structures:**
- list: the cells on the path I'm walking now
- set: the same cells, so I can check "already on my path" quickly
- list: the shortest full path found so far

**Approach:** I will start at S and try every move that doesn't revisit a cell on my current path. When I reach E,
I keep the path if it's the shortest so far. Then I step back and try the next move. Every path is tried, so the
shortest one is found, but an open 6×6 room already takes 103 s.

```text
def solve_brute_force():
    best = none
    explore(start)
    return best

def explore(pos):
    add pos to path and on_path
    if pos is the end:
        if best is none or path is shorter: best = copy of path
    else:
        for each neighbor not on_path:          # get_neighbors respects one-way cells
            explore(neighbor)
    remove pos from path and on_path            # undo, so other paths can use it
```
Time **O(P·L)**, space **O(V)** recursion depth. Bottleneck: the number of simple paths grows exponentially.

*Where:* P = simple paths from S, L = cells on a path, V = walkable cells.

## 4. Optimal
**Algorithm:** breadth-first search (BFS), which explores one step further at a time, so it reaches E by a shortest path first. It fits because every move costs the same.

**AI prompt:**
```text
Solve this with BFS, treating each open cell as a node linked to the cells get_neighbors returns, since
every move costs one step. Use a queue and a parent map, marking cells when queued. Return the path from
start to end, as short as the brute force's, or None if the end is unreachable.
```

**Data structures:**
- queue: hands me cells in order of distance from S
- dictionary: each cell → the cell I came from; it is also my "already seen" set

**Approach:** I will visit each cell only once. First, I explore cells in rings by distance, so the first time I
reach E is by a shortest path. Second, I mark a cell as seen when I add it to the queue, so no cell is queued twice.
Third, I store where each cell came from, so I can rebuild the path by walking back from E. It gives a path as short
as the brute force's, and solves the 150×150 maze in 0.11 s.

**Key insight:** the maze is a graph where every move costs one step, so BFS finds the shortest path in one pass.

```text
def solve():
    parent = {start: none}
    queue = [start]
    while queue:
        pos = take from the front of queue
        if pos is the end: return walk parent links back from pos, reversed
        for each neighbor of pos not in parent:  # mark when queued, not when popped
            parent[neighbor] = pos
            add neighbor to the back of queue
    return none                                  # end can't be reached
```
Time **O(V + E)**, space **O(V)**.

*Where:* V = walkable cells reachable from S (at most rows × columns), E = legal moves (at most 4V).

## 5. Complexity
| | Time | Space |
|---|---|---|
| Brute force | O(P·L), exponential | O(V) |
| Optimal (BFS) | O(V + E) | O(V) |

*Where:* P = simple paths from S, L = cells on a path, V = walkable cells, E = legal moves.

Measured (best of 5): open room 4×4 / 5×5 / 6×6: brute force **0.006 s / 0.47 s / 103 s**, BFS **< 0.3 ms**. Medium maze
1.07 ms → 0.34 ms. BFS on huge mazes: 75×75 **27 ms** (limit 0.3 s), 100×100 **48 ms** (0.5 s), 150×150 **108 ms** (1.0 s),
300×300 **434 ms**. Every huge-maze path equals the shortest possible length (Manhattan distance + 1).

## 6. Non-coding answers
- **How does the runtime grow?** BFS looks at each cell once, so a maze 4 times bigger takes about 4 times longer. The brute force gets 80 to 220 times slower each time an open room grows by one row and column.
- **Why BFS and not DFS?** DFS uses less memory but returns any path, not the shortest. BFS keeps the whole frontier to guarantee the shortest path.
- **What if moves had different costs, like mud cells?** BFS is no longer enough. I'd switch to Dijkstra's with a min-heap, after checking no cost is negative. The return type stays the same.
- **What does the data tell me?** The huge mazes' best paths are as short as possible, so A*, which aims straight at E using the Manhattan distance, would explore far fewer cells.

## 7. Tests added
**One-line coverage AI prompt**
```text
Review maze.py and solver.py against all test files and add any missing tests so that every line, branch and edge case (missing S or E, empty grid, moves off the grid, one-way cells entered or left the wrong way, walls in a rendered path, unreachable end, start next to end) is covered at 100% line and branch coverage, add non-functional tests for large input (a 300×300 maze under 2 s, BFS matching the brute force's path length on random small mazes) and for concurrent calls from multiple threads, then tell me whether the solver is thread-safe (and what would break it) and what CPU and memory VM I need to run it in production, using measured memory per cell and latency per solve, all without changing the solution code.
```
Expected answers (measured):
- **Thread-safe:** `solve` keeps its queue and parent map in locals and only reads the `Maze`, which is never changed (`render_with_path` copies the grid). 8 threads × 5 solves on one 100×100 maze gave identical paths (`test_concurrent_solves_are_consistent`). It would break if the grid were edited during a solve. The GIL means threads don't speed up this CPU-bound search, so scale with processes.
- **Sizing:** the `Maze` takes about 9 B per cell; a solve peaks at about 75 B per cell (1.6 MB for 150×150). One 150×150 solve takes 108 ms (about 9 solves/s per core); 100×100 takes 48 ms (about 21/s). A **2 vCPU / 2 GB** VM is plenty; cores ≈ target solves/s ÷ per-core rate, memory ≈ workers × (about 30 MB Python runtime + 85 B per cell).

Uncommented all 9 given solver tests (including 3 assert lines in `test_solve_simple_maze`) and both maze tests, and
filled in the 5 `????` values. The original tests alone cover **82%** of the solution (maze.py 95%, solver.py 62%); with
the tests added, `./run.sh coverage` reports **100% line and branch coverage** of `maze.py` and `solver.py` (31 tests).

**Gaps in the original tests, exposed by our implementation**
- **One-way cells are barely tested.** The right-only test passes even with Bug 2, because both routes are 9 cells. Only the blocked test catches it, and only for `<` entered moving right. Covered by M4, M5, X1.
- **No test checks that a path is legal.** The given tests check only the two endpoints and two lengths, so a solver that walks through walls would pass every timing test. Covered by V8, V9, X1 (each step is one legal move, no cell repeats).
- **No test checks the path is shortest on big mazes.** A DFS that returns any path passes all timing tests. Covered by V9 (length equals the Manhattan bound) and X1.
- **`solve_brute_force` is never called** (`solver.py:55-74`), so nothing proves BFS finds the shortest path. Covered by X1, X2.
- **Missing S or E, an empty grid, moves off the grid and walls in a rendered path are never exercised** (`maze.py:41`, `maze.py:71`, the wall branch of `render_with_path`). Covered by M3, M6, M8.
- **No plain walled-in case:** the only unreachable test depends on a one-way cell. Covered by V7.

Run against the original `maze.py`, the new tests catch both intern bugs (9 tests fail). They found no bug in the new solver.

| ID | Area | Scenario | Example → expected | Covering test |
|---|---|---|---|---|
| M1 | `_find_cell` | S in the top row (**Bug 1**) | `#S..E#` → `Position(0, 1)` | `test_find_start_in_top_row` |
| M2 | `_find_cell` | E in the top row, S in the last row | → `(0, 1)`, `(2, 2)` | `test_find_cells_on_any_row` |
| M3 | `Maze()` | No S, no E, empty grid | → `ValueError` | `test_missing_start_or_end_raises` |
| M4 | `is_valid_move` | `>`: enter or leave only moving right (**Bug 2**) | enter from left ✓; from right, from above ✗; leave right ✓, down or left ✗ | `test_right_only_cell` |
| M5 | `is_valid_move` | `<`: mirror image (**Bug 2**) | enter from right ✓; from left, from below ✗; leave left ✓, right ✗ | `test_left_only_cell` |
| M6 | `is_valid_move` | Moves off every edge of the grid | → invalid; corner has 2 neighbors | `test_moves_off_the_grid_are_invalid` |
| M7 | `get_neighbors` | Wall next to S | wall not a neighbor | `test_get_neighbors_near_wall` |
| M8 | `render_with_path` | Path drawn over S and E; walls kept; maze unchanged; empty path | `#*#*#`; `render()` unchanged | `test_render_with_path_preserves_start_end`, `test_render_with_path_keeps_walls_and_original` |
| V1 | `solve` | Simple maze | path from S to E | `test_solve_simple_maze` |
| V2 | `solve` | Right-only passage | → 9 cells | `test_directional_passage_right_only` |
| V3 | `solve` | Only route crosses `<` the wrong way (**Bug 2**) | → `None` | `test_directional_passage_blocked` |
| V4 | `solve` | S not in a corner | → 5 cells | `test_anywhere_start_end` |
| V5 | `solve` | Given limits | medium < 0.5 s; large 20/25/30; huge 75 < 0.3 s, 100 < 0.5 s, 150 < 1 s | given timing tests |
| V6 | `solve` | S next to E | → 2 cells | `test_start_next_to_end` |
| V7 | `solve` | S walled in | → `None` | `test_walled_in_start_returns_none` |
| V8 | `solve` | Given mazes: legal and shortest | lengths 5, 9, 26, 9, 5 | `test_given_mazes_give_valid_shortest_paths` |
| V9 | `solve` | Big mazes reach the Manhattan bound | 20×20 → 39, 30×30 → 59, 75×75 → 149 | `test_big_mazes_reach_the_shortest_possible_length` |
| V10 | `solve` | S in the top row (**Bug 1**) | → 4 cells along row 0 | `test_start_in_top_row` |
| X1 | `solve` vs brute | 1,500 random mazes with walls and one-way cells | both `None`, or both legal with equal length | `test_bfs_matches_brute_force` |
| X2 | `solve_brute_force` | Blocked; directional; small; adjacent; wall between | `None`, 9, 9, 2 cells, `None` | `test_brute_force_edge_cases` |
| X3 | `solve` | Scale: 300×300 | legal path in < 2 s (measured 0.43 s) | `test_scale_300x300` |
| X4 | `solve` | 8 threads × 5 solves on one maze | identical paths; maze unchanged | `test_concurrent_solves_are_consistent` |

Not tested: a `from_pos` that is off the grid (only `get_neighbors` calls `is_valid_move`, always from a real cell),
and the brute force on mazes with paths longer than Python's recursion limit (it is a test-only reference).

**Coverage AI prompt**
```text
Using only the original tests (uncommented, ???? filled in), maze.py and solver.py have 82% line and branch
coverage (maze.py 95%, solver.py 62%). Please add tests only for what they miss, then confirm 100%.

Lines and branches never reached:
1. maze.py _find_cell raising ValueError: a grid with no S, one with no E, and an empty grid [].
2. maze.py is_valid_move returning False for a move off the grid: from a corner of ["S.", ".E"], moving
   up, left, down or right off the edge; the corner (1,1) has exactly 2 neighbors.
3. maze.py render_with_path skipping a wall: for ["#####", "#S#E#", "#####"] and the path (1,1),(1,2),(1,3),
   row 1 renders "#*#*#", and render() is unchanged afterwards.
4. solver.py solve_brute_force (never called): blocked directional maze -> None, directional maze -> 9 cells,
   ["SE"] -> [(0,0), (0,1)], ["S#E"] -> None.

Behavior the original tests don't check, even where lines are covered:
5. A ">" cell can be entered and left only moving right, and "<" only moving left: entering ">" from above
   or leaving it downward is invalid, and its neighbors list is just the cell to its right.
6. Every solved path is legal: starts at S, ends at E, each step is one up/down/left/right move that
   is_valid_move allows, and no cell repeats.
7. solve returns a shortest path: on 1,000+ random small mazes with walls and one-way cells, its length
   equals solve_brute_force's (or both are None); on large and huge mazes the length equals the
   Manhattan distance from S to E plus 1.
8. A start fully surrounded by walls returns None; a start next to the end returns 2 cells.

Run: python3 -m coverage run --branch -m unittest <test files>, then coverage report -m for maze.py and
solver.py. Line and branch coverage must be 100%. Add tests only; don't change the solution code.
```

## 8. Gotchas
- **Check both cells of a move for one-way rules.** An AI fix often checks only the cell being entered; then stepping down out of a `>` slips through (M4).
- **Mark cells when queued, not when popped.** Marking on pop queues the same cell many times (184,755 pushes instead of 100 on an open 10×10 grid). Check this line in the AI's BFS first.
- **The render test's name says "preserves", but its single expected value forces `"*"`.** Don't "fix" `render_with_path` to keep S and E, or the given test fails; raise the mismatch with the interviewer.
- **Return `None`, not `[]`, when E is unreachable,** and return the path from S to E, not reversed.
- **The brute force is only a test reference.** It explodes past a 5×5 open room and hits Python's recursion limit on paths over about 1,000 cells.
