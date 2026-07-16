"""Simulation of a persistent sharded key-value store. Each "shard file" is just
a string of appended records; every write is immediately persisted to a shard.

Record encoding (keys/values are ASCII letters/digits, never '|' or ';'):
    put record:    P|key|value;
    delete record: D|key;

Sharding: append a record to the last shard unless that would make it longer
than shard_size; if it would exceed, start a new shard. (A single record is
guaranteed to fit in a fresh shard.)

Operations: put, get, delete, shutdown (no-op — already persisted), and restore
(discard the in-memory map and rebuild by replaying shards in creation order,
ignoring any incomplete trailing fragment not ending in ';').
"""


# Approach (in plain terms):
#   Imagine a notebook where you only ever ADD lines to the bottom, never erasing.
#   To remember key -> value we append "P|key|value;", and to forget a key we append
#   "D|key;" (a tombstone). When the current page (shard) would overflow, we start a
#   new page. For fast reads we also keep the latest value of every key in a plain
#   map. "Restore" is like losing your memory and rebuilding it: re-read every page
#   from the first to the last and apply each line in order, so the last write wins
#   and deletes take effect. A half-written line at the very end (missing its ';')
#   is skipped.
class ShardedKvStore:

    def __init__(self, shard_size):
        """Start empty: remember the shard size limit, the map, and the shards."""
        # Time: O(1), Space: O(1) - stores the limit and two empty containers.
        self._shard_size = shard_size
        self._store = {}      # dict preserves insertion order
        self._shards = []     # each shard is a string of appended records

    def put(self, key, value):
        """put: persist a put record and set the current value."""
        # r = length of the new record, s = length of the last shard.
        # Time: O(r + s) - append to the last shard (string concat rebuilds it).
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
        # Time: O(r + s) when the key exists (append), else O(1). Space: O(r + s).
        if key in self._store:
            self._append_record(f"D|{key};")
            del self._store[key]

    def shutdown(self):
        """shutdown: no-op in this simulation (every write is already persisted)."""
        # Time: O(1), Space: O(1) - does nothing; writes are already on "disk".

    def restore(self):
        """restore: discard the in-memory map and rebuild it by replaying shards."""
        # S = total bytes across all shards, k = number of live keys afterwards.
        # Time: O(S) - replay every record once. Space: O(k) - the rebuilt map.
        self._store.clear()
        for shard in self._shards:
            self._replay_shard(shard)

    def _append_record(self, record):
        """Append to the last shard, or start a new shard if it would overflow."""
        # r = length of the record, s = length of the last shard.
        # Time: O(r + s) to concat onto a shard, or O(r) to start a fresh one.
        # Space: O(r + s) - the (possibly) rebuilt shard string.
        if not self._shards or len(self._shards[-1]) + len(record) > self._shard_size:
            self._shards.append(record)  # record always fits a fresh shard
        else:
            self._shards[-1] += record

    def _replay_shard(self, shard):
        """Replay every complete ';'-terminated record; ignore a trailing fragment."""
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
        """Apply one decoded record body ("P|key|value" or "D|key") to the map."""
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
        """Result of a run: the get outputs (in order) and the final shard list."""

        def __init__(self, get_results, shards):
            # Time: O(1), Space: O(1) - stores two references.
            self.get_results = get_results  # entries may be None
            self.shards = shards

    @staticmethod
    def simulate(shard_size, operations):
        """Run a sequence of operations and return a Result(get_results, shards)."""
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
        # n = total size of the result. Time: O(n), Space: O(n) - a repr string.
        return repr((result.get_results, result.shards))


if __name__ == "__main__":
    # Test 1: overwrite persists a new record; restore rebuilds the latest values.
    shard1 = [
        ["put", "a", "1"], ["put", "b", "22"], ["get", "a"], ["put", "a", "333"],
        ["get", "a"], ["restore"], ["get", "b"],
    ]
    print(ShardedKvStore.py_repr(ShardedKvStore.simulate(10, shard1)))
    # (['1', '333', '22'], ['P|a|1;', 'P|b|22;', 'P|a|333;'])

    # Test 2: delete writes a tombstone; the key stays gone after restore.
    shard2 = [
        ["put", "ab", "x"], ["put", "c", "yz"], ["delete", "ab"], ["get", "ab"],
        ["restore"], ["get", "c"], ["get", "ab"],
    ]
    print(ShardedKvStore.py_repr(ShardedKvStore.simulate(20, shard2)))
    # ([None, 'yz', None], ['P|ab|x;P|c|yz;D|ab;'])

    # Test 3: empty program -> no gets and no shards.
    print(ShardedKvStore.py_repr(ShardedKvStore.simulate(10, [])))
    # ([], [])

    # Test 4: get a never-seen key -> None; deleting a missing key writes nothing.
    shard4 = [
        ["put", "a", "1"], ["delete", "zzz"], ["get", "a"], ["get", "zzz"],
    ]
    print(ShardedKvStore.py_repr(ShardedKvStore.simulate(100, shard4)))
    # (['1', None], ['P|a|1;'])

    # Test 5: overwrite then restore keeps only the last value (both records kept).
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

    # Test 7: a record exactly filling a shard forces the next one onto a new shard.
    shard7 = [
        ["put", "a", "1"], ["put", "b", "2"], ["get", "a"], ["get", "b"],
    ]
    print(ShardedKvStore.py_repr(ShardedKvStore.simulate(6, shard7)))
    # (['1', '2'], ['P|a|1;', 'P|b|2;'])

    # Test 8: many small shards; restore honors creation order (last write wins).
    shard8 = [
        ["put", "x", "1"], ["put", "y", "2"], ["put", "x", "3"], ["delete", "y"],
        ["restore"], ["get", "x"], ["get", "y"],
    ]
    print(ShardedKvStore.py_repr(ShardedKvStore.simulate(8, shard8)))
    # (['3', None], ['P|x|1;', 'P|y|2;', 'P|x|3;', 'D|y;'])
