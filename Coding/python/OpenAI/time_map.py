"""A time-based key-value store where each key keeps a history of values
stamped with strictly increasing timestamps, and a lookup returns the value
that was current at (or before) a queried timestamp.

  - set(key, value, timestamp): record `value` for `key` at the given time.
  - get(key, timestamp): return the value stored at the largest timestamp
    that is <= the queried timestamp, or None if there is no such value.

Per key, set() is called with strictly increasing timestamps, so each key's
timestamp list stays sorted and supports binary search.
"""

from bisect import bisect_right


# Approach (in plain terms):
#   Think of each key as having its own dated logbook. Every time you set a
#   value you add one dated entry to that key's logbook, and because the
#   dates only ever move forward the logbook is always in date order.
#   To answer "what was the value at time T?" we don't read the whole
#   logbook: we jump straight to the last entry whose date is on or before T
#   using binary search. If the very first entry is already later than T,
#   there is no answer yet and we report nothing.
#   Data structures used:
#     - a dict from key to a sorted list of timestamps - the ordered dates
#       in each key's logbook.
#     - a parallel dict from key to a list of values - the value written at
#       each of those timestamps (same position means the same entry).
#     - binary search (bisect_right) - finds the newest timestamp <= the
#       query in logarithmic time.
class TimeMap:

    def __init__(self):
        # Time: O(1), Space: O(1) - starts with two empty dicts.
        self._times = {}
        self._values = {}

    def set(self, key, value, timestamp):
        """Record that `key` holds `value` starting at `timestamp`."""
        # Time: O(1) amortized (two list appends), Space: O(1) per call.
        self._times.setdefault(key, []).append(timestamp)
        self._values.setdefault(key, []).append(value)

    def get(self, key, timestamp):
        """Return the value stored for `key` at the largest timestamp that is
        <= `timestamp`, or None if the key has no such entry."""
        # n = number of entries stored under this key.
        # Time:  O(log n) - binary search over the key's timestamps.
        # Space: O(1) - only index bookkeeping.
        times = self._times.get(key)
        if not times:
            return None
        idx = bisect_right(times, timestamp) - 1
        if idx < 0:
            return None
        return self._values[key][idx]


if __name__ == "__main__":
    tm = TimeMap()
    tm.set("exchangeRate", "1.10", 2)
    tm.set("exchangeRate", "1.12", 5)

    print(tm.get("exchangeRate", 1))    # None  (before the first timestamp)
    print(tm.get("exchangeRate", 2))    # 1.10  (exact first timestamp)
    print(tm.get("exchangeRate", 4))    # 1.10  (newest ts <= 4)
    print(tm.get("exchangeRate", 5))    # 1.12  (exact second timestamp)
    print(tm.get("exchangeRate", 9))    # 1.12  (newest ts <= 9)
    print(tm.get("unknownKey", 3))      # None  (key never set)

    # A second, independent key keeps its own sorted history.
    tm.set("featureFlag", "off", 10)
    tm.set("featureFlag", "on", 20)
    print(tm.get("featureFlag", 5))     # None  (before first timestamp)
    print(tm.get("featureFlag", 15))    # off   (newest ts <= 15)
    print(tm.get("featureFlag", 25))    # on    (newest ts <= 25)
