"""Idiomatic Python 3 port of java/Threading.java (original package code.ds).

Interview / DSA reference implementation of classic concurrency exercises:
per-instance synchronized work, parallel merge sort, a deadlock illustration,
a compare-and-set number range, ordered 1-2-3 printing with three threads,
odd/even alternating printers using a monitor, and a reentrant read/write lock.

Java -> Python mapping:
  * ``Thread`` / ``Runnable``                 -> :class:`threading.Thread`
  * ``synchronized`` + ``wait`` / ``notify``  -> :class:`threading.Condition`
  * ``ReentrantLock`` + ``Condition``         -> :class:`threading.Condition`
  * ``AtomicReference`` + ``compareAndSet``   -> small lock-backed
    :class:`AtomicReference` helper
  * ``Thread.currentThread()``                -> :func:`threading.current_thread`

The demos are made DETERMINISTIC and TERMINATING: the Java ``main`` did not
join its threads (relying on the JVM keeping non-daemon threads alive), whereas
here every started thread is joined (with a safety timeout) so the program
always finishes and never hangs.

This module is intentionally named ``threading_impl`` so that the top-level
``import threading`` resolves to the standard library, not to this file.
"""

from __future__ import annotations

import threading


# ---------------------------------------------------------------------------
# Multi-threading: each instance does work while holding its own lock
# ---------------------------------------------------------------------------
class MultiThreading(threading.Thread):
    """Java ``MultiThreading implements Runnable``.

    Each instance owns a private lock (``t_lock``); because the lock is
    per-instance there is no cross-thread mutual exclusion - faithfully matching
    the original ``synchronized (tLock)`` over a per-object monitor.
    """

    def __init__(self, parameter):
        super().__init__()
        self.t_lock = threading.Lock()
        self.parameter = parameter

    def run(self):
        with self.t_lock:
            # do work
            pass

    @staticmethod
    def thread_exe():
        threads = [MultiThreading(i) for i in range(5)]
        for t in threads:
            t.start()
        # Join so the helper terminates deterministically (Java did not join).
        for t in threads:
            t.join()


# ---------------------------------------------------------------------------
# Merge sort (parallel + sequential)
# ---------------------------------------------------------------------------
def parallel_merge_sort(a, num_threads):
    """Merge sort that forks a thread per half until the thread budget runs out."""
    if num_threads <= 1:
        merge_sort(a)
        return
    mid = len(a) // 2
    left = a[0:mid]
    right = a[mid:len(a)]

    left_sorter = threading.Thread(
        target=parallel_merge_sort, args=(left, num_threads // 2))
    right_sorter = threading.Thread(
        target=parallel_merge_sort, args=(right, num_threads // 2))
    left_sorter.start()
    right_sorter.start()
    left_sorter.join()
    right_sorter.join()

    merge(left, right, a)


def merge_sort(a):
    if len(a) <= 1:
        return
    mid = len(a) // 2
    left = a[0:mid]
    right = a[mid:len(a)]
    merge_sort(left)
    merge_sort(right)
    merge(left, right, a)


def merge(a, b, r):
    """Merge sorted ``a`` and ``b`` into ``r`` in place (len(r) == len(a)+len(b))."""
    i = j = k = 0
    while i < len(a) and j < len(b):
        if a[i] < b[j]:
            r[k] = a[i]
            k += 1
            i += 1
        else:
            r[k] = b[j]
            k += 1
            j += 1
    while i < len(a):
        r[k] = a[i]
        k += 1
        i += 1
    while j < len(b):
        r[k] = b[j]
        k += 1
        j += 1


# ---------------------------------------------------------------------------
# Deadlock illustration - intentionally NOT invoked (it can hang)
# ---------------------------------------------------------------------------
def dead_lock():
    """Classic two-lock deadlock when locks are acquired in opposite orders.

    Provided for completeness only; it is never called by the demo because it
    can hang.  To avoid deadlock, all locks must be acquired in the same order.
    """
    resource1 = threading.Lock()
    resource2 = threading.Lock()

    def run1():
        with resource1:
            print("Thread 1: locked resource 1")
            with resource2:
                print("Thread 1: locked resource 2")

    def run2():
        with resource2:
            print("Thread 2: locked resource 2")
            with resource1:
                print("Thread 2: locked resource 1")

    t1 = threading.Thread(target=run1)
    t2 = threading.Thread(target=run2)
    t1.start()
    t2.start()


# ---------------------------------------------------------------------------
# Compare-and-set number range (lower <= upper invariant)
# ---------------------------------------------------------------------------
class IntPair:
    def __init__(self, lower, upper):
        self.lower = lower
        self.upper = upper


class AtomicReference:
    """Lock-backed stand-in for ``java.util.concurrent.atomic.AtomicReference``."""

    def __init__(self, initial):
        self._value = initial
        self._lock = threading.Lock()

    def get(self):
        return self._value

    def compare_and_set(self, expect, update):
        with self._lock:
            if self._value is expect:
                self._value = update
                return True
            return False


class CasNumberRange:
    """Multiple threads may update the range while preserving ``lower <= upper``."""

    def __init__(self):
        self.values = AtomicReference(IntPair(0, 0))

    def get_lower(self):
        return self.values.get().lower

    def set_lower(self, i):
        while True:
            oldv = self.values.get()
            if i > oldv.upper:
                raise ValueError("lower must not exceed upper")
            newv = IntPair(i, oldv.upper)
            if self.values.compare_and_set(oldv, newv):
                return

    def get_upper(self):
        return self.values.get().upper

    def set_upper(self, i):
        while True:
            oldv = self.values.get()
            if i < oldv.lower:
                raise ValueError("upper must not be below lower")
            newv = IntPair(oldv.lower, i)
            if self.values.compare_and_set(oldv, newv):
                return


# ---------------------------------------------------------------------------
# Three threads printing 1 2 3 1 2 3 ... in order
# ---------------------------------------------------------------------------
class ThreadId:
    """Mutable holder for the id of the thread allowed to print next."""

    def __init__(self):
        self._id = 0

    def get_id(self):
        return self._id

    def set_id(self, value):
        self._id = value


class ThreeThreads:
    @staticmethod
    def three():
        condition = threading.Condition()
        thread_id = ThreadId()
        thread_id.set_id(1)
        t1 = ThreeThreads._set_thread(condition, 1, 2, thread_id)
        t2 = ThreeThreads._set_thread(condition, 2, 3, thread_id)
        t3 = ThreeThreads._set_thread(condition, 3, 1, thread_id)
        t1.start()
        t2.start()
        t3.start()
        # Join so the demo is deterministic and terminates.
        t1.join()
        t2.join()
        t3.join()

    @staticmethod
    def _set_thread(condition, current_thread_id, next_thread_id, thread_id):
        def run():
            for _ in range(3):
                with condition:
                    while thread_id.get_id() != current_thread_id:
                        condition.wait()
                    print(current_thread_id)
                    thread_id.set_id(next_thread_id)
                    condition.notify_all()
        return threading.Thread(target=run)


# ---------------------------------------------------------------------------
# Odd / even alternating printers via a shared monitor
# ---------------------------------------------------------------------------
class OddEvenMonitor:
    ODD_TURN = True
    EVEN_TURN = False

    def __init__(self):
        self._cond = threading.Condition()
        self.turn = OddEvenMonitor.ODD_TURN

    def wait_turn(self, old_turn):
        with self._cond:
            while self.turn != old_turn:
                self._cond.wait()
            # Move on, it's our turn.

    def toggle_turn(self):
        with self._cond:
            self.turn = not self.turn
            self._cond.notify()


class OddThread(threading.Thread):
    """Prints odd numbers.  ``max_num`` (default 100) mirrors the Java bound but
    is parameterised so demos can use a smaller, quieter range."""

    def __init__(self, monitor, max_num=100):
        super().__init__()
        self.monitor = monitor
        self.max_num = max_num

    def run(self):
        for i in range(1, self.max_num + 1, 2):
            self.monitor.wait_turn(OddEvenMonitor.ODD_TURN)
            print("i =", i)
            self.monitor.toggle_turn()


class EvenThread(threading.Thread):
    """Prints even numbers (companion to :class:`OddThread`)."""

    def __init__(self, monitor, max_num=100):
        super().__init__()
        self.monitor = monitor
        self.max_num = max_num

    def run(self):
        for i in range(2, self.max_num + 1, 2):
            self.monitor.wait_turn(OddEvenMonitor.EVEN_TURN)
            print("i =", i)
            self.monitor.toggle_turn()


# ---------------------------------------------------------------------------
# Reentrant read/write lock
# ---------------------------------------------------------------------------
class ReadWriteLock:
    """Reentrant read/write lock.

    Ported faithfully from the Java reference, including its quirks.  In
    particular :meth:`lock_read` reproduces a bug present in the original: on
    the very first read acquisition ``readers.get(thread)`` is ``None`` and the
    subsequent ``None + 1`` raises (a ``NullPointerException`` in Java, a
    ``TypeError`` here).  The demo therefore exercises only the write path.
    """

    def __init__(self):
        self._cond = threading.Condition()
        self.write_requests = 0
        self.write_access = 0
        self.writing_thread = None
        self.readers = {}

    def lock_read(self):
        with self._cond:
            calling_thread = threading.current_thread()
            while not self._can_grant_read_access(calling_thread):
                self._cond.wait()
            # Faithful to the buggy Java reference (None + 1 on first acquire).
            self.readers[calling_thread] = self.readers.get(calling_thread) + 1

    def _can_grant_read_access(self, calling_thread):
        if self.writing_thread == calling_thread:
            return True
        if self.writing_thread is not None:
            return False
        if self.readers.get(calling_thread) is not None:
            return True
        if self.write_requests > 0:
            return False
        return True

    def unlock_read(self):
        with self._cond:
            calling_thread = threading.current_thread()
            if self.readers.get(calling_thread) == 1:
                del self.readers[calling_thread]
            else:
                self.readers[calling_thread] = self.readers.get(calling_thread) - 1
            self._cond.notify_all()

    def lock_write(self):
        with self._cond:
            self.write_requests += 1
            calling_thread = threading.current_thread()
            while not self._can_grant_write_access(calling_thread):
                self._cond.wait()
            self.write_requests -= 1
            self.write_access += 1
            self.writing_thread = calling_thread

    def _can_grant_write_access(self, calling_thread):
        if len(self.readers) == 1 and self.readers.get(calling_thread) is not None:
            return True
        if len(self.readers) > 0:
            return False
        if self.writing_thread is None:
            return True
        if self.writing_thread != calling_thread:
            return False
        return True

    def unlock_write(self):
        with self._cond:
            self.write_access -= 1
            if self.write_access == 0:
                self.writing_thread = None
            self._cond.notify_all()


if __name__ == "__main__":
    # Primary behaviour from the Java main: three threads print 1 2 3 in order.
    print("ThreeThreads (prints 1 2 3 repeated):")
    ThreeThreads.three()

    # Parallel merge sort (forks threads, joins internally -> deterministic).
    arr = [9, 3, 7, 1, 8, 2, 6, 5, 4, 0]
    parallel_merge_sort(arr, 4)
    print("parallel_merge_sort:", arr)

    # Sequential merge sort.
    arr2 = [5, 1, 4, 2, 8, 3]
    merge_sort(arr2)
    print("merge_sort:", arr2)

    # Odd/even interleaving up to a small, quiet bound (classes default to 100).
    print("Odd/Even interleave up to 10:")
    monitor = OddEvenMonitor()
    odd = OddThread(monitor, max_num=10)
    even = EvenThread(monitor, max_num=10)
    odd.start()
    even.start()
    odd.join(timeout=5)
    even.join(timeout=5)

    # Compare-and-set number range. Widen the upper bound before raising the
    # lower bound (the range starts at (0, 0) and enforces lower <= upper).
    rng = CasNumberRange()
    rng.set_upper(9)
    rng.set_lower(3)
    print("CasNumberRange lower/upper:", rng.get_lower(), rng.get_upper())
    try:
        rng.set_lower(20)  # 20 > upper(9) -> rejected
    except ValueError as exc:
        print("CasNumberRange rejected set_lower(20):", exc)

    # Reentrant read/write lock: the write path works; the read path is faithful
    # to the buggy Java reference (raises on first acquire), shown deliberately.
    rw = ReadWriteLock()
    rw.lock_write()
    print("ReadWriteLock: acquired write lock")
    rw.unlock_write()
    print("ReadWriteLock: released write lock")
    try:
        rw.lock_read()
    except TypeError as exc:
        print("ReadWriteLock.lock_read faithful-to-Java bug:", exc)

    # MultiThreading helper (each thread holds its own lock); joins internally.
    MultiThreading.thread_exe()
    print("MultiThreading.thread_exe completed")

    print("done")
