"""In-memory counter for chat activity per exact (user_id, chat_id) pair.

process_event records one event; 
get_count returns how many events for that
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


# Approach (in plain terms):
#   Keep a separate guest book (a list of timestamps) for each exact (user_id,
#   chat_id) pair. Every event just stamps the current time on that pair's
#   page, and because events for a pair arrive in time order the page stays
#   sorted. To count the last 15 minutes (900 s): look at the newest stamp T,
#   work out the cutoff T - 900, and since the page is already sorted, do a
#   quick binary search to find where the cutoff lands. Everything from that
#   spot to the end is inside the window, so the answer is how many stamps
#   come after.
#   Data structures used:
#     - dict mapping the (user, chat) key -> a list of timestamps kept
#       in sorted (non-decreasing) order - O(1) grouping/append.
#     - binary search (bisect) over that already-sorted list - counts
#       the window in O(log m) with no re-sorting.
class ChatEventCounter:

    def __init__(self):
        # Time: O(1), Space: O(1) - starts with an empty event dictionary.
        # (user_id, chat_id) -> ascending list of event timestamps.
        self._events = {}

    @staticmethod
    def _key(user_id, chat_id):
        # u = len(user_id), c = len(chat_id).
        # Time:  O(u + c) - builds one key string from both ids.
        # Space: O(u + c) - the returned key string.
        # Length-prefix the user_id so distinct pairs can never collide
        # (e.g. ("a", "bc") vs ("ab", "c")).
        return f"{len(user_id)}:{user_id}{chat_id}"

    def process_event(self, user_id, chat_id, timestamp):
        """Record one event for (user_id, chat_id) at the given timestamp."""
        # Time:  O(1) amortized - one dictionary lookup plus a list append.
        # Space: O(1) - stores a single extra timestamp.
        key = self._key(user_id, chat_id)
        self._events.setdefault(key, []).append(timestamp)

    def get_count(self, user_id, chat_id):
        """Events for (user_id, chat_id) within [T - 900, T], T = latest ts."""
        # m = number of events stored for this pair.
        # Time:  O(log m) - bisect_left binary-searches for the window start.
        # Space: O(1) - only a few index variables.
        ts = self._events.get(self._key(user_id, chat_id))
        if not ts:
            return 0
        latest = ts[-1]  # list is sorted -> last is the max
        window_start = latest - 900
        # bisect_left is a stdlib binary search: O(log m) to find the first
        # timestamp >= window_start; everything from there to the end is inside
        # the inclusive 900 s window.
        lo = bisect_left(ts, window_start)
        return len(ts) - lo

    @staticmethod
    def simulate(operations):
        """Replay operations, returning the result of every getCount in
        order."""
        # p = number of operations, m = events for the busiest pair.
        # Time:  O(p log m) - each getCount does one binary search.
        # Space: O(p) - the results list plus the stored timestamps.
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
    # Test 1: three events for one pair, all inside the 15-minute window.
    chat1 = [
        ["processEvent", "u1", "c1", 100], ["processEvent", "u1", "c1", 200],
        ["processEvent", "u1", "c1", 1000], ["getCount", "u1", "c1"],
    ]
    print(ChatEventCounter.simulate(chat1))                          # [3]

    # Test 2: asking about a pair that has no events at all -> 0.
    print(ChatEventCounter.simulate([["getCount", "u1", "c1"]]))      # [0]

    # Test 3: a single event is always inside its own window -> 1.
    chat3 = [
        ["processEvent", "u1", "c1", 500], ["getCount", "u1", "c1"],
    ]
    print(ChatEventCounter.simulate(chat3))                          # [1]

    # Test 4: event exactly 900 s before the latest -> boundary is inclusive.
    chat4 = [
        ["processEvent", "u1", "c1", 0], ["processEvent", "u1", "c1", 900],
        ["getCount", "u1", "c1"],
    ]
    print(ChatEventCounter.simulate(chat4))                          # [2]

    # Test 5: event 901 s before the latest -> just outside the window.
    chat5 = [
        ["processEvent", "u1", "c1", 0], ["processEvent", "u1", "c1", 901],
        ["getCount", "u1", "c1"],
    ]
    print(ChatEventCounter.simulate(chat5))                          # [1]

    # Test 6: only the newest event stays in the window; older ones drop off.
    chat6 = [
        ["processEvent", "u1", "c1", 0], ["processEvent", "u1", "c1", 500],
        ["processEvent", "u1", "c1", 2000], ["getCount", "u1", "c1"],
    ]
    print(ChatEventCounter.simulate(chat6))                          # [1]

    # Test 7: two independent pairs are counted separately.
    chat7 = [
        ["processEvent", "u1", "c1", 100], ["processEvent", "u1", "c1", 200],
        ["processEvent", "u2", "c2", 5000],
        ["getCount", "u1", "c1"], ["getCount", "u2", "c2"],
    ]
    print(ChatEventCounter.simulate(chat7))                          # [2, 1]

    # Test 8: length-prefixed keys keep look-alike pairs from colliding.
    chat8 = [
        ["processEvent", "a", "bc", 100], ["processEvent", "ab", "c", 200],
        ["getCount", "a", "bc"], ["getCount", "ab", "c"],
    ]
    print(ChatEventCounter.simulate(chat8))                          # [1, 1]
