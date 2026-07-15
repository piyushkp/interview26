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


class ShardedKvStore:

    def __init__(self, shard_size):
        self._shard_size = shard_size
        self._store = {}      # dict preserves insertion order
        self._shards = []     # each shard is a string of appended records

    def put(self, key, value):
        """put: persist a put record and set the current value."""
        self._append_record(f"P|{key}|{value};")
        self._store[key] = value

    def get(self, key):
        """get: the current value, or None if absent."""
        return self._store.get(key)

    def delete(self, key):
        """delete: if the key exists, persist a tombstone and remove it."""
        if key in self._store:
            self._append_record(f"D|{key};")
            del self._store[key]

    def shutdown(self):
        """shutdown: no-op in this simulation (every write is already persisted)."""

    def restore(self):
        """restore: discard the in-memory map and rebuild it by replaying shards."""
        self._store.clear()
        for shard in self._shards:
            self._replay_shard(shard)

    def _append_record(self, record):
        """Append to the last shard, or start a new shard if it would overflow."""
        if not self._shards or len(self._shards[-1]) + len(record) > self._shard_size:
            self._shards.append(record)  # record always fits a fresh shard
        else:
            self._shards[-1] += record

    def _replay_shard(self, shard):
        """Replay every complete ';'-terminated record; ignore a trailing fragment."""
        i = 0
        while i < len(shard):
            end = shard.find(";", i)
            if end < 0:
                break  # incomplete trailing fragment -> ignore
            self._apply_record(shard[i:end])  # record body without the ';'
            i = end + 1

    def _apply_record(self, rec):
        """Apply one decoded record body ("P|key|value" or "D|key") to the map."""
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
        return list(self._shards)

    class Result:
        """Result of a run: the get outputs (in order) and the final shard list."""

        def __init__(self, get_results, shards):
            self.get_results = get_results  # entries may be None
            self.shards = shards

    @staticmethod
    def simulate(shard_size, operations):
        """Run a sequence of operations and return a Result(get_results, shards)."""
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
        return repr((result.get_results, result.shards))


if __name__ == "__main__":
    shard1 = [
        ["put", "a", "1"], ["put", "b", "22"], ["get", "a"], ["put", "a", "333"],
        ["get", "a"], ["restore"], ["get", "b"],
    ]
    print(ShardedKvStore.py_repr(ShardedKvStore.simulate(10, shard1)))
    # (['1', '333', '22'], ['P|a|1;', 'P|b|22;', 'P|a|333;'])
    shard2 = [
        ["put", "ab", "x"], ["put", "c", "yz"], ["delete", "ab"], ["get", "ab"],
        ["restore"], ["get", "c"], ["get", "ab"],
    ]
    print(ShardedKvStore.py_repr(ShardedKvStore.simulate(20, shard2)))
    # ([None, 'yz', None], ['P|ab|x;P|c|yz;D|ab;'])
