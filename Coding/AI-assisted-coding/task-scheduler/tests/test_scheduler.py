"""Tests for Scheduler. All of this is just boilerplate to make test cases compact and understandable."""

import os
import sys

# NEW: lets this file run directly (python3 test_x.py); run.sh's PYTHONPATH still takes priority.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "solution", "src"))
import unittest

from scheduler import CycleError, Scheduler
from task import Task


class SchedulerTest(unittest.TestCase):

    def test_valid_linear_chain(self) -> None:
        tasks = [
            Task("a", 3, []),
            Task("b", 2, ["a"]),
            Task("c", 1, ["b"]),
        ]
        scheduler = Scheduler(tasks)
        ready = scheduler.get_ready_tasks(set())
        self.assertEqual([t.name for t in ready], ["a"])
        self.assertEqual(scheduler.earliest_start("b", {"a": 3}), 3)

    def test_direct_cycle_detected(self) -> None:
        tasks = [
            Task("a", 1, ["b"]),
            Task("b", 1, ["a"]),
        ]
        with self.assertRaises(CycleError):
            Scheduler(tasks)

    def test_multiple_ready(self) -> None:
        tasks = [
            Task("a", 2, []),
            Task("b", 3, []),
            Task("c", 1, ["a", "b"]),
        ]
        scheduler = Scheduler(tasks)
        ready = scheduler.get_ready_tasks(set())
        names = sorted(t.name for t in ready)
        self.assertEqual(names, ["a", "b"])

    # UNCOMMENTED (original test_scheduler.py lines 41-52).
    def test_transitive_cycle(self) -> None:
        tasks = [
            Task("a", 1, ["c"]),
            Task("b", 1, ["a"]),
            Task("c", 1, ["b"]),
        ]
        # FILLED IN (original test_scheduler.py line 47). Old: raises_error = "????"
        raises_error = True  # catches Bug 1: a -> c -> b -> a is a cycle, just not a two-task one
        try:
            Scheduler(tasks)
            self.assertEqual(raises_error, False)
        except CycleError:
            self.assertEqual(raises_error, True)

    # UNCOMMENTED (original test_scheduler.py lines 54-62).
    def test_earliest_start_multiple_deps(self) -> None:
        tasks = [
            Task("a", 3, []),
            Task("b", 5, []),
            Task("c", 2, ["a", "b"]),
        ]
        scheduler = Scheduler(tasks)
        result = scheduler.earliest_start("c", {"a": 3, "b": 5})
        # FILLED IN (original test_scheduler.py line 62). Old: self.assertEqual(result, "????")
        self.assertEqual(result, 5)  # catches Bug 2: c waits for its last dependency, b, which ends at 5


    # NEW: edge cases S5-S7 (not in the original tests).
    def test_self_dependency_is_a_cycle(self) -> None:  # S5
        with self.assertRaises(CycleError):
            Scheduler([Task("a", 1, ["a"])])

    def test_diamond_is_not_a_cycle_but_a_loop_behind_it_is(self) -> None:  # S6
        diamond = [Task("a", 1, []), Task("b", 1, ["a"]), Task("c", 1, ["a"]), Task("d", 1, ["b", "c"])]
        Scheduler(diamond)  # shared dependencies are fine
        with self.assertRaises(CycleError):
            Scheduler(diamond + [Task("e", 1, ["d", "h"]), Task("f", 1, ["e"]), Task("g", 1, ["f"]),
                                 Task("h", 1, ["g"])])  # e -> h -> g -> f -> e
        with self.assertRaises(ValueError):
            Scheduler([Task("a", 1, ["missing"])])  # unknown dependency is still reported first

    def test_earliest_start_edges(self) -> None:  # S7
        scheduler = Scheduler([Task("a", 3, []), Task("b", 0, []), Task("c", 2, ["a", "b"])])
        self.assertEqual(scheduler.earliest_start("a", {}), 0)
        self.assertEqual(scheduler.earliest_start("c", {"a": 3, "b": 0}), 3)
        self.assertEqual(scheduler.earliest_start("c", {"a": 4, "b": 4}), 4)
        self.assertEqual([t.name for t in scheduler.get_ready_tasks({"a"})], ["b"])  # finished tasks are skipped
        self.assertEqual([t.name for t in scheduler.get_ready_tasks({"a", "b"})], ["c"])

if __name__ == "__main__":
    unittest.main()
