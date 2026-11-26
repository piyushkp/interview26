# NEW FILE: not in the original. Tests the solution-only method (solve_brute_force), scale and concurrency.
"""Solution-only checks: BFS must match the brute force, scale, and be thread-safe."""

import os
import sys

# NEW: lets this file run directly (python3 test_x.py); run.sh's PYTHONPATH still takes priority.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "solution", "src"))
import random
import threading
import time
import unittest

from maze import Maze, Position
from mazes import get_directional_maze, get_directional_maze_blocked, get_huge_maze, get_small_maze
from solver import Solver
from test_solver import assert_valid_path


def random_maze(rng: random.Random) -> Maze:
    rows, cols = rng.randint(1, 5), rng.randint(2, 5)
    cells = [rng.choices("#.><", weights=(30, 50, 10, 10))[0] for _ in range(rows * cols)]
    s, e = rng.sample(range(rows * cols), 2)
    cells[s], cells[e] = "S", "E"
    return Maze(["".join(cells[r * cols:(r + 1) * cols]) for r in range(rows)])


class SolutionOnlyTest(unittest.TestCase):
    def test_bfs_matches_brute_force(self) -> None:  # X1
        rng = random.Random(11)
        reachable = 0
        for _ in range(1500):
            maze = random_maze(rng)
            solver = Solver(maze)
            fast, brute = solver.solve(), solver.solve_brute_force()
            self.assertEqual(fast is None, brute is None, maze.render())
            if fast is not None:
                reachable += 1
                assert_valid_path(self, maze, fast)
                assert_valid_path(self, maze, brute)
                self.assertEqual(len(fast), len(brute), maze.render())
        self.assertGreater(reachable, 300)  # both branches are well exercised

    def test_brute_force_edge_cases(self) -> None:  # X2
        self.assertIsNone(Solver(get_directional_maze_blocked()).solve_brute_force())
        self.assertEqual(len(Solver(get_directional_maze()).solve_brute_force()), 9)
        self.assertEqual(len(Solver(get_small_maze()).solve_brute_force()), 9)
        self.assertEqual(Solver(Maze(["SE"])).solve_brute_force(), [Position(0, 0), Position(0, 1)])
        self.assertIsNone(Solver(Maze(["S#E"])).solve_brute_force())

    def test_scale_300x300(self) -> None:  # X3
        maze = get_huge_maze(300, seed=7)
        start = time.time()
        path = Solver(maze).solve()
        elapsed = time.time() - start
        assert_valid_path(self, maze, path)
        self.assertLess(elapsed, 2.0, f"took {elapsed:.2f}s")

    def test_concurrent_solves_are_consistent(self) -> None:  # X4
        maze = get_huge_maze(100, seed=42)
        expected = Solver(maze).solve()
        results = []

        def worker() -> None:
            for _ in range(5):
                results.append(Solver(maze).solve())

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(len(results), 40)
        self.assertTrue(all(r == expected for r in results))
        self.assertEqual(maze.render(), get_huge_maze(100, seed=42).render())  # the shared maze is untouched


if __name__ == "__main__":
    unittest.main()
