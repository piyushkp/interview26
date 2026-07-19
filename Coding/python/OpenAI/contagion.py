"""Simulate disease contagion on a grid where infected cells spread to
healthy neighbors and, after enough infectious rounds, recover into a
permanently immune state.

  - simulate_contagion(grid, rounds, recovery_time): run the model for a
    fixed number of rounds and return the resulting grid.

Cell values: 0 empty, 1 healthy, 2 infected, 3 immune. Infection spreads to
the four orthogonal neighbors. An infected cell that has completed
`recovery_time` infectious rounds becomes immune.
"""


# The four orthogonal moves: down, up, right, left.
_DIRECTIONS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def _copy_grid(grid):
    """Return an independent copy of a 2D grid so the caller's grid is never
    mutated."""
    # rows = number of rows, cols = number of columns.
    # Time:  O(rows * cols) - visits every cell once.
    # Space: O(rows * cols) - the new grid holds every cell.
    copy = []
    for row in grid:
        new_row = []
        for value in row:
            new_row.append(value)
        copy.append(new_row)
    return copy


def _make_age_grid(grid):
    """Return a 2D grid of zeros shaped like `grid`; age[r][c] counts the
    infectious rounds an infected cell has completed."""
    # rows = number of rows, cols = number of columns.
    # Time:  O(rows * cols) - one zero written per cell.
    # Space: O(rows * cols) - the age grid holds every cell.
    age = []
    for row in grid:
        new_row = []
        for _ in range(len(row)):
            new_row.append(0)
        age.append(new_row)
    return age


# Approach (in plain terms):
#   Picture a map of squares: some hold a sick person, some a healthy
#   person, some are empty, and some hold someone who already recovered and
#   can never get sick again. Each round is like one day.
#     - Every square that is sick at the start of the day coughs on its four
#       up/down/left/right neighbors; any healthy neighbor is marked to fall
#       sick.
#     - Every sick square also grows one day older in its illness. Once it
#       has been sick for `recovery_time` days it is marked to recover.
#   We decide everything from the board as it looked at the START of the day,
#   then apply all new infections and recoveries together at the day's end.
#   So a square infected today cannot spread until tomorrow, and a square
#   still coughs on the very day it recovers.
#   Data structures used:
#     - a copied 2D grid - the board we evolve without touching the caller's
#       grid.
#     - a parallel 2D age grid - counts infectious rounds each cell has
#       completed so we know when it recovers.
#     - a per-round set of newly infected cells - dedupes a healthy cell
#       reached by two sick neighbors in the same round.
#     - a tuple of direction deltas - the four orthogonal moves.
def simulate_contagion(grid, rounds, recovery_time):
    """Run the contagion model for `rounds` rounds and return the resulting
    grid (a new list of lists; the input grid is not modified)."""
    # rows, cols = grid dimensions; k = number of rounds.
    # Time:  O(k * rows * cols) - each round scans every cell once.
    # Space: O(rows * cols) - the working grid plus the parallel age grid.
    if not grid:
        return grid
    work = _copy_grid(grid)
    age = _make_age_grid(grid)
    rows = len(work)
    cols = len(work[0])

    round_index = 0
    while round_index < rounds:
        newly = set()
        becoming_immune = []
        for row in range(rows):
            for col in range(cols):
                if work[row][col] != 2:
                    continue
                for d_row, d_col in _DIRECTIONS:
                    n_row = row + d_row
                    n_col = col + d_col
                    in_bounds = 0 <= n_row < rows and 0 <= n_col < cols
                    if in_bounds and work[n_row][n_col] == 1:
                        newly.add((n_row, n_col))
                age[row][col] += 1
                if age[row][col] >= recovery_time:
                    becoming_immune.append((row, col))
        # Apply after the full scan so the round is simultaneous.
        for row, col in becoming_immune:
            work[row][col] = 3
        for n_row, n_col in newly:
            work[n_row][n_col] = 2
            age[n_row][n_col] = 0
        round_index += 1
    return work


if __name__ == "__main__":
    # Test 1: the worked example. A single row; infection spreads outward
    # while the earliest cells recover into immunity. The board evolves
    # [1,2,1,1] -> [2,2,2,1] -> [2,3,2,2] -> [3,3,3,2].
    original = [[1, 2, 1, 1]]
    print(simulate_contagion(original, rounds=3, recovery_time=2))
    # -> [[3, 3, 3, 2]]

    # Test 2: the input grid is never mutated by the simulation.
    print(original)
    # -> [[1, 2, 1, 1]]

    # Test 3: rounds == 0 returns an unchanged copy of the grid.
    print(simulate_contagion([[1, 2, 1, 1]], rounds=0, recovery_time=2))
    # -> [[1, 2, 1, 1]]

    # Test 4: an empty grid is returned as-is.
    print(simulate_contagion([], rounds=5, recovery_time=3))
    # -> []

    # Test 5: one round from a center infection spreads to the four
    # orthogonal neighbors (recovery_time high, so nobody recovers yet).
    grid_a = [
        [1, 1, 1],
        [1, 2, 1],
        [1, 1, 1],
    ]
    print(simulate_contagion(grid_a, rounds=1, recovery_time=5))
    # -> [[1, 2, 1], [2, 2, 2], [1, 2, 1]]

    # Test 6: two rounds with recovery_time == 1. The wave moves outward -
    # the first ring recovers (3) while the corners become infected (2).
    grid_b = [
        [1, 1, 1],
        [1, 2, 1],
        [1, 1, 1],
    ]
    print(simulate_contagion(grid_b, rounds=2, recovery_time=1))
    # -> [[2, 3, 2], [3, 3, 3], [2, 3, 2]]
