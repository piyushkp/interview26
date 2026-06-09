"""Idiomatic Python 3 port of java/QueueImp.java (original package code.ds).

Four queue implementations:
  * TwoStackQueue       - queue built from two stacks (Java inner ``Queue<E>``)
  * BoundedBuffer       - blocking bounded queue using a Lock + two Conditions
  * LinkedQueue         - Michael-Scott non-blocking queue (put only)
  * CircularArrayQueue  - circular buffer with automatic capacity growth

Java's ``size()`` method on the two-stack queue clashed with its ``size``
field, so the method was renamed ``get_size``. Python has no atomic CAS
primitive, so ``LinkedQueue`` uses a small ``_AtomicReference`` helper backed
by a lock. The Java source aliases ``tail = head`` (the *same*
``AtomicReference``); that quirk is preserved faithfully below.
"""

import threading


# ---------------------------------------------------------------------------
# Queue implemented using two stacks
# ---------------------------------------------------------------------------
class TwoStackQueue:
    def __init__(self):
        self.s1 = []
        self.s2 = []
        self.front = 0
        self.size = 0

    def en_queue(self, item):
        if not self.s1:
            self.front = item
        self.s1.append(item)
        self.size += 1

    def dequeue(self):
        if len(self.s2) == 0:
            while len(self.s1) != 0:
                self.s2.append(self.s1.pop())
        self.size -= 1
        return self.s2.pop()

    def empty(self):
        return not self.s1 and not self.s2

    def peek(self):
        if self.s2:
            return self.s2[-1]
        return self.front

    def get_size(self):  # Java size(); renamed to avoid clash with the field
        return self.size


# ---------------------------------------------------------------------------
# Blocking bounded buffer (blocks on full put / empty take)
# ---------------------------------------------------------------------------
class BoundedBuffer:
    def __init__(self, capacity=100):
        # Two Conditions sharing one underlying lock, mirroring the Java code.
        self._lock = threading.Lock()
        self.not_full = threading.Condition(self._lock)
        self.not_empty = threading.Condition(self._lock)
        self.items = [None] * capacity
        self.putptr = 0
        self.takeptr = 0
        self.count = 0

    def put(self, x):
        with self.not_full:
            while self.count == len(self.items):
                self.not_full.wait()
            self.items[self.putptr] = x
            self.putptr += 1
            if self.putptr == len(self.items):
                self.putptr = 0
            self.count += 1
            self.not_empty.notify()

    def take(self):
        with self.not_empty:
            while self.count == 0:
                self.not_empty.wait()
            x = self.items[self.takeptr]
            self.takeptr += 1
            if self.takeptr == len(self.items):
                self.takeptr = 0
            self.count -= 1
            self.not_full.notify()
            return x


# ---------------------------------------------------------------------------
# Non-blocking linked queue (Michael-Scott); put() only, as in the source.
# https://www.ibm.com/developerworks/java/library/j-jtp04186/
# ---------------------------------------------------------------------------
class _AtomicReference:
    def __init__(self, value=None):
        self._value = value
        self._lock = threading.Lock()

    def get(self):
        return self._value

    def set(self, v):
        with self._lock:
            self._value = v

    def compare_and_set(self, expect, update):
        with self._lock:
            if self._value is expect:
                self._value = update
                return True
            return False


class _Node:
    def __init__(self, item, nxt):
        self.item = item
        self.next = _AtomicReference(nxt)


class LinkedQueue:
    def __init__(self):
        dummy = _Node(None, None)
        self.head = _AtomicReference(dummy)
        # Faithful to Java: tail is the SAME reference object as head.
        self.tail = self.head

    def put(self, item):
        new_node = _Node(item, None)
        while True:
            cur_tail = self.tail.get()
            residue = cur_tail.next.get()
            if cur_tail is self.tail.get():
                if residue is None:  # A
                    if cur_tail.next.compare_and_set(None, new_node):  # C
                        self.tail.compare_and_set(cur_tail, new_node)  # D
                        return True
                else:
                    self.tail.compare_and_set(cur_tail, residue)  # B

    def to_list(self):  # demo helper (not in the Java source)
        result = []
        node = self.head.get().next.get()
        while node is not None:
            result.append(node.item)
            node = node.next.get()
        return result


# ---------------------------------------------------------------------------
# Circular array queue with capacity growth
# ---------------------------------------------------------------------------
class CircularArrayQueue:
    DEFAULT_CAPACITY = 100

    def __init__(self, initial_capacity=None):
        cap = initial_capacity if initial_capacity is not None else self.DEFAULT_CAPACITY
        self.front = 0
        self.rear = 0
        self.count = 0
        self.queue = [None] * cap

    def enqueue(self, element):
        if self.size() == len(self.queue):
            self.expand_capacity()
        self.queue[self.rear] = element
        self.rear = (self.rear + 1) % len(self.queue)
        self.count += 1

    def dequeue(self):
        if self.is_empty():
            raise Exception("queue is Empty")
        result = self.queue[self.front]
        self.queue[self.front] = None
        self.front = (self.front + 1) % len(self.queue)
        self.count -= 1
        return result

    def first(self):
        if self.is_empty():
            raise Exception("queue is Empty= ")
        return self.queue[self.front]

    def is_empty(self):
        return self.count == 0

    def size(self):
        return self.count

    def __str__(self):
        result = ""
        scan = 0
        while scan < self.count:
            if self.queue[scan] is not None:
                result += str(self.queue[scan]) + "\n"
            scan += 1
        return result

    def expand_capacity(self):
        larger = [None] * (len(self.queue) * 2)
        for scan in range(self.count):
            larger[scan] = self.queue[self.front]
            self.front = (self.front + 1) % len(self.queue)
        self.front = 0
        self.rear = self.count
        self.queue = larger


if __name__ == "__main__":
    print("QueueImp")
    print()

    q = TwoStackQueue()
    for v in [1, 2, 3]:
        q.en_queue(v)
    print("TwoStackQueue   peek:", q.peek(), "size:", q.get_size())
    print("TwoStackQueue   dequeue:", q.dequeue(), q.dequeue())

    bb = BoundedBuffer(4)
    bb.put("a")
    bb.put("b")
    print("BoundedBuffer   take:", bb.take(), bb.take())

    lq = LinkedQueue()
    print("LinkedQueue     put:", lq.put(10), lq.put(20))

    caq = CircularArrayQueue(2)
    for v in [5, 6, 7]:  # 7 triggers expand_capacity
        caq.enqueue(v)
    print("CircularQueue   size:", caq.size(), "first:", caq.first())
    print("CircularQueue   dequeue:", caq.dequeue(), caq.dequeue(), caq.dequeue())
