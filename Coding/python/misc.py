"""
misc.py - idiomatic Python 3 port of Coding/java/MISC.java (original package code.ds).

A grab-bag of interview / DSA reference implementations: interval problems, expression
evaluation, iterators, geometry, caches (LRU), randomized data structures, stream/log
processing and assorted utilities.

Created by Piyush Patel (Java original).  Ported faithfully to Python; a handful of
reference methods are intentionally buggy in the source - those are preserved as-is and
flagged with NOTE comments.  They are not exercised by the __main__ demo.
"""

import collections
import enum
import heapq
import math
import os
import random
import re
import threading

INT_MAX = 2147483647
INT_MIN = -2147483648


# ---------------------------------------------------------------------------
# Intervals
# ---------------------------------------------------------------------------
# Given a set of time intervals in any order, merge all overlapping intervals into one.
# {{1,3}, {2,4}, {5,7}, {6,8}} -> {1,4} and {5,8}.  Time Complexity: O(n log n)
class Interval:
    def __init__(self, s, e):
        self.start = s
        self.end = e

    def __repr__(self):
        return "[%d,%d]" % (self.start, self.end)


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "(%d,%d)" % (self.x, self.y)


class Room(enum.Enum):
    Open = 0
    Closed = 1
    GUARD = 2


# ---------------------------------------------------------------------------
# Singleton / iterables
# ---------------------------------------------------------------------------
class Singleton:
    _lock = threading.Lock()

    def __init__(self):
        self.uniq_instance = None

    def get_instance(self):  # "synchronized" in Java
        with Singleton._lock:
            if self.uniq_instance is None:
                self.uniq_instance = Singleton()
            return self.uniq_instance


class Line:
    def __init__(self):
        self.line_number = 0
        self.line_data = None


# implement an iterable to read a "file" (byte buffer)
class FileReaderIterator:
    def __init__(self, dat):
        self.data = dat
        self.buffer = collections.deque()
        self._lock = threading.Lock()

    def has_next(self):
        with self._lock:
            self._try_get_next()
            return len(self.buffer) > 0

    def __next__(self):
        if not self.has_next():
            raise StopIteration("Nothing left")
        return self.buffer.popleft()

    def __iter__(self):
        return self

    def _try_get_next(self):
        if not self.buffer:
            for item in self.data:
                self.buffer.append(item)

    def remove(self):
        raise NotImplementedError("It is read-only")


class FileReaderIterable:
    def __init__(self, data):
        self.data = data

    def __iter__(self):
        return FileReaderIterator(self.data)


# Airbnb: 2D Iterator with remove().  Traverses left->right, top->bottom.
class TwoDArrayIterator:
    def __init__(self, array):
        self.array = array
        self.row_id = 0
        self.col_id = 0
        self.num_rows = len(array)

    def has_next(self):
        if not self.array:
            return False
        while self.row_id < self.num_rows and (
            self.array[self.row_id] is None or len(self.array[self.row_id]) == 0
        ):
            self.row_id += 1
        return self.row_id < self.num_rows

    def next(self):
        ret = self.array[self.row_id][self.col_id]
        self.col_id += 1
        if self.col_id == len(self.array[self.row_id]):
            self.row_id += 1
            self.col_id = 0
        return ret

    def remove(self):
        # Case 1: removing last element of the row
        if self.col_id == 0:
            row_to_remove = self.row_id - 1
            list_to_remove = self.array[row_to_remove]
            col_to_remove = len(list_to_remove) - 1
            del list_to_remove[col_to_remove]
        else:  # Case 2: not the last element
            row_to_remove = self.row_id
            list_to_remove = self.array[row_to_remove]
            col_to_remove = self.col_id - 1
            del list_to_remove[col_to_remove]
        if len(list_to_remove) == 0:
            self.array.remove(list_to_remove)
            self.row_id -= 1
        if self.col_id != 0:
            self.col_id -= 1


# ---------------------------------------------------------------------------
# Nested integer list (Airbnb mini parser)
# ---------------------------------------------------------------------------
class NestedIntList:
    def __init__(self, value=None):
        if value is None:
            self.int_list = []
            self.is_number = False
            self.value = 0
        else:
            self.value = value
            self.is_number = True
            self.int_list = None

    def add(self, num):
        self.int_list.append(num)

    def mini_parser(self, s):
        if s is None or len(s) == 0:
            return None
        # Corner case "123"
        if s[0] != '[':
            return NestedIntList(int(s))
        i = 0
        counter = 1
        stack = []
        result = None
        # NOTE: faithful port of reference; substring math is buggy for the leading '['.
        while i < len(s):
            c = s[i]
            if c == '[':
                num = NestedIntList(int(s[counter:i])) if s[counter:i] else NestedIntList()
                if stack:
                    stack[-1].add(num)
                stack.append(num)
                counter = i + 1
            elif c == ',' or c == ']':
                if counter != i:
                    value = int(s[counter:i])
                    stack[-1].add(NestedIntList(value))
                counter = i + 1
                if c == ']':
                    result = stack.pop()
            i += 1
        return result

    def __repr__(self):
        if self.is_number:
            return str(self.value)
        return repr(self.int_list)


# ---------------------------------------------------------------------------
# Interval tree (find conflicting appointments)
# ---------------------------------------------------------------------------
class Interval1:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.max = end
        self.left = None
        self.right = None

    def compare_to(self, i):
        if self.start < i.start:
            return -1
        elif self.start == i.start:
            return -1 if self.end <= i.end else 1
        return 1

    def __lt__(self, other):
        return self.compare_to(other) < 0


class IntervalTree:
    def __init__(self):
        self.root = None

    def insert(self, root, new_node):
        if root is None:
            return new_node
        low = root.start
        if new_node.start < low:
            root.left = self.insert(root.left, new_node)
        else:
            root.right = self.insert(root.right, new_node)
        if root.max < new_node.end:
            root.max = new_node.end
        return root

    # Find all overlapping intervals for given interval
    def intersect_interval(self, root, i, output):
        if root is None:
            return
        if not (root.start > i.end) or (root.end < i.start):
            output.append(root)
        if root.left is not None and root.left.max >= i.start:
            self.intersect_interval(root.left, i, output)
        self.intersect_interval(root.right, i, output)

    # Find all non-overlapping intervals for given interval
    def non_overlapping_interval(self, root, i, output):
        if root is None:
            return
        if not (root.start < i.end) or (root.end > i.start):
            output.append(root)
        if root.left is not None and root.left.max <= i.start:
            self.intersect_interval(root.left, i, output)
        self.intersect_interval(root.right, i, output)

    def do_overlap(self, i1, i2):
        return i1.start <= i2.end and i2.start <= i1.end

    def overlap_search(self, root, i):
        if root is None:
            return None
        if self.do_overlap(root, i):
            return root
        if root.left is not None and root.left.max >= i.start:
            return self.overlap_search(root.left, i)
        return self.overlap_search(root.right, i)

    def print_conflicting(self, appt, n):
        root = None
        root = self.insert(root, appt[0])
        for i in range(1, n):
            res = self.overlap_search(root, appt[i])
            if res is not None:
                print("[%d,%d] Conflicts with [%d,%d]" % (
                    appt[i].start, appt[i].end, res.start, res.end))
            root = self.insert(root, appt[i])


# ---------------------------------------------------------------------------
# LRU caches
# ---------------------------------------------------------------------------
class DoublyNode:
    def __init__(self):
        self.data = 0
        self.key = 0
        self.next = None
        self.prev = None


# Implement LRU Cache - O(1) all operations using pseudo head/tail to avoid null checks.
class LRU:
    def __init__(self, capacity):
        self.capacity = capacity
        self.map = {}
        self.head = DoublyNode()
        self.head.prev = None
        self.tail = DoublyNode()
        self.tail.next = None
        self.head.next = self.tail
        self.tail.prev = self.head

    def _add(self, item):
        item.prev = self.head
        item.next = self.head.next
        self.head.next.prev = item
        self.head.next = item

    def _remove(self, item):
        pre = item.prev
        post = item.next
        pre.next = post
        post.prev = pre

    def _move_first(self, item):
        self._remove(item)
        self._add(item)

    def _remove_last(self):
        res = self.tail.prev
        self._remove(res)
        return res

    def get(self, key):
        if key in self.map:
            node = self.map[key]
            self._move_first(node)
            return node.data
        return -1

    def set(self, key, value):
        if key in self.map:  # cache hit
            node = self.map[key]
            self._move_first(node)
            node.data = value
            self.map[key] = node
            return
        if len(self.map) >= self.capacity:  # cache full + miss
            end = self._remove_last()
            del self.map[end.key]
        node = DoublyNode()
        node.key = key
        node.data = value
        self._add(node)
        self.map[key] = node

    def remove_cache(self, key):
        if key in self.map:
            node = self.map[key]
            del self.map[key]
            self._remove(node)


# Thread safe LRU cache.
# NOTE: Java reference uses ConcurrentHashMap.contains() (== containsValue, a bug) and an
# uninitialized AtomicLong capacity; simplified here to a single lock + dict + deque so it runs.
class LRUThreadSafe:
    def __init__(self, capacity):
        self.queue = collections.deque()
        self.map = {}
        self._lock = threading.RLock()
        self.capacity = capacity
        self.total = 0

    def get(self, key):
        with self._lock:
            v = None
            if key in self.map:
                v = self.map[key]
                try:
                    self.queue.remove(key)
                except ValueError:
                    pass
                self.queue.append(key)
            return v

    def set(self, key, value):
        with self._lock:
            if key in self.map:
                try:
                    self.queue.remove(key)
                except ValueError:
                    pass
            while self.total >= self.capacity and self.queue:
                queue_key = self.queue.popleft()
                self.map.pop(queue_key, None)
                self.total -= 1
            self.queue.append(key)
            self.total += 1
            self.map[key] = value
            return value

    def remove(self, key):
        with self._lock:
            v = None
            if key in self.map:
                v = self.map.pop(key)
                try:
                    self.queue.remove(key)
                except ValueError:
                    pass
                self.total -= 1
            return v


# Implement a peek using an existing iterator's next/hasNext.
class PeekingIterator:
    def __init__(self, iterator):
        self.iterator = iter(iterator)
        self.exhausted = False
        self.slot_filled = False
        self.slot = None

    def _fill(self):
        if self.exhausted or self.slot_filled:
            return
        try:
            self.slot = next(self.iterator)
            self.slot_filled = True
        except StopIteration:
            self.exhausted = True
            self.slot = None
            self.slot_filled = False

    def peek(self):
        self._fill()
        return None if self.exhausted else self.slot

    def __next__(self):
        if not self.has_next():
            raise StopIteration()
        if self.slot_filled:
            x = self.slot
        else:
            x = next(self.iterator)
        self.slot = None
        self.slot_filled = False
        return x

    def has_next(self):
        if self.exhausted:
            return False
        if self.slot_filled:
            return True
        self._fill()
        return not self.exhausted

    def __iter__(self):
        return self


# ---------------------------------------------------------------------------
# O(1) data structures
# ---------------------------------------------------------------------------
# Design "Map" of (key, value) with O(1) insert/delete/get/getRandomKey.
class CustomMap:
    def __init__(self):
        self._map = {}
        self.arr = []
        self.index = 0
        self.size = 0

    def insert(self, key, value):
        if key not in self._map:
            self.index = self.size
            self._map[key] = [value, self.index]
            self.arr.insert(self.index, key)
            self.size += 1
        else:
            self._map[key][0] = value

    def get(self, key):
        return self._map[key][0]

    def delete(self, key):
        self.index = self._map[key][1]
        # copy last element to index then drop last -> O(1)
        self.arr[self.index] = self.arr[self.size - 1]
        self.arr.pop(self.size - 1)
        self.size -= 1
        del self._map[key]
        self._map[self.arr[self.index]][1] = self.index

    def get_random_key(self):
        # NOTE: faithful port - can index out of range (Math.random()*size + 1).
        r = int(random.random() * self.size + 1)
        return self.arr[r]

    def clear(self):
        self.size = 0


# Insert/Delete/Search/getRandom in Theta(1).  (Buggy with duplicate values, as in reference.)
class MyDS:
    def __init__(self):
        self.arr = []
        self.hash = {}

    def add(self, x):
        if self.hash.get(x) is not None:
            return
        s = len(self.arr)
        self.arr.append(x)
        self.hash[x] = s

    def remove(self, x):
        index = self.hash.get(x)
        if index is None:
            return
        del self.hash[x]
        size = len(self.arr)
        last = self.arr[size - 1]
        self.arr[index], self.arr[size - 1] = self.arr[size - 1], self.arr[index]
        self.arr.pop(size - 1)
        self.hash[last] = index

    def get_random(self):
        index = random.randrange(len(self.arr))
        return self.arr[index]

    def search(self, x):
        return self.hash.get(x)


# Insert/Delete/GetRandom O(1) - duplicates allowed.
class RandomizedCollection:
    def __init__(self):
        self.list = []
        self.map = {}  # value -> ordered set of indices (dict used as ordered set)

    def insert(self, val):
        ans = True
        loc = len(self.list)
        self.list.append(val)
        if val in self.map:
            ans = False
            indices = self.map[val]
        else:
            indices = {}
        indices[loc] = None
        self.map[val] = indices
        return ans

    def remove(self, val):
        if val not in self.map or not self.map[val]:
            return False
        loc_to_remove = next(iter(self.map[val]))
        self.map[val].pop(loc_to_remove, None)
        if loc_to_remove < len(self.list) - 1:
            num_to_swap = self.list[len(self.list) - 1]
            self.list[loc_to_remove] = num_to_swap
            if (len(self.list) - 1) in self.map[num_to_swap]:
                self.map[num_to_swap].pop(len(self.list) - 1, None)
            self.map[num_to_swap][loc_to_remove] = None
        self.list.pop(len(self.list) - 1)
        return True

    def get_random(self):
        if not self.list:
            return 0
        loc = random.randrange(len(self.list))
        return self.list[loc]


# HashMap with a time dimension: get(K, t) returns value at the greatest t' <= t.
class TimeHashMap:
    def __init__(self):
        self.map = {}  # key -> { time: value }

    def get(self, key, time):
        tree = self.map.get(key)
        if tree is None:
            return None
        floor = None
        for t in sorted(tree.keys()):
            if t <= time:
                floor = t
            else:
                break
        return None if floor is None else tree[floor]

    def put(self, key, time, value):
        self.map.setdefault(key, {})[time] = value


# Count visitors in the past minute.  (field `hit` renamed to `hits` to avoid clash with hit()).
class HitCounter:
    def __init__(self):
        self.time = [0] * 60
        self.hits = [0] * 60

    def hit(self, timestamp):
        index = timestamp % 60
        if self.time[index] != timestamp:
            self.time[index] = timestamp
            self.hits[index] = 1
        else:
            self.hits[index] += 1

    def get_hits(self, timestamp):
        total = 0
        for i in range(60):
            if timestamp - self.time[i] < 60:
                total += self.hits[i]
        return total


# ---------------------------------------------------------------------------
# Stream / log processing
# ---------------------------------------------------------------------------
class Log:
    def __init__(self, id="", time=0):
        self.id = id
        self.time = time


class LogCount:
    def __init__(self, time, count):
        self.time = time
        self.count = count


# Stream deduplication - print unique data of the last minute.
class Streamdedu:
    def __init__(self):
        self.time = [0] * 60
        self.data = [None] * 60

    def on_data_received(self, input_, timestamp):
        index = timestamp % 60
        if self.time[index] != timestamp:
            self.time[index] = timestamp
            temp = set()
            temp.add(input_)
            self.data[index] = temp
        else:
            temp = self.data[index]
            temp.add(input_)

    def print_data(self, timestamp):
        output = set()
        for i in range(60):
            if timestamp - self.time[i] < 60:
                if self.data[i]:
                    output.update(self.data[i])
        return output


# Logger: print a message only if not printed in the last 10 seconds.
class Logger:
    def __init__(self):
        self.map = {}

    def should_print_message(self, timestamp, message):
        if message in self.map and (timestamp - self.map[message] < 10):
            return False
        self.map[message] = timestamp
        return True


# Number of users logged in at each event time.
class Input:
    def __init__(self, name="", login=0.0, logout=0.0):
        self.name = name
        self.login = login
        self.logout = logout


class Type:
    def __init__(self, time, logged_in):
        self.time = time
        self.loggedin = logged_in

    def __lt__(self, other):
        return self.time < other.time


class Output:
    def __init__(self, t, num):
        self.time = t
        self.num_logged_in = num

    def __repr__(self):
        return "(%s, %d)" % (self.time, self.num_logged_in)


# ---------------------------------------------------------------------------
# Browser history (reference is buggy; preserved verbatim, not exercised)
# ---------------------------------------------------------------------------
class BrowserNode:
    def __init__(self, url):
        self.next = None
        self.prev = None
        self.url = url
        self.time = None
        self.curr = None


class Browser:
    def __init__(self, size):
        self.head = None
        self.end = None
        self.curr = None
        self.size = size

    def add(self, url):
        node = BrowserNode(url)
        if self.head is None:
            self.head = node
            self.end = self.head
        else:
            node.prev = self.end
            self.end.next = node
            self.end = node
        self.curr = node
        self.size += 1

    def forward(self):
        if self.curr is not None and self.curr.next is not None:
            self.curr.next = self.curr.next.next
            self.curr.prev = self.curr
            self.curr = self.curr.next
            return self.curr.next.url
        return None

    def backward(self):
        if self.curr is not None and self.curr.prev is not None:
            self.curr.next = self.curr
            self.curr.prev = self.curr.prev.prev
            self.curr = self.curr.prev
            return self.curr.prev.url
        return None


# Moving average of last N numbers.  time O(1), space O(window).
class MovingAverage:
    def __init__(self, size):
        self.window = [0] * size
        self.n = 0
        self.insert = 0
        self.sum = 0

    def next(self, val):
        if self.n < len(self.window):
            self.n += 1
        self.sum -= self.window[self.insert]
        self.sum += val
        self.window[self.insert] = val
        self.insert = (self.insert + 1) % len(self.window)
        return self.sum / self.n  # caller guards divide-by-zero


# Merge k sorted lists via a min-heap (used by MISC.process/next_element).
class Element:
    def __init__(self):
        self.value = 0
        self.position = 0
        self.k_index = 0


# Simple Pair (replaces javafx.util.Pair).
class Pair:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def get_key(self):
        return self.key

    def get_value(self):
        return self.value


# ---------------------------------------------------------------------------
# MISC: the algorithm collection
# ---------------------------------------------------------------------------
class MISC:
    # static fields from the Java class
    intervals = []
    coverage = 0
    column_flipping_stat = {}
    max_wishes = -1

    def __init__(self):
        # instance fields
        self.min_heap = []
        self._seq = 0
        self.data = None
        self.files = []

    # --- interval merging --------------------------------------------------
    @staticmethod
    def merge_intervals_in_place(intervals):
        # in place merge, space O(1), time O(n log n)
        if intervals is None:
            raise ValueError()
        intervals.sort(key=lambda iv: iv.start)
        result = []
        prev = None
        for cur in intervals:
            if prev is not None and prev.end >= cur.start:
                prev.end = max(prev.end, cur.end)
            else:
                result.append(cur)
                prev = cur
        intervals[:] = result
        return intervals

    @staticmethod
    def merge_intervals(intervals):
        # space O(n)
        intervals.sort(key=lambda iv: iv.start)
        merged = []
        for interval in intervals:
            if not merged or merged[-1].end < interval.start:
                merged.append(interval)
            else:
                merged[-1].end = max(merged[-1].end, interval.end)
        return merged

    # Find least number of intervals from A that fully cover B.
    @staticmethod
    def find_min_intervals(intervals, target):
        # sort by start asc, end desc
        intervals.sort(key=lambda iv: (iv.start, -iv.end))
        i = 0
        start = target.start
        max_end = -1
        num = 0
        while i < len(intervals) and max_end < target.end:
            if intervals[i].end <= start:
                i += 1
            else:
                if intervals[i].start > start:
                    break
                while (i < len(intervals) and max_end < target.end
                       and intervals[i].start <= start):
                    max_end = max(max_end, intervals[i].end)
                    i += 1
                if start != max_end:
                    start = max_end
                    num += 1
        if max_end < target.end:
            return 0
        return num

    # Russian doll envelopes - maximum nesting count.
    @staticmethod
    def max_envelope(intervals):
        if len(intervals) == 0 or len(intervals) == 1:
            return 0
        intervals.sort(key=lambda iv: (iv.start, -iv.end))
        first = intervals[0]
        width = first.start
        height = first.end
        count = 0
        for i in range(1, len(intervals)):
            curr = intervals[i]
            if width < curr.start and height < curr.end:
                count += 1
            width = curr.start
            height = curr.end
        return count + 1

    @staticmethod
    def add_interval(frm, to):
        MISC.intervals.append(Interval(frm, to))

    @staticmethod
    def add_interval1(frm, to):
        # NOTE: faithful port of buggy reference (appends inside the merge loop). Iterates a
        # snapshot so it terminates instead of raising ConcurrentModificationException.
        new_interval = Interval(frm, to)
        if len(MISC.intervals) == 0:
            MISC.intervals.append(new_interval)
            MISC.coverage = new_interval.end - new_interval.start
            return
        for prev in list(MISC.intervals):
            if prev.end >= new_interval.start:
                new_interval.end = max(prev.end, new_interval.end)
                new_interval.start = min(prev.start, new_interval.start)
                MISC.coverage -= prev.end - prev.start
                if prev in MISC.intervals:
                    MISC.intervals.remove(prev)
            MISC.intervals.append(new_interval)
            MISC.coverage += new_interval.end - new_interval.start

    def get_coverage_of_intervals(self, intervals=None):
        # no-arg overload returns running coverage; list overload computes unique coverage.
        if intervals is None:
            return MISC.coverage
        if not intervals:
            return 0
        intervals.sort(key=lambda iv: iv.start)
        length = 0
        prev = intervals[0]
        for i in range(1, len(intervals)):
            curr = intervals[i]
            if prev.end > curr.start:
                prev.end = max(prev.end, curr.end)
            else:
                length += prev.end - prev.start
                prev = curr
        length += prev.end - prev.start
        return length

    # Given non-overlapping intervals and a request interval, find the gaps inside the request.
    # [[10,15],[25,35],[45,65],[85,95]], req [17,100] -> [[17,25],[35,45],[65,85],[95,100]]
    @staticmethod
    def find_interval(intervals, request_interval):
        result = []
        if (intervals is None or len(intervals) == 0
                or request_interval.end < request_interval.start):
            return result
        # min-heap ordered by start; (start, seq, interval) avoids comparing Interval objects.
        heap = []
        for idx, interval in enumerate(intervals):
            heapq.heappush(heap, (interval.start, idx, interval))
        while heap and request_interval.start >= heap[0][2].end:
            heapq.heappop(heap)
        start = request_interval.start
        peek = heap[0][2]
        if start < peek.start:
            if request_interval.end <= peek.start:
                result.append(request_interval)
                return result
            else:
                result.append(Interval(start, peek.start))
        start = max(start, heapq.heappop(heap)[2].end)
        while heap and heap[0][2].start < request_interval.end:
            current = heapq.heappop(heap)[2]
            result.append(Interval(start, current.start))
            start = current.end
        if request_interval.end > start:
            result.append(Interval(start, request_interval.end))
        return result

    # Can a person attend all meetings?
    @staticmethod
    def can_attend(intervals):
        if not intervals:
            return True
        ordered = sorted(intervals, key=lambda iv: iv.start)
        for i in range(len(ordered) - 1):
            if ordered[i].end > ordered[i + 1].start:
                return False
        return True

    # Minimum meeting rooms required.
    @staticmethod
    def min_meeting_rooms(intervals):
        if not intervals:
            return 0
        ordered = sorted(intervals, key=lambda iv: iv.start)
        heap = []
        count = 1
        heapq.heappush(heap, ordered[0].end)
        for i in range(1, len(ordered)):
            if ordered[i].start < heap[0]:
                count += 1
            else:
                heapq.heappop(heap)
            heapq.heappush(heap, ordered[i].end)
        return count

    # Greedy variant.
    def min_meeting_rooms1(self, intervals):
        start = sorted(iv.start for iv in intervals)
        end = sorted(iv.end for iv in intervals)
        end_idx = 0
        res = 0
        for i in range(len(start)):
            if start[i] < end[end_idx]:
                res += 1
            else:
                end_idx += 1
        return res

    # Maximum number of simultaneously active drivers.
    @staticmethod
    def find_max_driver(input_):
        if not input_:
            return 0
        start = sorted(x.start for x in input_)
        end = sorted(x.end for x in input_)
        driver_in = 1
        max_driver = 1
        i = 1
        j = 0
        while i < len(input_) and j < len(input_):
            if start[i] < end[j]:
                driver_in += 1
                max_driver = max(driver_in, max_driver)
                i += 1
            else:
                driver_in -= 1
                j += 1
        return max_driver

    # --- expression evaluation --------------------------------------------
    @staticmethod
    def is_operator(c):
        return c in ('+', '-', '*', '/', '^', '(', ')')

    @staticmethod
    def is_space(c):
        return c == ' '

    @staticmethod
    def lower_precedence(op1, op2):
        # Does op1 (on the left) have lower precedence than op2 (on the right)?
        if op1 in ('+', '-'):
            return not (op2 == '+' or op2 == '-')
        if op1 in ('*', '/'):
            return op2 == '^' or op2 == '('
        if op1 == '^':
            return op2 == '('
        if op1 == '(':
            return True
        return False

    @staticmethod
    def infix_to_postfix(infix):
        operator_stack = []
        # StringTokenizer(infix, "+-*/^() ", returnDelims=true) equivalent:
        tokens = re.findall(r'[+\-*/^() ]|[^+\-*/^() ]+', infix)
        postfix = []
        for token in tokens:
            c = token[0]
            if len(token) == 1 and MISC.is_operator(c):
                while operator_stack and not MISC.lower_precedence(operator_stack[-1][0], c):
                    postfix.append(" " + operator_stack.pop())
                if c == ')':
                    operator = operator_stack.pop()
                    while operator[0] != '(':
                        postfix.append(" " + operator)
                        operator = operator_stack.pop()
                else:
                    operator_stack.append(token)
            elif len(token) == 1 and MISC.is_space(c):
                pass  # ignore spaces
            else:
                postfix.append(" " + token)
        while operator_stack:
            postfix.append(" " + operator_stack.pop())
        return "".join(postfix)

    def infix_to_prefix(self, infix):
        # Step 1. Reverse the infix expression.
        # Step 2. Swap '(' and ')'.
        # Step 3. Convert to postfix.
        # Step 4. Reverse the result.
        pass

    # Evaluate a postfix expression.
    @staticmethod
    def evaluate(expr):
        stack = []
        result = 0
        for token in expr.split():
            if MISC.is_operator(token[0]):
                op2 = stack.pop()
                op1 = stack.pop()
                result = MISC.eval_single_op(token[0], op1, op2)
                stack.append(result)
            else:
                stack.append(int(token))
        return result

    @staticmethod
    def eval_single_op(operation, op1, op2):
        if operation == '+':
            return op1 + op2
        if operation == '-':
            return op1 - op2
        if operation == '*':
            return op1 * op2
        if operation == '/':
            return int(op1 / op2)
        return 0

    # Evaluate reverse polish notation.
    @staticmethod
    def rpn(ops):
        if not ops:
            return 0
        stack = []
        for item in ops:
            # NOTE: faithful port - pops two operands for every token (buggy for operands).
            try:
                num1 = stack.pop()
                num2 = stack.pop()
            except IndexError:
                raise ValueError("ps don't represent a well-formed RPN expression")
            if item == "+":
                stack.append(num1 + num2)
            elif item == "/":
                if num1 == 0:
                    raise ZeroDivisionError("can not divide by Zero")
                stack.append(num2 / num1)
            elif item == "*":
                stack.append(num1 * num2)
            elif item == "-":
                stack.append(num2 - num1)
            else:
                try:
                    num = float(item)
                except ValueError:
                    raise ValueError("ps don't represent a well-formed RPN expression")
                stack.append(num)
        if len(stack) > 1:
            raise ValueError("ps don't represent a well-formed RPN expression")
        return stack.pop()

    # --- influencer / celebrity -------------------------------------------
    @staticmethod
    def get_influencer(following_matrix):
        if len(following_matrix) == 0 or len(following_matrix[0]) == 0:
            return -1
        c = 0  # candidate
        for i in range(1, len(following_matrix)):
            if following_matrix[c][i] is True:
                c = i
        for i in range(len(following_matrix)):
            if i != c and following_matrix[c][i] is True:
                return -1
        return c

    @staticmethod
    def find_celebrity(n):
        celeb = 0
        for i in range(1, n):
            if MISC.is_know(celeb, i):
                celeb = i
        for i in range(n):
            if i != celeb and (MISC.is_know(celeb, i) or not MISC.is_know(i, celeb)):
                return -1
        return celeb

    @staticmethod
    def is_know(i, j):
        return True

    # --- robot path / DP / geometry ---------------------------------------
    @staticmethod
    def is_circular(path):
        N, E, S, W = 0, 1, 2, 3
        x = 0
        y = 0
        direction = N
        for move in path:
            if move == 'R':
                direction = (direction + 1) % 4
            elif move == 'L':
                direction = (4 + direction - 1) % 4
            else:  # 'G'
                if direction == N:
                    y += 1
                elif direction == E:
                    x += 1
                elif direction == S:
                    y -= 1
                else:
                    x -= 1
        return x == 0 and y == 0

    # Egg dropping.  Time O(n k^2), space O(n k).
    @staticmethod
    def calculate(eggs, floors):
        T = [[0] * (floors + 1) for _ in range(eggs + 1)]
        for i in range(floors + 1):
            T[1][i] = i
        for e in range(2, eggs + 1):
            for f in range(1, floors + 1):
                T[e][f] = INT_MAX
                for k in range(1, f + 1):
                    c = 1 + max(T[e - 1][k - 1], T[e][f - k])
                    if c < T[e][f]:
                        T[e][f] = c
        return T[eggs][floors]

    def closest_pair_of_points(self, px, py, start, end):
        # NOTE: faithful port of an incomplete reference (brute-force base case is omitted),
        # which makes this recurse without terminating.  Not invoked by the demo.
        if end - start < 3:
            pass  # brute force return omitted in reference
        mid = (start + end) // 2
        py_left = [None] * (mid - start + 1)
        py_right = [None] * (end - mid)
        i = 0
        j = 0
        for p in px:
            if p.x <= px[mid].x:
                py_left[i] = p
                i += 1
            else:
                py_right[j] = p
                j += 1
        d1 = self.closest_pair_of_points(px, py_left, start, mid)
        d2 = self.closest_pair_of_points(px, py_right, mid + 1, end)
        d = min(d1, d2)
        delta_points = [p for p in px if math.sqrt(self.distance(p, px[mid])) < math.sqrt(d)]
        d3 = self.closest(delta_points)
        return min(d3, d)

    def closest(self, delta_points):
        min_distance = INT_MAX
        for i in range(len(delta_points)):
            j = i + 1
            while j <= i + 7 and j < len(delta_points):
                dist = self.distance(delta_points[i], delta_points[j])
                if min_distance < dist:
                    min_distance = dist
                j += 1
        return min_distance

    def distance(self, p1, p2):
        return (p1.x - p2.x) * (p1.x - p2.x) + (p1.y - p2.y) * (p1.y - p2.y)

    # Draw a circle (rasterization stub - draw() is a no-op like the reference).
    @staticmethod
    def draw_circle(r):
        x = 0.0
        y = float(r)
        MISC.draw(x, y)
        MISC.draw(-x, y)
        MISC.draw(x, -y)
        MISC.draw(-x, -y)
        MISC.draw(y, x)
        MISC.draw(-y, x)
        MISC.draw(y, -x)
        MISC.draw(-y, -x)
        while x < y:
            y = math.sqrt(y * y - x * x)
            x += 1
            MISC.draw(x, y)
            MISC.draw(-x, y)
            MISC.draw(x, -y)
            MISC.draw(-x, -y)
            MISC.draw(y, x)
            MISC.draw(-y, x)
            MISC.draw(y, -x)
            MISC.draw(-y, -x)

    @staticmethod
    def draw_circle1(n):
        for i in range(-n, n + 1):
            row = []
            for j in range(-n, n + 1):
                if i * i + j * j <= n * n + 1:
                    row.append("* ")
                else:
                    row.append("  ")
            print("".join(row))

    @staticmethod
    def draw(x, y):
        pass

    # Museum problem: distance from every open cell to the nearest guard via multi-source BFS.
    @staticmethod
    def find_shortest(input_):
        distance = [[INT_MAX] * len(input_[0]) for _ in range(len(input_))]
        for i in range(len(input_)):
            for j in range(len(input_[i])):
                if input_[i][j] == Room.GUARD:
                    distance[i][j] = 0
                    MISC.set_distance(input_, i, j, distance)
        return distance

    @staticmethod
    def set_distance(input_, x, y, distance):
        visited = [[False] * len(input_[0]) for _ in range(len(input_))]
        q = collections.deque()
        q.append(Point(x, y))
        while q:
            p = q.popleft()
            MISC.set_distance_util(q, input_, p, MISC.get_neighbor(input_, p.x + 1, p.y), distance, visited)
            MISC.set_distance_util(q, input_, p, MISC.get_neighbor(input_, p.x, p.y + 1), distance, visited)
            MISC.set_distance_util(q, input_, p, MISC.get_neighbor(input_, p.x - 1, p.y), distance, visited)
            MISC.set_distance_util(q, input_, p, MISC.get_neighbor(input_, p.x, p.y - 1), distance, visited)

    @staticmethod
    def set_distance_util(q, input_, p, new_point, distance, visited):
        if new_point is not None and not visited[new_point.x][new_point.y]:
            if (input_[new_point.x][new_point.y] != Room.GUARD
                    and input_[new_point.x][new_point.y] != Room.Closed):
                distance[new_point.x][new_point.y] = min(
                    distance[new_point.x][new_point.y], 1 + distance[p.x][p.y])
                visited[new_point.x][new_point.y] = True
                q.append(new_point)

    @staticmethod
    def get_neighbor(input_, x, y):
        if x < 0 or x >= len(input_) or y < 0 or y >= len(input_[0]):
            return None
        return Point(x, y)

    # Sum of integers in a nested list weighted by depth.
    @staticmethod
    def depth_nested_int_sum(input_, level):
        if not input_:
            return 0
        total = 0
        for i in range(len(input_)):
            if input_[i].is_number:
                total += input_[i].value * level
            else:
                total += MISC.depth_nested_int_sum(input_[i].int_list, level + 1)
        return total

    # Do two rectangles overlap?  (l = top-left, r = bottom-right)
    def do_overlap(self, l1, r1, l2, r2):
        if l1.x > r2.x or l2.x > r1.x:
            return False
        if l1.y < r2.y or l2.y < r1.y:
            return False
        return True

    # --- stack reversal via recursion -------------------------------------
    def reverse(self, stack):
        if not stack or len(stack) == 1:
            return
        top = stack.pop()
        self.reverse(stack)
        self.insert_at_bottom(stack, top)

    def insert_at_bottom(self, stack, val):
        if not stack:
            stack.append(val)
            return
        temp = stack.pop()
        self.insert_at_bottom(stack, val)
        stack.append(temp)

    # --- Palantir magic box -----------------------------------------------
    @staticmethod
    def find_flipping_set(row):
        all_p = []
        all_t = []
        for ch in row:
            if ch == 'P':
                all_p.append('0')
                all_t.append('1')
            else:
                all_p.append('1')
                all_t.append('0')
        all_p_freq = MISC.update_set("".join(all_p))
        all_t_freq = MISC.update_set("".join(all_t))
        MISC.max_wishes = max(MISC.max_wishes, max(all_p_freq, all_t_freq))

    @staticmethod
    def update_set(flipped_cols):
        freq = MISC.column_flipping_stat.get(flipped_cols, 0)
        MISC.column_flipping_stat[flipped_cols] = freq + 1
        return freq + 1

    # --- Connect4 board decode --------------------------------------------
    @staticmethod
    def decode_board(s):
        inp = list(s)
        output = [['\0'] * 7 for _ in range(6)]
        temp = ['\0'] * 42
        index = 0
        i = 0
        while i < len(inp):
            if MISC.is_integer(inp[i]):
                number = int(inp[i])
                for l in range(number):
                    temp[index + l] = inp[i + 1]
                index += number
                i += 1
            else:
                temp[index] = inp[i]
                index += 1
            i += 1
        for k in range(6):
            for j in range(7):
                output[k][j] = temp[7 * k + j]
        return output

    @staticmethod
    def is_integer(s):
        try:
            int(s)
        except (ValueError, TypeError):
            return False
        return True

    # --- knight tour on a keypad (reference stub/buggy) -------------------
    def knight_tour(self):
        # NOTE: faithful port; keypad is 3x4 but the loops index [0..3][0..2] and `count`
        # is not advanced inside - exactly as in the reference (would raise if run).
        keypad = [[0] * 4 for _ in range(3)]
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, -1, 0, -1]
        count = 0
        for i in range(4):
            for j in range(3):
                keypad[i][j] = values[count]
        count += 1
        mtable = [[0] * 10 for _ in range(11)]  # noqa: F841

    def knight_util(self, table, mem, digits, start):
        if digits == 1:
            return 1
        if mem[digits][start] == 0:
            for nxt in self.next_knight_move(start, table):
                mem[digits][start] += self.knight_util(table, mem, digits - 1, nxt)
        return mem[digits][start]

    def next_knight_move(self, start, table):
        return [0, 0]

    # --- travel buddies ----------------------------------------------------
    @staticmethod
    def pre_process(input_, user):
        # map: location -> list of users
        map_ = {}
        for p in input_:
            for location in p.get_value():
                if map_.get(location) is None:
                    _users = []
                else:
                    _users = map_[location]
                map_[location] = _users
        return MISC.find_travel_buddy(user, map_)

    @staticmethod
    def find_travel_buddy(user, map_):
        _output = []
        temp = []
        n = len(user.get_value())
        _common_users = {}
        for _loc in user.get_value():
            if _loc in map_:
                temp.extend(map_[_loc])
        for _user in temp:
            if _user in _common_users:
                _common_users[_user] = _common_users[_user] + 1
            else:
                _common_users[_user] = 1
        for u in _common_users:
            if _common_users[u] > n // 2:
                _output.append(u)
        return _output

    # --- filesystem helpers (rely on a real directory; not exercised) ------
    def list_files_for_folder(self, folder):
        for name in os.listdir(folder):
            path = os.path.join(folder, name)
            if os.path.isdir(path):
                self.list_files_for_folder(path)
            else:
                print(os.path.basename(path))
                self.files.append(path)

    @staticmethod
    def find_duplicate_files(paths):
        output = []
        map_size = {}
        map_ = {}
        for path in paths:
            size = os.path.getsize(path) if os.path.exists(path) else 0
            map_size.setdefault(size, []).append(path)
        for size, files in map_size.items():
            if len(files) > 1:
                for file in files:
                    hash_code = ""  # placeholder for content hash
                    map_.setdefault(hash_code, []).append(file)
        for hash_code, file in map_.items():
            if len(file) > 1:
                output.append(file)
        return output

    # --- a bot id that hits m times in the last n seconds ------------------
    @staticmethod
    def get_bots1(logs, m, n):
        map_ = {}
        out = set()
        for log in logs:
            if log.id in map_ and (log.time - map_[log.id].time <= n):
                lc = map_[log.id]
                lc.time = log.time
                lc.count += 1
                map_[log.id] = lc
                if map_[log.id].count == m:
                    print(log.id)
                    out.add(log.id)
            else:
                map_[log.id] = LogCount(log.time, 1)
        return out

    @staticmethod
    def get_bots(logs, m, n):
        time = [0] * n
        data = [None] * n
        output = set()
        count = 0
        for log in logs:
            index = log.time % n
            if time[index] != log.time:
                temp = data[index]
                if temp is not None and log.id in temp:
                    temp[log.id] = temp[log.id] + 1
                else:
                    time[index] = log.time
                    temp = {}
                    temp[log.id] = 1
                    data[index] = temp
            else:
                temp = data[index]
                if log.id not in temp:
                    temp[log.id] = 1
                else:
                    temp[log.id] = temp[log.id] + 1
            if count > n:
                for i in range(n):
                    if log.time - time[i] < n:
                        _map = data[i]
                        if _map:
                            for key in _map:
                                if _map[key] >= m:
                                    print(key)
                                    output.add(key)
            count += 1
        return output

    # Number of users logged in at each event time.
    def find_logged_in(self, lst):
        logged_in = []
        ret_value = []
        logged_in_now = 0
        for iv in lst:
            logged_in.append(Type(iv.login, True))
            logged_in.append(Type(iv.logout, False))
        logged_in.sort()
        for t in logged_in:
            if t.loggedin is True:
                logged_in_now += 1
            else:
                logged_in_now -= 1
            ret_value.append(Output(t.time, logged_in_now))
        return ret_value

    # --- merge k sorted lists iterator ------------------------------------
    def process(self, data):
        self.data = data
        for i in range(len(data)):
            e = Element()
            e.position = 0
            e.value = data[i][0]
            e.k_index = i
            heapq.heappush(self.min_heap, (e.value, self._seq, e))
            self._seq += 1

    def next_element(self):
        result = None
        if self.min_heap:
            _, _, output = heapq.heappop(self.min_heap)
            result = output.value
            if output.position + 1 < len(self.data[output.k_index]):
                output.value = self.data[output.k_index][output.position + 1]
                output.position += 1
                heapq.heappush(self.min_heap, (output.value, self._seq, output))
                self._seq += 1
        return result


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    i1 = Interval(10, 15)
    i2 = Interval(25, 35)
    i3 = Interval(45, 65)
    i4 = Interval(85, 95)
    intervals = [i3, i2, i4, i1]
    target = Interval(17, 100)
    # find non-overlapping gaps inside the request interval
    for iv in MISC.find_interval(intervals, target):
        print("%d %d" % (iv.start, iv.end))
