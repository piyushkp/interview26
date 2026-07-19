"""Iterate a list of int chunks value-by-value, resumable from a token.

ResumableIterator([[7, 8, 9], [10], [], [11, 12]]) yields 7, 8, 9, 10, 11, 12
- empty chunks are skipped. next() returns the next int (raising StopIteration
once exhausted) and hasNext() reports whether one remains. getState() hands
back an opaque "chunk:item" token for the NEXT position, and the fromState
factory rebuilds an iterator parked at exactly that position.
"""


def _drain_all(iterator):
    """Collect every remaining value from an iterator into a list."""
    # Time: O(m) for m remaining values. Space: O(m) for the result.
    values = []
    while iterator.hasNext():
        values.append(iterator.next())
    return values


# Approach (in plain terms):
#   Picture a stack of numbered pages where each page holds a handful of
#   numbers, and some pages are blank. We keep two counters: which page we
#   are on and which number on that page comes next. After every read - and
#   whenever we resume - we "normalize": if the current spot is past the end
#   of its page (or the page is blank), we flip forward to the top of the
#   next page, repeating until we land on a real number or run out of pages.
#   That way the two counters always point at the very next number to hand
#   out, so blank pages simply get skipped. Saving progress is just writing
#   those two counters down as a small "page:number" note; resuming reads the
#   note back and normalizes once so it lands on the right number.
#   Data structures used:
#     - the input data (a list of int chunks) - read in place, never copied.
#     - two integer indices (chunk, item) - the next value's position,
#       normalized to a real value or one-past-the-end.
#     - a compact "chunk:item" string - the opaque, resumable state token.
class ResumableIterator:

    def __init__(self, data):
        """Start at the first value of data (a list of int chunks)."""
        # Time: O(c) worst case to skip leading empty chunks (c = chunks).
        # Space: O(1) - only two index counters are stored.
        self._data = data
        self._chunk = 0     # index of the chunk holding the next value
        self._item = 0      # index within that chunk of the next value
        self._normalize()

    def _normalize(self):
        """Advance the (chunk, item) cursor past any exhausted or empty
        chunks so it points at a real next value or one-past-the-end."""
        # Time: O(c) worst case across empty chunks (c = chunks).
        # Space: O(1) - adjusts the two counters in place.
        while self._chunk < len(self._data):
            chunk = self._data[self._chunk]
            if self._item < len(chunk):
                break
            self._chunk += 1
            self._item = 0

    def hasNext(self):
        """True while another value remains to be handed out."""
        # Time: O(1), Space: O(1).
        return self._chunk < len(self._data)

    def next(self):
        """Return the next int, advancing the cursor; raise StopIteration
        once the chunks are exhausted."""
        # Time: O(c) worst case for the trailing normalize (c = chunks).
        # Space: O(1).
        if not self.hasNext():
            raise StopIteration("no more elements")
        value = self._data[self._chunk][self._item]
        self._item += 1
        self._normalize()
        return value

    def getState(self):
        """Opaque token 'chunk:item' marking the NEXT value's position."""
        # Time: O(1), Space: O(1) - formats two ints into a short string.
        return f"{self._chunk}:{self._item}"

    @staticmethod
    def fromState(data, state):
        """Rebuild an iterator over data parked at a saved 'chunk:item'
        token, normalized to the next real value."""
        # Time: O(c) worst case for the normalize (c = chunks).
        # Space: O(1) beyond the new iterator object.
        iterator = ResumableIterator(data)
        parts = state.split(":")
        iterator._chunk = int(parts[0])
        iterator._item = int(parts[1])
        iterator._normalize()
        return iterator


if __name__ == "__main__":
    # Example 1: empty chunks contribute nothing to the sequence.
    data1 = [[7, 8, 9], [10], [], [11, 12]]
    it = ResumableIterator(data1)
    print(_drain_all(it))          # [7, 8, 9, 10, 11, 12]

    # Example 2: save state after one value, then resume from it.
    data2 = [[1, 2], [3, 4]]
    it = ResumableIterator(data2)
    print(it.next())               # 1
    state = it.getState()
    it2 = ResumableIterator.fromState(data2, state)
    print(_drain_all(it2))         # [2, 3, 4]
    print(it2.hasNext())           # False

    # Example 3: next() past the end raises StopIteration.
    it3 = ResumableIterator([[5]])
    print(it3.next())              # 5
    try:
        it3.next()
    except StopIteration as exc:
        print(str(exc))            # no more elements

    # Example 4: a sequence of only empty chunks yields nothing.
    it4 = ResumableIterator([[], [], []])
    print(it4.hasNext())           # False
    print(_drain_all(it4))         # []

    # Example 5: state can be captured and restored mid-chunk.
    it5 = ResumableIterator([[1], [2, 3]])
    print(it5.next())              # 1
    print(it5.next())              # 2
    saved = it5.getState()
    revived = ResumableIterator.fromState([[1], [2, 3]], saved)
    print(_drain_all(revived))     # [3]
