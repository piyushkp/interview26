"""A small spreadsheet whose cells are literal ints or two-cell adders.

Overview:
  Cells are stored by name. A cell is either a literal integer or a
  formula that adds the values of two other cells (referenced by name).
  Reading a cell resolves the whole chain of references beneath it.
  Results are cached for speed, and editing a cell surgically invalidates
  only the cells whose values could have changed.

Interface:
  - Cell.literal(value) -> Cell: a cell holding the integer `value`.
  - Cell.formula(child1, child2) -> Cell: a cell equal to
    value(child1) + value(child2), where child1/child2 are cell names.
  - Spreadsheet() -> a new, empty sheet.
  - setCell(key, cell) -> None: define or redefine the cell named `key`.
  - getCellValue(key) -> int: the literal value, or the sum for a formula,
    resolved recursively through referenced cells.

Semantics and rules:
  - Evaluation is memoized: repeated reads of an unchanged cell are O(1).
  - setCell invalidates the cached value of `key` and every cell that
    transitively depends on it, so later reads stay correct while
    untouched cells are not recomputed.
  - Redefining a cell rewires its dependency edges before invalidating.

Errors (both raise EvaluationError):
  - a formula references a cell name that was never set (unknown cell);
  - the references form a cycle, e.g. A -> B -> A.

Example:
  setCell("A", Cell.literal(10)); setCell("B", Cell.literal(5))
  setCell("C", Cell.formula("A", "B")); getCellValue("C") -> 15
  setCell("A", Cell.literal(20)); getCellValue("C") -> 25
"""


class EvaluationError(Exception):
    """Raised when a cell cannot be evaluated (unknown cell or a cycle)."""


class Cell:
    """A literal integer cell or a formula adding two referenced cells."""

    def __init__(self, value, child1, child2, is_literal):
        # Time: O(1), Space: O(1).
        self.value = value
        self.child1 = child1
        self.child2 = child2
        self.is_literal = is_literal

    @staticmethod
    def literal(value):
        """A cell holding the integer value directly."""
        # Time: O(1), Space: O(1).
        return Cell(value, None, None, True)

    @staticmethod
    def formula(child1, child2):
        """A cell whose value is value(child1) + value(child2)."""
        # Time: O(1), Space: O(1).
        return Cell(None, child1, child2, False)


# Approach (in plain terms):
#   Keep every cell in a lookup table by name. Reading a cell is a little
#   depth-first walk: a literal returns its number, a formula returns the sum
#   of its two children (evaluated the same way). We carry a "currently
#   visiting" set down the walk; if we reach a cell already on that path the
#   formulas loop, so we stop and raise. To avoid recomputing, we remember each
#   answer in a cache. When a cell is changed we clear the cache for it and for
#   every cell that depends on it (found via a reverse "who uses me" map), so
#   the next read recomputes exactly what changed and reuses the rest.
#   Data structures used:
#     - dict name -> Cell - the stored cell definitions.
#     - dict name -> cached value - memoized results for O(1) repeat reads.
#     - dict name -> set of dependents (reverse edges) - drives invalidation
#       when a cell is updated.
#     - a 'visiting' set on the DFS path - detects reference cycles.
class Spreadsheet:

    def __init__(self):
        # Time: O(1), Space: O(1) - empty maps.
        self._cells = {}
        self._cache = {}
        self._dependents = {}

    def setCell(self, key, cell):
        """Define/redefine a cell, then invalidate whatever it affects."""
        # d = cells that transitively depend on key.
        # Time: O(d). Space: O(1) beyond the edges.
        old = self._cells.get(key)
        if old is not None and not old.is_literal:
            self._detach(key, old)
        self._cells[key] = cell
        if not cell.is_literal:
            self._dependents.setdefault(cell.child1, set()).add(key)
            self._dependents.setdefault(cell.child2, set()).add(key)
        self._invalidate(key)

    def getCellValue(self, key):
        """Evaluate a cell; raise EvaluationError on unknown cell or cycle."""
        # Time: O(size of the reachable formula tree), O(1) if cached.
        # Space: O(depth) - the recursion and visiting set.
        return self._evaluate(key, set())

    def _detach(self, key, old_cell):
        """Drop key from its old children's dependent sets."""
        # Time: O(1), Space: O(1).
        for child in (old_cell.child1, old_cell.child2):
            dependents = self._dependents.get(child)
            if dependents is not None:
                dependents.discard(key)

    def _invalidate(self, key):
        """Clear the cache for key and everything depending on it."""
        # d = affected cells. Time: O(d). Space: O(d) - stack + visited set.
        visited = set()
        stack = [key]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            self._cache.pop(current, None)
            for parent in self._dependents.get(current, ()):
                stack.append(parent)

    def _evaluate(self, key, visiting):
        """Recursive value with memoization and cycle detection."""
        # Time: O(size). Space: O(depth).
        if key in self._cache:
            return self._cache[key]
        if key not in self._cells:
            raise EvaluationError(f"unknown cell: {key}")
        if key in visiting:
            raise EvaluationError(f"cycle detected at {key}")
        cell = self._cells[key]
        if cell.is_literal:
            value = cell.value
        else:
            visiting.add(key)
            left = self._evaluate(cell.child1, visiting)
            right = self._evaluate(cell.child2, visiting)
            visiting.discard(key)
            value = left + right
        self._cache[key] = value
        return value


if __name__ == "__main__":
    sheet = Spreadsheet()

    # Example 1: a literal cell.
    sheet.setCell("A", Cell.literal(10))
    print(sheet.getCellValue("A"))     # 10

    # Example 2: a simple formula C = A + B.
    sheet.setCell("B", Cell.literal(5))
    sheet.setCell("C", Cell.formula("A", "B"))
    print(sheet.getCellValue("C"))     # 15

    # Example 3: updating A re-evaluates C (cache invalidation).
    sheet.setCell("A", Cell.literal(20))
    print(sheet.getCellValue("C"))     # 25

    # A missing reference -> error.
    sheet.setCell("D", Cell.formula("A", "missing"))
    try:
        sheet.getCellValue("D")
    except EvaluationError as err:
        print("error:", err)           # error: unknown cell: missing

    # Example 4: a cycle -> error.
    cyclic = Spreadsheet()
    cyclic.setCell("A", Cell.formula("B", "B"))
    cyclic.setCell("B", Cell.formula("A", "A"))
    try:
        cyclic.getCellValue("A")
    except EvaluationError as err:
        print("error:", err)           # error: cycle detected at A
