"""A GPU credit ledger fed by a stream of requests whose timestamps are NOT
necessarily increasing. Each GET reflects only the requests that have arrived
so far, evaluated at the query timestamp; a later-arriving request with an
earlier timestamp affects future GETs but never retroactively changes a GET
that was already returned.

Request forms:
    ["GRANT",  user, amount, timestamp]  add amount at timestamp
    ["CHARGE", user, amount, timestamp]  subtract amount IF the running balance
                                         at that moment is >= amount, else
                                         ignore
    ["GET",    user, timestamp]          balance considering only arrived
                                         events with timestamp <= the query
                                         timestamp

Within a user, events are applied in (timestamp, arrival-order) order — a
stable tie-breaker for equal timestamps. Each GET replays that user's eligible
events from scratch so charge successes reflect the correct ordering.
"""


class _Event:
    """One ledger event for a user."""

    def __init__(self, is_grant, amount, timestamp, arrival):
        # Time: O(1), Space: O(1) - just stores four fields.
        self.is_grant = is_grant
        self.amount = amount
        self.timestamp = timestamp
        # index in the input stream -> stable tie-breaker
        self.arrival = arrival


def _event_order(event):
    """Sort key: order events by (timestamp, arrival) so equal timestamps keep
    their original arrival order (a stable tie-break)."""
    # Time: O(1), Space: O(1) - returns a two-field tuple.
    return (event.timestamp, event.arrival)


# Approach (in plain terms):
#   Imagine each user has a shoebox where we drop in slips of paper as they
#   arrive: "+10 credits at time 5" or "-4 credits at time 7". Slips can be
#   dropped in any order and can even be back-dated.
#   When someone asks "what's the balance at time t?", we pull out only the
#   slips dated at or before t, lay them out in date order (using arrival order
#   to break ties), and add them up starting from zero. A "-" slip only counts
#   if there is enough money at that moment; otherwise we skip it. Because we
#   recompute from scratch every time, a slip that shows up late but is
#   back-dated changes future answers without
#   rewriting answers we already gave.
#   Data structures used:
#     - dict mapping user -> list of event objects in arrival order -
#       groups events per user and keeps arrival order for stable
#       tie-breaks.
#     - a list sorted per query for just the eligible subset - avoids
#       sorting everything.
class CreditLedger:

    def __init__(self):
        # Time: O(1), Space: O(1) - starts with an empty per-user map.
        # user -> events that have arrived so far (in arrival order).
        self._ledger = {}

    def grant(self, user, amount, timestamp, arrival):
        """Record a GRANT for user."""
        # Time: O(1) amortized (dict lookup + list append),
        # Space: O(1) per call.
        self._ledger.setdefault(user, []).append(
            _Event(True, amount, timestamp, arrival))

    def charge(self, user, amount, timestamp, arrival):
        """Record a CHARGE for user (success is decided later, at replay
        time)."""
        # Time: O(1) amortized (dict lookup + list append),
        # Space: O(1) per call.
        self._ledger.setdefault(user, []).append(
            _Event(False, amount, timestamp, arrival))

    def get(self, user, timestamp):
        """Balance for user at timestamp, replaying eligible events in
        order."""
        # n = events stored for this user, k = eligible events (k <= n).
        # Time:  O(n + k log k) - scan all n events, then sort the k
        #        eligible ones.
        # Space: O(k) - the list of eligible events.
        events = self._ledger.get(user)
        if events is None:
            return 0
        # Eligible events: timestamp <= query time.
        eligible = []
        for event in events:
            if event.timestamp <= timestamp:
                eligible.append(event)
        # Apply in (timestamp, arrival) order — stable tie-break by arrival.
        eligible.sort(key=_event_order)
        balance = 0
        for event in eligible:
            if event.is_grant:
                balance += event.amount
            elif balance >= event.amount:
                balance -= event.amount  # charge applied only when affordable
        return balance

    @staticmethod
    def simulate(requests):
        """Process requests in arrival order, returning every GET in order."""
        # m = number of requests, n = events for the busiest user.
        # Time:  O(m * n log n) worst case (each GET replays and sorts events).
        # Space: O(m + n) - the results list plus the stored events.
        ledger = CreditLedger()
        results = []
        for i, req in enumerate(requests):
            kind = req[0]
            user = req[1]
            if kind == "GRANT":
                ledger.grant(user, req[2], req[3], i)
            elif kind == "CHARGE":
                ledger.charge(user, req[2], req[3], i)
            elif kind == "GET":
                results.append(ledger.get(user, req[2]))
            else:
                raise ValueError(f"Unknown request: {kind}")
        return results


if __name__ == "__main__":
    # Test 1: a charge applied, then a back-dated charge drains the balance.
    led1 = [
        ["GRANT", "alice", 10, 5], ["CHARGE", "alice", 4, 7],
        ["GET", "alice", 7],
        ["CHARGE", "alice", 10, 6], ["GET", "alice", 7],
    ]
    print(CreditLedger.simulate(led1))  # [6, 0]

    # Test 2: two users kept independent; GET honors timestamp <= query time.
    led2 = [
        ["GRANT", "alice", 5, 10], ["GRANT", "bob", 7, 1],
        ["CHARGE", "bob", 2, 3],
        ["GET", "bob", 2], ["GET", "bob", 3],
        ["GET", "alice", 9], ["GET", "alice", 10],
    ]
    print(CreditLedger.simulate(led2))  # [7, 5, 0, 5]

    # Test 3: empty input -> no GETs -> empty result.
    led3 = []
    print(CreditLedger.simulate(led3))  # []

    # Test 4: GET for a user that never appears -> balance 0 (not found).
    led4 = [
        ["GET", "nobody", 5],
    ]
    print(CreditLedger.simulate(led4))  # [0]

    # Test 5: an unaffordable CHARGE is ignored, balance unchanged.
    led5 = [
        ["GRANT", "u", 3, 1], ["CHARGE", "u", 5, 2],
        ["GET", "u", 2], ["GET", "u", 5],
    ]
    print(CreditLedger.simulate(led5))  # [3, 3]

    # Test 6: a late, back-dated GRANT changes future GETs but not past
    # answers.
    led6 = [
        ["GRANT", "u", 10, 10], ["GET", "u", 10], ["GRANT", "u", 5, 3],
        ["GET", "u", 10], ["GET", "u", 5],
    ]
    print(CreditLedger.simulate(led6))  # [10, 15, 5]

    # Test 7: equal timestamps use arrival order - CHARGE before GRANT is
    # skipped.
    led7 = [
        ["CHARGE", "u", 5, 5], ["GRANT", "u", 10, 5], ["GET", "u", 5],
    ]
    print(CreditLedger.simulate(led7))  # [10]

    # Test 8: same timestamps, GRANT arrives first so the CHARGE succeeds.
    led8 = [
        ["GRANT", "u", 10, 5], ["CHARGE", "u", 5, 5], ["GET", "u", 5],
    ]
    print(CreditLedger.simulate(led8))  # [5]

    # Test 9: GET strictly before an event's timestamp excludes it (boundary).
    led9 = [
        ["GRANT", "u", 8, 5], ["GET", "u", 4], ["GET", "u", 5],
    ]
    print(CreditLedger.simulate(led9))  # [0, 8]
