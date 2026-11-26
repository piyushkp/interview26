"""You'll implement this."""

from typing import List, Optional

from maze import Maze, Position

# NEW: a queue for BFS, and type hints for the parent map and the cells on the current path.
from collections import deque
from typing import Dict, Set

# V = walkable cells reachable from S (at most R·C), E = legal moves between them (at most 4V),
# P = simple paths from S (exponential in V), L = cells on a path.


class Solver:
    def __init__(self, maze: Maze) -> None:
        self.maze = maze

    # AI prompt: "Solve this with BFS, treating each open cell as a node linked to the cells get_neighbors
    #   returns, since every move costs one step. Use a queue and a parent map, marking cells when queued.
    #   Return the path from start to end, as short as the brute force's, or None if the end is unreachable."
    # Optimized: BFS from S, marking each cell when it is queued. Time O(V + E), Space O(V)
    def solve(self) -> Optional[List[Position]]:
        # CHANGED (original solver.py lines 12-13): implemented. Old code:
        #     pass
        start = self.maze.get_start()
        parent: Dict[Position, Optional[Position]] = {start: None}  # visited set and path links in one map
        queue = deque([start])
        while queue:  # each cell is queued at most once: O(V)
            pos = queue.popleft()
            if self.maze.is_end(pos):
                return self._build_path(parent, pos)
            for nxt in self.maze.get_neighbors(pos):  # up to 4 moves; one-way cells already filtered
                if nxt not in parent:  # mark when queued, not when popped, so no cell is queued twice
                    parent[nxt] = pos
                    queue.append(nxt)
        return None

    # NEW: follows the parent links back from E to S, then reverses them. Time O(L), Space O(L)
    def _build_path(self, parent: Dict[Position, Optional[Position]], end: Position) -> List[Position]:
        path: List[Position] = []
        pos: Optional[Position] = end
        while pos is not None:
            path.append(pos)
            pos = parent[pos]
        path.reverse()
        return path

    # NEW: brute force kept so tests can compare it with the optimized solve.
    # AI prompt: "Solve this with backtracking: from the start, walk every simple path using get_neighbors,
    #   so one-way cells are respected, and undo each step after exploring it. Keep the shortest path that
    #   reaches the end, or return None if none does."
    # Brute force: try every simple path from S, keep the shortest. Time O(P·L), Space O(V) recursion depth
    def solve_brute_force(self) -> Optional[List[Position]]:
        best: Optional[List[Position]] = None
        path: List[Position] = []
        on_path: Set[Position] = set()

        def explore(pos: Position) -> None:
            nonlocal best
            path.append(pos)
            on_path.add(pos)
            if self.maze.is_end(pos):
                if best is None or len(path) < len(best):  # first shortest path found wins a tie
                    best = list(path)
            else:
                for nxt in self.maze.get_neighbors(pos):  # every branch: P paths in total
                    if nxt not in on_path:  # a simple path never revisits a cell
                        explore(nxt)
            path.pop()  # undo, so other paths can use this cell
            on_path.discard(pos)

        explore(self.maze.get_start())
        return best
