"""Five self-contained IP exercises that share IPv4 parse/format helpers:
  - parse_ipv4(ip)              validate + parse a dotted IPv4 into octets
  - adjacent_ipv4(ip, dir)      the IPv4 one above/below
  - cidr_range(cidr)            first + last address of a CIDR block
  - ip_in_cidr(ip, cidr)        membership test for a CIDR block
  - adjacent_ipv6(ip, dir)      the IPv6 one above/below (period-separated)
No networking libraries are used - only manual parsing and arithmetic.
"""


# ---------- Part 1: validate & parse IPv4 ----------
def parse_ipv4(ip):
    """Parse a dotted-decimal IPv4 into 4 octets, or [] if invalid."""
    octets = _to_octets(ip)
    if octets is None:
        return []  # invalid -> empty list
    return list(octets)


# ---------- Part 2: adjacent IPv4 ----------
def adjacent_ipv4(ip, direction):
    """The IPv4 one above ('up') or below ('down'); "" on invalid/over/underflow."""
    o = _to_octets(ip)
    if o is None:
        return ""
    v = _octets_to_long(o)
    if direction == "up":
        if v == 0xFFFFFFFF:
            return ""  # would overflow above 255.255.255.255
        v += 1
    elif direction == "down":
        if v == 0:
            return ""  # would underflow below 0.0.0.0
        v -= 1
    else:
        return ""  # invalid direction
    return _long_to_ipv4(v)


# ---------- Part 3: first & last address of a CIDR block ----------
def cidr_range(cidr):
    """Inclusive [first, last] addresses of A.B.C.D/P; [] if invalid."""
    first_last = _cidr_first_last(cidr)
    if first_last is None:
        return []
    return [_long_to_ipv4(first_last[0]), _long_to_ipv4(first_last[1])]


# ---------- Part 4: membership in a CIDR block ----------
def ip_in_cidr(ip, cidr):
    """1 if ip is inside cidr (inclusive), 0 if not, -1 if either input is invalid."""
    o = _to_octets(ip)
    first_last = _cidr_first_last(cidr)
    if o is None or first_last is None:
        return -1
    v = _octets_to_long(o)
    return 1 if first_last[0] <= v <= first_last[1] else 0


# ---------- Part 5: adjacent IPv6 (8 period-separated hex groups) ----------
def adjacent_ipv6(ip, direction):
    """The IPv6 one above ('up') or below ('down'), normalized to eight
    lowercase 4-digit hex groups separated by '.'; "" on invalid input, invalid
    direction, or 128-bit over/underflow. Compressed '::' is NOT allowed."""
    groups = _to_groups(ip)
    if groups is None:
        return ""
    if direction == "up":
        up = True
    elif direction == "down":
        up = False
    else:
        return ""  # invalid direction

    i = 7
    if up:
        # propagate carry from the least-significant group
        while i >= 0 and groups[i] == 0xFFFF:
            groups[i] = 0
            i -= 1
        if i < 0:
            return ""  # overflow above ffff.ffff...ffff
        groups[i] += 1
    else:
        # propagate borrow from the least-significant group
        while i >= 0 and groups[i] == 0:
            groups[i] = 0xFFFF
            i -= 1
        if i < 0:
            return ""  # underflow below 0000.0000...0000
        groups[i] -= 1

    return ".".join(_to_hex4(g) for g in groups)


# ---------- shared helpers ----------

def _to_octets(ip):
    """Validate and split a dotted-decimal IPv4 into 4 octets, or None if invalid."""
    parts = _split_exact(ip, ".", 4)
    if parts is None:
        return None
    octets = []
    for p in parts:
        v = _parse_octet(p)
        if v < 0:
            return None
        octets.append(v)
    return octets


def _parse_octet(s):
    """Parse a decimal octet (digits only, leading zeros allowed, 0..255); -1 if invalid."""
    if not s:
        return -1
    value = 0
    for c in s:
        if c < "0" or c > "9":
            return -1
        value = value * 10 + (ord(c) - ord("0"))
        if value > 255:
            return -1  # also guards against overflow on long inputs
    return value


def _cidr_first_last(cidr):
    """[first, last] of a CIDR block, or None if invalid."""
    parts = _split_exact(cidr, "/", 2)
    if parts is None:
        return None
    o = _to_octets(parts[0])
    if o is None:
        return None
    prefix = _parse_prefix(parts[1])
    if prefix < 0:
        return None  # prefix must be 0..32
    base = _octets_to_long(o)
    mask = 0 if prefix == 0 else ((0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF)
    first = base & mask
    last = first | (~mask & 0xFFFFFFFF)
    return [first, last]


def _parse_prefix(s):
    """Parse a CIDR prefix length (digits only); -1 if not an integer in [0, 32]."""
    if not s:
        return -1
    value = 0
    for c in s:
        if c < "0" or c > "9":
            return -1
        value = value * 10 + (ord(c) - ord("0"))
        if value > 32:
            return -1
    return value


def _to_groups(ip):
    """Parse the 8 period-separated hex groups (1..4 hex digits each); None if invalid."""
    parts = _split_exact(ip, ".", 8)
    if parts is None:
        return None
    groups = []
    for p in parts:
        v = _parse_hex_group(p)
        if v < 0:
            return None
        groups.append(v)
    return groups


def _parse_hex_group(s):
    """Parse a 1..4 digit hex group into 0..0xFFFF; -1 if invalid."""
    if not s or len(s) > 4:
        return -1
    value = 0
    for c in s:
        d = _hex_val(c)
        if d < 0:
            return -1
        value = value * 16 + d
    return value


def _hex_val(c):
    if "0" <= c <= "9":
        return ord(c) - ord("0")
    if "a" <= c <= "f":
        return ord(c) - ord("a") + 10
    if "A" <= c <= "F":
        return ord(c) - ord("A") + 10
    return -1


def _to_hex4(v):
    """Format a 16-bit value as exactly 4 lowercase hex digits."""
    return f"{v:04x}"


def _split_exact(s, delim, expected):
    """Split s on delim (no merging, trailing empties kept); return the parts
    only if there are exactly 'expected' of them, else None."""
    if s is None:
        return None
    parts = s.split(delim)
    if len(parts) != expected:
        return None
    return parts


def _octets_to_long(o):
    return (o[0] << 24) | (o[1] << 16) | (o[2] << 8) | o[3]


def _long_to_ipv4(v):
    a = (v >> 24) & 0xFF
    b = (v >> 16) & 0xFF
    c = (v >> 8) & 0xFF
    d = v & 0xFF
    return f"{a}.{b}.{c}.{d}"


if __name__ == "__main__":
    print(parse_ipv4("192.168.0.1"))                       # [192, 168, 0, 1]
    print(adjacent_ipv4("192.168.0.255", "up"))            # 192.168.1.0
    print(cidr_range("192.168.0.0/24"))                    # ['192.168.0.0', '192.168.0.255']
    print(ip_in_cidr("192.168.0.10", "192.168.0.0/24"))    # 1
    print(adjacent_ipv6("0000.0000.0000.0000.0000.0000.0000.ffff", "up"))
    # 0000.0000.0000.0000.0000.0000.0001.0000
