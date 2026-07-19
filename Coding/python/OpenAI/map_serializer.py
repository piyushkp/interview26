"""Invertible, binary-safe length-prefixed encoding of a dict[str, str].

Overview:
  Flattens a string->string map into one string and rebuilds it
  exactly, even when keys or values contain otherwise-dangerous
  characters such as '#', ':', '|', '=', or spaces. Every field is
  written as <length>#<content>, so a reader takes a length and then
  consumes exactly that many characters - the content is never scanned
  for a delimiter and may hold anything.

Interface (module-level functions):
  - serialize(mapping) -> str
        Encode the map. Pairs are written in lexicographically sorted
        key order, so the same map always yields the same string.
  - deserialize(data) -> dict
        Rebuild the original map from a serialized string; raises
        ValueError on malformed input.
  - solution(operation, data) -> str | dict
        Dispatch helper: "serialize" runs serialize(data),
        "deserialize" runs deserialize(data), anything else raises
        ValueError.

Format:
  <pair_count>#<key_len>#<key><value_len>#<value>...
  A length is decimal digits terminated by '#'; the content that
  follows is taken verbatim for exactly that many characters.

Semantics / rules:
  - Sorting keys makes serialize deterministic: equal maps encode to
    byte-identical strings.
  - Empty pieces are fine: the empty map encodes as "0#" and an empty
    key or value contributes "0#".
  - deserialize raises ValueError when a length is missing, a length
    token holds a non-digit, or a field runs past the end of the input.

Example:
  serialize({"a": "hi", "b": ""}) -> "2#1#a2#hi1#b0#"
  deserialize("2#1#a2#hi1#b0#")   -> {"a": "hi", "b": ""}
  serialize({})                   -> "0#"
"""


# Approach (in plain terms):
#   We need to flatten a dictionary into one string and later rebuild it
#   exactly, even when keys or values contain tricky characters like '#', ':'
#   or spaces. The trick is the one shipping labels use: write the LENGTH of
#   each piece right before the piece itself. To read it back you first read
#   the number, then grab exactly that many characters - so the content can be
#   anything without ever confusing the reader about where a piece ends.
#     - serialize: first write how many pairs there are, then for each key and
#       each value write "<length>#<text>". Keys are sorted so the same map
#       always produces the exact same string.
#     - deserialize: read the pair count, then repeatedly read a length, take
#       that many characters, and rebuild each key and value.
#   It is like tearing off exactly the number of squares of tape someone told
#   you to take, instead of guessing where one piece stops and the next begins.
#   Data structures used:
#     - a dict for the map, with keys sorted for deterministic output.
#     - a single-element list used as a movable read cursor while parsing -
#       lets a helper advance the parse position by reference.
def serialize(mapping):
    """Serialize a map to the length-prefixed format (keys sorted
    lexicographically)."""
    # n = number of pairs, m = total characters across all keys and values.
    # Time:  O(n log n + m) - sort the n keys, then copy m characters of
    #        content.
    # Space: O(n + m) - the collected pieces and the joined output string.
    parts = [f"{len(mapping)}#"]
    for key in sorted(mapping):  # deterministic key order
        value = mapping[key]
        parts.append(f"{len(key)}#{key}")
        parts.append(f"{len(value)}#{value}")
    return "".join(parts)


def deserialize(data):
    """Reconstruct the original map from a serialized string."""
    # L = length of the serialized string.
    # Time:  O(L) - one left-to-right scan, reading each character a constant
    #        number of times. Space: O(L) - the rebuilt keys, values, and map.
    mapping = {}
    pos = [0]
    count = _read_length(data, pos)
    for pair_number in range(count):
        key = _read_field(data, pos)
        value = _read_field(data, pos)
        mapping[key] = value
    return mapping


def _read_length(s, pos):
    """Read a run of digits terminated by '#', returning the int; advance
    past '#'."""
    # d = number of digit characters in this length token.
    # Time: O(d) - walks the digits once. Space: O(1).
    start = pos[0]
    while pos[0] < len(s) and s[pos[0]] != "#":
        ch = s[pos[0]]
        if ch < "0" or ch > "9":
            raise ValueError(f"Malformed: expected digit at index {pos[0]}")
        pos[0] += 1
    if pos[0] >= len(s) or start == pos[0]:
        raise ValueError("Malformed: missing length or '#'")
    length = int(s[start:pos[0]])
    pos[0] += 1  # skip the '#'
    return length


def _read_field(s, pos):
    """Read a length-prefixed field: <len>#<exactly len chars>."""
    # f = length of this field's content (taken from its length prefix).
    # Time:  O(f) - reads the prefix and slices f characters.
    # Space: O(f) - the slice.
    length = _read_length(s, pos)
    if pos[0] + length > len(s):
        raise ValueError("Malformed: field length exceeds input")
    field = s[pos[0]:pos[0] + length]
    pos[0] += length
    return field


def solution(operation, data):
    """Judge-style entry point: "serialize" a dict -> str, or "deserialize" a
    str -> dict."""
    # Time/Space: O(1) dispatch that delegates to serialize or deserialize, so
    # the cost is whichever of those runs (see their complexity notes above).
    if operation == "serialize":
        return serialize(data)
    if operation == "deserialize":
        return deserialize(data)
    raise ValueError(f"Unknown operation: {operation}")


if __name__ == "__main__":
    # ----- serialize -----
    print(solution("serialize", {}))                        # 0#
    encoded = solution("serialize", {"a": "hi", "b": ""})
    print(encoded)                                          # 2#1#a2#hi1#b0#
    print(serialize({"key": "value"}))                      # 1#3#key5#value
    print(serialize({"": ""}))                              # 1#0#0#
    print(serialize({"a#b": "c#d", "x": "y"}))  # 2#3#a#b3#c#d1#x1#y
    print(serialize({"n": "12#34"}))                        # 1#1#n5#12#34

    # ----- deserialize (round-trips) -----
    print(solution("deserialize", encoded))  # {'a': 'hi', 'b': ''}
    print(deserialize("0#"))                                # {}
    print(deserialize("1#0#0#"))                            # {'': ''}
    # -> {'a#b': 'c#d', 'x': 'y'}
    print(deserialize(serialize({"a#b": "c#d", "x": "y"})))
    print(deserialize(serialize({"n": "12#34"})))           # {'n': '12#34'}

    # ----- malformed input raises ValueError -----
    try:
        deserialize("")
    except ValueError as err:
        print("error:", err)          # error: Malformed: missing length or '#'
    try:
        deserialize("xyz")
    except ValueError as err:
        print("error:", err)  # error: Malformed: expected digit at index 0
    try:
        deserialize("1#5#ab")
    except ValueError as err:
        print("error:", err)  # error: Malformed: field length exceeds input

    # ----- unknown operation raises ValueError -----
    try:
        solution("frobnicate", {})
    except ValueError as err:
        print("error:", err)          # error: Unknown operation: frobnicate
