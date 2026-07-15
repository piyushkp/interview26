"""Invertible, binary-safe encoding for a dict[str, str].

Because keys/values may contain any character (including '#', ':', '|', '=',
spaces), a delimiter-only format is unsafe. Instead each field is
LENGTH-PREFIXED as <len>#<content>, and after reading a length we consume
exactly that many characters — so the content may contain anything.

Format: <pair_count>#<key_len>#<key><value_len>#<value>... with pairs written
in lexicographically sorted key order, so the output is deterministic.
Example: {"a": "hi", "b": ""} -> "2#1#a2#hi1#b0#"; the empty map -> "0#".
"""


def serialize(mapping):
    """Serialize a map to the length-prefixed format (keys sorted lexicographically)."""
    parts = [f"{len(mapping)}#"]
    for k in sorted(mapping):  # deterministic key order
        v = mapping[k]
        parts.append(f"{len(k)}#{k}")
        parts.append(f"{len(v)}#{v}")
    return "".join(parts)


def deserialize(data):
    """Reconstruct the original map from a serialized string."""
    mapping = {}
    pos = [0]
    count = _read_length(data, pos)
    for _ in range(count):
        key = _read_field(data, pos)
        value = _read_field(data, pos)
        mapping[key] = value
    return mapping


def _read_length(s, pos):
    """Read a run of digits terminated by '#', returning the int; advance past '#'."""
    start = pos[0]
    while pos[0] < len(s) and s[pos[0]] != "#":
        c = s[pos[0]]
        if c < "0" or c > "9":
            raise ValueError(f"Malformed: expected digit at index {pos[0]}")
        pos[0] += 1
    if pos[0] >= len(s) or start == pos[0]:
        raise ValueError("Malformed: missing length or '#'")
    length = int(s[start:pos[0]])
    pos[0] += 1  # skip the '#'
    return length


def _read_field(s, pos):
    """Read a length-prefixed field: <len>#<exactly len chars>."""
    length = _read_length(s, pos)
    if pos[0] + length > len(s):
        raise ValueError("Malformed: field length exceeds input")
    field = s[pos[0]:pos[0] + length]
    pos[0] += length
    return field


def solution(operation, data):
    """Judge-style entry point: "serialize" a dict -> str, or "deserialize" a
    str -> dict."""
    if operation == "serialize":
        return serialize(data)
    if operation == "deserialize":
        return deserialize(data)
    raise ValueError(f"Unknown operation: {operation}")


if __name__ == "__main__":
    print(solution("serialize", {}))            # 0#
    encoded = solution("serialize", {"a": "hi", "b": ""})
    print(encoded)                              # 2#1#a2#hi1#b0#
    print(solution("deserialize", encoded))     # {'a': 'hi', 'b': ''}
