"""Scheduled-task demo ported from scheduleService.java (Java package code.ds).

The Java version uses a ScheduledExecutorService and the SAME Runnable instance
is scheduled twice while its `delay` field is mutated to 15 before either task
fires -- so both runs observe 15 (shared mutable state). This port preserves
that behaviour with threading.Timer, but:
  * scales the delays down so the demo finishes quickly, and
  * joins the timers so the program terminates deterministically.
"""

import threading


class ScheduleService:

    # Java schedules in seconds; we shrink the unit to keep the demo fast.
    _SCALE = 0.01

    def __init__(self):
        self.delay = 0
        self._lock = threading.Lock()   # guard the shared `delay` field

    def run(self):
        with self._lock:
            print(self.delay)


if __name__ == "__main__":
    obj = ScheduleService()
    timers = []

    obj.delay = 10
    timers.append(threading.Timer(10 * ScheduleService._SCALE, obj.run))
    obj.delay = 15
    timers.append(threading.Timer(15 * ScheduleService._SCALE, obj.run))

    for t in timers:
        t.start()
    # Wait for all scheduled tasks to finish (analogous to awaiting shutdown).
    # Both fire after delay was set to 15, so the output is: 15 then 15.
    for t in timers:
        t.join()
