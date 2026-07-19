"""In-memory single-table store of string cells with SQL-like commands.

Overview:
  A tiny database holding ONE table. Each row has a string row_key and
  maps column keys to string values (every cell is a string). Commands
  arrive as whitespace-separated token lists and are run in order.

Interface:
  - class InMemoryTable
      set(row_key, col_key, value) -> None
          Create or overwrite table[row_key][col_key].
      get(row_key, col_key) -> str
          The stored value, or "NULL" if the row or the cell is absent.
      select(where_col, where_value, order_by_col) -> str
          Space-joined row_keys whose where_col equals where_value,
          sorted by order_by_col value then row_key; "" if none match.
      process_commands(commands) -> list[str]  (static)
          Run a list of command strings; one output per GET/SELECT.

Commands (tokens split on single spaces):
  - SET row_key col_key value      store/overwrite a cell (no output).
  - GET row_key col_key            emit the value, or "NULL" if absent.
  - SELECT where_col where_value order_by_col
        emit the matching row_keys (see SELECT semantics below).

Semantics / rules:
  - GET returns "NULL" when the row is unknown OR the column is unset.
  - SELECT keeps rows where row[where_col] == where_value, then sorts
    by the order_by_col value ascending, breaks ties by row_key
    ascending, and joins the row_keys with single spaces ("" when
    nothing matches).
  - A row missing the order_by_col sorts as "" (before any real value).
  - Ordering is lexicographic on the string value, NOT numeric, so
    "10" sorts before "2".
  - process_commands emits one string per GET and SELECT (SET emits
    nothing); an unrecognized command raises ValueError.

Constraints / assumptions:
  - Values are single tokens: a command is split on spaces, so keys and
    values cannot themselves contain spaces.

Example:
  SET r1 age 2; SET r2 age 10; SET r1 name bob; SET r2 name bob;
  SELECT name bob age -> "r2 r1"  ("10" < "2" lexicographically).
"""


def _select_sort_key(order_value_and_row_key):
    """Sort key for SELECT: the (order_by value, row_key) pair, both
    ascending."""
    # Time: O(1), Space: O(1) - returns the decorated pair unchanged as
    # the key.
    return order_value_and_row_key


# Approach (in plain terms):
#   Picture a spreadsheet where every row has a name (row_key) and some
#   labelled boxes (columns) holding text. We store it as a dictionary of rows,
#   where each row is itself a small dictionary of column -> value.
#     - SET writes into a box, creating the row if it's new or overwriting what
#       was already there.
#     - GET reads one box, answering "NULL" when that row or box was never
#       filled.
#     - SELECT means "give me every row whose column X equals Y", then line
#       those rows up sorted by another column's value (ties broken by the
#       row's name).
#   To sort safely we first pair each matching row with the value we sort on,
#   sort those pairs, then read the names back out in order.
#   Data structures used:
#     - dict of dicts (row_key -> {col_key: value}) - O(1) cell get/set;
#       iterate the rows for SELECT then sort the matches.
class InMemoryTable:

    def __init__(self):
        """Start with an empty table."""
        # Time: O(1), Space: O(1) - creates one empty dict.
        # row_key -> (col_key -> value); dict preserves insertion order.
        self._table = {}

    def set(self, row_key, col_key, value):
        """SET: set or overwrite a cell."""
        # Time: O(1) average, Space: O(1) - one dict insert (plus a new row
        # dict the first time a row_key is seen).
        self._table.setdefault(row_key, {})[col_key] = value

    def get(self, row_key, col_key):
        """GET: the cell value, or "NULL" if the row or column is absent."""
        # Time: O(1) average, Space: O(1) - at most two dict lookups.
        row = self._table.get(row_key)
        if row is None:
            return "NULL"
        value = row.get(col_key)
        return "NULL" if value is None else value

    def select(self, where_col, where_value, order_by_col):
        """SELECT: matching row_keys sorted by order_by_col then row_key."""
        # n = number of rows in the table, k = number of matching rows
        # (k <= n).
        # Time:  O(n + k log k) - scan all n rows, then sort the k matches.
        # Space: O(k) - the list of decorated matches.
        # Pair every matching row with the value we will sort it by.
        decorated = []
        for row_key, row in self._table.items():
            if row.get(where_col) == where_value:
                sort_value = self._sort_value(row_key, order_by_col)
                decorated.append((sort_value, row_key))
        # Sort by order_by_col value, ties broken by row_key (both ascending).
        decorated.sort(key=_select_sort_key)
        # Read the row_keys back out, now in sorted order.
        matches = []
        for sort_value, row_key in decorated:
            matches.append(row_key)
        return " ".join(matches)

    def _sort_value(self, row_key, order_by_col):
        """The order_by_col value for a row, or "" if the row lacks it."""
        # Time: O(1) average, Space: O(1) - one dict lookup.
        value = self._table[row_key].get(order_by_col)
        return "" if value is None else value

    @staticmethod
    def process_commands(commands):
        """Process commands, returning one output per GET/SELECT in order."""
        # m = number of commands, n = rows in the table.
        # Time:  O(m * n log n) worst case (each SELECT scans and sorts the
        #        rows).
        # Space: O(m + n) - the outputs list plus the stored rows.
        db = InMemoryTable()
        outputs = []
        for command in commands:
            tokens = command.split(" ")
            if tokens[0] == "SET":
                db.set(tokens[1], tokens[2], tokens[3])
            elif tokens[0] == "GET":
                outputs.append(db.get(tokens[1], tokens[2]))
            elif tokens[0] == "SELECT":
                outputs.append(db.select(tokens[1], tokens[2], tokens[3]))
            else:
                raise ValueError(f"Unknown command: {tokens[0]}")
        return outputs


if __name__ == "__main__":
    # Test 1: GET a cell, then SELECT ordered by a numeric-looking string
    # column.
    sql1 = [
        "SET r1 name bob", "SET r1 age 2", "SET r2 name bob", "SET r2 age 10",
        "GET r1 name", "SELECT name bob age",
    ]
    print(InMemoryTable.process_commands(sql1))  # ['bob', 'r2 r1']

    # Test 2: GET a missing row -> NULL; SELECT with no matches -> "".
    print(InMemoryTable.process_commands(
        ["GET missing name", "SELECT status active score"]))  # ['NULL', '']

    # Test 3: empty program -> no outputs at all.
    print(InMemoryTable.process_commands([]))  # []

    # Test 4: overwrite -> the latest SET to a cell wins.
    over = ["SET r1 v a", "SET r1 v b", "GET r1 v"]
    print(InMemoryTable.process_commands(over))  # ['b']

    # Test 5: GET a column the row never set -> NULL (row exists, cell does
    # not).
    absent = ["SET r1 name x", "GET r1 age"]
    print(InMemoryTable.process_commands(absent))  # ['NULL']

    # Test 6: SELECT whose filter matches nothing -> "".
    no_match = ["SET r1 name x", "SELECT name y age"]
    print(InMemoryTable.process_commands(no_match))  # ['']

    # Test 7: ties on the order_by value are broken by row_key ascending.
    ties = [
        "SET r3 name x", "SET r3 k 5", "SET r1 name x", "SET r1 k 5",
        "SET r2 name x", "SET r2 k 5", "SELECT name x k",
    ]
    print(InMemoryTable.process_commands(ties))  # ['r1 r2 r3']

    # Test 8: a missing order_by value sorts as "" (before any real value).
    missing_order = ["SET a f m", "SET b f m", "SET b s 9", "SELECT f m s"]
    print(InMemoryTable.process_commands(missing_order))  # ['a b']

    # Test 9: ordering is lexicographic on the string value, not numeric.
    numeric = [
        "SET r1 g h", "SET r1 n 9", "SET r2 g h", "SET r2 n 10",
        "SET r3 g h", "SET r3 n 100", "SELECT g h n",
    ]
    print(InMemoryTable.process_commands(numeric))  # ['r2 r3 r1']
