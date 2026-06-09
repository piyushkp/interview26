"""Leaky-bucket rate limiter ported from LeakyBucket.java (Java package code.ds).

A "meter" variant with lazy refill: the bucket starts full and refills `rate`
tokens per second (capped at `capacity`) only when consume() is called. The
demo issues fast successive calls so no refill happens between them, keeping the
output deterministic.
"""

import math
import threading
import time


class LeakyBucket:

    def __init__(self, capacity, rate):
        self._current_budget = capacity   # level of the bucket right now
        self._capacity = capacity         # maximum level / capacity
        self._rate = rate                 # tokens added per second
        self._last_update = self._now_millis()
        self._lock = threading.Lock()     # the Java method was `synchronized`

    @staticmethod
    def _now_millis():
        return int(time.time() * 1000)

    def consume(self, nb_tokens):
        """Try to remove nb_tokens; return True on success, False otherwise."""
        if nb_tokens < 0:
            raise ValueError(
                "Cannot add negative number of tokens: %s" % nb_tokens)
        with self._lock:
            now = self._now_millis()
            # Lazily refill based on elapsed whole seconds since last update.
            seconds = math.floor((now - self._last_update) / 1000)
            self._current_budget = min(
                self._capacity, self._current_budget + self._rate * seconds)
            self._last_update = now
            if self._current_budget >= nb_tokens:
                self._current_budget -= nb_tokens
                return True
            return False


if __name__ == "__main__":
    bucket = LeakyBucket(capacity=5, rate=1)
    # Fast successive calls => no refill in between (deterministic): 5 tokens.
    results = [bucket.consume(2) for _ in range(4)]
    print("consume(2) x4 ->", results)   # [True, True, False, False]

    try:
        bucket.consume(-1)
    except ValueError as exc:
        print("error:", exc)
