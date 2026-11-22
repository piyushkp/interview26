# NEW FILE: not in the original. Tests solution-only methods (schedule_brute_force, _lower_bound),
# scale and concurrency.
"""Solution-only checks: optimized == brute force, the lower bound is safe, scale, and thread safety."""

import os
import sys

# NEW: lets this file run directly (python3 test_x.py); run.sh's PYTHONPATH still takes priority.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "solution", "src"))
import random
import threading
import time
import unittest

from chefs import make_default_chefs
from kitchen import Kitchen
from recipes import RecipeId
from test_kitchen import assert_valid, make_order


class SolutionOnlyTest(unittest.TestCase):
    def test_optimized_matches_brute_force(self) -> None:
        kitchen = Kitchen(make_default_chefs())
        rng = random.Random(11)
        for _ in range(150):
            order = make_order(*rng.choices(list(RecipeId), k=rng.randint(0, 6)))
            optimized = kitchen.schedule(order)
            brute = kitchen.schedule_brute_force(order)
            assert_valid(self, order, optimized)
            assert_valid(self, order, brute)
            self.assertEqual(optimized.makespan, brute.makespan)
            self.assertGreaterEqual(brute.makespan, kitchen._lower_bound(order.dishes))  # bound is safe

    def test_lower_bound_edge_cases(self) -> None:
        kitchen = Kitchen(make_default_chefs())
        self.assertEqual(kitchen._lower_bound([]), 0)
        self.assertEqual(kitchen._lower_bound(make_order(RecipeId.PASTA).dishes), 90)  # longest single dish
        deep = make_order(RecipeId.BURGER, RecipeId.PASTA, RecipeId.SALAD, RecipeId.SALAD, RecipeId.PASTA,
                          RecipeId.BURGER, RecipeId.SALAD, RecipeId.PASTA, RecipeId.SALAD)
        self.assertEqual(kitchen._lower_bound(deep.dishes), 240)  # 15 s first prep + 5 x 45 s grill

    def test_brute_force_empty_order(self) -> None:
        self.assertEqual(Kitchen(make_default_chefs()).schedule_brute_force(make_order()).makespan, 0)

    def test_scale_twelve_dishes(self) -> None:
        order = make_order(*([RecipeId.BURGER] * 4 + [RecipeId.SALAD] * 4 + [RecipeId.PASTA] * 4))
        start = time.perf_counter()
        schedule = Kitchen(make_default_chefs()).schedule(order)
        elapsed = time.perf_counter() - start
        assert_valid(self, order, schedule)
        self.assertEqual(schedule.makespan, 375)  # = lower bound: 15 s first prep + 8 grills x 45 s
        self.assertLess(elapsed, 5.0, f"took {elapsed:.2f}s")

    def test_concurrent_schedules_are_consistent(self) -> None:
        kitchen = Kitchen(make_default_chefs())
        order = make_order(RecipeId.BURGER, RecipeId.PASTA, RecipeId.SALAD, RecipeId.SALAD, RecipeId.PASTA,
                           RecipeId.BURGER, RecipeId.SALAD, RecipeId.PASTA, RecipeId.SALAD)
        expected = kitchen.schedule(order).entries
        results = []
        threads = [threading.Thread(target=lambda: results.append(kitchen.schedule(order).entries))
                   for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(results, [expected] * 8)


if __name__ == "__main__":
    unittest.main()
