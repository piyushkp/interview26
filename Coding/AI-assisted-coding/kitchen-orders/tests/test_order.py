"""Tests for Order behavior."""

import os
import sys

# NEW: lets this file run directly (python3 test_x.py); run.sh's PYTHONPATH still takes priority.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "solution", "src"))
import unittest

from dish import Dish, DishStatus
from order import Order, OrderStatus
from recipes import RecipeId, make_recipe

def make_dish(dish_id: int, status: DishStatus) -> Dish:
    return Dish(dish_id, make_recipe(RecipeId.BURGER), status)


class TestOrder(unittest.TestCase):
    def test_single_done_is_complete(self) -> None:
        order = Order(1, [make_dish(1, DishStatus.DONE)])
        self.assertTrue(order.is_complete())

    def test_single_pending_is_not_complete(self) -> None:
        order = Order(1, [make_dish(1, DishStatus.PENDING)])
        self.assertFalse(order.is_complete())

    def test_all_done_is_complete(self) -> None:
        order = Order(
            1,
            [
                make_dish(1, DishStatus.DONE),
                make_dish(2, DishStatus.DONE),
            ],
        )
        self.assertTrue(order.is_complete())

    def test_all_pending_is_not_complete(self) -> None:
        order = Order(
            1,
            [
                make_dish(1, DishStatus.PENDING),
                make_dish(2, DishStatus.PENDING),
            ],
        )
        self.assertFalse(order.is_complete())

    def test_assign_marks_order_assigned(self) -> None:
        order = Order(1, [make_dish(1, DishStatus.PENDING)])
        order.assign()
        self.assertEqual(order.status, OrderStatus.ASSIGNED)


    # NEW: catches Bug 1. Every given test has all-done or all-pending dishes, so they all pass with `any`.
    def test_mixed_done_and_pending_is_not_complete(self) -> None:
        order = Order(1, [make_dish(1, DishStatus.DONE), make_dish(2, DishStatus.PENDING)])
        self.assertFalse(order.is_complete())

    # NEW: edge cases O2-O4 (not in the original tests).
    def test_status_edge_cases(self) -> None:
        self.assertFalse(Order(1, [make_dish(1, DishStatus.IN_PROGRESS)]).is_complete())
        self.assertTrue(Order(1, []).is_complete())  # all() of nothing is True: an empty order is complete
        order = Order(1, [make_dish(1, DishStatus.PENDING)])
        self.assertEqual(order.status, OrderStatus.PENDING)  # default before assign()
        order.assign()
        order.assign()
        self.assertEqual(order.status, OrderStatus.ASSIGNED)  # assigning twice is harmless


if __name__ == "__main__":
    unittest.main()
