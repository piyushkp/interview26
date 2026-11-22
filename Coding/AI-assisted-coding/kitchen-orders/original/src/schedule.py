"""Schedule data structures."""

from dataclasses import dataclass

from chefs import Chef
from dish import Dish
from station import Station


@dataclass(frozen=True)
class ScheduleEntry:
    dish: Dish
    step_index: int
    station: Station
    chef: Chef
    start: int
    end: int


@dataclass
class Schedule:
    entries: list[ScheduleEntry]

    @property
    def makespan(self) -> int:
        if not self.entries:
            return 0
        return max(entry.end for entry in self.entries)
