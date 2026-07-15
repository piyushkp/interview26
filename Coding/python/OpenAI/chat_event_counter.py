"""In-memory counter for chat activity per exact (user_id, chat_id) pair.

process_event records one event; get_count returns how many events for that
pair fall in the inclusive 15-minute (900 s) window ending at the pair's most
recent timestamp T, i.e. timestamps in [T - 900, T]. Returns 0 if the pair has
no events.

Because, for a given pair, process_event timestamps arrive non-decreasing,
each pair's list is already sorted, so get_count is a binary search for the
window start (no per-call sorting).
  - process_event: O(1) amortized append.
  - get_count:     O(log m) over that pair's m events.
"""
from bisect import bisect_left


class ChatEventCounter:

    def __init__(self):
        # (user_id, chat_id) -> ascending list of event timestamps.
        self._events = {}

    @staticmethod
    def _key(user_id, chat_id):
        # Length-prefix the user_id so distinct pairs can never collide
        # (e.g. ("a", "bc") vs ("ab", "c")).
        return f"{len(user_id)}:{user_id}{chat_id}"

    def process_event(self, user_id, chat_id, timestamp):
        """Record one event for (user_id, chat_id) at the given timestamp."""
        self._events.setdefault(self._key(user_id, chat_id), []).append(timestamp)

    def get_count(self, user_id, chat_id):
        """Events for (user_id, chat_id) within [T - 900, T], T = latest ts."""
        ts = self._events.get(self._key(user_id, chat_id))
        if not ts:
            return 0
        latest = ts[-1]  # list is sorted -> last is the max
        window_start = latest - 900
        # First index whose timestamp is >= window_start; everything from
        # there to the end is inside the inclusive window.
        lo = bisect_left(ts, window_start)
        return len(ts) - lo

    @staticmethod
    def simulate(operations):
        """Replay operations, returning the result of every getCount in order."""
        counter = ChatEventCounter()
        results = []
        for op in operations:
            kind = op[0]
            if kind == "processEvent":
                counter.process_event(op[1], op[2], op[3])
            elif kind == "getCount":
                results.append(counter.get_count(op[1], op[2]))
            else:
                raise ValueError(f"Unknown op: {kind}")
        return results


if __name__ == "__main__":
    chat1 = [
        ["processEvent", "u1", "c1", 100], ["processEvent", "u1", "c1", 200],
        ["processEvent", "u1", "c1", 1000], ["getCount", "u1", "c1"],
    ]
    print(ChatEventCounter.simulate(chat1))            # [3]
    print(ChatEventCounter.simulate([["getCount", "u1", "c1"]]))  # [0]
