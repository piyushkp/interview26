# Task Scheduler — Summary

## 1. Problem
`Scheduler` stores build tasks with durations and dependencies and has two bugs. Implement
`Optimizer.compute_execution_order()` (an order where every task follows its dependencies) and
`parallel_schedule(num_workers)` (start and end times on that many workers, and the total time).
**Pattern:** topological sort (Kahn's algorithm) for the order; greedy list scheduling by critical path for the workers.

1. Run main and the tests; uncomment the given tests (baseline: 4 pass; main prints an empty order and total time 0).
2. Fix the two `Scheduler` bugs and fill in the `????` values (`test_scheduler.py` passes).
3. Implement `compute_execution_order` (the three order tests pass).
4. Optimize: the three parallel-schedule tests pass (8, 26 and 26).

## 2. Bugs
| # | Symptom | Original line | Solution line | Old code → New code |
|---|---|---|---|---|
| 1 | `a → c → b → a` is accepted, expected `CycleError` | `scheduler.py:24-29` (`_check_cycles`) | `scheduler.py:37-50` (fix comment at 29) | compare each task with its direct dependencies → Kahn's algorithm: any task never freed is on a cycle |
| 2 | `earliest_start("c", {"a": 3, "b": 5})` is 3, expected 5 | `scheduler.py:50` (`earliest_start`) | `scheduler.py:75` (fix comment at 72) | `min(...)` → `max(...)` |

**Bug 1, root cause:** the check only asks "does my dependency depend on me?", so it finds two-task cycles but misses
`a → c → b → a`. Peel off tasks whose dependencies are all done; anything left over is stuck on a cycle.

**Bug 2, root cause:** a task needs all its dependencies finished, so it waits for the latest one. `min` lets `c`
start at 3 while `b` is still running until 5. Use `max`.

`????` values:
| Original line | Old | New |
|---|---|---|
| `test_scheduler.py:47` | `raises_error = "????"` | `raises_error = True` |
| `test_scheduler.py:62` | `self.assertEqual(result, "????")` | `self.assertEqual(result, 5)` |

## 3. Brute force
**Algorithm:** backtracking over every valid task order, scheduling each order greedily on the workers and keeping the fastest.

**AI prompt:**
```text
Solve this with backtracking over every valid task order, adding a task only once all its dependencies are
placed and undoing it after exploring. Schedule each order greedily on the workers and keep the shortest
total time; with no tasks, return zero and an empty timeline.
```

**Data structures:**
- list: the task order I'm building
- dictionary: how many unplaced dependencies each task still has
- heap: the running tasks by finish time, in the simulation

**Approach:** I will build every order that respects the dependencies, one task at a time, and undo each choice
after trying it. For each order, I fill free workers with the earliest task in that order whose dependencies are
done. I keep the order with the smallest total time. It's the best over all task orders with greedy filling, not
all schedules, and 10 tasks already take 2.1 s.

```text
def brute_force(workers):
    best = none
    explore([])
    return best

def explore(order):
    if order has every task:
        keep simulate(order, workers) if its total time is the smallest so far
        return
    for each task whose dependencies are all in order and isn't placed yet:
        explore(order + [task])                         # undo after
```
Time **O(O·(V log V + E))**, space **O(V + E)**. Bottleneck: the number of valid orders grows like V!.

*Where:* O = valid task orders, V = tasks, E = dependency links.

## 4. Optimal
**Algorithm:** greedy list scheduling by critical path, which always starts the ready task with the longest chain of work still behind it.

**AI prompt:**
```text
Step 1: get the execution order with Kahn's algorithm, then give each task a weight, its duration plus the
largest weight among the tasks that depend on it. Build the dependents map from depends_on, then fill
weights by walking that order backward, so no recursion is needed.

Step 2: implement parallel_schedule with greedy list scheduling, tracking readiness like Kahn's algorithm
(a task is ready when its unfinished-dependency count hits zero): a max-heap of ready tasks by weight, and
a min-heap of running tasks by finish time. Start tasks at the current time, and free every task finishing
at the same moment before refilling workers. Raise ValueError for fewer than one worker, and return 0 and
an empty timeline when there are no tasks; expect 8, 26 and 26 on the given tests.
```

**Data structures:**
- dictionary: each task's longest chain of durations to the end, its priority
- heap: hands me the ready task with the longest chain
- heap: running tasks by finish time, so I jump straight to the next finish

**Approach:** I will look at one order only, chosen well. First, I work out each task's longest chain to the end,
going backward through the execution order. Second, whenever a worker is free, it takes the ready task with the
longest chain, so the slowest chain never waits. Third, I jump from one finish time to the next instead of ticking
the clock. It matches the brute force on all three given builds, and schedules 3,000 tasks in 7 ms.

**Key insight:** the total time can't beat the longest chain of dependent work, so start that chain first; taking tasks in input order runs the four scans first and finishes at 38 instead of 26.

```text
def parallel_schedule(workers):
    if workers < 1: raise error
    chain = longest chain to the end for each task       # backward over the execution order
    ready = tasks with no dependencies, longest chain first
    while ready or running:
        while a worker is free and ready isn't empty:
            start the ready task with the longest chain now
        now = the next finish time
        free every task finishing now; add newly ready dependents
    return the last finish time, timeline
```
Time **O(V log V + E)**, space **O(V + E)**. Kahn's execution order alone is O(V + E).

*Where:* V = tasks, E = dependency links.

## 5. Complexity
| | Time | Space |
|---|---|---|
| Brute force | O(O·(V log V + E)), factorial | O(V + E) |
| Optimal (critical path) | O(V log V + E) | O(V + E) |

*Where:* O = valid task orders, V = tasks, E = dependency links.

Measured: brute force on random builds with 3 workers: 8 tasks **0.06 s**, 10 tasks **2.1 s** (stopped there). Critical path:
given builds **< 0.1 ms**, 3,000 tasks **7 ms**, 30,000 tasks **90 ms**. Brute force on the given builds: 8, 26, 26, the same.

## 6. Non-coding answers
- **How does the runtime grow?** The critical-path version touches each task and link once plus heap steps, so 10 times more tasks takes about 13 times longer. The brute force multiplies by the number of valid orders and hits 2 s at just 10 tasks.
- **Is the greedy always best?** No. Scheduling with dependencies on several workers has no known fast exact method. Greedy list scheduling is always within 2 − 1/W of the best, and it matched the brute force on 293 of 300 random builds.
- **What if workers had different speeds, or some tasks needed a special worker?** The `num_workers` contract becomes a list of workers with speeds or skills. The heap picks the worker that would finish soonest, and the timeline gains a worker field.
- **What does the data tell me?** In all three given builds, the longest chain equals the total time, so critical path reaches the best possible answer. The trap build hides a long chain behind a 1-minute setup task.

## 7. Edge cases
| ID | Area | Scenario | Example → expected | Covering test |
|---|---|---|---|---|
| S1 | `_check_cycles` | Three-task cycle (**Bug 1**) | `a → c → b → a` → `CycleError` | `test_transitive_cycle` |
| S2 | `earliest_start` | Several dependencies (**Bug 2**) | `{a: 3, b: 5}` → 5 | `test_earliest_start_multiple_deps` |
| S3 | `_check_cycles` | Self-dependency | `a → a` → `CycleError` | `test_self_dependency_is_a_cycle` |
| S4 | `_check_cycles` | Diamond is fine; a 4-cycle behind it isn't; unknown dependency | no error; `CycleError`; `ValueError` | `test_diamond_is_not_a_cycle_but_a_loop_behind_it_is` |
| S5 | `Scheduler` | No dependencies; a zero-duration dependency; ready tasks skip finished ones | 0; 3; `[b]`, `[c]` | `test_earliest_start_edges` |
| O1 | `compute_execution_order` | Given build: every task, dependencies first | 5 tasks, valid order | given order tests |
| O2 | `parallel_schedule` | Given builds | 8 (2 workers), 26 (3), 26 (2) | given schedule tests |
| O3 | `parallel_schedule` | Critical-path trap: input order would give 38 | 26 | `test_parallel_schedule_critical_path` |
| O4 | `parallel_schedule` | 1, 2, 3, 4 and 20 workers: valid, never overbooked; 1 worker = sum of durations | valid; 11 / 45 / 50 | `test_schedules_are_valid_for_any_worker_count` |
| O5 | `compute_execution_order` | Large build | every dependency comes first | `test_order_on_large_build_is_valid` |
| O6 | both | No tasks; zero workers | `[]`, `(0, {})`; `ValueError` | `test_empty_build_and_bad_worker_count` |
| X1 | vs brute force | 300 random builds, 0-minute tasks, 1–3 workers | brute ≤ greedy ≤ (2 − 1/W) × brute; both valid | `test_critical_path_vs_brute_force` |
| X2 | brute force | Given builds, empty, zero workers | 26, 8, `(0, {})`, `ValueError` | `test_brute_force_edge_cases` |
| X3 | scale | 3,000 tasks, 8 workers | valid in < 1 s (measured 7 ms) | `test_scale_3000_tasks` |

## 8. Gotchas
- **Start a task at the current time, not at `earliest_start`.** `earliest_start` only says when its dependencies allow it. My first version used it and double-booked a single worker (O4 and X1 caught it; the given tests didn't).
- **Pick the ready task by longest chain, not input order.** The trap build finishes at 38 instead of 26 otherwise.
- **Free every task that finishes at the same moment before filling workers again,** or a zero-duration task can delay its dependents.
- **Cycle checks must cover long cycles and self-dependencies.** Kahn's leftover count does both in one pass.
- **Don't call the greedy "optimal".** It's a heuristic; it's provably best only when the total equals the longest chain, as in all three given builds.
