"""Tests for Order behavior."""

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


if __name__ == "__main__":
    unittest.main()
