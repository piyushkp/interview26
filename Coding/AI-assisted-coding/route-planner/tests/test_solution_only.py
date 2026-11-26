# NEW FILE: not in the original. Tests the solution-only method (find_route_brute_force), scale and concurrency.
"""Solution-only checks: Dijkstra's must match the brute force, scale, and be thread-safe."""

import os
import sys

# NEW: lets this file run directly (python3 test_x.py); run.sh's PYTHONPATH still takes priority.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "solution", "src"))
import random
import threading
import time
import unittest

from maps import get_large_map, get_line_coupling_map, get_standard_map, get_transfer_trap_map
from network import Network
from planner import Planner
from test_planner import assert_honest_route


def random_network(rng: random.Random) -> Network:
    net = Network()
    stations = [f"S{i}" for i in range(rng.randint(2, 7))]
    for name in stations:
        net.add_station(name)
    lines = ["Red", "Blue", "Green"][: rng.randint(1, 3)]
    for _ in range(rng.randint(1, 12)):
        a, b = rng.sample(stations, 2)
        net.add_connection(a, b, rng.randint(0, 9), rng.choice(lines), one_way=rng.random() < 0.25)
    return net


def summary(route):
    return None if route is None else (route.total_time, route.transfers)


class SolutionOnlyTest(unittest.TestCase):
    def test_dijkstra_matches_brute_force(self) -> None:  # X1
        rng = random.Random(3)
        found = 0
        for _ in range(1500):
            net = random_network(rng)
            planner = Planner(net)
            start, end = rng.choice(sorted(net.get_all_stations())), rng.choice(sorted(net.get_all_stations()))
            limit = rng.choice([None, -1, 0, 1, 2, 3])
            fast = (planner.find_route(start, end) if limit is None
                    else planner.find_route_with_max_transfers(start, end, limit))
            brute = planner.find_route_brute_force(start, end, limit)
            self.assertEqual(summary(fast), summary(brute), (start, end, limit))
            if fast is not None:
                found += 1
                assert_honest_route(self, net, fast, start, end, limit)
                assert_honest_route(self, net, brute, start, end, limit)
                if limit is not None:
                    self.assertLessEqual(fast.transfers, limit)
        self.assertGreater(found, 500)  # both the "found" and "no route" branches are well exercised

    def test_brute_force_edge_cases(self) -> None:  # X2
        self.assertEqual(summary(Planner(get_line_coupling_map()).find_route_brute_force("Start", "End")), (4, 0))
        trap = Planner(get_transfer_trap_map())
        self.assertEqual(summary(trap.find_route_brute_force("Start", "End")), (13, 2))
        self.assertEqual(summary(trap.find_route_brute_force("Start", "End", 1)), (14, 1))
        self.assertIsNone(trap.find_route_brute_force("Start", "End", 0))
        self.assertIsNone(trap.find_route_brute_force("Start", "End", -1))
        self.assertIsNone(trap.find_route_brute_force("Start", "Moon"))
        self.assertEqual(trap.find_route_brute_force("A", "A").stations, ["A"])
        self.assertEqual(summary(Planner(get_standard_map()).find_route_brute_force("Downtown", "Uptown", 0)), (7, 0))

    def test_scale_300x300(self) -> None:  # X3
        net = get_large_map(300, 300, seed=6)
        planner = Planner(net)
        t0 = time.time()
        route = planner.find_route("S_0_0", "S_299_299")
        elapsed = time.time() - t0
        assert_honest_route(self, net, route, "S_0_0", "S_299_299")
        self.assertLess(elapsed, 3.0, f"took {elapsed:.2f}s")

    def test_concurrent_routes_are_consistent(self) -> None:  # X4
        net = get_large_map(80, 80, seed=2)
        expected = Planner(net).find_route_with_max_transfers("S_0_0", "S_79_79", 2)
        results = []

        def worker() -> None:
            for _ in range(5):
                route = Planner(net).find_route_with_max_transfers("S_0_0", "S_79_79", 2)
                results.append((route.stations, route.total_time, route.transfers))

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(len(results), 40)
        self.assertTrue(all(r == (expected.stations, expected.total_time, expected.transfers) for r in results))


if __name__ == "__main__":
    unittest.main()
