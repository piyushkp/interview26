"""Iterate every IPv4 address in a CIDR block, in ascending order.

IPv4CIDRIterator("172.16.5.9/30") yields each address in the /30 block that
contains the given IP - from the block's network address to its last address.
next() returns the next address string, or None once the block is exhausted;
hasNext() reports whether another address is still available. If the given IP
is not the network address, the enclosing CIDR network is used.
"""


def _ip_to_int(ip):
    """Pack a dotted IPv4 string into a 32-bit integer."""
    # Time: O(1) - four octets. Space: O(1).
    value = 0
    for octet in ip.split("."):
        value = value * 256 + int(octet)
    return value


def _int_to_ip(value):
    """Format a 32-bit integer as a dotted IPv4 string."""
    # Time: O(1), Space: O(1).
    octet1 = (value >> 24) & 0xFF
    octet2 = (value >> 16) & 0xFF
    octet3 = (value >> 8) & 0xFF
    octet4 = value & 0xFF
    return f"{octet1}.{octet2}.{octet3}.{octet4}"


# Approach (in plain terms):
#   An IPv4 address is really just a 32-bit number, and a CIDR block is a run
#   of consecutive numbers. The "/p" says the first p bits are fixed and the
#   rest are free, so masking the address gives the block's first number
#   (network) and setting all the free bits gives its last number. Iterating
#   is then simple counting: keep a cursor at the current number, hand it out
#   (formatted back into dotted form) and step forward, stopping once we pass
#   the last number. Calling next() past the end keeps returning None.
#   Data structures used:
#     - two integers (a current cursor and the last address) - the whole
#       block is just a numeric range, so no collection is needed.
#     - integer bit masking - derives the first/last address from the prefix.
class IPv4CIDRIterator:

    def __init__(self, cidr):
        """Parse "a.b.c.d/p"; pin down the block's first and last address."""
        # Time: O(1), Space: O(1).
        ip_text, prefix_text = cidr.split("/")
        prefix = int(prefix_text)
        address = _ip_to_int(ip_text)
        # The 'prefix' leading bits are fixed; the rest span the block.
        if prefix == 0:
            mask = 0
        else:
            mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
        network = address & mask
        self._current = network                  # next address to hand out
        self._last = network | (~mask & 0xFFFFFFFF)

    def hasNext(self):
        """True while another address in the block remains."""
        # Time: O(1), Space: O(1).
        return self._current <= self._last

    def next(self):
        """Next address as a string, or None once the block is exhausted."""
        # Time: O(1), Space: O(1).
        if self._current > self._last:
            return None
        address = _int_to_ip(self._current)
        self._current += 1
        return address


if __name__ == "__main__":
    it = IPv4CIDRIterator("172.16.5.9/30")
    print(it.next())        # 172.16.5.8
    print(it.next())        # 172.16.5.9
    print(it.hasNext())     # True
    print(it.next())        # 172.16.5.10
    print(it.next())        # 172.16.5.11
    print(it.next())        # None
    print(it.hasNext())     # False

    # A /32 block is a single address.
    single = IPv4CIDRIterator("10.0.0.7/32")
    print(single.next())    # 10.0.0.7
    print(single.next())    # None

    # An IP that is not the network address still uses the enclosing block.
    block = IPv4CIDRIterator("192.168.1.130/29")
    print(block.next())     # 192.168.1.128
    print(block.hasNext())  # True
