"""A spreadsheet that evaluates cells containing numbers or '+' formulas.

setCell(cell_id, value) stores a number or a formula (a string starting with
'=', e.g. '=A1+B1' or '=A1+5'); getCell(cell_id) returns the cell's value.

Two implementations are provided:
  - SpreadsheetDFS (Part 1): lazy - getCell resolves dependencies on demand
    with depth-first search; O(subtree) per read.
  - Spreadsheet   (Part 2): eager - setCell recomputes the changed cell and
    its downstream dependents in topological order, so getCell is O(1).
Both detect circular references and report a cyclic cell's value as None.
"""

from collections import deque


def _is_int(text):
    """True if text parses as an integer literal."""
    # Time: O(len(text)). Space: O(1).
    try:
        int(text)
        return True
    except ValueError:
        return False


def _parse_formula(formula):
    """Parse '=A1+B1+5' into (referenced cells, sum of integer literals)."""
    # f = length of the formula string.
    # Time: O(f) - one split and scan. Space: O(r) - the r references.
    refs = set()
    const = 0
    for token in formula[1:].split("+"):   # formula[1:] drops the '='
        piece = token.strip()
        if piece == "":
            continue
        if _is_int(piece):
            const += int(piece)
        else:
            refs.add(piece)
    return refs, const


def _parse_cell_value(value):
    """Normalize a raw cell value into (referenced cells, constant). A plain
    number has no references; a formula (leading '=') is parsed."""
    # Time: O(len(value)). Space: O(r) references for a formula, else O(1).
    if isinstance(value, int):
        return set(), value
    text = value.strip()
    if text.startswith("="):
        return _parse_formula(text)
    return set(), int(text)   # a plain numeric string like "5"


# Approach (in plain terms):
#   Store each cell as either a number or a parsed formula (the cells it
#   references plus a constant). getCell walks the formula like a tree: to
#   value a cell, value each cell it points at (recursively) and add them up;
#   a plain number is the base case. Nothing is cached, so every read is fresh
#   but costs O(size of the dependency subtree).
#   A 'visiting' set tracks the cells on the current path; if we reach one
#   that is already on the path, the formulas loop, so we return None.
#   Data structures used:
#     - dict - maps each cell to a number or parsed formula.
#     - set - the cells on the current DFS path, for cycle
#       detection.
class SpreadsheetDFS:
    """Part 1: lazy evaluation. getCell resolves dependencies on demand with
    DFS and detects circular references (returns None for a cyclic cell)."""

    def __init__(self):
        # Time: O(1), Space: O(1) - one map of cell -> number or (refs, const).
        self._cells = {}

    def setCell(self, cell_id, value):
        """Store a number or a formula for a cell (parsed once, up front)."""
        # Time: O(f) to parse a length-f formula. Space: O(r) references.
        refs, const = _parse_cell_value(value)
        if refs:
            self._cells[cell_id] = (refs, const)
        else:
            self._cells[cell_id] = const

    def getCell(self, cell_id):
        """Evaluate a cell now via DFS; None if it lies on a cycle."""
        # V, E = cells and edges reachable from cell_id.
        # Time: O(V + E) - visits each reachable cell/edge once.
        # Space: O(V) - the recursion stack and the 'visiting' set.
        return self._eval(cell_id, set())

    def _eval(self, cell_id, visiting):
        """Recursively value a cell; None if a cycle is found on this path."""
        # Time: O(V + E) across the traversal. Space: O(V) call depth.
        entry = self._cells.get(cell_id, 0)
        if isinstance(entry, int):
            return entry              # a plain number (or an unset cell -> 0)
        if cell_id in visiting:
            return None               # cycle: cell_id is already on the path
        refs, const = entry
        visiting.add(cell_id)
        total = const
        cyclic = False
        for ref in refs:
            value = self._eval(ref, visiting)
            if value is None:
                cyclic = True
                break
            total += value
        visiting.discard(cell_id)
        if cyclic:
            return None
        return total


# Approach (in plain terms):
#   To make getCell instant, we do the work when a cell is SET, not when it is
#   read. We keep two wiring diagrams: for each cell, which cells it reads (its
#   formula's references) and which cells read IT (its dependents). getCell
#   just returns a cached number.
#   When a cell changes, only that cell and everything downstream of it can
#   change, so we recompute exactly that set - in dependency order (a cell
#   after all the cells it reads) using a topological sort. That order means a
#   shared upstream cell is recomputed once, before any cell that needs it.
#   If some cells in that set can never be ordered, they form a loop, so we
#   mark them None (a circular-reference indicator).
#   Data structures used:
#     - dicts - forward references, constants, and reverse
#       dependents (adjacency lists).
#     - dict - a value cache that makes getCell O(1).
#     - deque - Kahn's topological sort queue that orders the
#       recompute.
class Spreadsheet:
    """Part 2: O(1) getCell. All work happens in setCell, which recomputes the
    changed cell and its downstream dependents in topological order and caches
    the results. Circular references are cached as None."""

    def __init__(self):
        # Time: O(1), Space: O(1) - empty maps to start.
        self._refs = {}         # cell -> set of cells it references
        self._const = {}        # cell -> constant part of its value
        self._dependents = {}   # cell -> set of cells that reference it
        self._value = {}        # cell -> cached value (None if cyclic)

    def setCell(self, cell_id, value):
        """Store a value/formula and refresh affected cached values."""
        # a = affected cells (this cell + its transitive dependents),
        # e = dependency edges among them.
        # Time: O(a + e) - rewire O(refs) plus a topological recompute.
        # Space: O(a) - the affected set and the queue.
        refs, const = _parse_cell_value(value)
        old_refs = self._refs.get(cell_id, set())
        self._rewire(cell_id, old_refs, refs)
        self._refs[cell_id] = refs
        self._const[cell_id] = const
        self._recompute(cell_id)

    def getCell(self, cell_id):
        """Return the cached value (0 if unset, None if part of a cycle)."""
        # Time: O(1) - a single dictionary lookup. Space: O(1).
        return self._value.get(cell_id, 0)

    def _rewire(self, cell_id, old_refs, new_refs):
        """Update reverse edges: drop cell_id from old references' dependent
        sets and add it to the new ones."""
        # Time: O(|old_refs| + |new_refs|). Space: O(1) beyond the sets.
        for ref in old_refs:
            dependents = self._dependents.get(ref)
            if dependents is not None:
                dependents.discard(cell_id)
        for ref in new_refs:
            self._dependents.setdefault(ref, set()).add(cell_id)

    def _collect_affected(self, start):
        """All cells whose value may change: start plus everything downstream
        (its transitive dependents)."""
        # Time: O(a + e) over a affected cells and e edges. Space: O(a).
        affected = set()
        stack = [start]
        while stack:
            cell = stack.pop()
            if cell in affected:
                continue
            affected.add(cell)
            for dependent in self._dependents.get(cell, ()):
                if dependent not in affected:
                    stack.append(dependent)
        return affected

    def _recompute(self, changed):
        """Recompute affected cells in dependency order; any that cannot be
        ordered form a cycle and are cached as None."""
        # a = affected cells, e = edges among them.
        # Time: O(a + e) - Kahn's topological sort. Space: O(a).
        affected = self._collect_affected(changed)
        indegree = {}
        for cell in affected:
            indegree[cell] = 0
        for cell in affected:
            for ref in self._refs.get(cell, ()):
                if ref in affected:
                    indegree[cell] += 1
        ready = deque()
        for cell in affected:
            if indegree[cell] == 0:
                ready.append(cell)
        processed = 0
        while ready:
            cell = ready.popleft()
            processed += 1
            self._value[cell] = self._compute(cell)
            for dependent in self._dependents.get(cell, ()):
                if dependent in affected:
                    indegree[dependent] -= 1
                    if indegree[dependent] == 0:
                        ready.append(dependent)
        if processed < len(affected):
            for cell in affected:       # leftover cells form a cycle
                if indegree[cell] > 0:
                    self._value[cell] = None

    def _compute(self, cell):
        """Value from cached references; None if any reference is cyclic."""
        # Time: O(r) over the cell's r references. Space: O(1).
        total = self._const.get(cell, 0)
        for ref in self._refs.get(cell, ()):
            value = self._value.get(ref, 0)
            if value is None:
                return None             # depends on a cyclic cell
            total += value
        return total


if __name__ == "__main__":
    # ----- Part 2: O(1) getCell (the class the example uses) -----
    sheet = Spreadsheet()
    sheet.setCell("A1", 1)
    sheet.setCell("A2", 2)
    sheet.setCell("A3", "=A1+A2")
    sheet.setCell("A4", "=A3+A2")
    sheet.setCell("A5", "=A3+A4")
    print(sheet.getCell("A5"))     # 8   (A3=3, A4=5, A5=8)

    sheet.setCell("A1", 10)        # update ripples downstream
    print(sheet.getCell("A5"))     # 26  (A3=12, A4=14, A5=26)

    print(sheet.getCell("Z9"))     # 0   (unset cell)

    sheet.setCell("B1", "=B2+1")   # introduce a circular reference
    sheet.setCell("B2", "=B1+1")
    print(sheet.getCell("B1"))     # None  (cycle)

    sheet.setCell("B1", 5)         # break the cycle -> values recover
    print(sheet.getCell("B2"))     # 6

    # ----- Part 1: lazy DFS getCell -----
    dfs = SpreadsheetDFS()
    dfs.setCell("A1", 1)
    dfs.setCell("A2", 2)
    dfs.setCell("A3", "=A1+A2")
    dfs.setCell("A4", "=A3+A2")
    dfs.setCell("A5", "=A3+A4")
    print(dfs.getCell("A5"))       # 8
    dfs.setCell("A1", 10)
    print(dfs.getCell("A5"))       # 26

    dfs.setCell("C1", "=C2+1")     # circular reference
    dfs.setCell("C2", "=C1+1")
    print(dfs.getCell("C1"))       # None  (cycle)
