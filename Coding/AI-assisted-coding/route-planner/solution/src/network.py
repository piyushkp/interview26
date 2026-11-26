"""Read this first."""

from typing import Dict, List, NamedTuple, Optional, Set

TRANSFER_PENALTY: int = 5


class Connection(NamedTuple):
    destination: str
    travel_time: int
    line: str
    one_way: bool


class Network:
    def __init__(self) -> None:
        self._stations: Dict[str, List[Connection]] = {}

    def add_station(self, name: str) -> None:
        if name not in self._stations:
            self._stations[name] = []

    # Adds a connection in both directions, or only forward if it is one-way. Time O(1), Space O(1)
    def add_connection(
        self, from_station: str, to_station: str,
        travel_time: int, line: str, one_way: bool = False
    ) -> None:
        self.add_station(from_station)
        self.add_station(to_station)

        self._stations[from_station].append(
            Connection(to_station, travel_time, line, one_way)
        )
        # BUG FIX 1 (original network.py lines 33-35): the reverse connection was added even for one-way
        # connections, so riders could travel against them (Downtown -> Uptown on the Uptown-only Loop in 6).
        # Old code:
        #     self._stations[to_station].append(
        #         Connection(from_station, travel_time, line, one_way)
        #     )
        if not one_way:
            self._stations[to_station].append(
                Connection(from_station, travel_time, line, one_way)
            )

    # Ride time, plus the transfer penalty only when switching lines. Time O(1), Space O(1)
    def get_travel_cost(
        self, connection: Connection, current_line: Optional[str]
    ) -> int:
        base_cost = connection.travel_time
        # BUG FIX 2 (original network.py line 41): the penalty is for changing lines, but it was charged on
        # every ride after the first, even when staying on the same line. The first ride has no penalty.
        # Old code:
        #     if current_line is not None:
        if current_line is not None and current_line != connection.line:
            base_cost += TRANSFER_PENALTY
        return base_cost

    def get_neighbors(self, station: str) -> List[Connection]:
        return self._stations.get(station, [])

    def get_all_stations(self) -> Set[str]:
        return set(self._stations.keys())

    def has_station(self, name: str) -> bool:
        return name in self._stations
