"""Five self-contained IP exercises that share IPv4 parse/format helpers:
  - parse_ipv4(ip)              validate + parse a dotted IPv4 into octets
  - adjacent_ipv4(ip, dir)      the IPv4 one above/below
  - cidr_range(cidr)            first + last address of a CIDR block
  - ip_in_cidr(ip, cidr)        membership test for a CIDR block
  - adjacent_ipv6(ip, dir)      the IPv6 one above/below (period-separated)
No networking libraries are used - only manual parsing and arithmetic.
"""


# Approach (in plain terms):
#   Treat an IP address like the number on a car's odometer. Each octet (or hex
#   group) is one "wheel", and the whole address is just one big number written in
#   separate pieces.
#     - parse: read the dotted text and make sure every wheel holds a legal number.
#     - adjacent: roll the odometer one click up or down; when a wheel passes its
#       max it rolls over to 0 and nudges the wheel on its left (a carry), and the
#       mirror image happens when rolling down (a borrow).
#     - CIDR block: a "street" where every address shares the same leading bits;
#       the prefix says how many leading bits are fixed, which pins down the first
#       and last address on that street.
#     - membership: check whether an address falls between that street's first and
#       last address.
#   It is all plain integer and bit-mask math - no networking libraries.


# ---------- Part 1: validate & parse IPv4 ----------
def parse_ipv4(ip):
    """Parse a dotted-decimal IPv4 into 4 octets, or [] if invalid."""
    # n = length of the ip string.
    # Time: O(n) - scans each character once while validating. Space: O(1) - 4 octets.
    octets = _to_octets(ip)
    if octets is None:
        return []  # invalid -> empty list
    return list(octets)


# ---------- Part 2: adjacent IPv4 ----------
def adjacent_ipv4(ip, direction):
    """The IPv4 one above ('up') or below ('down'); "" on invalid/over/underflow."""
    # n = length of the ip string.
    # Time: O(n) - one parse pass plus O(1) arithmetic. Space: O(1).
    octets = _to_octets(ip)
    if octets is None:
        return ""
    value = _octets_to_long(octets)
    if direction == "up":
        if value == 0xFFFFFFFF:
            return ""  # would overflow above 255.255.255.255
        value += 1
    elif direction == "down":
        if value == 0:
            return ""  # would underflow below 0.0.0.0
        value -= 1
    else:
        return ""  # invalid direction
    return _long_to_ipv4(value)


# ---------- Part 3: first & last address of a CIDR block ----------
def cidr_range(cidr):
    """Inclusive [first, last] addresses of A.B.C.D/P; [] if invalid."""
    # n = length of the cidr string.
    # Time: O(n) - parse the address and prefix once, then O(1) math. Space: O(1).
    first_last = _cidr_first_last(cidr)
    if first_last is None:
        return []
    return [_long_to_ipv4(first_last[0]), _long_to_ipv4(first_last[1])]


# ---------- Part 4: membership in a CIDR block ----------
def ip_in_cidr(ip, cidr):
    """1 if ip is inside cidr (inclusive), 0 if not, -1 if either input is invalid."""
    # n = combined length of the ip and cidr strings.
    # Time: O(n) - parse both inputs once, then O(1) comparisons. Space: O(1).
    octets = _to_octets(ip)
    first_last = _cidr_first_last(cidr)
    if octets is None or first_last is None:
        return -1
    value = _octets_to_long(octets)
    return 1 if first_last[0] <= value <= first_last[1] else 0


# ---------- Part 5: adjacent IPv6 (8 period-separated hex groups) ----------
def adjacent_ipv6(ip, direction):
    """The IPv6 one above ('up') or below ('down'), normalized to eight
    lowercase 4-digit hex groups separated by '.'; "" on invalid input, invalid
    direction, or 128-bit over/underflow. Compressed '::' is NOT allowed."""
    # n = number of hex groups (always 8 when the input is valid).
    # Time: O(n) - parse the groups, propagate one carry/borrow, format each group.
    # Space: O(n) - the list of 8 groups plus the hex pieces we join.
    groups = _to_groups(ip)
    if groups is None:
        return ""
    if direction == "up":
        up = True
    elif direction == "down":
        up = False
    else:
        return ""  # invalid direction

    idx = 7
    if up:
        # propagate carry from the least-significant group
        while idx >= 0 and groups[idx] == 0xFFFF:
            groups[idx] = 0
            idx -= 1
        if idx < 0:
            return ""  # overflow above ffff.ffff...ffff
        groups[idx] += 1
    else:
        # propagate borrow from the least-significant group
        while idx >= 0 and groups[idx] == 0:
            groups[idx] = 0xFFFF
            idx -= 1
        if idx < 0:
            return ""  # underflow below 0000.0000...0000
        groups[idx] -= 1

    # Build the eight hex pieces one at a time, then join them with '.'.
    pieces = []
    for group in groups:
        pieces.append(_to_hex4(group))
    return ".".join(pieces)


# ---------- shared helpers ----------

def _to_octets(ip):
    """Validate and split a dotted-decimal IPv4 into 4 octets, or None if invalid."""
    # n = length of the ip string.
    # Time: O(n) - split, then validate every character once. Space: O(1) - 4 octets.
    parts = _split_exact(ip, ".", 4)
    if parts is None:
        return None
    octets = []
    for part in parts:
        value = _parse_octet(part)
        if value < 0:
            return None
        octets.append(value)
    return octets


def _parse_octet(s):
    """Parse a decimal octet (digits only, leading zeros allowed, 0..255); -1 if invalid."""
    # n = number of characters in s (at most a handful).
    # Time: O(n) - one pass over the digits. Space: O(1).
    if not s:
        return -1
    value = 0
    for ch in s:
        if ch < "0" or ch > "9":
            return -1
        value = value * 10 + (ord(ch) - ord("0"))
        if value > 255:
            return -1  # also guards against overflow on long inputs
    return value


def _cidr_first_last(cidr):
    """[first, last] of a CIDR block, or None if invalid."""
    # n = length of the cidr string.
    # Time: O(n) - parse the address and prefix once, then O(1) bit math. Space: O(1).
    parts = _split_exact(cidr, "/", 2)
    if parts is None:
        return None
    octets = _to_octets(parts[0])
    if octets is None:
        return None
    prefix = _parse_prefix(parts[1])
    if prefix < 0:
        return None  # prefix must be 0..32
    base = _octets_to_long(octets)
    mask = 0 if prefix == 0 else ((0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF)
    first = base & mask
    last = first | (~mask & 0xFFFFFFFF)
    return [first, last]


def _parse_prefix(s):
    """Parse a CIDR prefix length (digits only); -1 if not an integer in [0, 32]."""
    # n = number of characters in s (at most a couple).
    # Time: O(n) - one pass over the digits. Space: O(1).
    if not s:
        return -1
    value = 0
    for ch in s:
        if ch < "0" or ch > "9":
            return -1
        value = value * 10 + (ord(ch) - ord("0"))
        if value > 32:
            return -1
    return value


def _to_groups(ip):
    """Parse the 8 period-separated hex groups (1..4 hex digits each); None if invalid."""
    # n = length of the ip string.
    # Time: O(n) - split, then validate every hex digit once. Space: O(1) - 8 groups.
    parts = _split_exact(ip, ".", 8)
    if parts is None:
        return None
    groups = []
    for part in parts:
        value = _parse_hex_group(part)
        if value < 0:
            return None
        groups.append(value)
    return groups


def _parse_hex_group(s):
    """Parse a 1..4 digit hex group into 0..0xFFFF; -1 if invalid."""
    # n = number of characters in s (at most 4).
    # Time: O(n) - one pass over the hex digits. Space: O(1).
    if not s or len(s) > 4:
        return -1
    value = 0
    for ch in s:
        digit = _hex_val(ch)
        if digit < 0:
            return -1
        value = value * 16 + digit
    return value


def _hex_val(c):
    # Time: O(1) - a few range checks on a single character. Space: O(1).
    if "0" <= c <= "9":
        return ord(c) - ord("0")
    if "a" <= c <= "f":
        return ord(c) - ord("a") + 10
    if "A" <= c <= "F":
        return ord(c) - ord("A") + 10
    return -1


def _to_hex4(v):
    """Format a 16-bit value as exactly 4 lowercase hex digits."""
    # Time: O(1) - formats a fixed-width 4-digit string. Space: O(1).
    return f"{v:04x}"


def _split_exact(s, delim, expected):
    """Split s on delim (no merging, trailing empties kept); return the parts
    only if there are exactly 'expected' of them, else None."""
    # n = length of the string s.
    # Time: O(n) - a single split pass. Space: O(n) - the list of split parts.
    if s is None:
        return None
    parts = s.split(delim)
    if len(parts) != expected:
        return None
    return parts


def _octets_to_long(octets):
    # Time: O(1) - four shifts/ors on a fixed-size list. Space: O(1).
    return (octets[0] << 24) | (octets[1] << 16) | (octets[2] << 8) | octets[3]


def _long_to_ipv4(value):
    # Time: O(1) - four shifts/masks and one format. Space: O(1).
    octet1 = (value >> 24) & 0xFF
    octet2 = (value >> 16) & 0xFF
    octet3 = (value >> 8) & 0xFF
    octet4 = value & 0xFF
    return f"{octet1}.{octet2}.{octet3}.{octet4}"


if __name__ == "__main__":
    # ----- parse_ipv4 -----
    print(parse_ipv4("192.168.0.1"))          # [192, 168, 0, 1]
    print(parse_ipv4("0.0.0.0"))              # [0, 0, 0, 0]
    print(parse_ipv4("255.255.255.255"))      # [255, 255, 255, 255]
    print(parse_ipv4("010.0.0.1"))            # [10, 0, 0, 1]  (leading zeros allowed)
    print(parse_ipv4("256.1.1.1"))            # []  (octet > 255)
    print(parse_ipv4("1.2.3"))                # []  (too few octets)
    print(parse_ipv4("1.2.3.4.5"))            # []  (too many octets)
    print(parse_ipv4("1.2.3.a"))              # []  (non-digit)
    print(parse_ipv4(""))                     # []  (empty string)

    # ----- adjacent_ipv4 -----
    print(adjacent_ipv4("192.168.0.255", "up"))     # 192.168.1.0
    print(adjacent_ipv4("192.168.1.0", "down"))     # 192.168.0.255
    print(adjacent_ipv4("0.0.0.0", "up"))           # 0.0.0.1
    print(adjacent_ipv4("255.255.255.255", "up"))   # ""  (overflow -> empty line)
    print(adjacent_ipv4("0.0.0.0", "down"))         # ""  (underflow -> empty line)
    print(adjacent_ipv4("192.168.0.1", "sideways")) # ""  (bad direction -> empty line)
    print(adjacent_ipv4("999.1.1.1", "up"))         # ""  (invalid ip -> empty line)

    # ----- cidr_range -----
    print(cidr_range("192.168.0.0/24"))    # ['192.168.0.0', '192.168.0.255']
    print(cidr_range("0.0.0.0/0"))         # ['0.0.0.0', '255.255.255.255']
    print(cidr_range("192.168.1.130/25"))  # ['192.168.1.128', '192.168.1.255']
    print(cidr_range("10.0.0.5/32"))       # ['10.0.0.5', '10.0.0.5']
    print(cidr_range("1.2.3.4/33"))        # []  (prefix > 32)
    print(cidr_range("1.2.3.4"))           # []  (no prefix)

    # ----- ip_in_cidr -----
    print(ip_in_cidr("192.168.0.10", "192.168.0.0/24"))   # 1
    print(ip_in_cidr("192.168.0.0", "192.168.0.0/24"))    # 1  (first address)
    print(ip_in_cidr("192.168.0.255", "192.168.0.0/24"))  # 1  (last address)
    print(ip_in_cidr("192.168.1.10", "192.168.0.0/24"))   # 0  (outside block)
    print(ip_in_cidr("10.0.0.0", "0.0.0.0/0"))            # 1  (whole address space)
    print(ip_in_cidr("bad", "192.168.0.0/24"))            # -1 (invalid ip)
    print(ip_in_cidr("192.168.0.1", "192.168.0.0/33"))    # -1 (invalid cidr)

    # ----- adjacent_ipv6 -----
    print(adjacent_ipv6("0000.0000.0000.0000.0000.0000.0000.ffff", "up"))
    # 0000.0000.0000.0000.0000.0000.0001.0000
    print(adjacent_ipv6("0000.0000.0000.0000.0000.0000.0001.0000", "down"))
    # 0000.0000.0000.0000.0000.0000.0000.ffff
    print(adjacent_ipv6("ffff.ffff.ffff.ffff.ffff.ffff.ffff.ffff", "up"))    # ""  (overflow)
    print(adjacent_ipv6("0000.0000.0000.0000.0000.0000.0000.0000", "down"))  # ""  (underflow)
    print(adjacent_ipv6("0000.0000.0000.0000.0000.0000.0000.0001", "left"))  # ""  (bad direction)
    print(adjacent_ipv6("0.0.0.0.0.0.0", "up"))                              # ""  (only 7 groups)
