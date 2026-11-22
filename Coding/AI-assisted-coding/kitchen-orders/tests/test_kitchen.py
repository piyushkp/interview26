"""Tests for Kitchen scheduling."""

import os
import sys

# NEW: lets this file run directly (python3 test_x.py); run.sh's PYTHONPATH still takes priority.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "solution", "src"))
import time
import unittest

from chefs import ChefId, make_chef, make_default_chefs
from dish import Dish
from kitchen import Kitchen
from order import Order
from recipes import RecipeId, make_recipe
from schedule_cases import get_benchmark_cases


# NEW: checks every rule of a valid schedule from the problem statement.
def assert_valid(test: unittest.TestCase, order: Order, schedule) -> None:
    expected = {(d.id, i) for d in order.dishes for i in range(len(d.recipe.ordered_steps))}
    seen = [(e.dish.id, e.step_index) for e in schedule.entries]
    test.assertEqual(sorted(seen), sorted(expected), "every step exactly once")
    for e in schedule.entries:
        station, base = e.dish.recipe.ordered_steps[e.step_index]
        test.assertEqual(e.station, station, "step on its recipe station")
        test.assertEqual(e.end - e.start, e.chef.time_for_step(station, base), "chef-specific duration")
        test.assertGreaterEqual(e.start, 0)
    by_dish = {}
    for e in schedule.entries:
        by_dish.setdefault(e.dish.id, []).append(e)
    for steps in by_dish.values():
        steps.sort(key=lambda e: e.step_index)
        for a, b in zip(steps, steps[1:]):
            test.assertLessEqual(a.end, b.start, "recipe order within a dish")
    for key in (lambda e: e.chef.id, lambda e: e.station):
        groups = {}
        for e in schedule.entries:
            groups.setdefault(key(e), []).append(e)
        for items in groups.values():
            items.sort(key=lambda e: e.start)
            for a, b in zip(items, items[1:]):
                test.assertLessEqual(a.end, b.start, "no chef or station double-booked")


def make_order(*recipe_ids: RecipeId) -> Order:
    return Order(1, [Dish(i + 1, make_recipe(r)) for i, r in enumerate(recipe_ids)])


class TestKitchen(unittest.TestCase):
    def test_kitchen_constructs_with_default_chefs(self) -> None:
        kitchen = Kitchen(make_default_chefs())
        self.assertEqual([chef.id for chef in kitchen.chefs], [ChefId.ALICE, ChefId.BOB, ChefId.CAROL])


    # NEW: the given benchmarks, run as tests (task 4).
    def test_benchmarks_meet_makespan_and_runtime(self) -> None:
        kitchen = Kitchen(make_default_chefs())
        for case in get_benchmark_cases():
            order = make_order(*case.recipe_ids)
            start = time.perf_counter()
            schedule = kitchen.schedule(order)
            elapsed = time.perf_counter() - start
            assert_valid(self, order, schedule)
            self.assertLessEqual(schedule.makespan, case.max_makespan, case.name)
            self.assertLess(elapsed, case.max_seconds, case.name)

    # NEW: edge cases K1-K6 (not in the original tests).
    def test_schedule_edge_cases(self) -> None:
        kitchen = Kitchen(make_default_chefs())
        empty = kitchen.schedule(make_order())
        self.assertEqual((empty.entries, empty.makespan), ([], 0))
        for recipes, expected in [((RecipeId.BURGER,), 60), ((RecipeId.SALAD,), 45),
                                  ((RecipeId.PASTA,), 90), ((RecipeId.BURGER, RecipeId.SALAD, RecipeId.PASTA), 105),
                                  ((RecipeId.SALAD,) * 4, 135)]:
            order = make_order(*recipes)
            schedule = kitchen.schedule(order)
            assert_valid(self, order, schedule)
            self.assertEqual(schedule.makespan, expected, recipes)

    # NEW: each step goes to the chef who finishes first (3x faster specialist), not who starts first.
    def test_uses_station_specialists(self) -> None:
        schedule = Kitchen(make_default_chefs()).schedule(make_order(RecipeId.PASTA))
        self.assertEqual([e.chef.id for e in schedule.entries], [ChefId.CAROL, ChefId.BOB, ChefId.ALICE])

    # NEW: one chef must do every step one after another.
    def test_single_chef_kitchen(self) -> None:
        order = make_order(RecipeId.BURGER, RecipeId.SALAD)
        schedule = Kitchen([make_chef(ChefId.ALICE)]).schedule(order)
        assert_valid(self, order, schedule)
        self.assertEqual(schedule.makespan, 45 + 45 + 45 + 90)  # every step by Alice, back to back


if __name__ == "__main__":
    unittest.main()
