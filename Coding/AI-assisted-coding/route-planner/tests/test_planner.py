"""Tests for Planner. Outlines for optional tests, maybe useful after Planner is functioning."""

import os
import sys

# NEW: lets this file run directly (python3 test_x.py); run.sh's PYTHONPATH still takes priority.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "solution", "src"))
import time
import unittest

from maps import get_test_map, get_standard_map, get_large_map
from planner import Planner

# NEW: needed by the new tests below.
from maps import get_line_coupling_map, get_transfer_trap_map
from network import Network


# NEW: the best (minutes, transfers) for riding exactly these stations in order, trying every line choice
# and keeping at most max_transfers. A route is honest only if its reported numbers equal this.
def best_cost_along(net: Network, stations, max_transfers=None):
    costs = {(None, 0): 0}  # (line I'm on, transfers so far) -> fewest minutes
    for here, there in zip(stations, stations[1:]):
        nxt = {}
        for (line, transfers), minutes in costs.items():
            for conn in net.get_neighbors(here):
                if conn.destination != there:
                    continue
                key = (conn.line, transfers + (line is not None and conn.line != line))
                if max_transfers is not None and key[1] > max_transfers:
                    continue
                total = minutes + net.get_travel_cost(conn, line)
                if key not in nxt or total < nxt[key]:
                    nxt[key] = total
        if not nxt:
            return None  # two neighbors in the route aren't connected within the limit
        costs = nxt
    return min((minutes, transfers) for (_, transfers), minutes in costs.items())


def assert_honest_route(test: unittest.TestCase, net: Network, route, start: str, end: str,
                        max_transfers=None) -> None:
    test.assertEqual(route.stations[0], start)
    test.assertEqual(route.stations[-1], end)
    test.assertEqual(len(set(route.stations)), len(route.stations))
    test.assertEqual(best_cost_along(net, route.stations, max_transfers), (route.total_time, route.transfers))


class PlannerTest(unittest.TestCase):

    def test_find_shortest_route(self) -> None:
        planner = Planner(get_test_map())
        route = planner.find_route("Central", "Airport")
        # UNCOMMENTED (original test_planner.py lines 15-18).
        self.assertIsNotNone(route)
        self.assertEqual(route.stations[0], "Central")
        self.assertEqual(route.stations[-1], "Airport")
        self.assertEqual(route.total_time, 7)

    # UNCOMMENTED (original test_planner.py lines 20-24).
    def test_transfer_limit(self) -> None:
        planner = Planner(get_standard_map())
        route = planner.find_route_with_max_transfers("Downtown", "Uptown", max_transfers=0)
        self.assertIsNotNone(route)
        self.assertEqual(route.total_time, 7)

    # UNCOMMENTED (original test_planner.py lines 26-29).
    def test_no_route_within_transfer_limit(self) -> None:
        planner = Planner(get_standard_map())
        route = planner.find_route_with_max_transfers("Downtown", "Uptown", max_transfers=-1)
        self.assertIsNone(route)

    # UNCOMMENTED (original test_planner.py lines 31-43).
    def test_efficiency_on_large_network(self) -> None:
        trials = [
            (get_large_map(50, 50, seed=1), "S_0_0", "S_49_49"),
            (get_large_map(60, 60, seed=2), "S_0_0", "S_59_59"),
            (get_large_map(50, 50, seed=3), "S_10_10", "S_40_40"),
        ]
        for network, start, end in trials:
            planner = Planner(network)
            t0 = time.time()
            route = planner.find_route(start, end)
            elapsed = time.time() - t0
            self.assertIsNotNone(route, f"no route from {start} to {end}")
            self.assertLess(elapsed, 2.0, f"{start}->{end} took {elapsed:.2f}s")

    # NEW: edge cases P5-P15 (not in the original tests).
    def test_test_map_route_details(self) -> None:  # P5
        net = get_test_map()
        route = Planner(net).find_route("Central", "Airport")
        self.assertEqual(route.stations, ["Central", "Mall", "Stadium", "Airport"])  # all Blue
        self.assertEqual(route.transfers, 0)
        assert_honest_route(self, net, route, "Central", "Airport")

    def test_start_equals_end(self) -> None:  # P6
        planner = Planner(get_test_map())
        for route in (planner.find_route("Park", "Park"),
                      planner.find_route_with_max_transfers("Park", "Park", 0)):
            self.assertEqual((route.stations, route.total_time, route.transfers), (["Park"], 0, 0))
        self.assertIsNone(planner.find_route_with_max_transfers("Park", "Park", -1))

    def test_unknown_station(self) -> None:  # P7
        planner = Planner(get_test_map())
        self.assertIsNone(planner.find_route("Central", "Moon"))
        self.assertIsNone(planner.find_route("Moon", "Central"))
        self.assertIsNone(planner.find_route_with_max_transfers("Moon", "Central", 3))

    def test_unreachable(self) -> None:  # P8
        net = Network()
        net.add_connection("A", "B", 2, "Red", one_way=True)
        net.add_station("Island")
        planner = Planner(net)
        self.assertIsNone(planner.find_route("B", "A"))  # only against a one-way connection
        self.assertIsNone(planner.find_route("A", "Island"))
        self.assertEqual(planner.find_route("A", "B").total_time, 2)

    def test_one_way_respected_in_routes(self) -> None:  # P9, catches Bug 1
        net = get_standard_map()
        planner = Planner(net)
        forward = planner.find_route("Downtown", "Uptown")  # the Loop only runs Uptown -> Downtown
        self.assertEqual((forward.stations, forward.total_time), (["Downtown", "Midtown", "Uptown"], 7))
        back = planner.find_route("Uptown", "Downtown")
        self.assertEqual((back.stations, back.total_time, back.transfers), (["Uptown", "Downtown"], 6, 0))

    def test_line_coupling_trap(self) -> None:  # P10, needs (station, line) states
        net = get_line_coupling_map()
        route = Planner(net).find_route("Start", "End")
        self.assertEqual((route.stations, route.total_time, route.transfers), (["Start", "B", "End"], 4, 0))

    def test_transfer_trap(self) -> None:  # P11, needs the transfer count in the state
        net = get_transfer_trap_map()
        planner = Planner(net)
        fastest = planner.find_route("Start", "End")
        self.assertEqual((fastest.stations, fastest.total_time, fastest.transfers),
                         (["Start", "A", "B", "End"], 13, 2))
        self.assertEqual(planner.find_route_with_max_transfers("Start", "End", 2).total_time, 13)
        limited = planner.find_route_with_max_transfers("Start", "End", 1)
        self.assertEqual((limited.stations, limited.total_time, limited.transfers), (["Start", "B", "End"], 14, 1))
        self.assertIsNone(planner.find_route_with_max_transfers("Start", "End", 0))

    def test_parallel_lines_between_two_stations(self) -> None:  # P12
        net = Network()
        net.add_connection("A", "B", 2, "Red")
        net.add_connection("A", "B", 3, "Blue")
        net.add_connection("B", "C", 1, "Blue")
        route = Planner(net).find_route("A", "C")
        self.assertEqual((route.total_time, route.transfers), (4, 0))  # Blue all the way beats Red + transfer

    def test_time_tie_prefers_fewer_transfers(self) -> None:  # P13
        net = Network()
        net.add_connection("A", "B", 1, "Red")
        net.add_connection("B", "C", 1, "Blue")  # 1 + 1 + 5 = 7, one transfer
        net.add_connection("A", "D", 3, "Green")
        net.add_connection("D", "C", 4, "Green")  # 7, no transfers
        route = Planner(net).find_route("A", "C")
        self.assertEqual((route.stations, route.total_time, route.transfers), (["A", "D", "C"], 7, 0))

    def test_large_network_with_transfer_limit(self) -> None:  # P14
        net = get_large_map(150, 150, seed=4)
        planner = Planner(net)
        t0 = time.time()
        fastest = planner.find_route("S_0_0", "S_149_149")
        limited = planner.find_route_with_max_transfers("S_0_0", "S_149_149", 3)
        elapsed = time.time() - t0
        self.assertEqual((fastest.total_time, fastest.transfers), (1181, 4))
        self.assertEqual((limited.total_time, limited.transfers), (1185, 3))
        assert_honest_route(self, net, limited, "S_0_0", "S_149_149", 3)
        self.assertLess(elapsed, 2.0, f"took {elapsed:.2f}s")

    def test_given_maps_routes_are_honest(self) -> None:  # P15
        for net, start, end in ((get_test_map(), "Central", "Airport"), (get_standard_map(), "Westside", "Station"),
                                (get_standard_map(), "Eastside", "Uptown"), (get_large_map(20, 20, 5), "S_3_0", "S_19_17")):
            planner = Planner(net)
            assert_honest_route(self, net, planner.find_route(start, end), start, end)
            assert_honest_route(self, net, planner.find_route_with_max_transfers(start, end, 1), start, end, 1)


if __name__ == "__main__":
    unittest.main()
