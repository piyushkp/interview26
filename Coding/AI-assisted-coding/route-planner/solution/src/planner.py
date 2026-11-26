"""You'll implement this."""

from typing import List, Optional

from network import Network

# NEW: a min-heap for Dijkstra's, a counter so the heap never has to compare states, and type hints.
import heapq
from itertools import count
from typing import Dict, Set, Tuple

# V = stations, E = connections, T = lines that reach one station, K = max_transfers + 1,
# P = simple paths from start, L = stations on a path.
# A search state is (station, line I arrived on, transfers used);
# transfers is always 0 when there is no limit.
State = Tuple[str, Optional[str], int]


class Route:
    def __init__(self, stations: List[str], total_time: int, transfers: int):
        self.stations = stations
        self.total_time = total_time
        self.transfers = transfers


class Planner:
    """Finds optimal routes through a transit network."""

    def __init__(self, network: Network):
        self.network = network

    # AI prompt: "Solve this with Dijkstra's algorithm on (station, current line) states, since ride times
    #   and the 5-minute penalty are never negative. Use a min-heap ordered by time, then transfers, skipping
    #   stale entries. Return None for unknown or unreachable stations, zero minutes when start equals end,
    #   and match the brute force."
    # Optimized: Dijkstra's over (station, line) states. Time O(E·T log(E·T)), Space O(E·T)
    def find_route(self, start: str, end: str) -> Optional[Route]:
        # CHANGED (original planner.py lines 22-23): implemented. Old code:
        #     pass
        #     return None
        return self._dijkstra(start, end, None)

    # AI prompt: "Extend that Dijkstra's search to (station, line, transfers used) states, so a slower arrival
    #   with fewer transfers is never thrown away, and skip any move that goes over max_transfers. Return None
    #   if max_transfers is negative or no route fits, and match the brute force's time and transfers."
    # Optimized: Dijkstra's over (station, line, transfers) states.
    # Time O(E·T·K log(E·T·K)), Space O(E·T·K)
    def find_route_with_max_transfers(
        self, start: str, end: str, max_transfers: int
    ) -> Optional[Route]:
        # CHANGED (original planner.py lines 28-29): implemented. Old code:
        #     pass
        #     return None
        if max_transfers < 0:  # no route can use fewer than zero transfers
            return None
        return self._dijkstra(start, end, max_transfers)

    # NEW: shared Dijkstra's. Costs are (minutes, transfers), compared in that order, so a time tie goes to
    # fewer transfers. Time and space as in the two callers above.
    def _dijkstra(self, start: str, end: str, max_transfers: Optional[int]) -> Optional[Route]:
        if not (self.network.has_station(start) and self.network.has_station(end)):
            return None
        first: State = (start, None, 0)
        best: Dict[State, Tuple[int, int]] = {first: (0, 0)}
        parent: Dict[State, Optional[State]] = {first: None}
        tie = count()
        heap = [(0, 0, next(tie), first)]  # min-heap of (minutes, transfers, tie, state)
        while heap:
            minutes, transfers, _, state = heapq.heappop(heap)  # O(log(heap)) per pop
            if best[state] < (minutes, transfers):  # stale entry: this state was already settled cheaper
                continue
            station, line, _ = state
            if station == end:  # the first time the end is popped, its cost is final
                return Route(self._stations_on_path(parent, state), minutes, transfers)
            for conn in self.network.get_neighbors(station):  # each state scans its station's connections
                new_transfers = transfers + (line is not None and conn.line != line)
                if max_transfers is not None and new_transfers > max_transfers:
                    continue
                nxt: State = (conn.destination, conn.line, new_transfers if max_transfers is not None else 0)
                cost = (minutes + self.network.get_travel_cost(conn, line), new_transfers)
                if nxt not in best or cost < best[nxt]:
                    best[nxt] = cost
                    parent[nxt] = state
                    heapq.heappush(heap, (cost[0], cost[1], next(tie), nxt))
        return None

    # NEW: follows the parent links back from the end state. Time O(L), Space O(L)
    def _stations_on_path(self, parent: Dict[State, Optional[State]], state: State) -> List[str]:
        stations: List[str] = []
        current: Optional[State] = state
        while current is not None:
            stations.append(current[0])
            current = parent[current]
        stations.reverse()
        return stations

    # NEW: brute force kept so tests can compare it with both optimized searches.
    # AI prompt: "Solve this with backtracking: walk every route that never revisits a station, trying every
    #   connection out of each station, and undo each step after exploring it. Add ride times plus 5 minutes
    #   per line change, keep the fastest route, fewer transfers on a tie, and return None if none fits."
    # Brute force: try every simple path, keep the cheapest. Time O(P·L), Space O(V) recursion depth
    def find_route_brute_force(
        self, start: str, end: str, max_transfers: Optional[int] = None
    ) -> Optional[Route]:
        if not (self.network.has_station(start) and self.network.has_station(end)):
            return None
        best: Optional[Tuple[int, int, List[str]]] = None
        path: List[str] = [start]
        on_path: Set[str] = {start}

        def explore(station: str, line: Optional[str], minutes: int, transfers: int) -> None:
            nonlocal best
            if station == end:
                fits = max_transfers is None or transfers <= max_transfers
                if fits and (best is None or (minutes, transfers) < best[:2]):
                    best = (minutes, transfers, list(path))
                return
            for conn in self.network.get_neighbors(station):  # every branch: P paths in total
                if conn.destination in on_path:  # a simple path never revisits a station
                    continue
                path.append(conn.destination)
                on_path.add(conn.destination)
                explore(conn.destination, conn.line,
                        minutes + self.network.get_travel_cost(conn, line),
                        transfers + (line is not None and conn.line != line))
                path.pop()  # undo, so other routes can use this station
                on_path.discard(conn.destination)

        explore(start, None, 0, 0)
        return None if best is None else Route(best[2], best[0], best[1])
