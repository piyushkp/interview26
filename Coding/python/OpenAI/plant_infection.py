"""Compute Plant Infection Time (multi-source BFS, a.k.a. "Rotting Oranges").

Grid values: 0 = empty ground, 1 = healthy plant, 2 = infected plant,
-1 = wall/blocked. Each minute every infected plant infects its orthogonally
adjacent healthy plants. Return the minutes until no plant can be infected, or
-1 if some healthy plant is unreachable, or 0 if there are no healthy plants to
begin with.
"""
from collections import deque


def infection_time(grid):
    """Time:  O(m * n) - each cell is enqueued/visited at most once.
    Space: O(m * n) - the BFS frontier in the worst case."""
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
    print(infection_time([[2, 1, 1], [1, 1, 0], [0, 1, 1]]))     # 4
    print(infection_time([[2, 1, -1], [-1, 1, 1], [1, -1, 1]]))  # -1
    print(infection_time([[0, 2, 0]]))                           # 0
