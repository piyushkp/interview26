"""Dish state for an order."""

from dataclasses import dataclass
from enum import Enum

from recipes import Recipe


class DishStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


@dataclass
class Dish:
    id: int
    recipe: Recipe
    status: DishStatus = DishStatus.PENDING
