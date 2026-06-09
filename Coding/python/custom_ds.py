"""Custom data structures.

Port of java/Custom_DS.java (original package code.ds):
  - SparseSet    : O(1) get / set / set_all over a dynamically-indexed array.
  - AllOne       : O(1) inc/dec/get_max_key/get_min_key (reference is an
                   unimplemented stub).
  - Combo/SetAll : timestamp-based alternative to SparseSet's set_all.

The main demo exercises SparseSet (mirrors the Java main).
"""

from __future__ import annotations

import datetime
from typing import Dict, List, Optional


class AllOne:
    """O(1) inc / dec / get_max_key / get_min_key.

    The Java reference leaves every method unimplemented; ported faithfully as a
    stub.
    """

    def __init__(self):
        pass

    def inc(self, key: str) -> None:
        """Insert a new key with value 1, or increment an existing key by 1."""
        pass

    def dec(self, key: str) -> None:
        """Decrement a key by 1; remove it if its value reaches 0."""
        pass

    def get_max_key(self) -> str:
        """Return one of the keys with maximal value, or "" if empty."""
        return ""

    def get_min_key(self) -> str:
        """Return one of the keys with minimal value, or "" if empty."""
        return ""


class SparseSet:
    """Dynamically-sized array with O(1) get / set / set_all.

    set_all records a "checkpoint" pointer; any index written before the latest
    set_all reads back the set_all value, otherwise its own value.
    """

    def __init__(self, capacity: int):
        self.data: List[Optional[int]] = [None] * capacity
        self.indexer: List[Optional[int]] = [None] * capacity
        self.index_pointer = 0
        self.set_all_pointer = 0
        self.set_all_value: Optional[int] = None

    def set(self, index: int, value: int) -> None:
        self.data[index] = value
        self.indexer[index] = self.index_pointer
        self.index_pointer += 1

    def get(self, index: int) -> Optional[int]:
        if self.data[index] is not None:
            if self.indexer[index] >= self.set_all_pointer:
                return self.data[index]
            else:
                return self.set_all_value
        return None

    def set_all(self, value: int) -> None:
        self.set_all_value = value
        # Java: setAllPointer = indexPointer++  (post-increment).
        self.set_all_pointer = self.index_pointer
        self.index_pointer += 1


class Combo:
    """A (timestamp, value) pair used by SetAll."""

    def __init__(self, time: datetime.datetime, value: Optional[int]):
        self.time_stamp = time
        self.value = value


class SetAll:
    """Timestamp-based set / set_all / get (not exercised by the main demo)."""

    def __init__(self):
        self.default_value = Combo(datetime.datetime.now(), None)
        self.map: Dict[int, Combo] = {}

    def set_all(self, val: int) -> None:
        self.default_value.time_stamp = datetime.datetime.now()
        self.default_value.value = val

    def set(self, index: int, val: int) -> None:
        c = Combo(datetime.datetime.now(), val)
        self.map[index] = c

    def get(self, index: int) -> Optional[int]:
        if index not in self.map:
            return None
        if self.map[index].time_stamp > self.default_value.time_stamp:
            return self.map[index].value
        else:
            return self.default_value.value


if __name__ == "__main__":
    ds = SparseSet(20)
    ds.set(1, 5)
    ds.set(2, 6)

    ds.set_all(7)

    ds.set(2, 8)
    ds.set_all(7)
    ds.set(1, 9)
    ds.set(3, 6)
    ds.set(4, 8)
    ds.set_all(10)
    ds.set(4, 88)
    ds.set(5, 80)

    ds.set(1, 7)
    ds.set_all(99)
    ds.set(6, 9)

    print(ds.get(1))
    print(ds.get(2))
    print(ds.get(3))
    print(ds.get(4))
    print(ds.get(5))
    print(ds.get(6))
    # Expected: 99 / 99 / 99 / 99 / 99 / 9
