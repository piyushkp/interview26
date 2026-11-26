"""
Provides sample transit maps for testing and benchmarking.
get_test_map() is useful when developing your Planner.
get_standard_map() adds one-way connections for more advanced tests.
get_large_map() generates a grid network for performance testing.
"""

from typing import List

from network import Network


def get_test_map() -> Network:
    net = Network()
    net.add_connection("Central", "Park", 4, "Green")
    net.add_connection("Park", "Airport", 6, "Green")
    net.add_connection("Central", "Mall", 2, "Blue")
    net.add_connection("Mall", "Stadium", 3, "Blue")
    net.add_connection("Stadium", "Airport", 2, "Blue")
    net.add_connection("Central", "Harbor", 5, "Red")
    net.add_connection("Harbor", "Airport", 3, "Red")
    return net


def get_standard_map() -> Network:
    net = Network()
    net.add_connection("Downtown", "Midtown", 3, "Express")
    net.add_connection("Midtown", "Uptown", 4, "Express")
    net.add_connection("Downtown", "Eastside", 2, "Crosstown")
    net.add_connection("Eastside", "Midtown", 5, "Crosstown")
    net.add_connection("Midtown", "Westside", 2, "Crosstown")
    net.add_connection("Westside", "Uptown", 3, "Crosstown")
    net.add_connection("Downtown", "Station", 1, "Shuttle")
    net.add_connection("Station", "Eastside", 1, "Shuttle")

    net.add_connection("Uptown", "Downtown", 6, "Loop", one_way=True)
    net.add_connection("Eastside", "Westside", 7, "Bypass", one_way=True)

    return net


def get_line_coupling_map() -> Network:
    """Plain routing trap: the fastest route to End stays on one line.

    Start->A->B is all Red (cheap per hop), but continuing from there to End
    forces a Red->Blue transfer. Start->B->End stays Blue end to end. Keying
    visited on station alone settles B via the Red arrival and never reconsiders
    the Blue one, so it returns 8 instead of the correct 4.
    """
    net = Network()
    net.add_connection("Start", "A", 1, "Red")
    net.add_connection("A", "B", 1, "Red")
    net.add_connection("Start", "B", 3, "Blue")
    net.add_connection("B", "End", 1, "Blue")
    return net


def get_transfer_trap_map() -> Network:
    """Transfer-limit trap: reaching B faster costs an extra transfer.

    Start->A->B is quicker but switches Red->Blue (1 transfer) before the final
    Blue->Yellow hop to End (2 transfers total). Start->B stays Blue (0
    transfers), leaving one transfer for Blue->Yellow. Keying visited on
    (station, line) settles B via the cheaper 1-transfer arrival and discards
    the 0-transfer arrival, so under max_transfers=1 it returns None even though
    Start->B->End (time 14, 1 transfer) is valid.
    """
    net = Network()
    net.add_connection("Start", "A", 1, "Red")
    net.add_connection("A", "B", 1, "Blue")
    net.add_connection("Start", "B", 8, "Blue")
    net.add_connection("B", "End", 1, "Yellow")
    return net


LINES: List[str] = ["Red", "Blue", "Green", "Yellow", "Orange", "Purple"]


def get_large_map(rows: int, cols: int, seed: int = 0) -> Network:
    net = Network()
    for r in range(rows):
        for c in range(cols):
            station = f"S_{r}_{c}"
            net.add_station(station)

    for r in range(rows):
        for c in range(cols):
            here = f"S_{r}_{c}"
            mix = (r * 7 + c * 13 + seed * 31) % 97

            if c + 1 < cols:
                right = f"S_{r}_{c + 1}"
                line = LINES[(r + seed) % len(LINES)]
                time = 1 + mix % 9
                net.add_connection(here, right, time, line)

            if r + 1 < rows:
                down = f"S_{r + 1}_{c}"
                line = LINES[(c + seed) % len(LINES)]
                time = 1 + (mix * 3) % 9
                net.add_connection(here, down, time, line)

    return net
