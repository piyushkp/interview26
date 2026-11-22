"""Benchmark order cases for scheduling tests."""

from dataclasses import dataclass
import os

from recipes import RecipeId


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


@dataclass(frozen=True)
class ScheduleCase:
    name: str
    max_makespan: int
    max_seconds: float
    recipe_ids: tuple[RecipeId, ...]


def _load_cases(filename: str) -> list[ScheduleCase]:
    path = os.path.join(DATA_DIR, filename)
    cases = []
    with open(path, "r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line:
                continue
            name, max_makespan, max_seconds, recipes = line.split("|")
            recipe_ids = tuple(RecipeId[recipe.strip()] for recipe in recipes.split(","))
            cases.append(ScheduleCase(name, int(max_makespan), float(max_seconds), recipe_ids))
    return cases


def get_benchmark_cases() -> list[ScheduleCase]:
    return _load_cases("benchmark_cases.txt")
