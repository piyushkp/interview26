"""Tests for Network. All of this is just boilerplate to make test cases compact and understandable."""

import os
import sys

# NEW: lets this file run directly (python3 test_x.py); run.sh's PYTHONPATH still takes priority.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "solution", "src"))
import unittest

from network import Network

# NEW: needed by the new tests below.
from network import TRANSFER_PENALTY


class NetworkTest(unittest.TestCase):

    def test_bidirectional_connection(self) -> None:
        net = Network()
        net.add_connection("A", "B", 5, "Red")
        neighbors_a = [c.destination for c in net.get_neighbors("A")]
        neighbors_b = [c.destination for c in net.get_neighbors("B")]
        self.assertIn("B", neighbors_a)
        self.assertIn("A", neighbors_b)

    def test_travel_time_preserved(self) -> None:
        net = Network()
        net.add_connection("A", "B", 7, "Blue")
        conn = net.get_neighbors("A")[0]
        self.assertEqual(conn.travel_time, 7)

    def test_multiple_connections(self) -> None:
        net = Network()
        net.add_connection("A", "B", 3, "Red")
        net.add_connection("A", "C", 5, "Blue")
        neighbors = [c.destination for c in net.get_neighbors("A")]
        self.assertEqual(sorted(neighbors), ["B", "C"])

    # UNCOMMENTED (original test_network.py lines 31-36).
    def test_one_way_neighbors(self) -> None:
        net = Network()
        net.add_connection("A", "B", 4, "Express", one_way=True)
        neighbors_b = [c.destination for c in net.get_neighbors("B")]
        # FILLED IN (original test_network.py line 35). Old: expected = "????"
        expected = []  # catches Bug 1: a one-way connection gives B no way back to A
        self.assertEqual(neighbors_b, expected)

    # UNCOMMENTED (original test_network.py lines 38-44).
    def test_travel_cost_same_line(self) -> None:
        net = Network()
        net.add_connection("A", "B", 3, "Red")
        conn = net.get_neighbors("A")[0]
        cost = net.get_travel_cost(conn, "Red")
        # FILLED IN (original test_network.py line 43). Old: expected = "????"
        expected = 3  # catches Bug 2: staying on the Red line is not a transfer, so no penalty
        self.assertEqual(cost, expected)

    # NEW: edge cases N3-N6 (not in the original tests).
    def test_one_way_keeps_the_forward_direction(self) -> None:  # N3
        net = Network()
        net.add_connection("A", "B", 4, "Express", one_way=True)
        net.add_connection("B", "A", 9, "Local")  # a separate two-way line back
        self.assertEqual([(c.destination, c.line) for c in net.get_neighbors("A")],
                         [("B", "Express"), ("B", "Local")])
        self.assertEqual([(c.destination, c.line) for c in net.get_neighbors("B")], [("A", "Local")])

    def test_travel_cost_first_ride_and_line_change(self) -> None:  # N4
        net = Network()
        net.add_connection("A", "B", 3, "Red")
        conn = net.get_neighbors("A")[0]
        self.assertEqual(net.get_travel_cost(conn, None), 3)  # first ride: no penalty
        self.assertEqual(net.get_travel_cost(conn, "Blue"), 3 + TRANSFER_PENALTY)
        self.assertEqual(TRANSFER_PENALTY, 5)

    def test_unknown_and_lone_stations(self) -> None:  # N5
        net = Network()
        self.assertEqual(net.get_neighbors("Nowhere"), [])
        self.assertFalse(net.has_station("Nowhere"))
        net.add_station("Lone")
        net.add_station("Lone")  # adding twice keeps one station
        self.assertEqual(net.get_all_stations(), {"Lone"})
        self.assertEqual(net.get_neighbors("Lone"), [])

    def test_one_way_adds_both_stations(self) -> None:  # N6
        net = Network()
        net.add_connection("A", "B", 4, "Express", one_way=True)
        self.assertTrue(net.has_station("B"))
        self.assertEqual(net.get_all_stations(), {"A", "B"})


if __name__ == "__main__":
    unittest.main()
