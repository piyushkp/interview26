"""Idiomatic Python 3 port of java/test.java (original package code.ds).

Interview / DSA reference implementation: IP range -> CIDR block conversion,
the "pour water" simulation, and simple word-frequency utilities.

Java has no method overloading, so the two ``iprange2cidr`` overloads were
renamed ``iprange2cidr_str`` (String, String) and ``iprange2cidr_long``
(long, long). The Java static method ``print(int)`` was renamed
``print_grid`` to avoid shadowing the built-in ``print``. Java
``Pattern``/``Matcher`` regex maps to the standard ``re`` module.
"""

import math
import re

# Java: static List<List<Integer>> data; (declared but unused)
data = None


# ---------------------------------------------------------------------------
# Grid printing demo helper (Java static String print(int precision))
# ---------------------------------------------------------------------------
def print_grid(precision):
    builder = []
    for _r in range(10):
        builder.append("| ")
        for _c in range(10):
            # Java used Double.toString(1233424234); the exact text is
            # irrelevant here (this helper is not exercised by the demo).
            s = str(1233424234)
            if len(s) < precision:
                builder.append(" " * (precision - len(s)))
            builder.append(s)
            builder.append("  ")
        builder.append("|\n")
    return "".join(builder)


# ---------------------------------------------------------------------------
# IP range -> CIDR blocks
# http://stackoverflow.com/questions/5020317
# ---------------------------------------------------------------------------
def iprange2cidr_str(ip_start, ip_end):
    """Overload taking dotted-decimal strings."""
    start = ip2long(ip_start)
    end = ip2long(ip_end)

    result = []
    while end >= start:
        max_size = 32
        while max_size > 0:
            mask = i_mask(max_size - 1)
            mask_base = start & mask
            if mask_base != start:
                break
            max_size -= 1
        x = math.log(end - start + 1) / math.log(2)
        max_diff = 32 - math.floor(x)
        if max_size < max_diff:
            max_size = max_diff
        ip = long2ip(start)
        result.append(ip + "/" + str(max_size))
        start += 2 ** (32 - max_size)
    return result


def iprange2cidr_long(start, end):
    """Overload taking already-converted long integer bounds."""
    result = []
    while end >= start:
        max_v = 32
        while max_v > 0:
            mask = i_mask(max_v - 1)
            mask_base = start & mask
            if mask_base != start:
                break
            max_v -= 1
        x = math.log(end - start + 1) / math.log(2)
        max_diff = 32 - math.floor(x)
        if max_v < max_diff:
            max_v = max_diff
        ip = long2ip(start)
        result.append(ip + "/" + str(max_v))
        start += 2 ** (32 - max_v)
    return result


def i_mask(s):
    return round(2 ** 32 - 2 ** (32 - s))


def ip2long(ipstring):
    parts = ipstring.split(".")
    num = 0
    for x in range(3, -1, -1):
        ip = int(parts[3 - x])
        num |= ip << (x << 3)
    return num


def long2ip(long_ip):
    return "{}.{}.{}.{}".format(
        (long_ip >> 24) & 0xFF,
        (long_ip >> 16) & 0xFF,
        (long_ip >> 8) & 0xFF,
        long_ip & 0xFF,
    )


# ---------------------------------------------------------------------------
# "Pour water" simulation
# ---------------------------------------------------------------------------
def pour_water(heights, v, k):
    n = len(heights)
    for _ in range(v):
        l = k
        r = k
        while l > 0 and heights[l] >= heights[l - 1]:
            l -= 1
        while l < k and heights[l] == heights[l + 1]:
            l += 1
        while r < n - 1 and heights[r] >= heights[r + 1]:
            r += 1
        while r > k and heights[r] == heights[r - 1]:
            r -= 1
        if heights[l] < heights[k]:
            heights[l] += 1
        else:
            heights[r] += 1
    return heights


# ---------------------------------------------------------------------------
# Word-frequency utilities
# ---------------------------------------------------------------------------
def count_unique_words(s):
    m = {}
    words = s.split(" ")
    for wrd in words:
        m[wrd] = m.get(wrd, 0) + 1
    count = 0
    for value in m.values():
        if value == 1:
            count += 1
    return count


def print_uniqued_words(s):
    # Extract words using a regex, then print those occurring exactly once.
    hm = {}
    for match in re.finditer(r"[a-zA-Z]+", s):
        word = match.group()
        hm[word] = hm.get(word, 0) + 1
    for w, c in hm.items():
        if c == 1:
            print(w)


if __name__ == "__main__":
    print(count_unique_words("Java is great. Grails is also great"))
    print_uniqued_words("Java is great. Grails is also great")
