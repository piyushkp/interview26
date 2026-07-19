"""Compute Plant Infection Time (multi-source BFS, a.k.a. "Rotting Oranges").

Grid values: 0 = empty ground, 1 = healthy plant, 2 = infected plant,
-1 = wall/blocked. Each minute every infected plant infects its orthogonally
adjacent healthy plants. Return the minutes until no plant can be infected, or
-1 if some healthy plant is unreachable, or 0 if there are no healthy plants to
begin with.
"""
from collections import deque


# Approach (in plain terms):
#   Picture every infected plant as a small fire that all start spreading at
#   the same moment. Each minute, every fire jumps to the healthy plants
#   directly next to it (up, down, left, right). We flood outward one ring at a
#   time and count the minutes as we go, stopping once no healthy plant can
#   catch fire. If every healthy plant was reached, the answer is the minutes
#   it took; if a plant is walled off and can never be reached, we return -1;
#   and if there were no healthy plants to begin with, it takes 0 minutes.
#   Data structures used:
#     - deque - the BFS frontier; O(1) popleft spreads outward
#       level-by-level (minute-by-minute).
#     - grid (2D list) - reused as the visited marker; overwriting
#       infected cells avoids a separate visited set.
def infection_time(grid):
    """Minutes until every healthy plant is infected via multi-source BFS,
    -1 if some healthy plant is unreachable, or 0 if none need infecting."""
    # m = number of rows, n = number of columns.
    # Time:  O(m * n) - each cell is enqueued and visited at most once.
    # Space: O(m * n) - the BFS queue can hold up to every cell.
    if not grid or not grid[0]:
        return 0  # no plants at all -> nothing to infect
    m, n = len(grid), len(grid[0])
    queue = deque()
    healthy = 0

    # Seed the BFS with every initially-infected plant; count healthy ones.
    for r in range(m):
        for c in range(n):
            if grid[r][c] == 2:
                queue.append((r, c))
            elif grid[r][c] == 1:
                healthy += 1
    if healthy == 0:
        return 0  # nothing healthy -> 0 minutes

    dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))
    minutes = 0

    # Expand the infection one layer (one minute) at a time.
    while queue and healthy > 0:
        for _ in range(len(queue)):
            r, c = queue.popleft()
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] == 1:
                    grid[nr][nc] = 2  # infect (also marks visited)
                    healthy -= 1
                    queue.append((nr, nc))
        minutes += 1

    # Any healthy plant left was unreachable.
    return minutes if healthy == 0 else -1


if __name__ == "__main__":
    # Test 1: classic spread from one corner reaches every plant in 4 minutes.
    print(infection_time([[2, 1, 1], [1, 1, 0], [0, 1, 1]]))     # 4

    # Test 2: walls trap some healthy plants -> unreachable, so -1.
    print(infection_time([[2, 1, -1], [-1, 1, 1], [1, -1, 1]]))  # -1

    # Test 3: no healthy plants (only infected/empty) -> 0 minutes.
    print(infection_time([[0, 2, 0]]))                           # 0

    # Test 4: completely empty grid -> nothing to infect -> 0.
    print(infection_time([]))                                    # 0

    # Test 5: grid with only an empty row -> still nothing to infect -> 0.
    print(infection_time([[]]))                                  # 0

    # Test 6: healthy plants but no infection source -> all unreachable -> -1.
    print(infection_time([[1, 1], [1, 1]]))                      # -1

    # Test 7: every plant already infected -> 0 minutes needed.
    print(infection_time([[2, 2], [2, 2]]))                      # 0

    # Test 8: a wall seals off the lone healthy plant -> -1.
    print(infection_time([[2, -1, 1]]))                          # -1

    # Test 9: single infected cell, nothing healthy -> 0.
    print(infection_time([[2]]))                                 # 0

    # Test 10: single healthy cell with no source -> unreachable -> -1.
    print(infection_time([[1]]))                                 # -1

    # Test 11: single empty cell -> 0.
    print(infection_time([[0]]))                                 # 0
