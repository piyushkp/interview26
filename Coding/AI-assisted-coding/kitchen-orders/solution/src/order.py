"""Order state for a kitchen request."""

from dataclasses import dataclass
from enum import Enum

from dish import Dish, DishStatus


class OrderStatus(Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"


@dataclass
class Order:
    id: int
    dishes: list[Dish]
    status: OrderStatus = OrderStatus.PENDING

    def is_complete(self) -> bool:
        # BUG FIX 1 (original order.py line 21): an order is complete only when every dish is done,
        # but `any` returned True as soon as one dish was done.
        # Old code:
        #     return any(dish.status == DishStatus.DONE for dish in self.dishes)
        return all(dish.status == DishStatus.DONE for dish in self.dishes)

    def assign(self) -> None:
        self.status = OrderStatus.ASSIGNED
