"""Chef definitions and station speed helpers."""

from dataclasses import dataclass
from enum import IntEnum

from station import Station


class ChefId(IntEnum):
    ALICE = 1
    BOB = 2
    CAROL = 3


@dataclass(frozen=True)
class Chef:
    id: ChefId
    name: str
    multipliers: dict[Station, float]

    def multiplier_for(self, station: Station) -> float:
        return self.multipliers[station]

    def time_for_step(self, station: Station, base_seconds: int) -> int:
        return round(base_seconds * self.multiplier_for(station))


CHEF_DEFINITIONS: dict[ChefId, tuple[str, dict[Station, float]]] = {
    ChefId.ALICE: (
        "Alice",
        {
            Station.PREP: 1.5,
            Station.CHOP: 1.5,
            Station.GRILL: 0.5,
        },
    ),
    ChefId.BOB: (
        "Bob",
        {
            Station.PREP: 1.5,
            Station.CHOP: 0.5,
            Station.GRILL: 1.5,
        },
    ),
    ChefId.CAROL: (
        "Carol",
        {
            Station.PREP: 0.5,
            Station.CHOP: 1.5,
            Station.GRILL: 1.5,
        },
    ),
}


def make_chef(chef_id: ChefId) -> Chef:
    try:
        name, multipliers = CHEF_DEFINITIONS[chef_id]
    except KeyError as exc:
        raise ValueError(f"Unknown chef id: {chef_id}") from exc
    return Chef(chef_id, name, dict(multipliers))


def make_default_chefs() -> list[Chef]:
    return [make_chef(chef_id) for chef_id in ChefId]
