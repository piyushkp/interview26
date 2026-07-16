"""A persistent key-value store with a binary-safe serialization format.

Keys and values are Python str or bytes blobs. Persistence uses LENGTH-PREFIXED
encoding (no delimiters), so keys/values may contain any byte (including '|',
':', newlines):
    field = [type:1][len:4 big-endian][raw bytes]
    map   = [count:4][field key][field value] x count

  - Part 1 (simulate_part1): serialize/deserialize a snapshot to a label.
  - Part 2 (simulate_part2): split a snapshot into size-bounded, order-
    independent segments (each segment = [total:4][index:4][chunk]).
  - Part 3 (simulate_part3): snapshot + append-only log with replay on restart
    and threshold-based compaction.

A str value round-trips as str (UTF-8) and a bytes value as bytes, so the demo
output distinguishes 'x' (str) from b'x' (bytes).
"""


# ---------- binary-safe codec ----------

def _write_int(out, v):
    """Append a 4-byte big-endian integer (length or count) to the buffer."""
    # Time: O(1), Space: O(1) - writes a fixed 4 bytes.
    out.extend(v.to_bytes(4, "big"))


def _write_field(out, field):
    """Append one length-prefixed field: [type:1][len:4][raw bytes]."""
    # n = number of bytes in the field.
    # Time: O(n) - encode (if str) and copy n bytes. Space: O(n) - the encoded copy.
    is_str = isinstance(field, str)
    data = field.encode("utf-8") if is_str else field
    out.append(1 if is_str else 0)
    _write_int(out, len(data))
    out.extend(data)


def _encode_map(mapping):
    """Serialize a map to a binary-safe blob."""
    # n = number of entries, b = total bytes across all keys and values.
    # Time: O(n + b) - one field per key and value. Space: O(n + b) - the blob.
    out = bytearray()
    _write_int(out, len(mapping))
    for key, value in mapping.items():
        _write_field(out, key)
        _write_field(out, value)
    return bytes(out)


class _Reader:
    """Sequential reader over a blob produced by _encode_map."""

    def __init__(self, blob):
        # Time: O(1), Space: O(1) - stores the blob and a cursor position.
        self._b = blob
        self._i = 0

    def read_int(self):
        # Time: O(1), Space: O(1) - reads a fixed 4-byte integer.
        v = int.from_bytes(self._b[self._i:self._i + 4], "big")
        self._i += 4
        return v

    def read_field(self):
        # n = length of this field. Time: O(n) - slice n bytes (plus a UTF-8
        # decode for str). Space: O(n) - the returned bytes/str.
        tag = self._b[self._i]
        self._i += 1
        length = self.read_int()
        data = bytes(self._b[self._i:self._i + length])
        self._i += length
        return data.decode("utf-8") if tag == 1 else data


def _decode_map(blob):
    """Rebuild a map from a blob produced by _encode_map."""
    # n = number of entries, b = total key/value bytes.
    # Time: O(n + b) - read every field once. Space: O(n + b) - the rebuilt map.
    reader = _Reader(blob)
    count = reader.read_int()
    mapping = {}
    for _ in range(count):
        key = reader.read_field()
        value = reader.read_field()
        mapping[key] = value
    return mapping


def _read_int_at(b, off):
    """Read a 4-byte big-endian integer at a fixed offset in a blob."""
    # Time: O(1), Space: O(1) - reads 4 bytes.
    return int.from_bytes(b[off:off + 4], "big")


# ---------- Part 2 segment helpers ----------
_SEG_HEADER = 8  # [total:4][index:4]


def _segment_index(segment):
    """Sort key: a segment's stored index header (bytes 4..8)."""
    # Time: O(1), Space: O(1) - reads one 4-byte integer header.
    return _read_int_at(segment, 4)


def _split_into_segments(snap, max_segment_size):
    """Split a snapshot blob into size-bounded, index-stamped segments."""
    # s = len(snap), t = number of segments produced.
    # Time: O(s) - copy the snapshot into chunks. Space: O(s) - the segments
    # together hold the whole snapshot (plus t small headers).
    chunk = max_segment_size - _SEG_HEADER  # >= 1 since max_segment_size >= 9
    total = max(1, (len(snap) + chunk - 1) // chunk)
    segs = []
    for idx in range(total):
        off = idx * chunk
        length = min(chunk, len(snap) - off)
        seg = bytearray()
        _write_int(seg, total)
        _write_int(seg, idx)
        if length > 0:
            seg.extend(snap[off:off + length])
        segs.append(bytes(seg))
    return segs


def _join_segments(segments):
    """Reassemble the snapshot from segments given in any order."""
    # t = number of segments, s = total payload bytes.
    # Time: O(t log t + s) - sort by index header, then concatenate. Space: O(s).
    # Segments may be in any order; sort by their stored index header.
    ordered = sorted(segments, key=_segment_index)
    out = bytearray()
    for seg in ordered:
        out.extend(seg[_SEG_HEADER:])
    return bytes(out)


# Approach (in plain terms):
#   We need to save a dictionary to "disk" and read it back, even when keys or
#   values contain tricky bytes (spaces, '|', ':', newlines). The trick: never rely
#   on separators. Instead, right before every chunk we write its exact length -
#   like labelling a parcel "5 bytes follow". The reader then grabs exactly that many
#   bytes, so nothing inside can ever be mistaken for a separator (binary-safe).
#     - Part 1: write the whole map as one length-prefixed blob and read it back.
#     - Part 2: chop that blob into fixed-size parcels, each stamped with its index,
#       so they can be stored or shuffled and later sorted back into the right order.
#     - Part 3: keep a saved snapshot plus a running list (the log) of recent changes.
#       On restart, load the snapshot then re-apply the log. When the log grows past a
#       threshold, fold everything into a fresh snapshot (compaction) and clear the log.
class PersistentKvStore:

    @staticmethod
    def by(s):
        """Demo helper: Python bytes from a str (ISO-8859-1, 1 char == 1 byte)."""
        # n = len(s). Time: O(n) - encode n characters. Space: O(n) - the bytes.
        return s.encode("latin-1")

    @staticmethod
    def py_repr(results):
        """Render a results list Python-style (str -> 'x', bytes -> b'x',
        None -> None, tuple -> (...))."""
        # n = total size of results. Time: O(n), Space: O(n) - builds a repr string.
        return repr(results)

    # ---------- Part 1: serialize / deserialize a single snapshot ----------
    @staticmethod
    def simulate_part1(operations):
        """Part 1: serialize/deserialize a whole snapshot to and from a label."""
        # m = number of ops, s = current store's serialized size, r = get-results.
        # Time: O(m * s) worst case (serialize/deserialize copy the whole store).
        # Space: O(s + r) - a snapshot blob plus the results list.
        store = {}
        disk = {}  # fake disk: label -> blob
        results = []
        for op in operations:
            kind = op[0]
            if kind == "put":
                store[op[1]] = op[2]
            elif kind == "delete":
                store.pop(op[1], None)
            elif kind == "get":
                results.append(store.get(op[1]))  # value or None
            elif kind == "serialize":
                disk[op[1]] = _encode_map(store)
            elif kind == "deserialize":
                store = _decode_map(disk[op[1]])
            else:
                raise ValueError(f"Unknown op: {kind}")
        return results

    # ---------- Part 2: snapshot split across size-bounded segments ----------
    @staticmethod
    def simulate_part2(max_segment_size, operations):
        """Part 2: serialize into size-bounded segments that survive reordering."""
        # m = number of ops, s = serialized store size, t = segments per snapshot.
        # Time: O(m * (s + t log t)) worst case. Space: O(s + r) - segments plus
        # the r results.
        store = {}
        disk = {}  # prefix -> list of segment blobs
        results = []
        for op in operations:
            kind = op[0]
            if kind == "put":
                store[op[1]] = op[2]
            elif kind == "delete":
                store.pop(op[1], None)
            elif kind == "get":
                results.append(store.get(op[1]))
            elif kind == "serialize":
                disk[op[1]] = _split_into_segments(_encode_map(store), max_segment_size)
            elif kind == "segment_count":
                results.append(len(disk[op[1]]))
            elif kind == "reorder":
                cur = disk[op[1]]
                order = op[2]
                # Physical shuffle; the index header preserves the true order.
                shuffled = []
                for idx in order:
                    shuffled.append(cur[idx])
                disk[op[1]] = shuffled
            elif kind == "deserialize":
                store = _decode_map(_join_segments(disk[op[1]]))
            else:
                raise ValueError(f"Unknown op: {kind}")
        return results

    # ---------- Part 3: snapshot + append-only log with replay & compaction ----------
    @staticmethod
    def simulate_part3(compact_threshold, operations):
        """Part 3: snapshot + append-only log, replayed on restart and folded in on
        compaction."""
        # m = number of ops, s = store size, L = pending log length, r = results.
        # Time: O(m * s) worst case (compaction/restart re-encode or replay).
        # Space: O(s + L + r) - snapshot, log, and results.
        store = {}
        # Persisted artifacts (survive a restart): a snapshot blob + a pending log.
        snapshot = [_encode_map(store)]
        log = []                 # list of (is_put, key, val); val is None for delete
        compactions = [0]
        results = []

        def maybe_compact():
            # Time: O(s) when it compacts (re-encode the whole store), else O(1).
            # Space: O(s) for the fresh snapshot when compaction happens.
            if len(log) >= compact_threshold:
                snapshot[0] = _encode_map(store)  # fresh full snapshot
                log.clear()                       # clear the pending log
                compactions[0] += 1

        for op in operations:
            kind = op[0]
            if kind == "put":
                k, v = op[1], op[2]
                store[k] = v
                log.append((True, k, v))
                maybe_compact()
            elif kind == "delete":
                k = op[1]
                store.pop(k, None)
                log.append((False, k, None))
                maybe_compact()
            elif kind == "get":
                results.append(store.get(op[1]))
            elif kind == "restart":
                # Throw away memory; reload the snapshot, then replay the log.
                store = _decode_map(snapshot[0])
                for is_put, k, v in log:
                    if is_put:
                        store[k] = v
                    else:
                        store.pop(k, None)
            elif kind == "status":
                # (live keys, pending log records, snapshots written)
                results.append((len(store), len(log), compactions[0]))
            else:
                raise ValueError(f"Unknown op: {kind}")
        return results


if __name__ == "__main__":
    by = PersistentKvStore.by

    # ----- Part 1: single-snapshot serialize / deserialize -----
    # Test 1: deserialize restores an older snapshot, undoing a later put.
    kv1 = [
        ["put", "a", "1"], ["get", "a"], ["serialize", "snap1"],
        ["put", "a", "2"], ["deserialize", "snap1"], ["get", "a"],
    ]
    print(PersistentKvStore.py_repr(PersistentKvStore.simulate_part1(kv1)))  # ['1', '1']

    # Test 2: get a missing key -> None; delete then get -> None.
    kv1b = [["get", "nope"], ["put", "a", "1"], ["delete", "a"], ["get", "a"]]
    print(PersistentKvStore.py_repr(PersistentKvStore.simulate_part1(kv1b)))  # [None, None]

    # Test 3: binary-safe - keys/values with '|', ':' and a newline round-trip.
    kv1c = [
        ["put", by("a|b"), by("v:1\n")], ["serialize", "s"],
        ["put", by("a|b"), by("zzz")], ["deserialize", "s"], ["get", by("a|b")],
    ]
    print(PersistentKvStore.py_repr(PersistentKvStore.simulate_part1(kv1c)))  # [b'v:1\n']

    # Test 4: a str value stays str and a bytes value stays bytes.
    kv1d = [["put", "k", "x"], ["put", by("k2"), by("x")], ["get", "k"], ["get", by("k2")]]
    print(PersistentKvStore.py_repr(PersistentKvStore.simulate_part1(kv1d)))  # ['x', b'x']

    # ----- Part 2: snapshot split into reorderable segments -----
    # Test 5: count segments, then read values back after a shuffle-proof join.
    kv2 = [
        ["put", by("a"), by("12345")], ["put", by("b"), by("67890")],
        ["serialize", "p"], ["segment_count", "p"], ["delete", by("a")],
        ["deserialize", "p"], ["get", by("a")], ["get", by("b")],
    ]
    print(PersistentKvStore.py_repr(PersistentKvStore.simulate_part2(15, kv2)))
    # [6, b'12345', b'67890']

    # Test 6: reversing the segment order still reassembles the snapshot correctly.
    kv2b = [
        ["put", by("k1"), by("AAAA")], ["put", by("k2"), by("BBBB")],
        ["serialize", "p"], ["segment_count", "p"], ["reorder", "p", [2, 1, 0]],
        ["deserialize", "p"], ["get", by("k1")], ["get", by("k2")],
    ]
    print(PersistentKvStore.py_repr(PersistentKvStore.simulate_part2(20, kv2b)))
    # [3, b'AAAA', b'BBBB']

    # Test 7: an empty store still serializes to exactly one segment.
    kv2c = [["serialize", "e"], ["segment_count", "e"], ["deserialize", "e"], ["get", by("x")]]
    print(PersistentKvStore.py_repr(PersistentKvStore.simulate_part2(15, kv2c)))
    # [1, None]

    # ----- Part 3: snapshot + append-only log with replay & compaction -----
    # Test 8: restart with no compaction yet -> empty snapshot + replayed log.
    kv3 = [
        ["put", "a", "1"], ["put", "b", "2"], ["restart"],
        ["get", "a"], ["get", "b"], ["status"],
    ]
    print(PersistentKvStore.py_repr(PersistentKvStore.simulate_part3(3, kv3)))
    # ['1', '2', (2, 2, 0)]

    # Test 9: hitting the threshold compacts, clearing the log and bumping the count.
    kv3b = [["put", "a", "1"], ["put", "b", "2"], ["put", "c", "3"], ["status"]]
    print(PersistentKvStore.py_repr(PersistentKvStore.simulate_part3(3, kv3b)))
    # [(3, 0, 1)]

    # Test 10: restart after a compaction reloads the snapshot then replays the log.
    kv3c = [
        ["put", "a", "1"], ["put", "b", "2"], ["put", "c", "3"],  # compaction here
        ["put", "d", "4"], ["delete", "a"], ["restart"],
        ["get", "a"], ["get", "d"], ["status"],
    ]
    print(PersistentKvStore.py_repr(PersistentKvStore.simulate_part3(3, kv3c)))
    # [None, '4', (3, 2, 1)]

    # Test 11: binary-safe snapshot survives compaction + restart (mixed str/bytes).
    kv3d = [
        ["put", by("k|1"), by("v:1")], ["put", "x", "y"], ["put", "p", "q"],
        ["restart"], ["get", by("k|1")],
    ]
    print(PersistentKvStore.py_repr(PersistentKvStore.simulate_part3(3, kv3d)))
    # [b'v:1']
