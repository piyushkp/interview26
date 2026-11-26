"""Tests for Solver implementation."""

import os
import sys

# NEW: lets this file run directly (python3 test_x.py); run.sh's PYTHONPATH still takes priority.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "solution", "src"))
import time
import unittest

from mazes import (
    get_simple_maze,
    get_small_maze,
    get_medium_maze,
    get_large_maze,
    get_huge_maze,
    get_directional_maze,
    get_directional_maze_blocked,
    get_anywhere_start_end_maze,
)
from solver import Solver

# NEW: needed by the new tests below.
from maze import Maze, Position


# NEW: a path must start at S, end at E, never repeat a cell, and only make legal moves.
def assert_valid_path(test: unittest.TestCase, maze: Maze, path) -> None:
    test.assertEqual(path[0], maze.get_start())
    test.assertEqual(path[-1], maze.get_end())
    test.assertEqual(len(set(path)), len(path))
    for a, b in zip(path, path[1:]):
        test.assertEqual(abs(a.row - b.row) + abs(a.col - b.col), 1, (a, b))
        test.assertTrue(maze.is_valid_move(a, b), (a, b))


class SolverTest(unittest.TestCase):

    def test_solve_simple_maze(self) -> None:
        solver = Solver(get_simple_maze())
        path = solver.solve()
        # UNCOMMENTED (original test_solver.py lines 24-26).
        self.assertIsNotNone(path)
        self.assertEqual(path[0], solver.maze.get_start())
        self.assertEqual(path[-1], solver.maze.get_end())

    # UNCOMMENTED (original test_solver.py lines 28-37).
    def test_solve_medium_maze_efficiency(self) -> None:
        solver = Solver(get_medium_maze())
        t0 = time.time()
        path = solver.solve()
        elapsed = time.time() - t0
        self.assertIsNotNone(path)
        self.assertEqual(path[0], solver.maze.get_start())
        self.assertEqual(path[-1], solver.maze.get_end())
        expected_time = 0.5
        self.assertLess(elapsed, expected_time)

    # UNCOMMENTED (original test_solver.py lines 39-51).
    def test_solve_large_maze_efficiency(self) -> None:
        trials = [
            (get_large_maze(20, seed=1), 1.0),
            (get_large_maze(25, seed=2), 2.0),
            (get_large_maze(30, seed=3), 3.0),
        ]
        for maze, max_time in trials:
            solver = Solver(maze)
            t0 = time.time()
            path = solver.solve()
            elapsed = time.time() - t0
            self.assertIsNotNone(path, f"No path found in {maze.rows}x{maze.cols} maze")
            self.assertLess(elapsed, max_time, f"Took {elapsed:.2f}s, expected < {max_time}s")

    # UNCOMMENTED (original test_solver.py lines 53-58).
    def test_directional_passage_right_only(self) -> None:
        solver = Solver(get_directional_maze())
        path = solver.solve()
        self.assertIsNotNone(path)
        # FILLED IN (original test_solver.py line 57). Old: expected_length = "????"
        expected_length = 9  # S down the left column and along the bottom; the top route is also 9 cells
        self.assertEqual(len(path), expected_length)

    # UNCOMMENTED (original test_solver.py lines 60-64).
    def test_directional_passage_blocked(self) -> None:
        solver = Solver(get_directional_maze_blocked())
        path = solver.solve()
        # FILLED IN (original test_solver.py line 63). Old: expected = "????"
        expected = None  # catches Bug 2: the only way down crosses "<" moving right, so E is unreachable
        self.assertEqual(path, expected)

    # UNCOMMENTED (original test_solver.py lines 66-73).
    def test_anywhere_start_end(self) -> None:
        solver = Solver(get_anywhere_start_end_maze())
        path = solver.solve()
        self.assertIsNotNone(path)
        self.assertEqual(path[0], solver.maze.get_start())
        self.assertEqual(path[-1], solver.maze.get_end())
        # FILLED IN (original test_solver.py line 72). Old: expected_length = "????"
        expected_length = 5  # S up the left column, then right to E; going around the right side is 9
        self.assertEqual(len(path), expected_length)

    # UNCOMMENTED (original test_solver.py lines 75-85).
    def test_huge_maze_75x75(self) -> None:
        maze = get_huge_maze(75, seed=42)
        solver = Solver(maze)
        t0 = time.time()
        path = solver.solve()
        elapsed = time.time() - t0
        self.assertIsNotNone(path, "No path found in 75x75 maze")
        self.assertEqual(path[0], solver.maze.get_start())
        self.assertEqual(path[-1], solver.maze.get_end())
        expected_time = 0.3
        self.assertLess(elapsed, expected_time, f"75x75: {elapsed:.3f}s, need < {expected_time}s")

    # UNCOMMENTED (original test_solver.py lines 87-97).
    def test_huge_maze_100x100(self) -> None:
        maze = get_huge_maze(100, seed=42)
        solver = Solver(maze)
        t0 = time.time()
        path = solver.solve()
        elapsed = time.time() - t0
        self.assertIsNotNone(path, "No path found in 100x100 maze")
        self.assertEqual(path[0], solver.maze.get_start())
        self.assertEqual(path[-1], solver.maze.get_end())
        expected_time = 0.5
        self.assertLess(elapsed, expected_time, f"100x100: {elapsed:.3f}s, need < {expected_time}s")

    # UNCOMMENTED (original test_solver.py lines 99-109).
    def test_huge_maze_150x150(self) -> None:
        maze = get_huge_maze(150, seed=99)
        solver = Solver(maze)
        t0 = time.time()
        path = solver.solve()
        elapsed = time.time() - t0
        self.assertIsNotNone(path, "No path found in 150x150 maze")
        self.assertEqual(path[0], solver.maze.get_start())
        self.assertEqual(path[-1], solver.maze.get_end())
        expected_time = 1.0
        self.assertLess(elapsed, expected_time, f"150x150: {elapsed:.3f}s, need < {expected_time}s")

    # NEW: edge cases V6-V10 (not in the original tests).
    def test_start_next_to_end(self) -> None:  # V6
        maze = Maze(["#####", "#SE.#", "#####"])
        self.assertEqual(Solver(maze).solve(), [Position(1, 1), Position(1, 2)])

    def test_walled_in_start_returns_none(self) -> None:  # V7
        self.assertIsNone(Solver(Maze(["#####", "#S#E#", "#####"])).solve())

    def test_given_mazes_give_valid_shortest_paths(self) -> None:  # V8
        expected = {get_simple_maze: 5, get_small_maze: 9, get_medium_maze: 26,
                    get_directional_maze: 9, get_anywhere_start_end_maze: 5}
        for make, length in expected.items():
            maze = make()
            path = Solver(maze).solve()
            assert_valid_path(self, maze, path)
            self.assertEqual(len(path), length, make.__name__)

    def test_big_mazes_reach_the_shortest_possible_length(self) -> None:  # V9
        # S is the top-left cell and E the bottom-right one, so no path can be shorter than the
        # Manhattan distance + 1 cells. Reaching that bound proves the path is shortest.
        for maze in (get_large_maze(20, seed=1), get_large_maze(30, seed=3), get_huge_maze(75, seed=42)):
            path = Solver(maze).solve()
            assert_valid_path(self, maze, path)
            start, end = maze.get_start(), maze.get_end()
            self.assertEqual(len(path), abs(end.row - start.row) + abs(end.col - start.col) + 1)

    def test_start_in_top_row(self) -> None:  # V10, needs Bug 1 fixed
        maze = Maze(["#S..E#", "#....#", "######"])
        self.assertEqual(Solver(maze).solve(), [Position(0, c) for c in range(1, 5)])


if __name__ == "__main__":
    unittest.main()
