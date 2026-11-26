"""You'll implement this."""

from typing import List, Optional

from network import Network


class Route:
    def __init__(self, stations: List[str], total_time: int, transfers: int):
        self.stations = stations
        self.total_time = total_time
        self.transfers = transfers


class Planner:
    """Finds optimal routes through a transit network."""

    def __init__(self, network: Network):
        self.network = network

    def find_route(self, start: str, end: str) -> Optional[Route]:
        pass
        return None

    def find_route_with_max_transfers(
        self, start: str, end: str, max_transfers: int
    ) -> Optional[Route]:
        pass
        return None
