"""Stack implementations and stack-based problems.

Idiomatic Python 3 port of java/StackImp.java (original package code.ds).
Each Java class becomes a Python class; static helpers become @staticmethod.
"""

import collections
import threading


class NoSuchElementException(Exception):
    """Python analogue of java.util.NoSuchElementException."""


class Stack:
    """Java inner interface ``Stack<T>`` (with the ``int size = 0`` constant)."""

    size = 0  # interface constant (static final in Java)

    def push(self, ele):
        raise NotImplementedError

    def pop(self):
        raise NotImplementedError


# Implement a stack with one queue.
class StackQueue:
    def __init__(self):
        self.q1 = collections.deque()

    def push(self, x):
        # Add then rotate so the newest element ends up at the front -> O(n) push.
        self.q1.append(x)
        sz = len(self.q1)
        while sz > 1:
            self.q1.append(self.q1.popleft())
            sz -= 1

    def pop(self):
        return self.q1.popleft()

    def empty(self):
        return len(self.q1) == 0

    def top(self):
        return self.q1[0]


# Implementing a stack using a (resizable) array.
class StackArray(Stack):
    def __init__(self):
        self.arr = [None] * 2
        self.total = 0

    def _resize(self, capacity):
        tmp = [None] * capacity
        for i in range(self.total):
            tmp[i] = self.arr[i]
        self.arr = tmp

    def push(self, ele):
        if len(self.arr) == self.total:
            self._resize(len(self.arr) * 2)
        self.arr[self.total] = ele
        self.total += 1
        return self

    def pop(self):
        if self.total == 0:
            raise NoSuchElementException()
        self.total -= 1
        ele = self.arr[self.total]
        self.arr[self.total] = None
        if self.total > 0 and self.total == len(self.arr) // 4:
            self._resize(len(self.arr) // 2)
        return ele

    def __str__(self):
        return str(self.arr)


# Implementing a stack using a linked list.
class StackLinkedList(Stack):
    class _Node:
        __slots__ = ("ele", "next")

        def __init__(self):
            self.ele = None
            self.next = None

    def __init__(self):
        self.total = 0
        self.head = None

    def push(self, ele):
        current = self.head
        self.head = StackLinkedList._Node()
        self.head.ele = ele
        self.head.next = current
        self.total += 1
        return self

    def pop(self):
        if self.head is None:
            # NOTE: faithful to the Java reference, which constructs the
            # exception but never throws it (a latent bug).
            NoSuchElementException()
        ele = self.head.ele
        self.head = self.head.next
        self.total -= 1
        return ele

    def __str__(self):
        parts = []
        tmp = self.head
        while tmp is not None:
            parts.append("{}, ".format(tmp.ele))
            tmp = tmp.next
        return "".join(parts)


# Non-blocking ConcurrentStack.
# The Java reference uses an AtomicReference + compareAndSet (lock-free) loop;
# Python lacks lock-free atomics, so we guard the same logic with a Lock to
# obtain equivalent thread-safety.
class ConcurrentStack:
    class _Node:
        __slots__ = ("item", "next")

        def __init__(self, item):
            self.item = item
            self.next = None

    def __init__(self):
        self._top = None
        self._lock = threading.Lock()

    def push(self, item):
        new_head = ConcurrentStack._Node(item)
        with self._lock:
            new_head.next = self._top
            self._top = new_head

    def pop(self):
        with self._lock:
            old_head = self._top
            if old_head is None:
                return None
            self._top = old_head.next
            return old_head.item


# Sort a stack using only one additional stack and no other data structure.
# Stacks are modelled as plain Python lists (append = push, pop = pop).
def sort_stack(input_stack):
    if input_stack is None:
        return None
    temp_stack = []
    while input_stack:
        temp = input_stack.pop()
        while temp_stack and temp_stack[-1] > temp:
            input_stack.append(temp_stack.pop())
        temp_stack.append(temp)
    return temp_stack


# A stack which additionally supports min() in O(1) time using a second stack.
class StackWithMin:
    def __init__(self):
        self._main = []
        self.s2 = []

    def push(self, value):
        temp = self.min()
        if temp is None or value <= temp:
            self.s2.append(value)
        self._main.append(value)

    def pop(self):
        value = self._main.pop()
        if value == self.min():
            self.s2.pop()
        return value

    def min(self):
        if not self.s2:
            return None
        return self.s2[-1]


# A SetOfStacks composed of several fixed-capacity stacks; a new stack is
# created once the previous one fills up. push/pop behave like a single stack.
class SetOfStacks:
    def __init__(self, capacity):
        self.capacity = capacity
        self.stacks = []  # list of inner stacks (each a Python list)

    def get_last_stack(self):
        if not self.stacks:
            return None
        return self.stacks[-1]

    def push(self, v):
        last = self.get_last_stack()
        # NOTE: the Java reference compares against last.capacity() (the Vector's
        # internal array capacity, a latent bug). We use the configured capacity
        # which matches the documented intent of SetOfStacks.
        if last is not None and len(last) != self.capacity:
            last.append(v)  # add to last
        else:  # must create a new stack
            stack = [v]
            self.stacks.append(stack)

    def pop(self):
        last = self.get_last_stack()
        if last is None:
            raise NoSuchElementException("EmptyStackException")
        v = last.pop()
        if len(last) == 0:
            self.stacks.pop()
        return v


if __name__ == "__main__":
    print("Stack Imp")

    # StackArray
    sa = StackArray()
    sa.push(1).push(2).push(3).push(4)
    print("StackArray:", sa)
    print("StackArray pop:", sa.pop(), sa.pop())
    print("StackArray after pops:", sa)

    # StackLinkedList
    sll = StackLinkedList()
    sll.push("a").push("b").push("c")
    print("StackLinkedList:", str(sll).strip())
    print("StackLinkedList pop:", sll.pop())

    # StackQueue
    sq = StackQueue()
    for n in (10, 20, 30):
        sq.push(n)
    print("StackQueue top/pop:", sq.top(), sq.pop(), sq.pop())

    # ConcurrentStack
    cs = ConcurrentStack()
    cs.push(100)
    cs.push(200)
    print("ConcurrentStack pop:", cs.pop(), cs.pop(), cs.pop())

    # sort_stack
    print("sort_stack:", sort_stack([3, 1, 4, 1, 5, 9, 2, 6]))

    # StackWithMin
    swm = StackWithMin()
    for n in (5, 3, 7, 2, 8):
        swm.push(n)
    print("StackWithMin min:", swm.min())
    swm.pop()  # removes 8
    swm.pop()  # removes 2 -> min should rise to 3
    print("StackWithMin min after pops:", swm.min())

    # SetOfStacks
    sos = SetOfStacks(2)
    for n in range(1, 6):
        sos.push(n)
    print("SetOfStacks count:", len(sos.stacks))
    print("SetOfStacks pop:", sos.pop(), sos.pop(), sos.pop())
    print("SetOfStacks count after pops:", len(sos.stacks))
