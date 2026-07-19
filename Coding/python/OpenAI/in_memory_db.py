"""In-memory database of schema-less records with SQL-like SELECT queries.

Overview:
  Records are plain dicts of field -> value (int, float, str, or bool)
  with no fixed schema. Each insert is filed under an auto-assigned
  integer id and mirrored into an equality inverted index so that
  "field = value" filters resolve by set lookup instead of a full scan.

Interface:
  - class InMemoryDb
      insert(record) -> int
          Store a COPY of the record under a fresh id (ids count up
          from 0) and index each field=value pair; returns the new id.
      query(query_string) -> list[dict]
          Run a SELECT and return the matching records, each projected
          to the requested fields, in the requested order.

Query grammar:
  SELECT <*|f1,f2,...> [WHERE cond AND cond ...]
         [ORDER BY field [ASC|DESC]] [LIMIT n]
  Each cond is "field OP literal"; OP is one of =, !=, <, >, <=, >=.
  A literal is a quoted string ('..' or ".."), true/false (bool), an
  int, a float, or otherwise a bare string.

Semantics / rules:
  - A condition holds only if the record HAS the field AND the compare
    is true; a missing field fails the condition, and comparing
    incompatible types (e.g. str vs number) counts as no match.
  - Equality (=) conditions are served from the index; other operators
    are checked by scanning the narrowed candidate ids.
  - SELECT * returns a full copy; a field list keeps only the requested
    fields that the record actually has.
  - ORDER BY sorts by the field ascending (DESC reverses); records
    missing that field sort LAST, and the id is the final tie-break.
  - LIMIT n keeps the first n rows after ordering.
  - Clause keywords are matched case-sensitively as " WHERE ",
    " ORDER BY ", and " LIMIT " with surrounding spaces.

Example:
  insert {'id':1,'name':'Alice','age':30}; insert Bob age 25;
  query("SELECT * WHERE age > 25 ORDER BY name ASC")
    -> [{'id': 1, 'name': 'Alice', 'age': 30}]
"""

from operator import itemgetter


def _parse_query(text):
    """Split a query into (select_fields, conditions, order, limit)."""
    # Time: O(length of the query). Space: O(number of clauses).
    text = text.strip()
    limit = None
    order = None
    limit_at = text.rfind(" LIMIT ")
    if limit_at != -1:
        limit = int(text[limit_at + 7:].strip())
        text = text[:limit_at].rstrip()
    order_at = text.rfind(" ORDER BY ")
    if order_at != -1:
        order = _parse_order(text[order_at + 10:].strip())
        text = text[:order_at].rstrip()
    where_at = text.find(" WHERE ")
    if where_at != -1:
        conditions = _parse_conditions(text[where_at + 7:].strip())
        select_clause = text[:where_at].strip()
    else:
        conditions = []
        select_clause = text
    return _parse_select(select_clause), conditions, order, limit


def _parse_select(clause):
    """Parse the SELECT list: None for '*', else a list of field names."""
    # Time: O(length). Space: O(number of fields).
    body = clause
    if body.startswith("SELECT"):
        body = body[len("SELECT"):]
    body = body.strip()
    if body == "*":
        return None
    fields = []
    for part in body.split(","):
        fields.append(part.strip())
    return fields


def _parse_order(clause):
    """Parse 'field [ASC|DESC]' into (field, descending)."""
    # Time: O(length). Space: O(1).
    parts = clause.split()
    field = parts[0]
    descending = len(parts) > 1 and parts[1].upper() == "DESC"
    return (field, descending)


def _parse_conditions(clause):
    """Parse 'a > 1 AND b = 2' into a list of (field, operator, value)."""
    # c = number of conditions. Time: O(length). Space: O(c).
    conditions = []
    for piece in clause.split(" AND "):
        conditions.append(_parse_condition(piece.strip()))
    return conditions


def _parse_condition(piece):
    """Parse one 'field OP literal' condition."""
    # Time: O(length). Space: O(1).
    for operator in ("<=", ">=", "!=", "="):     # two-char ops (and '=') first
        at = piece.find(operator)
        if at != -1:
            field = piece[:at].strip()
            literal = _parse_literal(piece[at + len(operator):].strip())
            return (field, operator, literal)
    for operator in ("<", ">"):
        at = piece.find(operator)
        if at != -1:
            field = piece[:at].strip()
            literal = _parse_literal(piece[at + len(operator):].strip())
            return (field, operator, literal)
    raise ValueError(f"cannot parse condition: {piece}")


def _parse_literal(text):
    """Turn a literal into a str (quoted), bool, int, or float."""
    # Time: O(length). Space: O(1).
    if len(text) >= 2 and text[0] in "'\"" and text[-1] == text[0]:
        return text[1:-1]
    if text == "true":
        return True
    if text == "false":
        return False
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return text


def _compare(actual, operator, value):
    """Apply one comparison; incomparable types count as no match."""
    # Time: O(1), Space: O(1).
    try:
        if operator == "=":
            return actual == value
        if operator == "!=":
            return actual != value
        if operator == "<":
            return actual < value
        if operator == ">":
            return actual > value
        if operator == "<=":
            return actual <= value
        if operator == ">=":
            return actual >= value
    except TypeError:
        return False        # e.g. comparing a str with a number
    return False


def _matches_all(record, conditions):
    """True if the record meets all conditions (a missing field -> False)."""
    # c = number of conditions. Time: O(c). Space: O(1).
    for field, operator, value in conditions:
        if field not in record or not _compare(record[field], operator, value):
            return False
    return True


def _project(record, select_fields):
    """Full copy for SELECT *, else only the requested fields present."""
    # Time: O(number of fields). Space: O(same).
    if select_fields is None:
        return dict(record)
    projected = {}
    for field in select_fields:
        if field in record:
            projected[field] = record[field]
    return projected


# Approach (in plain terms):
#   Keep every record in a table keyed by an id we hand out on insert. To make
#   "field = value" lookups fast we also keep an inverted index: for each field
#   and value, the set of ids that have it - so an equality filter is an
#   instant set lookup instead of a full scan. A query first narrows to
#   candidate ids (intersecting the index sets of any equality filters, or all
#   ids if there are none), then checks the remaining comparisons by scanning
#   just those candidates. Finally we sort the survivors by the ORDER BY field
#   (records missing that field go last, id breaks ties) and project the
#   requested columns.
#   Data structures used:
#     - dict id -> record - the primary store.
#     - nested dict field -> value -> set of ids - the equality inverted
#       index; equality filters become set lookups/intersections.
#     - lists + stable sort - ORDER BY with missing-last and id tie-break.
class InMemoryDb:

    def __init__(self):
        # Time: O(1), Space: O(1) - empty store and index.
        self._records = {}      # id -> record dict
        self._index = {}        # field -> value -> set of ids
        self._next_id = 0

    def insert(self, record):
        """Store a record under a fresh id and index its equality lookups."""
        # f = fields in the record. Time: O(f). Space: O(f).
        record_id = self._next_id
        self._next_id += 1
        self._records[record_id] = dict(record)
        for field in record:
            by_value = self._index.setdefault(field, {})
            by_value.setdefault(record[field], set()).add(record_id)
        return record_id

    def query(self, query_string):
        """Run a SELECT and return the matching records (projected/ordered)."""
        # r = candidates scanned, m = matches. Time: O(r + m log m).
        # Space: O(m).
        select_fields, conditions, order, limit = _parse_query(query_string)
        matches = []
        for record_id in self._candidate_ids(conditions):
            if _matches_all(self._records[record_id], conditions):
                matches.append(record_id)
        matches = self._order_ids(matches, order)
        if limit is not None:
            matches = matches[:limit]
        results = []
        for record_id in matches:
            results.append(_project(self._records[record_id], select_fields))
        return results

    def _candidate_ids(self, conditions):
        """Ids to consider: intersect the index sets of equality conditions,
        or all ids when there is no equality condition."""
        # Time: O(size of the smallest id sets). Space: O(that).
        equality_sets = []
        for field, operator, value in conditions:
            if operator == "=":
                ids = self._index.get(field, {}).get(value)
                if ids is None:
                    return []       # nothing has this field = value
                equality_sets.append(ids)
        if not equality_sets:
            return list(self._records.keys())
        equality_sets.sort(key=len)         # start from the smallest set
        candidates = set(equality_sets[0])
        for ids in equality_sets[1:]:
            candidates = candidates & ids
        return candidates

    def _order_ids(self, matches, order):
        """Sort matches by ORDER BY (missing field last, id as tie-break)."""
        # m = number of matches. Time: O(m log m). Space: O(m).
        if order is None:
            matches.sort()                  # deterministic: id ascending
            return matches
        field, descending = order
        present = []
        missing = []
        for record_id in matches:
            record = self._records[record_id]
            if field in record:
                present.append((record[field], record_id))
            else:
                missing.append(record_id)
        present.sort(key=itemgetter(1))                  # id ascending (base)
        present.sort(key=itemgetter(0), reverse=descending)  # value, stable
        missing.sort()
        ordered = []
        for value, record_id in present:
            ordered.append(record_id)
        for record_id in missing:
            ordered.append(record_id)
        return ordered


if __name__ == "__main__":
    db = InMemoryDb()
    db.insert({"id": 1, "name": "Alice", "age": 30})
    db.insert({"id": 2, "name": "Bob", "age": 25})

    print(db.query("SELECT * WHERE age > 25 ORDER BY name ASC"))
    # [{'id': 1, 'name': 'Alice', 'age': 30}]

    # Equality filter served by the inverted index.
    print(db.query("SELECT name WHERE name = 'Bob'"))
    # [{'name': 'Bob'}]

    # ORDER BY DESC, then a projection.
    db.insert({"id": 3, "name": "Cara", "age": 30})
    print(db.query("SELECT name, age ORDER BY age DESC LIMIT 2"))
    # [{'name': 'Alice', 'age': 30}, {'name': 'Cara', 'age': 30}]

    # Missing sort field sorts last; a condition on a missing field fails.
    db.insert({"id": 4, "name": "Dan"})
    print(db.query("SELECT name ORDER BY age ASC"))
    # [{'name': 'Bob'}, {'name': 'Alice'}, {'name': 'Cara'}, {'name': 'Dan'}]
    print(db.query("SELECT name WHERE age >= 30"))
    # [{'name': 'Alice'}, {'name': 'Cara'}]
