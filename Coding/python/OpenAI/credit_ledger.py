"""A GPU credit ledger fed by a stream of requests whose timestamps are NOT
necessarily increasing. Each GET reflects only the requests that have arrived
so far, evaluated at the query timestamp; a later-arriving request with an
earlier timestamp affects future GETs but never retroactively changes a GET
that was already returned.

Request forms:
    ["GRANT",  user, amount, timestamp]  add amount at timestamp
    ["CHARGE", user, amount, timestamp]  subtract amount IF the running balance
                                         at that moment is >= amount, else ignore
    ["GET",    user, timestamp]          balance considering only arrived events
                                         with timestamp <= the query timestamp

Within a user, events are applied in (timestamp, arrival-order) order — a
stable tie-breaker for equal timestamps. Each GET replays that user's eligible
events from scratch so charge successes reflect the correct ordering.
"""


class _Event:
    """One ledger event for a user."""
    __slots__ = ("is_grant", "amount", "timestamp", "arrival")

    def __init__(self, is_grant, amount, timestamp, arrival):
        self.is_grant = is_grant
        self.amount = amount
        self.timestamp = timestamp
        self.arrival = arrival  # index in the input stream -> stable tie-breaker


class CreditLedger:

    def __init__(self):
        # user -> events that have arrived so far (in arrival order).
        self._ledger = {}

    def grant(self, user, amount, timestamp, arrival):
        """Record a GRANT for user."""
        self._ledger.setdefault(user, []).append(_Event(True, amount, timestamp, arrival))

    def charge(self, user, amount, timestamp, arrival):
        """Record a CHARGE for user (success is decided later, at replay time)."""
        self._ledger.setdefault(user, []).append(_Event(False, amount, timestamp, arrival))

    def get(self, user, timestamp):
        """Balance for user at timestamp, replaying eligible events in order."""
        events = self._ledger.get(user)
        if events is None:
            return 0
        # Eligible events: timestamp <= query time.
        eligible = [e for e in events if e.timestamp <= timestamp]
        # Apply in (timestamp, arrival) order — stable tie-break by arrival.
        eligible.sort(key=lambda e: (e.timestamp, e.arrival))
        balance = 0
        for e in eligible:
            if e.is_grant:
                balance += e.amount
            elif balance >= e.amount:
                balance -= e.amount  # charge applied only when affordable
        return balance

    @staticmethod
    def simulate(requests):
        """Process requests in arrival order, returning every GET in order."""
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
    led1 = [
        ["GRANT", "alice", 10, 5], ["CHARGE", "alice", 4, 7], ["GET", "alice", 7],
        ["CHARGE", "alice", 10, 6], ["GET", "alice", 7],
    ]
    print(CreditLedger.simulate(led1))  # [6, 0]
    led2 = [
        ["GRANT", "alice", 5, 10], ["GRANT", "bob", 7, 1], ["CHARGE", "bob", 2, 3],
        ["GET", "bob", 2], ["GET", "bob", 3], ["GET", "alice", 9], ["GET", "alice", 10],
    ]
    print(CreditLedger.simulate(led2))  # [7, 5, 0, 5]
