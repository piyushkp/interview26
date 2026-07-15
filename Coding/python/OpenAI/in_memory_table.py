"""A simple in-memory SQL-like database for a single table of string cells.

A row is identified by a string row_key; each row maps col_key -> value.
Commands (whitespace-separated tokens):
  - SET row_key col_key value     set/overwrite table[row_key][col_key].
  - GET row_key col_key           the value, or "NULL" if the cell is absent.
  - SELECT where_col where_value order_by_col
        row_keys where table[row][where_col] == where_value, sorted by the
        value of order_by_col ascending (missing -> ""), ties broken by row_key
        ascending, joined by single spaces ("" if none match).

process_commands returns one output string per GET and SELECT, in order.
"""


class InMemoryTable:

    def __init__(self):
        # row_key -> (col_key -> value); dict preserves insertion order.
        self._table = {}

    def set(self, row_key, col_key, value):
        """SET: set or overwrite a cell."""
        self._table.setdefault(row_key, {})[col_key] = value

    def get(self, row_key, col_key):
        """GET: the cell value, or "NULL" if the row or column is absent."""
        row = self._table.get(row_key)
        if row is None:
            return "NULL"
        value = row.get(col_key)
        return "NULL" if value is None else value

    def select(self, where_col, where_value, order_by_col):
        """SELECT: matching row_keys sorted by order_by_col then row_key."""
        matches = [rk for rk, row in self._table.items()
                   if row.get(where_col) == where_value]
        # Sort lexicographically by order_by_col value, tie-break by row_key.
        matches.sort(key=lambda rk: (self._sort_value(rk, order_by_col), rk))
        return " ".join(matches)

    def _sort_value(self, row_key, order_by_col):
        """The order_by_col value for a row, or "" if the row lacks it."""
        v = self._table[row_key].get(order_by_col)
        return "" if v is None else v

    @staticmethod
    def process_commands(commands):
        """Process commands, returning one output per GET/SELECT in order."""
        db = InMemoryTable()
        outputs = []
        for command in commands:
            t = command.split(" ")
            if t[0] == "SET":
                db.set(t[1], t[2], t[3])
            elif t[0] == "GET":
                outputs.append(db.get(t[1], t[2]))
            elif t[0] == "SELECT":
                outputs.append(db.select(t[1], t[2], t[3]))
            else:
                raise ValueError(f"Unknown command: {t[0]}")
        return outputs


if __name__ == "__main__":
    sql1 = [
        "SET r1 name bob", "SET r1 age 2", "SET r2 name bob", "SET r2 age 10",
        "GET r1 name", "SELECT name bob age",
    ]
    print(InMemoryTable.process_commands(sql1))  # ['bob', 'r2 r1']
    print(InMemoryTable.process_commands(
        ["GET missing name", "SELECT status active score"]))  # ['NULL', '']
