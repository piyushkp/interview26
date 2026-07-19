"""
Simulate a persistent, log-structured sharded key-value store. Instead
of real files, each shard "file" is represented by a Python string, and
the full set of shards is a list of such strings.

You are given a shard_size and a list of operations. Process the
operations in order, maintaining both the persisted shard strings and a
live in-memory key->value map, then return what the get operations saw
together with the final shard contents.
What to implement

def solution(shard_size, operations):
    ...

    shard_size - the maximum allowed length of any single shard string.
    operations - a list of operation tuples (described below).

Operations

Each operation is a tuple whose first element names the operation:

    ('put', key, value) - write a put record for key, then set the
        current value of key to value (overwriting any existing value).
    ('get', key) - read the current value of key. Append the result to
        the list of get-results: the stored value if the key exists,
        otherwise None.
    ('delete', key) - if key currently exists, write a delete record for
        it and remove it from the live map. If key does not exist, do
        nothing (no record is written).
    ('shutdown',) - a no-op, included only for API completeness. Every
        write is already persisted to the shard strings, so there is
        nothing to flush.
    ('restore',) - discard the entire in-memory map and rebuild it by
        replaying the shard contents from the first shard to the last
        (see Restore below).

Record encoding

Each put and delete is encoded as a single semicolon-terminated record:

    Put record: P|key|value;
    Delete record: D|key;

The size of a record is its string length. Keys and values are ASCII
(letters and digits only), so a character equals one byte, and
keys/values never contain | or ;.
Sharding rule (where each new record is written)

Maintain shards as an ordered list, appended to in creation order. When
a new record must be written:

    If appending it to the last shard would keep that shard's length at
        most shard_size, append it there (the last shard's new length
        must be <= shard_size).
    Otherwise (appending would make the last shard's length exceed
        shard_size), create a new shard and write the record into it.

If there are no shards yet, the first record creates the first shard.
Because every individual record's encoded length is at most shard_size,
a record always fits in a fresh shard. If no records are ever written,
the shard list is empty ([]).
Restore rule (replaying shards)

On ('restore',), throw away the current in-memory map and rebuild it
from scratch by scanning the shards in creation order (first to last):

    Split each shard on the ; terminator and replay each complete record
        in order.
    A P|key|value; record sets key to value.
    A D|key; record removes key.
    If a shard ends with an incomplete fragment that is not terminated
        by ;, ignore that trailing fragment.

Because records are replayed in order, the last write to a key wins, so
the rebuilt map matches the live state that produced the shards.
Return value

Return a tuple (get_results, shards) where:

    get_results is the list of results from every get operation, in the
        order they occurred (each entry is a value string or None).
    shards is the final list of shard strings.

Constraints

    0 <= len(operations) <= 20000
    1 <= shard_size <= 10000
    Keys and values are non-empty ASCII strings of letters and digits
        only, so they never contain | or ;.
    The encoded length of every single put or delete record is at most
        shard_size.

Examples
Example 1

Input
    (10, [('put', 'a', '1'), ('put', 'b', '22'), ('get', 'a'),
          ('put', 'a', '333'), ('get', 'a'), ('restore',),
          ('get', 'b')])
Output
    (['1', '333', '22'], ['P|a|1;', 'P|b|22;', 'P|a|333;'])
Notes
    Each write would overflow the current shard, so three shards are
    created. After restore, the latest value of 'a' is '333' and 'b' is
    still '22'.

Example 2

Input
    (20, [('put', 'ab', 'x'), ('put', 'c', 'yz'), ('delete', 'ab'),
          ('get', 'ab'), ('restore',), ('get', 'c'), ('get', 'ab')])
Output
    ([None, 'yz', None], ['P|ab|x;P|c|yz;D|ab;'])
Notes
    All records fit in one shard. The delete operation writes a
    tombstone for 'ab', so it is missing both before and after restore.

Constraints

    0 <= len(operations) <= 20000
    1 <= shard_size <= 10000
    Keys and values are non-empty ASCII strings containing only letters
        and digits, so they never contain '|' or ';'
    The encoded length of every single put or delete record is at most
        shard_size
"""


# Approach (in plain terms):
#   Imagine a notebook where you only ever ADD lines to the bottom, never
#   erasing. To remember key -> value we append "P|key|value;", and to
#   forget a key we append "D|key;" (a tombstone). When the current page
#   (shard) would overflow, we start a new page. For fast reads we also
#   keep the latest value of every key in a plain map. "Restore" is like
#   losing your memory and rebuilding it: re-read every page from the first
#   to the last and apply each line in order, so the last write wins and
#   deletes take effect. A half-written line at the very end (missing its
#   ';') is skipped.
#   Data structures used:
#     - dict - the current values; answers get in O(1).
#     - list of append-only string shards - the persisted,
#       replayable write log.
class ShardedKvStore:

    def __init__(self, shard_size):
        """Start empty: remember the shard size limit, the map, and the
        shards."""
        # Time: O(1), Space: O(1) - stores the limit and two empty containers.
        self._shard_size = shard_size
        self._store = {}      # dict preserves insertion order
        self._shards = []     # each shard is a string of appended records

    def put(self, key, value):
        """put: persist a put record and set the current value."""
        # r = length of the new record, s = length of the last shard.
        # Time: O(r + s) - append to the last shard (string concat
        # rebuilds it).
        # Space: O(r + s) - the rebuilt shard string.
        self._append_record(f"P|{key}|{value};")
        self._store[key] = value

    def get(self, key):
        """get: the current value, or None if absent."""
        # Time: O(1) average, Space: O(1) - one dict lookup.
        return self._store.get(key)

    def delete(self, key):
        """delete: if the key exists, persist a tombstone and remove it."""
        # r = length of the tombstone, s = length of the last shard.
        # Time: O(r + s) when the key exists (append), else O(1).
        # Space: O(r + s).
        if key in self._store:
            self._append_record(f"D|{key};")
            del self._store[key]

    def shutdown(self):
        """shutdown: no-op in this simulation (every write is already
        persisted)."""
        # Time: O(1), Space: O(1) - does nothing; writes are already on "disk".

    def restore(self):
        """restore: discard the in-memory map and rebuild it by replaying
        shards."""
        # S = total bytes across all shards,
        # k = number of live keys afterwards.
        # Time: O(S) - replay every record once. Space: O(k) - the rebuilt map.
        self._store.clear()
        for shard in self._shards:
            self._replay_shard(shard)

    def _append_record(self, record):
        """Append to the last shard, or start a new shard if it would
        overflow."""
        # r = length of the record, s = length of the last shard.
        # Time: O(r + s) to concat onto a shard, or O(r) to start a fresh one.
        # Space: O(r + s) - the (possibly) rebuilt shard string.
        if (not self._shards
                or len(self._shards[-1]) + len(record) > self._shard_size):
            self._shards.append(record)  # record always fits a fresh shard
        else:
            self._shards[-1] += record

    def _replay_shard(self, shard):
        """Replay every complete ';'-terminated record; ignore a trailing
        fragment."""
        # L = length of the shard string.
        # Time: O(L) - walk the shard record by record. Space: O(1) extra.
        i = 0
        while i < len(shard):
            end = shard.find(";", i)
            if end < 0:
                break  # incomplete trailing fragment -> ignore
            self._apply_record(shard[i:end])  # record body without the ';'
            i = end + 1

    def _apply_record(self, rec):
        """Apply one decoded record body ("P|key|value" or "D|key") to the
        map."""
        # r = length of the record body.
        # Time: O(r) - slice out the key and value. Space: O(r) - the extracted
        # key/value strings.
        if rec.startswith("P|"):
            p1 = rec.index("|")             # after 'P'
            p2 = rec.index("|", p1 + 1)     # between key and value
            key = rec[p1 + 1:p2]
            value = rec[p2 + 1:]
            self._store[key] = value
        elif rec.startswith("D|"):
            self._store.pop(rec[2:], None)
        # any other (malformed) fragment is ignored

    def _shard_strings(self):
        """Final shard contents as plain strings."""
        # t = number of shards.
        # Time: O(t), Space: O(t) - a shallow copy of the shard list.
        return list(self._shards)

    class Result:
        """Result of a run: the get outputs (in order) and the final
        shard list."""

        def __init__(self, get_results, shards):
            # Time: O(1), Space: O(1) - stores two references.
            self.get_results = get_results  # entries may be None
            self.shards = shards

    @staticmethod
    def simulate(shard_size, operations):
        """Run a sequence of operations and return a Result(get_results,
        shards)."""
        # m = number of ops, S = total persisted bytes, g = number of gets.
        # Time: O(m + S) worst case (a restore replays everything).
        # Space: O(S + g) - the shards plus the collected get-results.
        db = ShardedKvStore(shard_size)
        get_results = []
        for op in operations:
            kind = op[0]
            if kind == "put":
                db.put(op[1], op[2])
            elif kind == "get":
                get_results.append(db.get(op[1]))
            elif kind == "delete":
                db.delete(op[1])
            elif kind == "shutdown":
                db.shutdown()
            elif kind == "restore":
                db.restore()
            else:
                raise ValueError(f"Unknown op: {kind}")
        return ShardedKvStore.Result(get_results, db._shard_strings())

    @staticmethod
    def py_repr(result):
        """Render a Result Python-tuple style: (['1', '333'], ['P|a|1;'])."""
        # n = total size of the result.
        # Time: O(n), Space: O(n) - a repr string.
        return repr((result.get_results, result.shards))


if __name__ == "__main__":
    # Test 1: overwrite persists a new record; restore rebuilds the
    # latest values.
    shard1 = [
        ["put", "a", "1"], ["put", "b", "22"], ["get", "a"],
        ["put", "a", "333"],
        ["get", "a"], ["restore"], ["get", "b"],
    ]
    print(ShardedKvStore.py_repr(ShardedKvStore.simulate(10, shard1)))
    # (['1', '333', '22'], ['P|a|1;', 'P|b|22;', 'P|a|333;'])

    # Test 2: delete writes a tombstone; the key stays gone after restore.
    shard2 = [
        ["put", "ab", "x"], ["put", "c", "yz"], ["delete", "ab"],
        ["get", "ab"],
        ["restore"], ["get", "c"], ["get", "ab"],
    ]
    print(ShardedKvStore.py_repr(ShardedKvStore.simulate(20, shard2)))
    # ([None, 'yz', None], ['P|ab|x;P|c|yz;D|ab;'])

    # Test 3: empty program -> no gets and no shards.
    print(ShardedKvStore.py_repr(ShardedKvStore.simulate(10, [])))
    # ([], [])

    # Test 4: get a never-seen key -> None; deleting a missing key
    # writes nothing.
    shard4 = [
        ["put", "a", "1"], ["delete", "zzz"], ["get", "a"], ["get", "zzz"],
    ]
    print(ShardedKvStore.py_repr(ShardedKvStore.simulate(100, shard4)))
    # (['1', None], ['P|a|1;'])

    # Test 5: overwrite then restore keeps only the last value (both
    # records kept).
    shard5 = [
        ["put", "k", "v1"], ["put", "k", "v2"], ["restore"], ["get", "k"],
    ]
    print(ShardedKvStore.py_repr(ShardedKvStore.simulate(100, shard5)))
    # (['v2'], ['P|k|v1;P|k|v2;'])

    # Test 6: delete then restore -> replaying put then tombstone yields None.
    shard6 = [
        ["put", "a", "1"], ["delete", "a"], ["restore"], ["get", "a"],
    ]
    print(ShardedKvStore.py_repr(ShardedKvStore.simulate(100, shard6)))
    # ([None], ['P|a|1;D|a;'])

    # Test 7: a record exactly filling a shard forces the next one onto
    # a new shard.
    shard7 = [
        ["put", "a", "1"], ["put", "b", "2"], ["get", "a"], ["get", "b"],
    ]
    print(ShardedKvStore.py_repr(ShardedKvStore.simulate(6, shard7)))
    # (['1', '2'], ['P|a|1;', 'P|b|2;'])

    # Test 8: many small shards; restore honors creation order (last
    # write wins).
    shard8 = [
        ["put", "x", "1"], ["put", "y", "2"], ["put", "x", "3"],
        ["delete", "y"],
        ["restore"], ["get", "x"], ["get", "y"],
    ]
    print(ShardedKvStore.py_repr(ShardedKvStore.simulate(8, shard8)))
    # (['3', None], ['P|x|1;', 'P|y|2;', 'P|x|3;', 'D|y;'])
