"""Tests for Maze class functionality."""

import os
import sys

# NEW: lets this file run directly (python3 test_x.py); run.sh's PYTHONPATH still takes priority.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "solution", "src"))
import unittest

from maze import Maze, Position, CellType


class MazeTest(unittest.TestCase):

    def test_maze_dimensions(self) -> None:
        grid = [
            "#####",
            "#S..#",
            "#..E#",
            "#####",
        ]
        maze = Maze(grid)
        self.assertEqual(maze.rows, 4)
        self.assertEqual(maze.cols, 5)

    def test_find_start_and_end(self) -> None:
        grid = [
            "#####",
            "#S..#",
            "#..E#",
            "#####",
        ]
        maze = Maze(grid)
        self.assertEqual(maze.get_start(), Position(1, 1))
        self.assertEqual(maze.get_end(), Position(2, 3))

    def test_get_neighbors_open_space(self) -> None:
        grid = [
            "#####",
            "#S..#",
            "#...#",
            "#..E#",
            "#####",
        ]
        maze = Maze(grid)
        neighbors = maze.get_neighbors(Position(2, 2))
        positions = set(neighbors)
        self.assertIn(Position(1, 2), positions)
        self.assertIn(Position(3, 2), positions)
        self.assertIn(Position(2, 1), positions)
        self.assertIn(Position(2, 3), positions)

    def test_get_neighbors_near_wall(self) -> None:
        grid = [
            "#####",
            "#S#.#",
            "#...#",
            "#..E#",
            "#####",
        ]
        maze = Maze(grid)
        neighbors = maze.get_neighbors(Position(1, 1))
        positions = set(neighbors)
        self.assertNotIn(Position(1, 2), positions)
        self.assertIn(Position(2, 1), positions)

    def test_render_returns_original_grid(self) -> None:
        grid = [
            "#####",
            "#S..#",
            "#..E#",
            "#####",
        ]
        maze = Maze(grid)
        self.assertEqual(maze.render(), grid)

    # UNCOMMENTED (original test_maze.py lines 72-84).
    def test_render_with_path_preserves_start_end(self) -> None:
        grid = [
            "#####",
            "#S..#",
            "#..E#",
            "#####",
        ]
        maze = Maze(grid)
        path = [Position(1, 1), Position(1, 2), Position(1, 3), Position(2, 3)]
        rendered = maze.render_with_path(path)
        # FILLED IN (original test_maze.py line 82). Old: expected = "????"
        # One expected value is checked against both S and E, so both must render as "*": the path is drawn
        # over S and E (only walls are kept). The test name says "preserves", but its asserts say otherwise.
        expected = "*"
        self.assertEqual(rendered[1][1], expected)
        self.assertEqual(rendered[2][3], expected)

    # UNCOMMENTED (original test_maze.py lines 86-94).
    def test_find_start_in_top_row(self) -> None:
        grid = [
            "#S..E#",
            "#....#",
            "######",
        ]
        maze = Maze(grid)
        # FILLED IN (original test_maze.py line 93). Old: expected = "????"
        expected = Position(0, 1)  # catches Bug 1: the scan skipped row 0 and raised ValueError
        self.assertEqual(maze.get_start(), expected)

    # NEW: edge cases M2-M8 (not in the original tests).
    def test_find_cells_on_any_row(self) -> None:  # M2
        maze = Maze(["#E.#", "#..#", "#.S#"])
        self.assertEqual(maze.get_end(), Position(0, 1))
        self.assertEqual(maze.get_start(), Position(2, 2))

    def test_missing_start_or_end_raises(self) -> None:  # M3
        with self.assertRaises(ValueError):
            Maze(["#...#", "#..E#"])
        with self.assertRaises(ValueError):
            Maze(["#S..#", "#...#"])
        with self.assertRaises(ValueError):
            Maze([])

    def test_right_only_cell(self) -> None:  # M4, catches Bug 2
        maze = Maze(["#.#", "S>.", "#.E"])
        left, cell, right, above, below = (Position(1, 0), Position(1, 1), Position(1, 2),
                                           Position(0, 1), Position(2, 1))
        self.assertTrue(maze.is_valid_move(left, cell))  # enter moving right
        self.assertFalse(maze.is_valid_move(right, cell))  # enter moving left
        self.assertFalse(maze.is_valid_move(above, cell))  # enter moving down
        self.assertTrue(maze.is_valid_move(cell, right))  # leave moving right
        self.assertFalse(maze.is_valid_move(cell, below))  # leave moving down
        self.assertFalse(maze.is_valid_move(cell, left))  # leave moving left
        self.assertEqual(maze.get_neighbors(cell), [right])

    def test_left_only_cell(self) -> None:  # M5, catches Bug 2
        maze = Maze(["#.#", "S<.", "#.E"])
        left, cell, right, below = Position(1, 0), Position(1, 1), Position(1, 2), Position(2, 1)
        self.assertTrue(maze.is_valid_move(right, cell))  # enter moving left
        self.assertFalse(maze.is_valid_move(left, cell))  # enter moving right
        self.assertFalse(maze.is_valid_move(below, cell))  # enter moving up
        self.assertTrue(maze.is_valid_move(cell, left))  # leave moving left
        self.assertFalse(maze.is_valid_move(cell, right))  # leave moving right
        self.assertEqual(maze.get_neighbors(cell), [left])

    def test_moves_off_the_grid_are_invalid(self) -> None:  # M6
        maze = Maze(["S.", ".E"])
        self.assertFalse(maze.is_valid_move(Position(0, 0), Position(-1, 0)))
        self.assertFalse(maze.is_valid_move(Position(0, 0), Position(0, -1)))
        self.assertFalse(maze.is_valid_move(Position(1, 1), Position(2, 1)))
        self.assertFalse(maze.is_valid_move(Position(1, 1), Position(1, 2)))
        self.assertEqual(set(maze.get_neighbors(Position(1, 1))), {Position(0, 1), Position(1, 0)})

    def test_render_with_path_keeps_walls_and_original(self) -> None:  # M8
        maze = Maze(["#####", "#S#E#", "#####"])
        rendered = maze.render_with_path([Position(1, 1), Position(1, 2), Position(1, 3)])
        self.assertEqual(rendered[1], "#*#*#")  # the wall in the path stays a wall
        self.assertEqual(maze.render()[1], "#S#E#")  # rendering never changes the maze itself
        self.assertEqual(maze.render_with_path([]), maze.render())
        self.assertEqual(maze.get_cell(Position(1, 2)), CellType.WALL.value)


if __name__ == "__main__":
    unittest.main()
