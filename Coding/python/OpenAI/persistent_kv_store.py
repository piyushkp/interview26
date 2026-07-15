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
    out.extend(v.to_bytes(4, "big"))


def _write_field(out, field):
    is_str = isinstance(field, str)
    data = field.encode("utf-8") if is_str else field
    out.append(1 if is_str else 0)
    _write_int(out, len(data))
    out.extend(data)


def _encode_map(mapping):
    """Serialize a map to a binary-safe blob."""
    out = bytearray()
    _write_int(out, len(mapping))
    for k, v in mapping.items():
        _write_field(out, k)
        _write_field(out, v)
    return bytes(out)


class _Reader:
    """Sequential reader over a blob produced by _encode_map."""

    def __init__(self, blob):
        self._b = blob
        self._i = 0

    def read_int(self):
        v = int.from_bytes(self._b[self._i:self._i + 4], "big")
        self._i += 4
        return v

    def read_field(self):
        tag = self._b[self._i]
        self._i += 1
        length = self.read_int()
        data = bytes(self._b[self._i:self._i + length])
        self._i += length
        return data.decode("utf-8") if tag == 1 else data


def _decode_map(blob):
    """Rebuild a map from a blob produced by _encode_map."""
    reader = _Reader(blob)
    count = reader.read_int()
    mapping = {}
    for _ in range(count):
        k = reader.read_field()
        v = reader.read_field()
        mapping[k] = v
    return mapping


def _read_int_at(b, off):
    return int.from_bytes(b[off:off + 4], "big")


# ---------- Part 2 segment helpers ----------
_SEG_HEADER = 8  # [total:4][index:4]


def _split_into_segments(snap, max_segment_size):
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
    # Segments may be in any order; sort by their stored index header.
    ordered = sorted(segments, key=lambda x: _read_int_at(x, 4))
    out = bytearray()
    for seg in ordered:
        out.extend(seg[_SEG_HEADER:])
    return bytes(out)


class PersistentKvStore:

    @staticmethod
    def by(s):
        """Demo helper: Python bytes from a str (ISO-8859-1, 1 char == 1 byte)."""
        return s.encode("latin-1")

    @staticmethod
    def py_repr(results):
        """Render a results list Python-style (str -> 'x', bytes -> b'x',
        None -> None, tuple -> (...))."""
        return repr(results)

    # ---------- Part 1: serialize / deserialize a single snapshot ----------
    @staticmethod
    def simulate_part1(operations):
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
                # physical shuffle; the index header preserves the truth.
                disk[op[1]] = [cur[idx] for idx in order]
            elif kind == "deserialize":
                store = _decode_map(_join_segments(disk[op[1]]))
            else:
                raise ValueError(f"Unknown op: {kind}")
        return results

    # ---------- Part 3: snapshot + append-only log with replay & compaction ----------
    @staticmethod
    def simulate_part3(compact_threshold, operations):
        store = {}
        # Persisted artifacts (survive a restart): a snapshot blob + a pending log.
        snapshot = [_encode_map(store)]
        log = []                 # list of (is_put, key, val); val is None for delete
        compactions = [0]
        results = []

        def maybe_compact():
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
    kv1 = [
        ["put", "a", "1"], ["get", "a"], ["serialize", "snap1"],
        ["put", "a", "2"], ["deserialize", "snap1"], ["get", "a"],
    ]
    print(PersistentKvStore.py_repr(PersistentKvStore.simulate_part1(kv1)))  # ['1', '1']
    kv2 = [
        ["put", by("a"), by("12345")], ["put", by("b"), by("67890")],
        ["serialize", "p"], ["segment_count", "p"], ["delete", by("a")],
        ["deserialize", "p"], ["get", by("a")], ["get", by("b")],
    ]
    print(PersistentKvStore.py_repr(PersistentKvStore.simulate_part2(15, kv2)))
    # [6, b'12345', b'67890']
    kv3 = [
        ["put", "a", "1"], ["put", "b", "2"], ["restart"],
        ["get", "a"], ["get", "b"], ["status"],
    ]
    print(PersistentKvStore.py_repr(PersistentKvStore.simulate_part3(3, kv3)))
    # ['1', '2', (2, 2, 0)]
