"""Delay-queue demo ported from DelayQueueTest.java (original Java package code.ds).

The Java version uses java.util.concurrent.DelayQueue and a real Thread.sleep(5s).
This port replaces wall-clock time with a *logical clock* so the demo is fully
deterministic and terminates instantly (no real sleeping, no threads to join).
"""

import heapq
import itertools


class DelayObject:
    """A delayed element; becomes "ready" once the clock passes start_time."""

    def __init__(self, data, delay, now=0):
        self.data = data
        # Java: startTime = currentTimeSeconds + delay. Here `now` is logical.
        self.start_time = now + delay

    def get_delay(self, now):
        # Seconds remaining until ready (<= 0 once elapsed).
        return self.start_time - now

    def __lt__(self, other):
        return self.start_time < other.start_time

    def __repr__(self):
        return "{data='%s', startTime=%d}" % (self.data, self.start_time)


class DelayQueue:
    """Deterministic stand-in for java.util.concurrent.DelayQueue.

    Backed by a min-heap keyed on start_time. A monotonic counter breaks ties so
    DelayObjects are never compared directly when their start_times are equal.
    """

    def __init__(self):
        self._heap = []
        self._counter = itertools.count()

    def offer(self, obj):
        heapq.heappush(self._heap, (obj.start_time, next(self._counter), obj))

    def size(self):
        return len(self._heap)

    def items(self):
        # Ascending start_time snapshot -> deterministic iteration order.
        return [entry[2] for entry in sorted(self._heap)]

    def remove(self, obj):
        self._heap = [entry for entry in self._heap if entry[2] is not obj]
        heapq.heapify(self._heap)


class DelayQueueTest:
    """Holds the shared queue + dedup set (the Java static fields)."""

    def __init__(self):
        self._dq = DelayQueue()
        self._set = set()
        self._now = 0  # logical clock in seconds

    def add(self, data, time):
        ob = DelayObject(data, time, self._now)
        if ob.data not in self._set:
            self._set.add(ob.data)
            self._dq.offer(ob)

    def get(self):
        out = []
        # Java does Thread.sleep(5000); we advance the logical clock instead.
        self._now += 5
        for dt in self._dq.items():
            if dt.get_delay(self._now) > 0:
                print(dt.data)
                out.append(dt.data)
            else:
                self._dq.remove(dt)
                self._set.discard(dt.data)
        print(self._dq.size())
        return out


if __name__ == "__main__":
    test = DelayQueueTest()
    test.add("foo", 10)
    test.add("bar", 4)
    test.add("bar2", 14)
    test.add("bar3", 12)
    test.add("foo1", 7)
    test.add("foo2", 8)
    test.add("foo3", 9)
    test.add("foo4", 3)

    # After advancing 5s, items with delay > 5 survive and are printed (in
    # ascending start_time order); the rest are evicted. Final size is printed.
    test.get()
