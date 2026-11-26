# Kitchen Orders — Summary

## 1. Problem
Fix `Order.is_complete()`, then implement `Kitchen.schedule(order)` to assign every recipe step to a chef and a time so
recipe order, one-step-per-chef and one-chef-per-station all hold, and make it fast enough to hit each benchmark's
makespan (total finish time) and runtime limit.

## 2. Bugs
| # | Symptom | Original line | Solution line | Old code → New code |
|---|---|---|---|---|
| 1 | Order with one DONE and one PENDING dish is "complete" | `order.py:21` (`is_complete`) | `order.py:25` (fix comment at 21) | `any(dish.status == DishStatus.DONE ...)` → `all(...)` |

**Bug 1, root cause:** an order is complete only when *every* dish is done, but `any` returns True as soon as one is.
The given tests only use all-done or all-pending orders, so they all pass with the bug; `test_mixed_done_and_pending_is_not_complete` catches it.

No `????` tests in this problem.

## 3. Brute force
**Algorithm:** try every order of dishes (brute force), and fill in each order greedily, which means each step takes the best choice right now and never goes back.

**AI prompt:**
```text
Solve this by trying every order of the dishes and scheduling each one greedily: each step, in recipe
order, goes to the chef who would finish it first. Return the schedule that finishes soonest, or an
empty schedule if there are no dishes.
```

**Data structures:**
- dictionary: when each chef is free next
- dictionary: when each station is free next
- list: the schedule entries

**Approach:** I will try every order of the dishes. For each order, I cook the steps one by one. Each step goes to the chef who finishes it first, once the chef and station are free. I keep the order that finishes soonest. It finds the best result over all dish orders, but `deep_nine` takes 12.5 s and the limit is 2.5 s. Greedy alone would try just one order, which is fast but can miss the best one.

```text
def schedule_brute_force(order):
    for each ordering of order.dishes:                              # n! orderings
        keep simulate(ordering) if its makespan is the smallest so far
    return best

def simulate(dishes):
    chef_free, station_free = 0 for every chef and station
    for dish in dishes:
        ready = 0                                                   # end of the dish's previous step
        for station, base in dish.recipe.steps:
            chef = chef that finishes first, starting at max(ready, chef_free, station_free)
            add entry(dish, step, station, chef, start, end)
            chef_free[chef] = station_free[station] = ready = end   # never double-books
```
Time **O(n!·S·C)**, space **O(S)**.

*Where:* n = dishes in the order, S = total recipe steps, C = chefs.

## 4. Optimal
**Algorithm:** backtracking, which builds an order step by step and undoes choices to try others, with an early stop.

**AI prompt:**
```text
Solve this with branch-and-bound backtracking: dishes of the same recipe are interchangeable, so only
try distinct recipe sequences, schedule each greedily, and stop once one hits the lower bound. Match
the brute force's makespan; an empty order gives an empty schedule.
```

**Data structures:**
- dictionary: recipe → its dishes, so same dishes count as one choice
- the same two "free next" dictionaries in the simulator

**Approach:** I will try far fewer orders. First, I treat dishes of the same recipe as one choice, since swapping two burgers changes nothing. That cuts 362,880 orders to 1,260. Second, I work out the fastest finish time possible and stop once I reach it. Third, each step goes to the chef who is fastest at that station. It gives the same answer as the brute force in 0.2–14 ms.

**Key insight:** the grill is the slowest station, so the best order just keeps the grill busy.

```text
def schedule(order):
    groups = {recipe: [dishes]}      # same recipe = interchangeable
    lb = lower_bound(order.dishes)
    search([])                       # distinct recipe sequences only
    return best

def search(seq):
    if len(seq) == n:
        best = min(best, simulate(dishes in seq order))
        return best.makespan <= lb   # proven optimal: stop everything
    for recipe in groups with dishes left:
        if search(seq + [recipe]): return True

def lower_bound(dishes):             # each step at its fastest chef
    per station: min wait before + all work on it + min work after
    return max(station bounds, longest single dish)
```
Time **O(M·S·C)** worst case, usually far less because of the early stop; space **O(S + n)**.

*Where:* M = distinct recipe orderings = n! / (count₁! · … · count_R!), R = distinct recipes, n = dishes, S = total steps, C = chefs.

## 5. Complexity
| | Time | Space |
|---|---|---|
| Brute force | O(n!·S·C) | O(S) |
| Optimal | O(M·S·C) worst, early stop at the lower bound | O(S + n) |

*Where:* n = dishes, S = total steps, C = chefs, M = distinct recipe orderings (n! divided by the factorial of each recipe count).

| Case | Target | Lower bound | Optimal | Brute force |
|---|---|---|---|---|
| balanced_six | 195 / 1.00 s | 195 | 195 in 0.2 ms | 195 in 0.02 s |
| prep_bottleneck_seven | 195 / 1.25 s | 195 | 195 in 5.7 ms | 195 in 0.13 s |
| mixed_eight | 210 / 1.75 s | 195 | 210 in 14.2 ms | 210 in 1.20 s |
| deep_nine | 240 / 2.50 s | 240 | 240 in 1.5 ms | 240 in **12.54 s** ✗ |

Worst case (bound not reachable, full search): 12 dishes 0.9 s, **16 dishes 60 s**; larger orders need a heuristic.

## 6. Tests added
**One-line coverage AI prompt**
```text
Without changing the solution code, add tests until line and branch coverage is 100% (edge cases: empty, ties, limits, boundaries, invalid input), plus a large-input test with a time limit and a multi-threaded test that must match single-threaded results. Measure memory (total and per item), latency per query (average and worst case), and requests per second per CPU core. Then tell me whether it's thread-safe (and if not, what breaks it and the fix) and what production VM (CPU and memory) it needs and how that scales. Write all of this to SUMMARY.md: coverage before and after, a table of the added tests, and the measurements.
```
Expected answers (measured):
- **Thread-safe:** `schedule` keeps all state (groups, counters, chef/station free times, best) in locals and only reads
  the chefs list and the order; 8 threads scheduling the same order got identical schedules
  (`test_concurrent_schedules_are_consistent`). It would break if the chefs list or an order's dishes were changed while
  scheduling. The GIL means threads don't speed this CPU-bound search up, so scale with processes.
- **Sizing:** peak memory ≈ 7 KB per schedule; the benchmark mix averages 3.2 ms (~310 schedules/s per core).
  A **2 vCPU / 1 GB** VM is plenty for orders up to ~12 dishes. The risk is CPU, not memory: an order of 16+ dishes whose
  bound isn't reachable can take a minute, so cap the search time and fall back to a heuristic.

No given tests were commented out and there were no `????` values. The original tests alone cover **22%** of the
solution (they never call `schedule`); with the tests added, `./run.sh coverage` reports **100% line and branch
coverage** of `order.py` and `kitchen.py` (17 tests).

**Gaps in the original tests, exposed by our implementation**
- **No mixed DONE/PENDING order**, so Bug 1 passes every given test. Covered by O1.
- **`schedule`, `schedule_brute_force`, `_simulate` and `_lower_bound` are never called** (`kitchen.py:27-120`):
  the only kitchen test checks the chef list. Covered by K1-K7, X1-X3.
- **No validity check at all**: nothing verifies recipe order, chef-specific durations, or that no chef or station is
  double-booked. Covered by `assert_valid` on every schedule (K1-K7, X1).
- **Benchmarks are never run as tests.** Covered by K7.
- **The lower bound and early stop are new**: a bound that's too high would stop the search with a worse schedule.
  Covered by X1 (bound ≤ brute-force makespan on 150 random orders) and X2.
- **No scale or concurrency.** Covered by X4, X5.

**Edge-case scenarios**
| ID | Area | Scenario | Example → expected | Test |
|---|---|---|---|---|
| O1 | is_complete | One DONE, one PENDING (**Bug 1**) | → False | `test_mixed_done_and_pending_is_not_complete` |
| O2 | is_complete | IN_PROGRESS dish | → False | `test_status_edge_cases` |
| O3 | is_complete | No dishes | → True (`all` of nothing) | `test_status_edge_cases` |
| O4 | assign | Default status; assign twice | PENDING → ASSIGNED | `test_status_edge_cases` |
| O5 | is_complete | Given cases | single/all done, single/all pending | the 5 original tests |
| K1 | schedule | Empty order | `[]`, makespan 0 | `test_schedule_edge_cases` |
| K2 | schedule | One dish of each recipe | burger 60, salad 45, pasta 90 | `test_schedule_edge_cases` |
| K3 | schedule | main.py order | burger, salad, pasta → 105 | `test_schedule_edge_cases` |
| K4 | schedule | All the same recipe (one group) | 4 salads → 135 | `test_schedule_edge_cases` |
| K5 | schedule | Earliest finish, not earliest start | pasta → Carol, Bob, Alice | `test_uses_station_specialists` |
| K6 | schedule | Single-chef kitchen | burger + salad, all Alice → 225 | `test_single_chef_kitchen` |
| K7 | schedule | All 4 benchmarks: valid, makespan and runtime | ≤ 195/195/210/240 within limits | `test_benchmarks_meet_makespan_and_runtime` |
| X1 | schedule | Optimized == brute force; bound ≤ makespan; both valid | 150 random orders, 0–6 dishes | `test_optimized_matches_brute_force` |
| X2 | _lower_bound | Empty, single dish, grill-bound | 0; pasta 90; deep_nine 240 | `test_lower_bound_edge_cases` |
| X3 | schedule_brute_force | Empty order | makespan 0 | `test_brute_force_empty_order` |
| X4 | schedule | Scale: 12 dishes (4/4/4) | 375 (= bound) in < 5 s | `test_scale_twelve_dishes` |
| X5 | schedule | 8 threads, same order | identical schedules | `test_concurrent_schedules_are_consistent` |

Not tested (by design): orders of 16+ dishes whose bound isn't reachable (60 s; needs a heuristic), a kitchen with no
chefs, and a chef missing a station multiplier (both raise errors).

**Coverage AI prompt** (only what the original tests miss)
```text
The original tests cover 22% of the solution (order.py 100%, kitchen.py 12%); they never call schedule.
Please add tests only for what they miss, then confirm 100% line and branch coverage.
1. order.py: is_complete is False for one DONE + one PENDING dish and for an IN_PROGRESS dish, True for no dishes.
2. Write assert_valid(order, schedule): every step once, on its recipe station, lasting chef.time_for_step,
   recipe order within a dish, and no chef or station with overlapping entries. Use it in every test below.
3. kitchen.schedule: empty order -> [] with makespan 0; burger 60, salad 45, pasta 90; burger+salad+pasta 105;
   4 salads 135; pasta uses Carol, Bob, Alice; a kitchen with only Alice gives 225 for burger+salad.
4. All 4 benchmark cases from get_benchmark_cases() meet max_makespan and max_seconds.
5. schedule_brute_force on an empty order -> 0, and the same makespan as schedule on random orders of up to 6
   dishes; _lower_bound is never above the brute-force makespan, is 0 for no dishes, 90 for one pasta, 240 for deep_nine.
6. Non-functional: 12 dishes (4 of each) -> 375 in < 5 s; 8 threads scheduling one order get identical results.
Run coverage with --branch on order.py and kitchen.py. Add tests only; don't change the solution code.
```

## 7. Gotchas
- `any` vs `all`: complete means every dish is done; an empty order counts as complete with `all`.
- Pick the chef who **finishes** first, not who **starts** first, or a 3× slower chef takes the grill.
- A burger must go first: prepping a pasta first delays the grill to 45 s; the pasta-first orderings I tried give 270 on `deep_nine` instead of 240.
- "Optimal" means the best ordering for this simulator, the same space the brute force searches; the lower bound proves
  it is truly optimal on 3 of 4 benchmarks (all except mixed_eight, where the bound 195 is not reachable).
- Check by hand: the lower bound must never exceed a real schedule (X1), or the early stop returns a worse answer.
