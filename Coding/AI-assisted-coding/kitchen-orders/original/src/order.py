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
        return any(dish.status == DishStatus.DONE for dish in self.dishes)

    def assign(self) -> None:
        self.status = OrderStatus.ASSIGNED
