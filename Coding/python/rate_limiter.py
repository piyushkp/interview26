"""Port of java/RateLimiter.java -> a rate gate (sliding-window semaphore).

Original Java package: code.ds

Java concurrency mapping:
  Semaphore                 -> threading.Semaphore
  ConcurrentLinkedQueue     -> collections.deque guarded by a Lock
  ScheduledExecutorService  -> threading.Timer (self-rescheduling)

The original Java had a bug: a *local* `scheduledPool` shadowed the field, so
the field stayed null and the rescheduling callback threw NullPointerException.
This port fixes that so the gate actually paces requests, and adds shutdown()
so the demo is deterministic & terminating (no lingering timers).

Idea: each WaitToProceed acquires a permit and records an "exit time"
(now + one time unit). A timer releases permits as their exit times come due,
re-arming itself for the next one.
"""

import threading
import time
from collections import deque
from typing import Deque, Optional


def _now_ms() -> int:
    return int(time.monotonic() * 1000)


class RateLimiter:
    def __init__(self, occurrences: int, time_seconds: int):
        if occurrences <= 0:
            raise ValueError("Number of occurrences must be a positive integer")
        self.occurrences = occurrences
        # TimeUnit.MILLISECONDS.convert(time, SECONDS)
        self.time_unit_ms = time_seconds * 1000

        self._semaphore = threading.Semaphore(occurrences)
        self._queue: Deque[int] = deque()
        self._lock = threading.Lock()
        self._shutdown = False
        self._future_task: Optional[threading.Timer] = None

        # Schedule the first exit check one time unit out (like scheduleWithFixedDelay).
        self._arm(self.time_unit_ms / 1000.0)

    def _arm(self, delay_seconds: float) -> None:
        if self._shutdown:
            return
        t = threading.Timer(delay_seconds, self._delayed_task)
        t.daemon = True
        self._future_task = t
        t.start()

    def _delayed_task(self) -> None:
        now = _now_ms()
        with self._lock:
            # Release the semaphore for every exit time that is now due.
            while self._queue and self._queue[0] - now <= 0:
                self._semaphore.release()
                self._queue.popleft()
            if self._queue:
                time_until_next_check = self._queue[0] - now
            else:
                time_until_next_check = self.time_unit_ms
        self.change_scheduler(time_until_next_check)

    def change_scheduler(self, time_ms: float) -> None:
        if self._shutdown:
            return
        if time_ms > 0:
            if self._future_task is not None:
                self._future_task.cancel()
            self._arm(time_ms / 1000.0)

    def wait_to_proceed(self) -> None:
        # Block until we can enter the semaphore, then record our exit time.
        self._semaphore.acquire()
        time_to_exit = _now_ms() + self.time_unit_ms
        with self._lock:
            self._queue.append(time_to_exit)

    def shutdown(self) -> None:
        self._shutdown = True
        with self._lock:
            if self._future_task is not None:
                self._future_task.cancel()


if __name__ == "__main__":
    # Allow 2 occurrences per 1 second; fire 5 requests and watch them get paced.
    gate = RateLimiter(2, 1)
    start = _now_ms()
    for i in range(5):
        gate.wait_to_proceed()
        print("request %d proceeded at +%d ms (approx)" % (i, _now_ms() - start))
    gate.shutdown()
    print("done")
