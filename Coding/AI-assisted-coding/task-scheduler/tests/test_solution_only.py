# NEW FILE: not in the original. Tests the solution-only brute force and scale.
"""Solution-only checks: the critical-path schedule against the brute force, and scale."""

import os
import sys

# NEW: lets this file run directly (python3 test_x.py); run.sh's PYTHONPATH still takes priority.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "solution", "src"))
import math
import random
import time
import unittest

from optimizer import Optimizer
from scheduler import Scheduler
from task import Task, get_critical_path_tasks, get_test_tasks
from test_optimizer import assert_valid_schedule


def random_build(rng: random.Random, size: int) -> list:
    tasks = []
    for i in range(size):  # only depend on earlier tasks, so there is never a cycle
        deps = [f"t{j}" for j in range(i) if rng.random() < 0.3]
        tasks.append(Task(f"t{i}", rng.randint(0, 9), deps))
    rng.shuffle(tasks)
    return tasks


class SolutionOnlyTest(unittest.TestCase):
    def test_critical_path_vs_brute_force(self) -> None:  # X1
        rng = random.Random(5)
        matches = trials = 0
        for _ in range(300):
            scheduler = Scheduler(random_build(rng, rng.randint(1, 7)))
            workers = rng.randint(1, 3)
            fast_total, fast = Optimizer(scheduler).parallel_schedule(workers)
            best_total, best = Optimizer(scheduler).parallel_schedule_brute_force(workers)
            assert_valid_schedule(self, scheduler, workers, fast_total, fast)
            assert_valid_schedule(self, scheduler, workers, best_total, best)
            self.assertLessEqual(best_total, fast_total)  # the brute force is the best list schedule
            self.assertLessEqual(fast_total, (2 - 1 / workers) * best_total)  # Graham's list-scheduling bound
            work = sum(t.duration for t in scheduler.get_all_tasks())
            self.assertGreaterEqual(best_total, math.ceil(work / workers))  # no schedule beats this
            trials += 1
            matches += fast_total == best_total
        self.assertGreater(matches / trials, 0.9)  # measured 293 of 300: the heuristic is almost always best

    def test_brute_force_edge_cases(self) -> None:  # X2
        self.assertEqual(Optimizer(Scheduler(get_critical_path_tasks())).parallel_schedule_brute_force(2)[0], 26)
        self.assertEqual(Optimizer(Scheduler(get_test_tasks())).parallel_schedule_brute_force(2)[0], 8)
        self.assertEqual(Optimizer(Scheduler([])).parallel_schedule_brute_force(2), (0, {}))
        with self.assertRaises(ValueError):
            Optimizer(Scheduler(get_test_tasks())).parallel_schedule_brute_force(0)

    def test_scale_3000_tasks(self) -> None:  # X3
        rng = random.Random(9)
        tasks = []
        for i in range(3000):
            deps = [f"t{j}" for j in rng.sample(range(i), min(i, rng.randint(0, 4)))]
            tasks.append(Task(f"t{i}", rng.randint(1, 20), deps))
        scheduler = Scheduler(tasks)
        start = time.time()
        total, timeline = Optimizer(scheduler).parallel_schedule(8)
        elapsed = time.time() - start
        self.assertEqual(len(timeline), 3000)
        completion = {name: end for name, (_, end) in timeline.items()}
        for name, (begin, _) in timeline.items():
            self.assertGreaterEqual(begin, scheduler.earliest_start(name, completion))
        self.assertLess(elapsed, 1.0, f"took {elapsed:.2f}s")


if __name__ == "__main__":
    unittest.main()
