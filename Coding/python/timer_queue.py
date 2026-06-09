"""Timer implemented with a priority queue of scheduled tasks.

Idiomatic Python 3 port of java/TimerQueue.java (original package code.ds).
The Java monitor (wait/notify) + worker Runnable thread + PriorityQueue are
modelled with ``threading.Condition`` + ``threading.Thread`` + ``heapq``.

The implementation is kept DETERMINISTIC and TERMINATING: the worker thread is a
daemon, ``stop()`` wakes it via the condition and joins it, and all demo waits
use timeouts so nothing can hang.
"""

import heapq
import threading
import time

# TimerTask states.
NEW = 1        # before the first execution
SCHEDULED = 2  # after first execution if repeating
EXECUTED = 3   # after first execution if not repeating
CANCELLED = 4  # when cancelled


def _now_millis():
    return time.monotonic() * 1000.0


class TimerTask:
    """Abstract analogue of Java's ``TimerTask``; subclasses implement execute()."""

    _seq_counter = 0
    _seq_lock = threading.Lock()

    def __init__(self, period=0):
        if period < 0:
            raise ValueError("Period can't be negative")
        self._lock = threading.Lock()
        self._state = NEW
        self._period = period  # constant; need not be locked
        self._next_execution_time = 0.0
        # Monotonic sequence number used only to break heap ties deterministically.
        with TimerTask._seq_lock:
            self._seq = TimerTask._seq_counter
            TimerTask._seq_counter += 1

    def cancel(self):
        """Cancel the next execution; returns True if a scheduled run is prevented."""
        with self._lock:
            ret = self._state == SCHEDULED
            self._state = CANCELLED
            return ret

    def execute(self):
        """The task to run, implemented in subclasses."""
        raise NotImplementedError

    # A task is "less than" another if it is scheduled earlier (Comparable).
    def __lt__(self, other):
        a = self.get_next_execution_time()
        b = other.get_next_execution_time()
        if a != b:
            return a < b
        return self._seq < other._seq

    def set_state(self, state):
        with self._lock:
            self._state = state

    def get_state(self):
        with self._lock:
            return self._state

    def is_periodic(self):
        return self._period > 0

    def get_next_execution_time(self):
        with self._lock:
            return self._next_execution_time

    def set_next_execution_time(self, t):
        with self._lock:
            self._next_execution_time = t

    def get_period(self):
        return self._period


class FuncTimerTask(TimerTask):
    """Concrete TimerTask whose execute() invokes a supplied callable."""

    def __init__(self, name, func, period=0):
        super().__init__(period)
        self.name = name
        self._func = func

    def execute(self):
        if self._func is not None:
            self._func()


class TimerQueue:
    def __init__(self):
        self._cond = threading.Condition()  # guards the heap and the stop flag
        self._heap = []                      # min-heap of TimerTask by next time
        self._stop = False
        self._worker = None

    def start(self):
        """Launch the worker thread that executes tasks on schedule."""
        if self._worker is None:
            self._worker = threading.Thread(target=self._timer_task_loop, daemon=True)
            self._worker.start()

    # schedule(t) and schedule(t, delay) merged via a default delay of 0.
    def schedule(self, t, delay=0):
        if t is None:
            raise ValueError("Can't schedule a null TimerTask")
        if delay < 0:
            delay = 0
        t.set_next_execution_time(_now_millis() + delay)
        self._put_job(t)

    def _put_job(self, task):
        with self._cond:
            heapq.heappush(self._heap, task)
            task.set_state(SCHEDULED)
            self._cond.notify_all()

    def _get_job(self):
        """Block until a live task is available; return None once stopped."""
        with self._cond:
            while True:
                while not self._heap and not self._stop:
                    self._cond.wait()
                if self._stop:
                    return None
                task = heapq.heappop(self._heap)
                st = task.get_state()
                if st in (CANCELLED, EXECUTED):
                    # Don't hold onto a dead task; fetch the next one.
                    continue
                if st in (NEW, SCHEDULED):
                    return task
                raise RuntimeError("TimerTask has an illegal state")

    def clear(self):
        with self._cond:
            self._heap.clear()

    def stop(self):
        """Terminate the worker loop and wake any waiters, then join."""
        with self._cond:
            if not self._stop:
                self._stop = True
                self._cond.notify_all()
        if self._worker is not None:
            self._worker.join(timeout=2.0)
            self._worker = None

    def _wait_or_stop(self, millis):
        """Wait up to `millis` ms (or until stopped/notified). Return True if stopped."""
        if millis <= 0:
            millis = 1
        with self._cond:
            if self._stop:
                return True
            self._cond.wait(timeout=millis / 1000.0)
            return self._stop

    def _timer_task_loop(self):
        """Worker: get the next job, wait until it is due, then execute it."""
        try:
            while True:
                task = self._get_job()
                if task is None:
                    return  # stopped
                now = _now_millis()
                execution_time = task.get_next_execution_time()
                time_to_wait = execution_time - now
                if time_to_wait > 0:
                    # A job was extracted but it is not yet time to run it:
                    # reschedule (put it back) and wait.
                    self._put_job(task)
                    if self._wait_or_stop(time_to_wait):
                        return
                else:
                    if task.is_periodic():
                        # Reschedule with the new time.
                        task.set_next_execution_time(execution_time + task.get_period())
                        self._put_job(task)
                    else:
                        # The one-shot task is already removed from the heap.
                        task.set_state(EXECUTED)
                    # Run it!
                    task.execute()
        finally:
            self.clear()


if __name__ == "__main__":
    print("TimerQueue demo")

    tq = TimerQueue()
    tq.start()

    results = []
    rlock = threading.Lock()
    counter = {"n": 0}
    done = threading.Event()
    total = 3

    def make_run(name):
        def run():
            with rlock:
                results.append(name)
                counter["n"] += 1
                if counter["n"] >= total:
                    done.set()
        return run

    # Three one-shot tasks due at 10/20/30 ms -> executed in that (deterministic) order.
    tq.schedule(FuncTimerTask("task-10ms", make_run("task-10ms")), 10)
    tq.schedule(FuncTimerTask("task-30ms", make_run("task-30ms")), 30)
    tq.schedule(FuncTimerTask("task-20ms", make_run("task-20ms")), 20)

    finished = done.wait(timeout=5.0)  # bounded wait so the demo can never hang
    tq.stop()

    print("all tasks executed:", finished)
    print("execution order:", results)
