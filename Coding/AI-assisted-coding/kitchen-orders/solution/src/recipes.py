"""Recipe definitions for the kitchen."""

from dataclasses import dataclass
from enum import IntEnum

from station import Station


@dataclass(frozen=True)
class Recipe:
    name: str
    ordered_steps: tuple[tuple[Station, int], ...]


class RecipeId(IntEnum):
    BURGER = 1
    SALAD = 2
    PASTA = 3


RECIPES = {
    RecipeId.BURGER: Recipe(
        "BURGER",
        (
            (Station.PREP, 30),
            (Station.GRILL, 90),
        ),
    ),
    RecipeId.SALAD: Recipe(
        "SALAD",
        (
            (Station.PREP, 30),
            (Station.CHOP, 60),
        ),
    ),
    RecipeId.PASTA: Recipe(
        "PASTA",
        (
            (Station.PREP, 30),
            (Station.CHOP, 60),
            (Station.GRILL, 90),
        ),
    ),
}


def make_recipe(recipe_id: RecipeId) -> Recipe:
    return RECIPES[recipe_id]


def all_recipe_ids() -> list[RecipeId]:
    return list(RecipeId)
